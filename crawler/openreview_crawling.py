import random
import openreview
from datetime import datetime
import time
import re
from .filtering import *

# v1은 2022까지의 자료 찾기
# accept 지원 따로 안하지만
# 나중에 필터링 걸 때 사용하기 위해 date, accept 필터링에 사용할 정보도 같이 들고오자
# --- OpenReview API v1 크롤링 함수 (주로 ~2022년 데이터) ---
def crawling_openreview_v1(search_query: str, limit: int, accept: bool = True) -> list[dict[str, any]]:
    """
    [구 버전 API] OpenReview에서 ~2022년까지의 논문을 페이징하여 검색합니다.
    - limit이 100을 초과하면 100개씩 나누어 요청하고 3초씩 대기합니다.
    """
    documents = []
    client = openreview.api.OpenReviewClient(baseurl='https://api1.openreview.net')

    # 날짜 범위를 유닉스 타임스탬프(ms)로 변환
    start_ts = int(datetime(2023, 1, 1).timestamp() * 1000)

    try:

        # get_all_notes 대신 search_notes를 사용합니다.
        search_iterator = client.search_notes(
            term=search_query
        )

        for note in search_iterator:
            # limit에 도달하면 검색 중단
            if len(documents) >= limit:
                print(f"Limit({limit})에 도달하여 검색을 중단합니다.")
                break

            # accept=True일 경우, 필터링 로직 수행
            if accept:
                decision = note.content.get('decision', {}).get('value', '')
                venue = note.content.get('venue', {}).get('value', '')

                # decision 또는 venue 필드에 'accept'가 포함되어 있는지 확인 (대소문자 무시)
                if re.search('accept', decision, re.IGNORECASE) or re.search('accept', venue, re.IGNORECASE):
                    documents.append({
                        'title': note.content.get('title', {}).get('value', 'N/A'),
                        'url': f"https://openreview.net/forum?id={note.id}",
                        'abstract': note.content.get('abstract', {}).get('value', 'N/A'),
                        'cdate': note.cdate,
                        'decision_info': decision or venue
                    })
            else:  # accept=False이면 필터링 없이 모두 추가
                documents.append({
                    'title': note.content.get('title', {}).get('value', 'N/A'),
                    'url': f"https://openreview.net/forum?id={note.id}",
                    'abstract': note.content.get('abstract', {}).get('value', 'N/A'),
                    'cdate': note.cdate,
                    'decision_info': ""  # 필터링 안했으므로 비워둠
                })

        print(f"v2 API에서 최종 {len(documents)}개의 논문을 찾았습니다.")

    except Exception as e:
        print(f"v2 API 검색 중 오류 발생: {e}")

    return documents


# --- 값 추출 유틸: v1( {'value': ...} ) / v2( "..." ) 모두 문자열로 ---
def _as_str(x) -> str:
    if isinstance(x, dict) and 'value' in x:
        v = x.get('value', '')
        return '' if v is None else str(v)
    return '' if x is None else (', '.join(map(str, x)) if isinstance(x, (list, tuple)) else str(x))

# --- resetTime 파싱 & 대기 유틸 ---
def _extract_reset_time(err) -> str | None:
    """
    OpenReview RateLimitError 메시지에서 resetTime(ISO) 뽑기.
    - err가 dict/객체/문자열 어느 형태로 와도 최대한 캐치
    """
    # 1) dict 형태로 들어온 경우
    if isinstance(err, dict):
        # {'details': {'resetTime': '2025-08-22T14:41:17.038Z'}} 같은 구조
        details = err.get('details') or {}
        if isinstance(details, dict) and details.get('resetTime'):
            return details['resetTime']
        if err.get('resetTime'):
            return err['resetTime']

    # 2) 예외 객체의 속성으로 들어온 경우
    if hasattr(err, 'details') and isinstance(getattr(err, 'details'), dict):
        rt = err.details.get('resetTime')
        if rt:
            return rt

    # 3) 문자열로 들어온 경우에서 정규식으로 추출
    msg = str(err)
    m = re.search(r'resetTime[\"\'\s:]*([=:]?)\s*[\"\']?([0-9T:\.\-]+Z)[\"\' ]?', msg)
    if m:
        return m.group(2)
    return None

def _sleep_until_iso(iso: str, fallback_secs: int = 3):
    """ISO8601(Z) 시간까지 대기. 실패 시 fallback 대기."""
    try:
        rt = datetime.fromisoformat(iso.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        wait = max(0.0, (rt - now).total_seconds())
        time.sleep(wait)
    except Exception:
        time.sleep(fallback_secs)


def crawling_openreview_v2(
        search_query: str,
        limit: int,
        accept: bool = True
) -> list[dict[str, any]]:
    """
    [신 버전 API] OpenReview에서 특정 기간의 논문을 검색하고 accept 여부로 필터링합니다.
    - get_all_notes 대신 search_notes를 사용하여 키워드 검색을 수행합니다.
    - sort_op='relevance'는 search_notes의 기본 동작이므로 별도 처리가 필요 없습니다.
    - limit이 100을 넘으면 100개 단위로 끊어 가져오며, 배치 사이에는 고정 3초 대기합니다.
    - 레이트리밋(429) 등 오류가 나면 배치당 최대 3회 재시도, 429면 resetTime까지 추가 대기합니다.
    - 재시도 실패 시 현재까지 수집한 documents를 반환합니다.
    """
    print(f"--- OpenReview v2 API로 검색을 시작합니다 ---")
    documents = []
    client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')

    # 최소 invitation 컷(댓글/리뷰/리스폰스 제거), 제출물 위주
    _non_submission = re.compile(r'/(Comment|Rebuttal|Review)\b', re.IGNORECASE)

    # 고정 대기(배치 사이)
    FIXED_SLEEP_SECS = 3
    # 배치 최대 크기
    BATCH_CAP = 100
    # 배치당 재시도 횟수
    MAX_RETRIES = 3

    try:
        collected = 0
        offset = 0

        while collected < limit:
            to_fetch = min(BATCH_CAP, max(1, limit - collected))

            # ---- 서버 호출 (재시도 포함, 429면 resetTime까지 추가 대기) ----
            notes = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    notes = client.search_notes(
                        term=search_query,
                        limit=to_fetch,
                        offset=offset
                    )
                    break  # 성공
                except Exception as e:
                    print(f"[경고] 배치 요청 실패({attempt}/{MAX_RETRIES}): {e}")
                    msg = str(e).lower()

                    # 429 / RateLimitError 감지 → resetTime까지 대기
                    if '429' in msg or 'ratelimiterror' in msg or 'too many requests' in msg:
                        reset_iso = None
                        # e 자체에서 추출 시도
                        if hasattr(e, 'args') and e.args:
                            reset_iso = _extract_reset_time(e.args[0])
                        if not reset_iso:
                            reset_iso = _extract_reset_time(e)
                        if reset_iso:
                            print(f"[안내] 레이트리밋 발생: resetTime={reset_iso} 까지 대기합니다.")
                            _sleep_until_iso(reset_iso, fallback_secs=FIXED_SLEEP_SECS)
                        else:
                            # resetTime을 못 읽으면 고정 3초만
                            time.sleep(FIXED_SLEEP_SECS)
                    else:
                        # 비-429 에러면 점증 대기(1,2) + 마지막은 고정 3초
                        time.sleep(FIXED_SLEEP_SECS if attempt == MAX_RETRIES else max(1, attempt - 1))

                    if attempt == MAX_RETRIES:
                        print("[오류] 재시도 한계를 초과했습니다. 지금까지 수집한 문서를 반환합니다.")
                        return documents  # 부분 결과 반환

            if not notes:
                break  # 더 이상 결과 없음

            got_from_server = 0
            for note in notes:
                got_from_server += 1

                # 제출물 위주: replyto가 있으면 댓글/리뷰 가능성 ↑ → 컷
                if getattr(note, 'replyto', None):
                    continue
                inv = getattr(note, 'invitation', '') or ''
                if _non_submission.search(inv):
                    continue

                c = note.content or {}
                title = _as_str(c.get('title')).strip()
                abstract = _as_str(c.get('abstract')).strip()
                if not title or not abstract:  # abstract 필수
                    continue

                decision = _as_str(c.get('decision'))
                venue    = _as_str(c.get('venue'))

                if accept:
                    blob = f"{decision} {venue}".lower()
                    if 'reject' in blob:
                        continue
                    decision_info = decision or venue
                else:
                    decision_info = ""

                forum_id = getattr(note, 'forum', None) or note.id
                documents.append({
                    'title': title,
                    'url': f"https://openreview.net/forum?id={forum_id}",
                    'abstract': abstract,
                    'cdate': note.cdate,
                    'decision_info': decision_info
                })

                collected += 1
                if collected >= limit:
                    print(f"Limit({limit})에 도달하여 검색을 중단합니다.")
                    break

            # 다음 페이지로
            offset += got_from_server

            # --- 배치 사이 고정 대기(요청자 요구 유지) ---
            if collected < limit:
                time.sleep(FIXED_SLEEP_SECS)

        print(f"v2 API에서 최종 {len(documents)}개의 논문을 찾았습니다.")

    except Exception as e:
        print(f"[오류] v2 API 검색 중 예외 발생: {e} — 현재까지 수집한 {len(documents)}개를 반환합니다.")

    return documents



def crawling_openreview_mix(search_query: str, search_query_v1, limit: int = 50, date: list[int] = [2021, 2025], accept = True):
    documents_v1 = []
    documents_v2 = []

    client_v1 = openreview.Client(baseurl='https://api.openreview.net')
    client_v2 = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')

    # 얼마씩 나눠서 가져올지 결정
    year_v1 = 2023 - date[0]
    year_v2 = date[1] - 2022

    total_year = year_v1 + year_v2

    # 변환한 limit
    limit_v1 = round((year_v1 / total_year) * limit)
    limit_v2 = round((year_v2 / total_year) * limit)

    # 혹시 모를 반올림 오류를 위해, 총합이 total_limit을 넘지 않도록 보정
    if limit_v1 + limit_v2 > limit:
        limit_v1 = limit - limit_v2
    if limit_v1 <= 0: limit_v1 = 1  # 최소 1개는 가져오도록 설정

    date_v1 = [date[0], 2022]
    date_v2 = [2023, date[1]]

    documents_v1 = crawling_openreview_v1(search_query_v1, limit_v1, accept=True)
    documents_v2 = crawling_openreview_v2(search_query, limit_v2, accept=True)

    return documents_v1 + documents_v2