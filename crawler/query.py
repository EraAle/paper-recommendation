# Set search keywords and maximum number of results
# When using this, ask them to write keywords within the list using only double quotes (""), not single quotes ('').
# The sort options are relevance, lastupdate, and submitted.
from collections import defaultdict
import re
from typing import Sequence, Union, Optional

def make_query_arxiv(keyword_list: list[str], operator: list[str] = ["AND"], field: list[str] = ["title"]) -> str:
    """
    arXiv API에 사용할 쿼리 문자열을 생성합니다.

    Args:
        keyword_list: 검색할 키워드 리스트.
        operator: 키워드를 연결할 논리 연산자 리스트.
                  요소가 1개이면 모든 키워드에 공통 적용되고,
                  여러 개이면 순차적으로 적용됩니다.
        field: 각 키워드를 검색할 필드 리스트.
               요소가 1개이면 모든 키워드에 공통 적용되고,
               여러 개이면 키워드와 1:1로 매칭됩니다.

    Returns:
        생성된 쿼리 문자열.
    """
    if not keyword_list:
        return ""

    prefix_map = {'title': 'ti', 'abstract': 'abs', 'all': 'all'}
    num_keywords = len(keyword_list)

    # --- 1. 단일 키워드 처리 (새로 추가된 부분) ---
    if num_keywords == 1:
        keyword = keyword_list[0]
        field_name = field[0]
        field_prefix = prefix_map.get(field_name)
        if not field_prefix:
            raise ValueError(f"Invalid field name: {field_name}")
        return f'{field_prefix}:"{keyword}"'

    # --- 2. 여러 키워드 처리 ---

    # operator 리스트 준비
    if len(operator) == 1:
        operators = operator * (num_keywords - 1)
    else:
        # 순차 연산자일 경우 개수 검증
        if len(operator) != num_keywords - 1:
            raise ValueError(
                f"operator가 여러 개일 경우, 개수는 키워드 개수보다 1개 적어야 합니다."
            )
        operators = operator

    # field 리스트 준비 (기존 버그 수정)
    if len(field) == 1: # <-- 이 부분이 len(operator)가 아닌 len(field)여야 합니다.
        fields = field * num_keywords
    else:
        if len(field) != num_keywords:
            raise ValueError("field가 여러 개일 경우, 개수는 키워드 개수와 일치해야 합니다.")
        fields = field

    # 각 키워드를 필드와 조합하여 쿼리 텀 생성
    query_terms = []
    for i, keyword in enumerate(keyword_list):
        field_prefix = prefix_map.get(fields[i])
        if not field_prefix:
            raise ValueError(f"Invalid field name: {fields[i]}")
        query_terms.append(f'{field_prefix}:"{keyword}"')

    # 쿼리 텀과 연산자를 번갈아 조합
    query_parts = [query_terms[0]]
    for i in range(num_keywords - 1):
        query_parts.append(f" {operators[i]} ")
        query_parts.append(query_terms[i + 1])

    return "".join  (query_parts)

def make_query_openreview_search(keyword_list: list[str], operator: list[str] = ["AND"], field: list[str] = ["all"]):
    """

      Args:
          keyword_list: 검색할 키워드 리스트.
          operator: 키워드를 연결할 논리 연산자 리스트.
                    요소가 1개이면 모든 키워드에 공통 적용되고,
                    여러 개이면 순차적으로 적용됩니다.
          field: 각 키워드를 검색할 필드 리스트.
                 요소가 1개이면 모든 키워드에 공통 적용되고,
                 여러 개이면 키워드와 1:1로 매칭됩니다.

      Returns:
          생성된 쿼리 문자열.
      """
    if not keyword_list:
        return ""

    num_keywords = len(keyword_list)

    # --- 1. "all" 필드 특별 처리 (새로 추가된 부분) ---
    if field and field[0].lower() == "all":
        # 키워드가 하나일 경우
        if num_keywords == 1:
            return f'"{keyword_list[0]}"'

        # 사용할 operator 리스트 준비
        if len(operator) == 1:
            operators = operator * (num_keywords - 1)
        else:
            if len(operator) != num_keywords - 1:
                raise ValueError("operator가 여러 개일 경우, 개수는 키워드 개수보다 1개 적어야 합니다.")
            operators = operator

        # 키워드에 따옴표 추가
        quoted_keywords = [f'"{k}"' for k in keyword_list]

        # 쿼리 텀과 연산자를 번갈아 조합
        query_parts = [quoted_keywords[0]]
        for i in range(num_keywords - 1):
            query_parts.append(f" {operators[i].upper()} ")
            query_parts.append(quoted_keywords[i + 1])

        return "".join(query_parts)

    # --- 1. 단일 키워드 처리 (새로 추가된 부분) ---
    if num_keywords == 1:
        keyword = keyword_list[0]
        field_name = field[0]
        return f'{field_name}:"{keyword}"'

    # --- 2. 여러 키워드 처리 ---

    # operator 리스트 준비
    if len(operator) == 1:
        operators = operator * (num_keywords - 1)
    else:
        # 순차 연산자일 경우 개수 검증
        if len(operator) != num_keywords - 1:
            raise ValueError(
                f"operator가 여러 개일 경우, 개수는 키워드 개수보다 1개 적어야 합니다."
            )
        operators = operator

    # field 리스트 준비 (기존 버그 수정)
    if len(field) == 1:  # <-- 이 부분이 len(operator)가 아닌 len(field)여야 합니다.
        fields = field * num_keywords
    else:
        if len(field) != num_keywords:
            raise ValueError("field가 여러 개일 경우, 개수는 키워드 개수와 일치해야 합니다.")
        fields = field

    # 각 키워드를 필드와 조합하여 쿼리 텀 생성
    query_terms = []
    for i, keyword in enumerate(keyword_list):
        query_terms.append(f'{fields[i]}:"{keyword}"')

    # 쿼리 텀과 연산자를 번갈아 조합
    query_parts = [query_terms[0]]
    for i in range(num_keywords - 1):
        query_parts.append(f" {operators[i]} ")
        query_parts.append(query_terms[i + 1])

    return "".join(query_parts)


def plan_openreview_v1_queries(keyword_list: list[str], operator: list[str], field: list[str]) -> list[dict]:
    """
    OpenReview API V1의 제약사항에 맞춰 복합 쿼리를 여러 개의 단순 쿼리로 분해하여 API 호출 계획을 생성합니다.

    이 함수는 사용자의 복합 논리식((A AND B) OR C)을 API V1이 실행할 수 있는
    단순 쿼리 딕셔너리의 리스트([{'f1':'A', 'f2':'B'}, {'f3':'C'}])로 변환합니다.
    반환된 리스트를 순회하며 여러 번 API를 호출하고 결과를 합쳐야 합니다.

    Args:
        keyword_list: 검색할 키워드 리스트.
        operator: 키워드 사이에 적용될 'AND' 또는 'OR' 연산자 리스트.
        field: 각 키워드에 매칭될 필드 리스트.

    Returns:
        get_notes()의 content 파라미터로 사용할 쿼리 딕셔너리들의 리스트.

    Raises:
        ValueError: 입력 리스트들의 길이가 맞지 않거나, AND로 연결된 덩어리 내에
                    동일한 필드가 중복될 경우 발생합니다.
    """
    # --- 1. 입력 유효성 검증 ---
    if not keyword_list:
        return []

    for i in range(len(field)):
        if field[i].lower() == "all":
            field[i] = "query"
    if len(field) == 1:
        field = field * len(keyword_list)

    if len(operator) == 1:
        operator = operator * (len(keyword_list) - 1)

    if len(keyword_list) == 1:
        return [{field[0]: keyword_list[0]}]

    # --- 2. 쿼리를 'OR' 기준으로 분해하기 ---
    query_plan = []
    current_and_clause = {}

    # 첫 번째 키워드로 초기화
    current_and_clause[field[0]] = keyword_list[0]

    for i, op in enumerate(operator):
        op_upper = op.upper()
        # 다음 키워드와 필드 정보
        next_keyword = keyword_list[i + 1]
        next_field = field[i + 1]

        if op_upper == "AND":
            # AND 덩어리에 추가. 동일 필드가 이미 있으면 V1에서 처리 불가.
            if next_field in current_and_clause:
                raise ValueError(
                    f"API V1은 AND로 연결된 쿼리 내에 동일한 필드('{next_field}')를 중복해서 사용할 수 없습니다."
                )
            current_and_clause[next_field] = next_keyword

        elif op_upper == "OR":
            # OR를 만나면, 지금까지 만든 AND 덩어리를 계획에 추가하고 새 덩어리 시작
            query_plan.append(current_and_clause)
            current_and_clause = {next_field: next_keyword}

        else:
            raise ValueError(f"지원하지 않는 operator입니다: '{op}'")

    # 마지막으로 만들어진 AND 덩어리 추가
    if current_and_clause:
        query_plan.append(current_and_clause)

    return query_plan

# 필드는 title, abstract, authorids   참고로 all은 없다. 이건 구현해야 함
def make_query_openreview_v1(keyword: list[str], field: list[str] = ["title"]) -> dict[str, str]:
    """
    Creates a query dictionary to use with the OpenReview API V1.

    NOTE: OpenReview API V1 has significant limitations compared to arXiv or API V2.
    - It does NOT support operators like 'AND' or 'OR' in a single query. The 'operator' parameter is ignored.
    - It can only search one keyword in one field at a time. Therefore, only the FIRST item
      from 'keyword_list' and 'field' will be used.

    Args:
        keyword_list: A list of keywords. Only the first keyword is used.
        field: A string or list representing the search field. Only the first field is used.
               Valid fields are 'title', 'abstract', 'authorids', etc.
        operator: This parameter is ignored as it is not supported by API V1.

    Returns:
        A query dictionary formatted for the 'content' parameter of client.get_notes().
    """
    # API V1은 한 번에 하나의 키워드와 필드만 처리 가능
    keyword_name = keyword[0]
    if not keyword_name:
        return {}


    # 유효한 필드명인지 간단히 확인 (필요에 따라 추가)
    valid_fields = {'title', 'abstract', 'authorids', 'all'}
    field_name = field[0]
    if field_name not in valid_fields:
        raise ValueError(f"Invalid field name for API v1: {field_name}. Use one of {valid_fields}")

    # API v1 쿼리는 {'필드명': '키워드'} 형태의 딕셔너리
    if field_name == 'all':
        return {'query': keyword}
    return {field_name: keyword_name}

def make_query_openreview_v2(keyword_list: list[str], operator: list[str] = ["AND"], field: list[str] = ["title"]) -> dict[str, str]:
    """
    OpenReview API V2를 위한 쿼리 딕셔너리를 생성합니다. (공통/순차 연산자 모두 지원)

    이 함수는 operator 리스트의 길이에 따라 두 가지 모드로 동작합니다.
    1. len(operator) == 1: 리스트의 단일 연산자를 모든 키워드 사이에 공통 적용합니다.
       예: keywords=["A", "B", "C"], operator=["OR"] -> "A" OR "B" OR "C"
    2. len(operator) > 1: 연산자를 키워드 사이에 순차적으로 적용합니다.
       예: keywords=["A", "B", "C"], operator=["AND", "OR"] -> "A" AND "B" OR "C"

    Args:
        keyword_list: 검색할 키워드 리스트.
        operator: 키워드를 연결할 논리 연산자 리스트.
        field: 각 키워드를 검색할 필드 리스트.

    Returns:
        API 호출의 'content' 파라미터로 사용할 수 있는 쿼리 딕셔너리.
    """
    if not keyword_list:
        return {}
    if len(keyword_list) == 1:
        return {field[0]: f'~"{keyword_list[0]}"'}

    # --- 키워드가 여러 개일 때의 로직 ---

    # 1. field 리스트 처리
    if len(field) == 1:
        fields = field * len(keyword_list)
    else:
        fields = field
    if len(keyword_list) != len(fields):
        raise ValueError("키워드의 개수와 필드의 개수가 일치해야 합니다.")

    # 2. operator를 실제 쿼리 기호 리스트(op_symbols)로 변환
    operator_map = {"AND": ",", "OR": " | "}
    op_symbols = []

    if len(operator) == 1:
        # Case 1: 공통 연산자. ["OR"]가 들어온 경우
        op = operator[0].upper()
        if op not in operator_map:
            raise ValueError(f"잘못된 operator입니다: '{op}'. 'AND' 또는 'OR'를 사용하세요.")
        symbol = operator_map[op]
        # 모든 키워드 사이에 적용되도록 연산자 기호를 복제
        op_symbols = [symbol] * (len(keyword_list) - 1)

    elif len(operator) > 1:
        # Case 2: 순차 연산자. ["AND", "OR"] 등이 들어온 경우
        if len(operator) != len(keyword_list) - 1:
            raise ValueError(
                f"operator가 여러 개일 경우, 개수는 키워드 개수보다 1개 적어야 합니다. "
                f"(키워드: {len(keyword_list)}개, operator: {len(operator)}개)"
            )
        for op in operator:
            op_upper = op.upper()
            if op_upper not in operator_map:
                raise ValueError(f"잘못된 operator입니다: '{op}'. 'AND' 또는 'OR'를 사용하세요.")
            op_symbols.append(operator_map[op_upper])
    else: # len(operator) == 0
        raise ValueError("키워드가 2개 이상일 때는 반드시 operator를 제공해야 합니다.")

    # 3. 쿼리 조립 (이하 로직은 op_symbols가 준비되었으므로 수정 불필요)
    query_parts_by_field = defaultdict(list)
    for i, (kw, f) in enumerate(zip(keyword_list, fields)):
        formatted_kw = f'~"{kw}"'
        query_parts_by_field[f].append(formatted_kw)

        if i < len(op_symbols):
            if f == fields[i+1]:
                query_parts_by_field[f].append(op_symbols[i])

    # 4. 최종 딕셔너리 생성
    final_query = {}
    for f, parts in query_parts_by_field.items():
        final_query[f] = "".join(parts)

    return final_query

# ES Query String에서 이스케이프 필요한 문자
_ES_SPECIALS = r'[\+\-\=\&\|\>\<\!\(\)\{\}\[\]\^"~\*\?:\\\/]'

def _escape_es(text: str) -> str:
    return re.sub(_ES_SPECIALS, lambda m: '\\' + m.group(0), text)

def _normalize_ops(ops: Union[str, Sequence[str]], n_terms: int) -> list[str]:
    if isinstance(ops, str):
        return [ops.upper()] * (n_terms - 1)
    ops = [o.upper() for o in ops]
    if len(ops) == n_terms - 1:
        return ops
    raise ValueError("operators 길이는 keywords 길이 - 1 과 같아야 함")

def _to_field_path(name: str) -> str:
    mapping = {
        "title": "content.title",
        "abstract": "content.abstract",
        "authors": "content.authors",
        "authorids": "content.authorids",
        "keywords": "content.keywords",
        "venue": "content.venue",
        "venueid": "content.venueid",
        "all": ""
    }
    return mapping.get(name.lower(), name)

def build_search_notes_query_v2(
    keywords: Sequence[str],
    operators: Union[str, Sequence[str]] = "AND",
    field: Union[str, Sequence[str]] = "all",
    negative_keywords: Optional[Sequence[str]] = None,
    phrase: bool = True
) -> str:
    """
    OpenReview API v2 search_notes(term=...)에 넣을 query-string을 생성.

    Args:
        keywords: 검색 키워드 리스트
        operators: AND/OR (문자열 또는 연산자 시퀀스)
        field: 단일 필드명("title", "abstract", "all" 등) 또는 각 키워드별 필드 시퀀스
        negative_keywords: 제외할 키워드 리스트
        phrase: True면 공백 있는 키워드는 자동으로 "..." 로 감싸줌
    """
    if not keywords:
        raise ValueError("keywords는 비어있을 수 없음")
    if isinstance(field, str):
        fields = [_to_field_path(field)] * len(keywords)
    else:
        if len(field) != len(keywords):
            raise ValueError("field 시퀀스 길이는 keywords와 같아야 함")
        fields = [_to_field_path(f) for f in field]

    ops = _normalize_ops(operators, len(keywords))

    def wrap(tok: str) -> str:
        tok = _escape_es(tok.strip())
        if phrase and " " in tok:
            return f"\"{tok}\""
        return tok

    parts = []
    for i, (kw, fpath) in enumerate(zip(keywords, fields)):
        token = wrap(kw)
        scoped = f"{fpath}:{token}" if fpath else token
        parts.append(scoped)
        if i < len(ops):
            parts.append(ops[i])

    query = " ".join(parts)
    if len(keywords) > 1:
        query = f"({query})"

    if negative_keywords:
        negs = [f"NOT {wrap(nk)}" for nk in negative_keywords]
        query = f"{query} " + " ".join(negs)

    return query