import arxiv
import time
import random
from .openreview_crawling import *

import arxiv
import time


def crawling_basic(search_query: str, num: int = 50, sort_op: str = "relevance") -> list[dict[str, str]]:
    """
    쿼리를 이용해 논문 정보를 리스트 형태로 가져옵니다.
    검색 중 오류 발생 시, 그때까지 수집된 데이터를 반환합니다.
    """
    documents = []  # try 블록 밖에서 선언해야 except에서도 접근 가능합니다.

    try:
        sort_criterion_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastupdate": arxiv.SortCriterion.LastUpdatedDate,
            "submitted": arxiv.SortCriterion.SubmittedDate
        }
        sort_criterion = sort_criterion_map.get(sort_op, arxiv.SortCriterion.SubmittedDate)

        search = arxiv.Search(
            query=search_query,
            max_results=num,
            sort_by=sort_criterion
        )

        client = arxiv.Client()
        results = client.results(search)

        print(f"총 {num}개의 논문 검색을 시작합니다.")

        for result in results:
            temp_dict = {
                'title': result.title,
                'url': result.pdf_url,
                'abstract': result.summary,
                'updated_date': result.updated
            }
            documents.append(temp_dict)

            # 100건마다 4초 대기
            if len(documents) % 100 == 0 and len(documents) < num:
                print(f"현재 {len(documents)}개 검색 완료. API 요청 제한을 위해 4초간 대기합니다...")
                time.sleep(4)

        print(f"총 {len(documents)}개의 논문 검색을 완료했습니다.")

    except Exception as e:
        # try 블록 안에서 어떤 종류의 에러든 발생하면 이 코드가 실행됩니다.
        print(f"\n[!] 검색 중 오류가 발생했습니다: {e}")
        print(f"지금까지 수집된 {len(documents)}개의 논문을 반환합니다.")

    # 성공적으로 완료되었거나, 오류가 발생하여 except 블록에서 반환되지 않은 경우
    # 최종적으로 수집된 documents를 반환합니다.
    return documents


def main_crawling(search_query,
                  num: int = 50,
                  sort_op: str = "relevance",
                  date: list[int] = None) -> list[dict[str, any]]:

    if date is None:
        documents = crawling_basic(search_query, num, sort_op)
    else:
        new_num = 3 * num
        documents = crawling_basic(search_query, new_num, sort_op)
        documents = arxiv_date_filter(documents, date)
        if len(documents) > num:
            documents = documents[:num]
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

