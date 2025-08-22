import arxiv
import time
import random
from .openreview_crawling import *

def crawling_basic(search_query: str, num: int = 50, sort_op: str="relevance") -> list[dict[str, str]]:
    """
    Takes a query generated using make_query and retrieves a list of dictionaries containing paper information,
    sorted according to the specified sort option.

    Args:
        search_query: A query generated using the make_query function.
        num (int): Maximum number of papers to retrieve.
        sort_op: Sorting option. Can be one of the following:
            - relevance: by relevance
            - lastupdate: by last updated date
            - submitted: by original submission date

    Returns:
        A list of dictionaries, each representing a document.
    """

    documents = []

    max_results = num

    if sort_op == "relevance":
        search = arxiv.Search(
            query=search_query,
            max_results=num,
            sort_by=arxiv.SortCriterion.Relevance
        )
    elif sort_op == "lastupdate":
        search = arxiv.Search(
            query=search_query,
            max_results=num,
            sort_by=arxiv.SortCriterion.LastUpdatedDate
        )
    else:
        search = arxiv.Search(
          query = search_query,
          max_results = max_results,
          sort_by = arxiv.SortCriterion.SubmittedDate
        )

    client = arxiv.Client()
    results = list(client.results(search))

    for result in results:
      temp_dict = {}

      title = result.title
      temp_dict['title'] = title

      url = result.pdf_url
      temp_dict['url'] = url

      abstract = result.summary
      temp_dict['abstract'] = abstract

      documents.append(temp_dict)

    return documents

# def main_crawling(keyword_list:list[str],
#                   operator: list[str] = ["AND"],
#                   field: list[str] = ["title"],
#                   limit: int = 50,
#                   date: list[int] = None,
#                   accept: bool = True) -> list[dict[str, any]]:
#     # date가 없다면
#     documents = []
#     crawling_num = 0
#     if date is None:
#         # accept 조건이 있다면 그래도 openreview
#         if accept == True:
#             # date 조건이 없으니 api v2 먼저 사용
#             search_query = make_query_openreview_search(keyword_list, operator, field)
#             documents = documents + crawling_openreview_v2(search_query, limit, accept=True)
#             crawling_num += len(documents)
#
#             if crawling_num < limit:
#                 time.sleep(3)
#                 remain_limit = limit - crawling_num
#                 search_query2 = plan_openreview_v1_queries(keyword_list, operator, field)
#                 documents = documents + crawling_openreview_v1(search_query2, remain_limit, accept=True)
#
#                 # 중복 제거 로직 예시 (v1, v2 호출 이후)
#                 unique_docs = {}
#                 for doc in documents:
#                     # url이나 id를 고유 키로 사용
#                     doc_id = doc.get('url') or doc.get('id')
#                     if doc_id not in unique_docs:
#                         unique_docs[doc_id] = doc
#
#                 documents = list(unique_docs.values())
#         # date 조건, accept 조건이 없으니 arxiv 사용
#         else:
#             search_query = make_query_arxiv(keyword_list, operator, field)
#             documents = documents + crawling_basic(search_query, limit)
#     else:
#         search_query = make_query_openreview_search(keyword_list, operator, field)
#         search_query_v1 = plan_openreview_v1_queries(keyword_list, operator, field)
#         documents = crawling_openreview_mix(search_query, search_query_v1, limit, date, accept)
#
#     return documents

def main_crawling(keyword_list: list[str],
                  operator: list[str] = ["AND"],
                  field: list[str] = ["title"],
                  limit: int = 50,
                  date: list[int] = None,
                  accept: bool = True) -> list[dict[str, any]]:
    documents = []
    crawling_num = 0

    if date is None:
        if accept == True:
            # V2 API는 make_query_openreview_search로 만든 문자열 쿼리 사용 (내부 crawling_openreview_v2 함수에서 'query' -> 'term' 수정 필요!)
            search_query_v2 = make_query_openreview_search(keyword_list, operator, field)
            documents += crawling_openreview_v2(search_query_v2, limit, accept=True)
            crawling_num += len(documents)

            if crawling_num < limit:
                print(f"v2 API에서 총 {crawling_num}개 수집. 3초 대기 후 v1 API로 추가 검색...")
                time.sleep(3)
                remain_limit = limit - crawling_num

                # 🛠️ V1 쿼리 생성 로직 수정: 'all' 필드 AND/OR 연산 시 단순 문자열 사용
                if field == ["all"]:
                    # 'all' 필드 검색은 make_query_openreview_search로 V1/V2 공통 쿼리 문자열 생성
                    search_query_v1 = make_query_openreview_search(keyword_list, operator, field)
                    documents += crawling_openreview_v1(search_query_v1, remain_limit, date=None, accept=True)
                else:
                    # 그 외 복합 쿼리는 plan_openreview_v1_queries 사용
                    search_query_v1 = plan_openreview_v1_queries(keyword_list, operator, field)
                    documents += crawling_openreview_v1(search_query_v1, remain_limit, date=None, accept=True)

                # 중복 제거 로직
                unique_docs = {}
                for doc in documents:
                    doc_id = doc.get('url') or doc.get('id')
                    if doc_id and doc_id not in unique_docs:
                        unique_docs[doc_id] = doc
                documents = list(unique_docs.values())
        else:
            # arxiv 사용 로직 (수정 필요 없음)
            search_query = make_query_arxiv(keyword_list, operator, field)
            documents += crawling_basic(search_query, limit)
    else:
        # 🛠️ V1 쿼리 생성 로직 수정: 'all' 필드 AND/OR 연산 시 단순 문자열 사용
        if field == ["all"]:
            search_query = make_query_openreview_search(keyword_list, operator, field)
            search_query_v1 = search_query
        else:
            search_query = make_query_openreview_search(keyword_list, operator, field)
            search_query_v1 = plan_openreview_v1_queries(keyword_list, operator, field)

        documents = crawling_openreview_mix(search_query, search_query_v1, limit, date, accept)

    return documents


def random_crawling(sample_size: int = 20, num: int = 10) -> list[dict[str, str]]:
    """
    Fetches random crawling results.

    Args:
        sample_size: The number of candidates to sample from.
        num: The actual number of documents to return.

    Returns:
        Documents crawled using a random query.
    """

    # List for generating random queries
    query_list = ["the", "a", "is", "of", "and", "in", "to"]

    # Randomly select one item from query_list
    random_query1 = random.choice(query_list)
    random_query2 = random.choice(query_list)
    random_query3 = random.choice(query_list)

    # Crawl using different sort options for the selected query
    doc_relevance = crawling_basic(random_query1, num=sample_size, sort_op="relevance")
    doc_lastupdate = crawling_basic(random_query2, num=sample_size, sort_op="lastupdate")
    doc_submitted = crawling_basic(random_query3, num=sample_size, sort_op="submitted")

    # Combine into one
    random_candidate = doc_relevance + doc_lastupdate + doc_submitted
    # shuffle
    random.shuffle(random_candidate)

    # Slice to keep only 'num' items
    random_document = random_candidate[:num]

    return random_document

