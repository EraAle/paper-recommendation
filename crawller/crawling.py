import arxiv
import random
import openreview
from datetime import datetime


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

# openreview는 두 가지 버전의 api.
# v1: 예전 api. 2023 이전의 자료는 여기서 찾아라
# v2: 2023 이후의 자료는 여기서 찾아라. 2023도 포함이다.
# 기간을 2021~2025 이런식으로 지정하면 그 구간 내에서 가져오자. 참고로 <= 다 이거다 부등호. '=' 들어감
def crawling_openreview(search_query: str, limit: int = 50, sort_op: str="relevance", date: list[int] = [2021, 2025], accept = True) -> list[dict[str, str]]:
    """
    Takes a query generated using make_query and retrieves a list of dictionaries containing paper information,
    sorted according to the specified sort option.

    Args:
        search_query: A query generated using the make_query function.
        limit (int): Maximum number of papers to retrieve.
        sort_op: Sorting option. Can be one of the following:
            - relevance: by relevance
            - lastupdate: by last updated date
            - submitted: by original submission date

    Returns:
        A list of dictionaries, each representing a document.
    """


    # 1. API 클라이언트 설정 (API V2 사용)
    if date[0] >= 2023:
        documents = []
        client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')
        # 3. OpenReview에 논문 검색 요청
        # client.get_all_notes()는 검색 결과를 순회할 수 있는 iterator를 반환합니다.
        # query: 제목, 초록, 저자 등 주요 필드에서 검색할 키워드입니다.

        client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')
        start_ts = int(datetime(date[0], 1, 1).timestamp() * 1000)
        end_ts = int(datetime(date[1], 12, 31, 23, 59, 59).timestamp() * 1000)

        search_results = client.get_all_notes(
            query=search_query,
            cdate=start_ts,
            details='direct',  # 리뷰나 댓글 등 부가 정보 제외, 직접적인 내용만 가져옵니다.
        )

        documents = []
        for note in search_results:
            if len(documents) >= limit: break
            if note.cdate <= end_ts:
                documents.append({
                    'title': note.content.get('title', {}).get('value', 'N/A'),
                    'url': f"https://openreview.net/forum?id={note.id}",
                    'abstract': note.content.get('abstract', {}).get('value', 'N/A'),
                    'cdate': note.cdate
                })

    elif date[1] < 2023:
        documents = []
        client = openreview.Client(baseurl='https://api.openreview.net')
        # 3. OpenReview에 논문 검색 요청
        # client.get_all_notes()는 검색 결과를 순회할 수 있는 iterator를 반환합니다.
        # query: 제목, 초록, 저자 등 주요 필드에서 검색할 키워드입니다.
        search_results = client.get_notes(
            query=search_query,
            details='direct',  # 리뷰나 댓글 등 부가 정보 제외, 직접적인 내용만 가져옵니다.
            limit=limit
        )

        for note in search_results:
            # 각 note 객체에서 필요한 정보 추출
            title = note.content.get('title', {}).get('value', 'N/A')
            abstract = note.content.get('abstract', {}).get('value', 'N/A')

            # 논문의 고유 ID를 사용하여 URL 생성
            paper_id = note.id
            url = f"https://openreview.net/forum?id={paper_id}"

            creation_timestamp = note.cdate

            documents.append({
                'title': title,
                'url': url,
                'abstract': abstract,
                'cdate': creation_timestamp
            })

    else:
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

        # 3. OpenReview에 논문 검색 요청
        # client.get_all_notes()는 검색 결과를 순회할 수 있는 iterator를 반환합니다.
        # query: 제목, 초록, 저자 등 주요 필드에서 검색할 키워드입니다.
        search1 = client_v1.get_notes(
            query=search_query,
            details='direct',  # 리뷰나 댓글 등 부가 정보 제외, 직접적인 내용만 가져옵니다.
            limit=limit_v1
        )

        search2 = client_v2.get_all_notes(
            query=search_query,
            details='direct',  # 리뷰나 댓글 등 부가 정보 제외, 직접적인 내용만 가져옵니다.
            limit=limit_v2
        )

        for note in search1:
            # 각 note 객체에서 필요한 정보 추출
            title = note.content.get('title', {}).get('value', 'N/A')
            abstract = note.content.get('abstract', {}).get('value', 'N/A')

            # 논문의 고유 ID를 사용하여 URL 생성
            paper_id = note.id
            url = f"https://openreview.net/forum?id={paper_id}"

            creation_timestamp = note.cdate

            documents_v1.append({
                'title': title,
                'url': url,
                'abstract': abstract,
                'cdate': creation_timestamp
            })
        documents_v1_filtering = crawling_filtering_api_v1(documents_v1, date)

        for note2 in search2:
            # 각 note 객체에서 필요한 정보 추출
            title = note2.content.get('title', {}).get('value', 'N/A')
            abstract = note2.content.get('abstract', {}).get('value', 'N/A')

            # 논문의 고유 ID를 사용하여 URL 생성
            paper_id = note2.id
            url = f"https://openreview.net/forum?id={paper_id}"

            creation_timestamp = note2.cdate

            documents_v2.append({
                'title': title,
                'url': url,
                'abstract': abstract,
                'cdate': creation_timestamp
            })

        documents = documents_v1_filtering + documents_v2
        random.shuffle(documents)
        documents = documents[:limit]

    return documents

# 만약 년도 상한은 필터로 쓰고 싶지 않고 accept여부만 쓰고 싶다면
# 년도 상한에는 None을 입력
# accept 여부는 필터링에 사용하지 않을거면 False로 두기
# openreview api는 두 가지로 나뉘어서, 년도 상한이 있다면 그걸 고려해야 할듯.
# 년도 상한에 맞게 crawling_openreview로 논문 가져와야겠다
# 최대한 num에 맞게 retry해서 사용하되, 에러 나도 3번 정도 시도하고 그래도 실패하면 그냥 거기서 끝내자

# api2는 날짜별 필터링 검색을 지원하지만
# api1은 지원하지 않아서 따로 filtering하자
def crawling_filtering_api_v1(document: list[dict[str, str]], date: list[int], sort_op: str="relevance", accept = True) -> list[dict[str, str]]:
    """
        crawling_openreview (API v1)로부터 받은 결과 리스트를 연도(date)에 맞게 필터링합니다.

        Args:
            documents: 'cdate' (Unix timestamp in ms)를 포함하는 논문 딕셔너리 리스트.
            date: 필터링할 시작 연도와 종료 연도. 예: [2021, 2022]

        Returns:
            지정된 연도 범위에 해당하는 논문 딕셔너리 리스트.
        """
    if not date or len(date) != 2:
        # 날짜 정보가 없으면 필터링 없이 그대로 반환
        return document

    start_year, end_year = date
    filtered_documents = []

    for paper in document:
        # 'cdate' 키가 없는 경우를 대비한 예외 처리
        if 'cdate' not in paper or not paper['cdate']:
            continue

        # 1. Unix 타임스탬프(ms)를 datetime 객체로 변환
        timestamp_ms = paper['cdate']
        creation_date = datetime.fromtimestamp(timestamp_ms / 1000)

        # 2. 연도를 추출하여 범위 내에 있는지 확인
        publication_year = creation_date.year
        if start_year <= publication_year <= end_year:
            filtered_documents.append(paper)

    return filtered_documents

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

