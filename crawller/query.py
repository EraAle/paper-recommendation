# Set search keywords and maximum number of results
# When using this, ask them to write keywords within the list using only double quotes (""), not single quotes ('').
# The sort options are relevance, lastupdate, and submitted.
from collections import defaultdict

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

    return "".join(query_parts)

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
    valid_fields = {'title', 'abstract', 'authorids'}
    field_name = field[0]
    if field_name not in valid_fields:
        raise ValueError(f"Invalid field name for API v1: {field_name}. Use one of {valid_fields}")

    # API v1 쿼리는 {'필드명': '키워드'} 형태의 딕셔너리
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