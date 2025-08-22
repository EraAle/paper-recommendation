from datetime import datetime
import re
from .query import *
from .openreview_crawling import *

# 만약 년도 상한은 필터로 쓰고 싶지 않고 accept여부만 쓰고 싶다면
# 년도 상한에는 None을 입력
# accept 여부는 필터링에 사용하지 않을거면 False로 두기
# openreview api는 두 가지로 나뉘어서, 년도 상한이 있다면 그걸 고려해야 할듯.
# 년도 상한에 맞게 crawling_openreview로 논문 가져와야겠다
# 최대한 num에 맞게 retry해서 사용하되, 에러 나도 3번 정도 시도하고 그래도 실패하면 그냥 거기서 끝내자

# api2는 날짜별 필터링 검색을 지원하지만
# api1은 지원하지 않아서 따로 filtering하자
# def crawling_filtering_api_v1(document: list[dict[str, str]], date: list[int], sort_op: str="relevance", accept = True) -> list[dict[str, str]]:
#     """
#         crawling_openreview (API v1)로부터 받은 결과 리스트를 연도(date)에 맞게 필터링합니다.
#
#         Args:
#             documents: 'cdate' (Unix timestamp in ms)를 포함하는 논문 딕셔너리 리스트.
#             date: 필터링할 시작 연도와 종료 연도. 예: [2021, 2022]
#
#         Returns:
#             지정된 연도 범위에 해당하는 논문 딕셔너리 리스트.
#         """
#     if not date or len(date) != 2:
#         # 날짜 정보가 없으면 필터링 없이 그대로 반환
#         return document
#
#     start_year, end_year = date
#     filtered_documents = []
#
#     for paper in document:
#         # 'cdate' 키가 없는 경우를 대비한 예외 처리
#         if 'cdate' not in paper or not paper['cdate']:
#             continue
#
#         # 1. Unix 타임스탬프(ms)를 datetime 객체로 변환
#         timestamp_ms = paper['cdate']
#         creation_date = datetime.fromtimestamp(timestamp_ms / 1000)
#
#         # 2. 연도를 추출하여 범위 내에 있는지 확인
#         publication_year = creation_date.year
#         if start_year <= publication_year <= end_year:
#             filtered_documents.append(paper)
#
#     return filtered_documents

def v1_accept_filter(documents: list[dict]) -> list[dict]:
    """
       crawling_openreview_v1 함수로 수집된 논문 리스트에서
       accept 되었다고 판단되는 논문만 필터링합니다.

       Args:
           documents: v1 API를 통해 수집된 논문 딕셔너리의 리스트

       Returns:
           필터링된 논문 딕셔너리의 리스트
       """
    # Accept으로 간주할 키워드 패턴 (대소문자 무시)
    # Oral, Poster, Spotlight 발표 역시 Accept된 논문이므로 포함합니다.
    accept_pattern = re.compile('accept|oral|poster|spotlight', re.IGNORECASE)

    filtered_documents = [
        doc for doc in documents
        if accept_pattern.search(doc.get('decision_info', ''))
    ]

    print(f"v1 필터링: {len(documents)}개 중 {len(filtered_documents)}개의 'Accept' 논문을 찾았습니다.")
    return filtered_documents

# def v1_all(keyword: list[str], operator: list[str] = ["AND"], limit: int = 50, date: list[int] = None, accept:bool = False) -> list[dict[str, any]]:
#     title_query = make_query_openreview_search(keyword, operator, field=["title"])
#     title_documents = crawling_openreview_v1(title_query, limit, date, accept)
#
#     abstract_query = make_query_openreview_search(keyword, operator, field=["abstract"])
#     abstract_documents = crawling_openreview_v1(abstract_query, limit, date)
#
#     authors_query = make_query_openreview_search(keyword, operator, field=["authors"])
#     authors_documents = crawling_openreview_v1(authors_query, limit, date)
#
#     authorids_query = make_query_openreview_search(keyword, operator, field=["authorids"])
#     authorids_documents = crawling_openreview_v1(authorids_query, limit, date)
#
#     venueid_query = make_query_openreview_search(keyword, operator, field=["venueid"])
#     venueid_documents = crawling_openreview_v1(venueid_query, limit, date)
#
#     documents = title_documents + abstract_documents + authors_documents + authorids_documents + venueid_documents
#
#     return documents

def arxiv_date_filter(documents: list[dict[str, any]], date: list[int]) -> list[dict[str, any]]:
    """
    논문 리스트에서 특정 연도 범위(최종 수정일 기준)에 해당하는 논문만 필터링합니다.
    """
    if not date or len(date) != 2:
        return documents

    start_year, end_year = date[0], date[1]
    filtered_documents = []

    print(f"\n{start_year}년부터 {end_year}년까지의 논문을 (최종 수정일 기준으로) 필터링합니다...")

    for doc in documents:
        # ★★★ updated_date를 기준으로 필터링하도록 변경 ★★★
        if 'updated_date' in doc and isinstance(doc['updated_date'], datetime):
            paper_year = doc['updated_date'].year
            if start_year <= paper_year <= end_year:
                filtered_documents.append(doc)

    print(f"필터링 완료: 총 {len(documents)}개 중 {len(filtered_documents)}개 논문이 선택되었습니다.")
    return filtered_documents


def na_filter(documents: list[dict[str, any]]) -> list[dict[str, any]]:
    filtered_documents = []
    for doc in documents:
        title = str(doc.get('title', '') or '').strip()
        abstract = str(doc.get('abstract', '') or '').strip()
        url = str(doc.get('url', '') or '').strip()

        # 모든 필드가 유효해야 통과 (AND)
        ok_title = (title and title.upper() != 'N/A')
        ok_abstract = (abstract and abstract.upper() != 'N/A')
        ok_url = (url and url.upper() != 'N/A' and url.startswith(('http://', 'https://')))

        if ok_title and ok_abstract and ok_url:
            filtered_documents.append(doc)

    print(f"필터링 완료: 총 {len(documents)}개 중 {len(filtered_documents)}개 논문이 선택되었습니다.")
    return filtered_documents