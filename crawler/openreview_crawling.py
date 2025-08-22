import random
import openreview
from datetime import datetime
import time
import re
from .filtering import *


# venue마다 형식이 달라서, 다 v2에서 사용하는 문자열로 변환
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

# search_notes를 사용하는데, 이건 relevance로 가져온다
# 100개 넘으면 귾어서 가져온다. 그 사이는 3초 쉬기
# 오류나면 3번 재시도. 만약 그 쉬라는 에러면 정말로 쉰다
# 중복 제거
def crawling_openreview_v2(
        search_query: str,
        limit: int,
        accept: bool = True
) -> list[dict[str, any]]:

    documents = []
    seen_forums = set()
    client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')

    _non_submission = re.compile(r'/(Comment|Rebuttal|Review)\b', re.IGNORECASE)
    FIXED_SLEEP_SECS = 3
    BATCH_CAP = 100
    MAX_RETRIES = 3

    try:
        collected = 0
        offset = 0

        while collected < limit:
            to_fetch = min(BATCH_CAP, max(1, limit - collected))

            notes = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    notes = client.search_notes(
                        term=search_query,
                        limit=to_fetch,
                        offset=offset
                    )
                    break
                except Exception as e:
                    print(f"error. retry ({attempt}/{MAX_RETRIES}): {e}")
                    msg = str(e).lower()
                    if '429' in msg or 'ratelimiterror' in msg or 'too many requests' in msg:
                        reset_iso = None
                        if hasattr(e, 'args') and e.args:
                            reset_iso = _extract_reset_time(e.args[0])
                        if not reset_iso:
                            reset_iso = _extract_reset_time(e)
                        if reset_iso:
                            print(f"limit error: resetTime={reset_iso} .")
                            _sleep_until_iso(reset_iso, fallback_secs=FIXED_SLEEP_SECS)
                        else:
                            time.sleep(FIXED_SLEEP_SECS)
                    else:
                        time.sleep(FIXED_SLEEP_SECS if attempt == MAX_RETRIES else max(1, attempt - 1))
                    if attempt == MAX_RETRIES:
                        print("error and return.")
                        return documents

            if not notes:
                break

            got_from_server = 0
            for note in notes:
                got_from_server += 1

                if getattr(note, 'replyto', None):
                    continue
                inv = getattr(note, 'invitation', '') or ''
                if _non_submission.search(inv):
                    continue

                c = note.content or {}
                title = _as_str(c.get('title')).strip()
                abstract = _as_str(c.get('abstract')).strip()
                if not title or not abstract:
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

                if forum_id in seen_forums:
                    continue
                seen_forums.add(forum_id)

                documents.append({
                    'title': title,
                    'url': f"https://openreview.net/forum?id={forum_id}",
                    'abstract': abstract,
                    'cdate': note.cdate,
                    'decision_info': decision_info
                })

                collected += 1
                if collected >= limit:
                    break

            offset += got_from_server
            if collected < limit:
                time.sleep(FIXED_SLEEP_SECS)


    except Exception as e:
        print(f"error and return: {e}")

    return documents

