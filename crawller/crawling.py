import arxiv
import requests

# 검색 키워드 및 최대 결과 수 설정
# 이거 쓸 때 리스트 내의 키워드는 ""로만 작성해달라 하기 ''은 안됨
# sort 옵션은 relevance, lastupdate, submitted 세 가지

def crawling_basic(keyword_list, num=50, operator="AND", sort_op="relevance"):
    """
    Args:
        keyword_list (list): 검색할 키워드가 담긴 리스트 (e.g., ["abc", "def gh"])
        num (int): 가져올 최대 논문 수
        operator (str): 키워드를 연결할 논리 연산자 ("AND", "OR")
    """
    # 1. 리스트의 모든 키워드를 큰따옴표(")로 감싸줍니다. (리스트 컴프리헨션)
    #    'def gh'와 같은 구문 검색을 위해 필수적입니다.
    quoted_keywords = [f'"{k}"' for k in keyword_list]

    # 2. 연산자 양옆에 공백을 넣어 ' AND ' 또는 ' OR ' 형태로 만듭니다.
    separator = f" {operator} "

    # 3. 따옴표로 감싸진 키워드들을 연산자로 연결합니다. (join 메서드)
    search_query = separator.join(quoted_keywords)

    documents = []

    print(f"✅ 생성된 쿼리: {search_query}")


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
        # 검색 객체 생성 (최신 제출일 순으로 정렬)
        search = arxiv.Search(
          query = search_query,
          max_results = max_results,
          sort_by = arxiv.SortCriterion.SubmittedDate
        )

    # 검색 실행 및 결과 출력
    # client에게 result라는 장바구니를 주고 거기에 받아오라는 것
    client = arxiv.Client()
    results = list(client.results(search))

    for result in results:
      temp_dict = {}
      # 논문 제목
      title = result.title
      temp_dict['title'] = title


      # 논문 저자 (첫 번째 저자만)
      first_author = result.authors[0]

      # 논문 PDF 링크
      url = result.pdf_url
      temp_dict['url'] = url

      # 논문 초록
      abstract = result.summary
      temp_dict['abstract'] = abstract
      # 논문 고유 ID (버전 정보 포함)
      entry_id = result.entry_id

      # 논문 게시일
      published_date = result.published.strftime('%Y-%m-%d')

      print(f"📄 제목: {title}")
      print(f"👤 저자: {first_author}")
      print(f"🗓️ 게시일: {published_date}")
      print(f"🔗 고유 주소: {entry_id}")
      print(f"🔗 논문 pdf 링크: {url}")
      print(f"📋 초록: {abstract[:20]}") # 초록은 너무 길어서 앞부분만 출력
      print("-" * 30)

      documents.append(temp_dict)

    return documents

# 이 함수는 한 번에 한 개의 논문 제목에 대한 citation을 받아옴
# crossref api로 검색 안 되는 것들은 그냥 citation 0으로 리턴
def get_citation(title,email):
    BASE_URL = "https://api.crossref.org/works"

    params = {
        "query.title": title,
        "rows": 1,  # 가장 관련성 높은 결과 1개만 요청
        "mailto": email  # Polite Pool 사용
    }

    # 6. try...except 블록을 사용해 오류 처리를 합니다.
    # try 블록 안의 코드를 실행하다가 지정된 오류가 발생하면, 프로그램이 중단되지 않고 except 블록이 실행됩니다.
    try:
        # 7. HTTP GET 요청을 보냅니다.
        # requests.get() 함수가 URL과 파라미터를 조합하여 Crossref 서버에 데이터를 요청합니다.
        response = requests.get(BASE_URL, params=params)

        # 8. HTTP 상태 코드를 확인합니다.
        # 응답이 성공적이지 않으면 (4xx 또는 5xx 오류 코드), HTTPError 예외를 발생시킵니다.
        response.raise_for_status()

        # 9. 응답 본문(response body)을 JSON에서 파이썬 딕셔너리로 변환합니다.
        data = response.json()

        # 10. 반환된 데이터에 검색 결과가 있는지 확인합니다.
        # Crossref 데이터 구조에 따라 data['message']['items'] 리스트가 비어있지 않은지 봅니다.
        if data['message']['items']:
            # 11. 첫 번째 검색 결과를 변수에 할당합니다.
            item = data['message']['items'][0]

            # 12. 인용수(is-referenced-by-count) 값을 추출합니다.
            # .get()을 사용하여 해당 키가 없을 경우 기본값으로 0을 사용합니다.
            citation_count = item.get('is-referenced-by-count', 0)

            # 13. 추출한 인용수를 함수의 결과로 반환합니다.
            return citation_count
        else:
            # 14. 검색 결과가 없으면 0을 반환합니다.
            return 0

    # 15. 예외 처리 블록입니다.
    # requests.get()에서 네트워크 오류 등이 발생하거나, JSON 구조가 예상과 다를 때 실행됩니다.
    except (requests.exceptions.RequestException, KeyError, IndexError):
        # 16. 오류 발생 시 0을 반환합니다.
        return 0


import requests


def get_citation_and_title(title_to_search, email):
    """
    논문 제목으로 Crossref를 검색하여, API가 실제로 찾은 논문의 제목과 인용수를 함께 반환합니다.

    Args:
        title_to_search (str): 검색할 논문 제목
        email (str): Crossref API의 Polite Pool 사용을 위한 이메일 주소

    Returns:
        tuple: (찾은 논문 제목, 인용 횟수) 형태의 튜플.
               논문을 찾지 못하거나 오류 발생 시 ('(논문을 찾지 못함)', 0)을 반환합니다.
    """
    BASE_URL = "https://api.crossref.org/works"
    params = {
        "query.title": title_to_search,
        "rows": 1,
        "mailto": email
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['message']['items']:
            item = data['message']['items'][0]

            # API가 찾은 논문의 제목 추출 (리스트 형태이므로 첫 번째 요소를 가져옴)
            found_title = item.get('title', ['(제목을 찾을 수 없음)'])[0]

            # 인용수 추출
            citation_count = item.get('is-referenced-by-count', 0)

            # 찾은 제목과 인용수를 튜플로 묶어서 반환
            return (found_title, citation_count)
        else:
            return ('(논문을 찾지 못함)', 0)

    except (requests.exceptions.RequestException, KeyError, IndexError):
        return ('(API 요청 오류)', 0)
# candidate_num = 후보 몇 개 둘건지
# num = citation top k개 선택
# 이거는 크롤링해서 가져온 dict을 citation에 따라 정렬

# crossref api는 사용할 때 email을 보내면 안정적인 서비스 제공
# 신원을 밝힌 것이라서
# citation이 높은 순으로 정렬된 paper_dict을 반환
# def sort_citation(paper_dict, email):
#     title_list = paper_dict.get("title")
#     abstract_list = paper_dict.get("abstract")
#     pdf_url_list = paper_dict.get("pdf_url")
#
#     citation_list = []
#     if not title_list:
#         print("title 없음")
#
#     BASE_URL = "https://api.crossref.org/works"
#
#     for title in title_list:
#         citation_count = get_citation(title, email)
#         citation_list.append(citation_count)
#
#     paper_dict["title"] = sort_list(title_list, citation_list)
#     paper_dict["abstract"] = sort_list(abstract_list, citation_list)
#     paper_dict["pdf_url"] = sort_list(pdf_url_list, citation_list)
#     paper_dict["citation_count"] = sorted(citation_list, reverse=True)
#
#     return paper_dict

def sort_citation(documents, email):
    BASE_URL = "https://api.crossref.org/works"

    title_list = [doc["title"] for doc in documents]
    citation_list = []

    for title in title_list:
        citation_count = get_citation(title, email)
        citation_list.append(citation_count)

    print(citation_list)
    # 1. title_list와 citation_count를 zip으로 묶어줍니다.
    #    결과: [('Attention...', 96172), ('BERT...', 83011), ('An Image...', 47538)]
    paired_list = list(zip(documents, citation_list))

    # 2. 묶인 리스트를 인용수(각 쌍의 두 번째 요소) 기준으로 내림차순 정렬합니다.
    #    key=lambda item: item[1]  --> 각 쌍(item)의 1번 인덱스 값(인용수)을 기준으로 정렬
    #    reverse=True             --> 내림차순 (큰 숫자가 먼저 오도록)
    sorted_pairs = sorted(paired_list, key=lambda item: item[1], reverse=True)

    # 3. 정렬된 쌍 리스트에서 제목(각 쌍의 첫 번째 요소)만 다시 추출합니다.
    sorted_target_list = [tar for tar, criteria in sorted_pairs]


    return sorted_target_list