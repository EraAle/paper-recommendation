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
# def crawling_openreview_v1(search_query: str, limit: int, date: list[int] = None, accept: bool = True) -> list[dict[str, any]]:
#     """
#     [구 버전 API] OpenReview에서 ~2022년까지의 논문을 페이징하여 검색합니다.
#     - limit이 100을 초과하면 100개씩 나누어 요청하고 3초씩 대기합니다.
#     """
#     print("--- OpenReview v1 API로 검색을 시작합니다 (~2022년 데이터) ---")
#     PAGE_SIZE = 100
#     documents = []
#     offset = 0
#     client = openreview.Client(baseurl='https://api.openreview.net')
#
#     # 2022년 12월 31일을 기준으로 그 이전 데이터만 가져오도록 설정
#     end_date_v1 = datetime(2023, 12, 31, 23, 59, 59)
#     maxtcdate_v1 = int(time.mktime(end_date_v1.timetuple()) * 1000)
#
#     try:
#         while len(documents) < limit:
#             # 이번 페이지에서 가져올 개수 계산
#             remaining_limit = limit - len(documents)
#             current_page_limit = min(PAGE_SIZE, remaining_limit)
#
#             print(f"v1 API: {offset}번째부터 {current_page_limit}개의 논문을 가져옵니다...")
#
#             if date is None:
#                 # offset과 limit을 사용하여 페이징 수행
#                 page_results = client.get_notes(
#                     query=search_query,
#                     limit=current_page_limit,
#                     offset=offset,
#                     maxtcdate=maxtcdate_v1
#                 )
#             else:
#                 end_date_v1 = datetime(date[1], 12, 31, 23, 59, 59)
#                 start_date_v1 = datetime(date[0], 1, 1, 00, 00, 00)
#
#                 maxtcdate_v1 = int(time.mktime(end_date_v1.timetuple()) * 1000)
#                 mintcdate_v1 = int(time.mktime(start_date_v1.timetuple()) * 1000)
#
#                 page_results = client.get_notes(
#                     query=search_query,
#                     limit=current_page_limit,
#                     offset=offset,
#                     mintcdate=mintcdate_v1,
#                     maxtcdate=maxtcdate_v1
#                 )
#
#             # 더 이상 가져올 결과가 없으면 루프 종료
#             if not page_results:
#                 print("더 이상 결과가 없어 검색을 중단합니다.")
#                 break
#
#             for note in page_results:
#                 decision = note.content.get('decision', {}).get('value', '')
#                 venue = note.content.get('venue', {}).get('value', '')
#                 documents.append({
#                     'title': note.content.get('title', 'N/A'),
#                     'url': f"https://openreview.net/forum?id={note.id}",
#                     'abstract': note.content.get('abstract', 'N/A'),
#                     'cdate': note.cdate,
#                     'decision_info': decision or venue
#                 })
#
#             offset += len(page_results)
#
#             if accept == True:
#                 documents = v1_accept_filter(documents)
#
#             # limit에 도달하지 않았고, 가져온 결과가 있다면 다음 요청 전에 대기
#             if len(documents) < limit and page_results:
#                 print(f"... 총 {len(documents)}개 수집 완료. 3초간 대기합니다 ...")
#                 time.sleep(3)
#
#         print(f"v1 API에서 최종 {len(documents)}개의 논문을 찾았습니다.")
#
#     except Exception as e:
#         print(f"v1 API 검색 중 오류 발생: {e}")
#
#     return documents
def crawling_openreview_v1(search_query: any, limit: int, date: list[int] = None, accept: bool = True) -> list[
    dict[str, any]]:
    print("--- OpenReview v1 API로 검색을 시작합니다 (~2022년 데이터) ---")
    PAGE_SIZE = 100
    documents = []
    offset = 0
    client = openreview.Client(baseurl='https://api.openreview.net')

    # 🛠️ 쿼리 파라미터를 동적으로 설정
    params = {'limit': PAGE_SIZE, 'offset': offset}
    if isinstance(search_query, str):
        params['term'] = search_query  # 🛠️ query -> term
    elif isinstance(search_query, dict):
        params['content'] = search_query  # 🛠️ plan_openreview_v1_queries의 결과(딕셔너리) 처리

    # 날짜 설정 (v1은 mintcdate, maxtcdate가 아직 유효)
    if date:
        params['mintcdate'] = int(datetime(date[0], 1, 1).timestamp() * 1000)
        params['maxtcdate'] = int(datetime(date[1], 12, 31, 23, 59, 59).timestamp() * 1000)
    else:
        # 기본값: 2022년 12월 31일 이전
        params['maxtcdate'] = int(datetime(2022, 12, 31, 23, 59, 59).timestamp() * 1000)

    try:
        while len(documents) < limit:
            params['limit'] = min(PAGE_SIZE, limit - len(documents))
            params['offset'] = offset

            print(f"v1 API: {offset}번째부터 {params['limit']}개의 논문을 가져옵니다...")
            page_results = client.get_notes(**params)

            if not page_results:
                print("더 이상 결과가 없어 검색을 중단합니다.")
                break

            # ... (기존 데이터 추가 및 필터링 로직) ...
            for note in page_results:
                decision = note.content.get('decision', {}).get('value', '')
                venue = note.content.get('venue', {}).get('value', '')
                documents.append({
                    'title': note.content.get('title', 'N/A'),
                    'url': f"https://openreview.net/forum?id={note.id}",
                    'abstract': note.content.get('abstract', 'N/A'),
                    'cdate': note.cdate,
                    'decision_info': decision or venue
                })

            offset += len(page_results)

            if accept:
                documents = v1_accept_filter(documents)  # v1_accept_filter 함수가 있다고 가정

            if len(documents) < limit and page_results:
                print(f"... 총 {len(documents)}개 수집 완료. 3초간 대기합니다 ...")
                time.sleep(3)

        print(f"v1 API에서 최종 {len(documents)}개의 논문을 찾았습니다.")
    except Exception as e:
        print(f"v1 API 검색 중 오류 발생: {e}")

    return documents

# def crawling_openreview_v2(
#         search_query: str,
#         limit: int,
#         date: list[int] = None,
#         accept: bool = True
# ) -> list[dict[str, any]]:
#     """
#     [신 버전 API] OpenReview에서 특정 기간의 논문을 검색하고 accept 여부로 필터링합니다.
#     - get_all_notes 대신 search_notes를 사용하여 키워드 검색을 수행합니다.
#     - sort_op='relevance'는 search_notes의 기본 동작이므로 별도 처리가 필요 없습니다.
#
#     Args:
#         search_query: 검색할 쿼리 문자열 (예: 'title:"large language model"')
#         limit: 가져올 최대 논문 수
#         sort_op: 정렬 옵션 ('relevance'가 기본값).
#         date: 검색할 연도 범위 [시작, 종료].
#         accept: True이면 Accept된 논문만 필터링.
#
#     Returns:
#         논문 정보 딕셔너리의 리스트
#     """
#     print(f"--- OpenReview v2 API로 검색을 시작합니다 ---")
#     documents = []
#     client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')
#
#     # 날짜 범위를 유닉스 타임스탬프(ms)로 변환
#     start_ts = int(datetime(2023, 1, 1).timestamp() * 1000)
#
#
#     try:
#         if date is None:
#             # get_all_notes 대신 search_notes를 사용합니다.
#             search_iterator = client.search_notes(
#                 term=search_query,
#                 mintcdate=start_ts
#             )
#         else:
#             # 날짜 범위를 유닉스 타임스탬프(ms)로 변환
#             start_ts = int(datetime(date[0], 1, 1).timestamp() * 1000)
#             end_ts = int(datetime(date[1], 12, 31, 23, 59, 59).timestamp() * 1000)
#
#             # get_all_notes 대신 search_notes를 사용합니다.
#             search_iterator = client.search_notes(
#                 term=search_query,
#                 mintcdate=start_ts,
#                 maxtcdate=end_ts
#             )
#
#         for note in search_iterator:
#             # limit에 도달하면 검색 중단
#             if len(documents) >= limit:
#                 print(f"Limit({limit})에 도달하여 검색을 중단합니다.")
#                 break
#
#             # accept=True일 경우, 필터링 로직 수행
#             if accept:
#                 decision = note.content.get('decision', {}).get('value', '')
#                 venue = note.content.get('venue', {}).get('value', '')
#
#                 # decision 또는 venue 필드에 'accept'가 포함되어 있는지 확인 (대소문자 무시)
#                 if re.search('accept', decision, re.IGNORECASE) or re.search('accept', venue, re.IGNORECASE):
#                     documents.append({
#                         'title': note.content.get('title', {}).get('value', 'N/A'),
#                         'url': f"https://openreview.net/forum?id={note.id}",
#                         'abstract': note.content.get('abstract', {}).get('value', 'N/A'),
#                         'cdate': note.cdate,
#                         'decision_info': decision or venue
#                     })
#             else:  # accept=False이면 필터링 없이 모두 추가
#                 documents.append({
#                     'title': note.content.get('title', {}).get('value', 'N/A'),
#                     'url': f"https://openreview.net/forum?id={note.id}",
#                     'abstract': note.content.get('abstract', {}).get('value', 'N/A'),
#                     'cdate': note.cdate,
#                     'decision_info': ""  # 필터링 안했으므로 비워둠
#                 })
#
#         print(f"v2 API에서 최종 {len(documents)}개의 논문을 찾았습니다.")
#
#     except Exception as e:
#         print(f"v2 API 검색 중 오류 발생: {e}")
#
#     return documents

def crawling_openreview_v2(
        search_query: str,
        limit: int,
        date: list[int] = None,
        accept: bool = True
) -> list[dict[str, any]]:
    print(f"--- OpenReview v2 API로 검색을 시작합니다 ---")
    documents = []
    client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')

    try:
        # 🛠️ 'query' -> 'term' 변경 및 날짜 검색 방식 수정
        params = {'term': search_query}

        if date is None:
            # 2023년 1월 1일 이후 데이터만 가져오도록 설정
            start_ts = int(datetime(2023, 1, 1).timestamp() * 1000)
            params['cdate'] = {'gte': start_ts}  # 🛠️ mintcdate 대신 cdate 사용
        else:
            start_ts = int(datetime(date[0], 1, 1).timestamp() * 1000)
            end_ts = int(datetime(date[1], 12, 31, 23, 59, 59).timestamp() * 1000)
            params['cdate'] = {'gte': start_ts, 'lte': end_ts}  # 🛠️ mintcdate, maxtcdate 대신 cdate 사용

        search_iterator = client.search_notes(**params)

        # 이하 로직은 동일
        for note in search_iterator:
            if len(documents) >= limit:
                break

            # ... (기존 accept 필터링 및 데이터 추가 로직) ...
            if accept:
                decision = note.content.get('decision', {}).get('value', '')
                venue = note.content.get('venue', {}).get('value', '')
                if re.search('accept', decision, re.IGNORECASE) or re.search('accept', venue, re.IGNORECASE):
                    documents.append({
                        'title': note.content.get('title', {}).get('value', 'N/A'),
                        'url': f"https://openreview.net/forum?id={note.id}",
                        'abstract': note.content.get('abstract', {}).get('value', 'N/A'),
                        'cdate': note.cdate,
                        'decision_info': decision or venue
                    })
            else:
                documents.append({
                    'title': note.content.get('title', {}).get('value', 'N/A'),
                    'url': f"https://openreview.net/forum?id={note.id}",
                    'abstract': note.content.get('abstract', {}).get('value', 'N/A'),
                    'cdate': note.cdate,
                    'decision_info': ""
                })

        print(f"v2 API에서 최종 {len(documents)}개의 논문을 찾았습니다.")
    except Exception as e:
        print(f"v2 API 검색 중 오류 발생: {e}")

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

    documents_v1 = crawling_openreview_v1(search_query_v1, limit_v1, date_v1, accept=True)
    documents_v2 = crawling_openreview_v2(search_query, limit_v2, date_v2, accept=True)

    return documents_v1 + documents_v2