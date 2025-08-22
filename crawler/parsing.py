from .query import *

# 근데 이거 반드시 ''로 감싼 키워드를 주든가 내가 ''를 없애고 다시 붙여서 사용해야 할듯
def hard_parsing(keyword_dict: dict, field: str = "all") -> str:
    """
    Main 키워드와 Optional 키워드를 모두 '반드시' 포함하는 쿼리를 생성합니다.
    (Main1 AND Main2) AND (Optional1 AND Optional2)
    """
    main_list = keyword_dict.get('main', [])
    optional_list = keyword_dict.get('optional', [])

    # 1. Main 키워드 부분 생성
    main_sub_queries = []
    for synonym_list in main_list:
        # 동의어 그룹을 "OR"로 묶어 쿼리 조각 생성
        sub_query = make_query_arxiv(synonym_list, operator=["OR"], field=[field])
        # 각 조각을 괄호로 감싸기
        main_sub_queries.append(f"({sub_query})")

    # 괄호로 감싸진 조각들을 "AND"로 연결
    main_query_block = " AND ".join(main_sub_queries)

    # 2. Optional 키워드 부분 생성
    optional_query_block = ""
    if optional_list:
        # 옵션 키워드 전체를 "OR"로 묶어 쿼리 조각 생성
        sub_query = make_query_arxiv(optional_list, operator=["AND"], field=[field])
        # 전체를 괄호로 감싸기
        optional_query_block = f"({sub_query})"

    # 3. Main과 Optional 부분 결합
    if main_query_block and optional_query_block:
        return f"({main_query_block}) AND ({optional_query_block})"
    elif main_query_block:
        return main_query_block
    else:
        return optional_query_block

def soft_parsing(keyword_dict: dict, field: str = "all") -> str:
    """
    Main 키워드 그룹 또는 Optional 키워드 그룹 중 하나를 만족하는 쿼리를 생성합니다.
    (Main1 AND Main2) OR (Optional1 OR Optional2)
    """
    main_list = keyword_dict.get('main', [])
    optional_list = keyword_dict.get('optional', [])

    # 1. Main 키워드 부분 생성 (hard_parsing과 동일)
    main_sub_queries = []
    for synonym_list in main_list:
        sub_query = make_query_arxiv(synonym_list, operator=["OR"], field=[field])
        main_sub_queries.append(f"({sub_query})")
    main_query_block = " AND ".join(main_sub_queries)

    # 2. Optional 키워드 부분 생성 (hard_parsing과 동일)
    optional_query_block = ""
    if optional_list:
        sub_query = make_query_arxiv(optional_list, operator=["OR"], field=[field])
        optional_query_block = f"({sub_query})"

    # 3. Main과 Optional 부분 결합 (OR 사용)
    if main_query_block and optional_query_block:
        # ★★★ 이 부분만 hard_parsing과 다릅니다. ★★★
        return f"({main_query_block}) AND ({optional_query_block})"
    elif main_query_block:
        return main_query_block
    else:
        return optional_query_block