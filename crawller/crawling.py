import arxiv
import requests
import re
import math
import random
import textwrap


# 검색 키워드 및 최대 결과 수 설정
# 이거 쓸 때 리스트 내의 키워드는 ""로만 작성해달라 하기 ''은 안됨
# sort 옵션은 relevance, lastupdate, submitted 세 가지

def make_query(keyword_list: list[str], operator: str | list[str] ="AND", field: str | list[str] = "title") -> str:
    """
    arxiv API에 사용할 query를 제작한다

    Args:
        keyword_list: instruction에서 추출한 keyword의 list
        list내의 keyword는 "로만 묶여야 함. '를 사용하면 문제가 발생.

        operator: keyword 사이를 연결할 operator str or list
        단일 str의 경우 해당 operator로 모든 keyword를 연결
        list의 경우 순서대로 keyword 사이를 채우게 됨

        field: 각 keyword의 검색 field list
        단일 str의 경우 해당 field를 모든 keyword에 사용
        list의 경우 순서대로 keyword 사이를 채우게 됨

    Returns: 연결된 query

    """
    # 1. 리스트의 모든 키워드를 큰따옴표(")로 감싸줍니다.
    #    'def gh'와 같은 구문 검색을 위해 필수적입니다.
    quoted_keywords = [f'"{k}"' for k in keyword_list]

    if isinstance(operator, str):
        separator = f" {operator} "
        search_query = separator.join(quoted_keywords)

    elif isinstance(operator, list):
        quoted_keywords = [f'"{k}"' for k in keyword_list]

        search_query = quoted_keywords[0]

        for op, keyword in zip(operator, quoted_keywords[1:]):
            search_query += f" {op} {keyword}"

    else:
        raise TypeError("operator TypeError")

    query = add_field(search_query, field)

    return query

def add_field(query: str, field:  str | list[str]) -> str:
    """
    쿼리 문자열과 필드(문자열 또는 리스트)를 받아 접두사를 추가합니다.

    Args:
        query: '"a" AND "b"' 형태의 검색 쿼리

        field: 필드 정보.
        'title', 'abstract', 'all' 이렇게 세 종류
        'title'처럼 단일 str이거나
        ['title', 'abstract', 'all']처럼
        list일 수 있음

    Returns: 접두사가 추가된 새로운 쿼리 문자열
        """
    # 필드 이름과 실제 접두사 매핑
    PREFIX_MAP = {
        'title': 'ti',
        'abstract': 'abs',
        'all': 'all'
    }

    # 1. 쿼리를 키워드와 연산자로 분리
    parts = re.split(r' (AND|OR|ANDNOT) ', query)
    keywords = parts[::2]
    num_keywords = len(keywords)

    field_prefixes = []

    # 2. fields 파라미터 타입에 따라 분기 처리
    if isinstance(field, str):
        # 문자열인 경우, 모든 키워드에 동일한 접두사 적용
        if field not in PREFIX_MAP:
            raise ValueError(f"field name error!: {field}")
        prefix = PREFIX_MAP[field]
        field_prefixes = [prefix] * num_keywords

    elif isinstance(field, list):
        # 리스트인 경우, 각 키워드에 순서대로 접두사 적용
        if num_keywords != len(field):
            raise ValueError(
                f"field length error: {len(field)} != {num_keywords}"
            )
        # 리스트의 각 필드 이름을 실제 접두사로 변환
        field_prefixes = [PREFIX_MAP.get(f) for f in field]
        if None in field_prefixes:
            raise ValueError(f"field name: {field}")

    else:
        raise TypeError("fields typeError")

    # 3. 각 키워드 앞에 변환된 접두사 추가
    for i, prefix in enumerate(field_prefixes):
        keyword_index = i * 2
        parts[keyword_index] = f"{prefix}:{parts[keyword_index]}"

    # 4. 모든 부분을 다시 하나의 문자열로 합침
    return " ".join(parts)

def crawling_basic(search_query: str, num: int = 50, sort_op: str="relevance") -> list[dict[str, str]]:
    """
    make_query를 이용하여 생성된 query를 받아
    지정한 sort option에 따라 num개 만큼의 논문 정보를 dictionary의 list로 만들어 반환한다

    Args:
        search_query: make_query 한수를 이용해 생성된 query
        num (int): 가져올 최대 논문 수
        sort_op: sorting option. relevance, lastupdate, submitted 이렇게 세 가지이다
        각각 관련도순, 논문이 마지막으로 업데이트 된 날짜순, 처음 제출된 날짜 순이다.

    Returns: dictionary의 list인 document
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

# 이 함수는 한 번에 한 개의 논문 제목에 대한 citation을 받아옴
# crossref api로 검색 안 되는 것들은 그냥 citation 0으로 리턴
def get_citation_crossref(title: str, email: str) -> int:
    """
    crossref API를 통해 title로 논문을 검색해서 해당 논문의 citation을 얻어온다

    Args:
        title: 논문 이름
        email: polite pool을 위한 인자.
        email을 입력해야 API를 큰 제약 없이 사용 가능

    Returns: title로 검색한 논문의 citation
    """
    BASE_URL = "https://api.crossref.org/works"

    params = {
        "query.title": title,
        "rows": 1,  # 가장 관련성 높은 결과 1개만 요청
        "mailto": email  # Polite Pool 사용
    }

    try:
        # requests.get() 함수가 URL과 파라미터를 조합하여 Crossref 서버에 데이터를 요청합니다.
        response = requests.get(BASE_URL, params=params)

        # 8. HTTP 상태 코드를 확인합니다.
        # 응답이 성공적이지 않으면 (4xx 또는 5xx 오류 코드), HTTPError 예외를 발생시킵니다.
        response.raise_for_status()

        # 응답 본문(response body)을 JSON에서 파이썬 딕셔너리로 변환합니다.
        data = response.json()

        # Crossref 데이터 구조에 따라 data['message']['items'] 리스트가 비어있지 않은지 봅니다.
        if data['message']['items']:
            # 11. 첫 번째 검색 결과를 변수에 할당합니다.
            item = data['message']['items'][0]

            # 인용수(is-referenced-by-count) 값을 추출합니다.
            # .get()을 사용하여 해당 키가 없을 경우 기본값으로 0을 사용합니다.
            citation_count = item.get('is-referenced-by-count', 0)

            # 추출한 인용수를 함수의 결과로 반환합니다.
            return citation_count
        else:
            # 검색 결과가 없으면 0을 반환합니다.
            return 0

    # requests.get()에서 네트워크 오류 등이 발생하거나, JSON 구조가 예상과 다를 때 실행됩니다.
    except (requests.exceptions.RequestException, KeyError, IndexError):
        return 0

import requests

def get_citation_openalex(title: str, email: str) -> int:
    """
       OpenAlex API를 이용해 논문 제목으로 인용 횟수를 검색합니다.

    Args:
        title: 논문 이름
        email: polite pool을 위한 인자.
        email을 입력해야 API를 큰 제약 없이 사용 가능

    Returns: title로 검색한 논문의 citation
       """
    base_url = "https://api.openalex.org/works"
    params = {
        'search': title,  # 논문 제목으로 검색
        'per_page': 1,  # 가장 관련성 높은 결과 1개만 요청
        'mailto': email  # Polite Pool 참여
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        data = response.json()

        # 검색 결과가 있고, 결과 리스트가 비어있지 않은지 확인
        if data.get('results') and len(data['results']) > 0:
            # 첫 번째 결과에서 인용 횟수('cited_by_count')를 가져옴
            citation_count = data['results'][0].get('cited_by_count', 0)
            return citation_count
        else:
            # 검색 결과가 없는 경우
            return 0

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return 0


def sort_citation_crossref(document: list[dict[str, str]], email: str) -> list[dict[str, str]]:
    """
    crossref API로 citation을 얻어 documents를 sorting

    Args:
        document: sorting할 document
        email: polite pool을 위한 인자.
        email을 입력해야 API를 큰 제약 없이 사용 가능

    Returns: citation으로 sorting한 document
    """
    BASE_URL = "https://api.crossref.org/works"

    title_list = [doc["title"] for doc in document]
    citation_list = []

    for title in title_list:
        citation_count = get_citation_crossref(title, email)
        citation_list.append(citation_count)

    print(citation_list)
    # title_list와 citation_count를 zip으로 묶어줍니다.
    paired_list = list(zip(document, citation_list))

    # 묶인 리스트를 인용수(각 쌍의 두 번째 요소) 기준으로 내림차순 정렬합니다.
    #    key=lambda item: item[1]  --> 각 쌍(item)의 1번 인덱스 값(인용수)을 기준으로 정렬
    #    reverse=True             --> 내림차순 (큰 숫자가 먼저 오도록)
    sorted_pairs = sorted(paired_list, key=lambda item: item[1], reverse=True)

    # 정렬된 쌍 리스트에서 제목(각 쌍의 첫 번째 요소)만 다시 추출합니다.
    sorted_target_list = [tar for tar, criteria in sorted_pairs]

    return sorted_target_list

def sort_citation_openalex(document: list[dict[str, str]], email: str) -> list[dict[str, str]]:
    """
    openalex API로 citation을 얻어 documents를 sorting

    Args:
        document: sorting할 document
        email: polite pool을 위한 인자.
        email을 입력해야 API를 큰 제약 없이 사용 가능

    Returns: citation으로 sorting한 document
    """
    BASE_URL = "https://api.openalex.org/works"

    title_list = [doc["title"] for doc in document]
    citation_list = []

    for title in title_list:
        citation_count = get_citation_openalex(title, email)
        citation_list.append(citation_count)

    print(citation_list)
    # title_list와 citation_count를 zip으로 묶어줍니다.
    paired_list = list(zip(document, citation_list))

    #  묶인 리스트를 인용수(각 쌍의 두 번째 요소) 기준으로 내림차순 정렬합니다.
    #    key=lambda item: item[1]  --> 각 쌍(item)의 1번 인덱스 값(인용수)을 기준으로 정렬
    #    reverse=True             --> 내림차순 (큰 숫자가 먼저 오도록)
    sorted_pairs = sorted(paired_list, key=lambda item: item[1], reverse=True)

    # 정렬된 쌍 리스트에서 제목(각 쌍의 첫 번째 요소)만 다시 추출합니다.
    sorted_target_list = [tar for tar, criteria in sorted_pairs]

    return sorted_target_list

def random_crawling(sample_size: int = 20, num: int = 10) -> list[dict[str, str]]:
    """
    랜덤한 crawling 결과를 가져오는 함수.

    Args:
        sample_size: 샘플링할 후보 사이즈
        num: 실제 리턴 document 사이즈

    Returns: 랜덤 query로 crawling한 document

    """

    # 랜덤한 query를 위한 list
    query_list = ["the", "a", "is", "of", "and", "in", "to"]

    # query_list에서 하나를 무작위로 선택
    random_query1 = random.choice(query_list)
    random_query2 = random.choice(query_list)
    random_query3 = random.choice(query_list)

    # 선택된 query에 대해 서로 다른 방식의 sort option 지정해서 crawling
    doc_relevance = crawling_basic(random_query1, num=sample_size, sort_op="relevance")
    doc_lastupdate = crawling_basic(random_query2, num=sample_size, sort_op="lastupdate")
    doc_submitted = crawling_basic(random_query3, num=sample_size, sort_op="submitted")

    # 하나로 합침
    random_candidate = doc_relevance + doc_lastupdate + doc_submitted
    # shuffle
    random.shuffle(random_candidate)

    # num 개수만큼 슬라이싱
    random_document = random_candidate[:num]

    return random_document

def document_print(document: list[dict[str, str]]) -> None:
    """
    논문 정보가 담긴 리스트를 받아와서 사람이 보기 좋은 형태로 출력합니다.

    Args:
        document: print할 document
       """
    if not document:
        print("document is empty")
        return

    # 각 문서를 번호와 함께 출력
    for i, doc in enumerate(document, 1):
        print(f"\n{'=' * 25} Document {i} {'=' * 25}")

        # 1. 제목 출력
        print(f"Title: {doc.get('title', 'N/A')}")

        # 2. URL 출력
        print(f"URL: {doc.get('url', 'N/A')}")

        # 3. 초록 출력 (자동 줄 바꿈)
        print("Abstract:")

        # textwrap을 사용해 가로 80자에 맞춰 들여쓰기와 함께 줄 바꿈
        abstract = doc.get('abstract', 'N/A')
        wrapped_abstract = textwrap.fill(
            abstract,
            width=80,
            initial_indent="    ",  # 첫 줄 들여쓰기
            subsequent_indent="    "  # 나머지 줄 들여쓰기
        )
        print(wrapped_abstract)

    print(f"\n{'=' * 58}")