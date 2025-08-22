from .query import *

# 근데 이거 반드시 ''로 감싼 키워드를 주든가 내가 ''를 없애고 다시 붙여서 사용해야 할듯
def hard_parsing_arxiv(keyword_dict: dict, field: str = "all") -> str:
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

def soft_parsing_arxiv(keyword_dict: dict, field: str = "all") -> str:
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

# ===== ES 용 이스케이프 & 토큰 빌드 =====
_ES_SPECIALS = r'[\+\-\=\&\|\>\<\!\(\)\{\}\[\]\^"~\*\?:\\\/]'

def _escape_es(s: str) -> str:
    return re.sub(_ES_SPECIALS, lambda m: '\\' + m.group(0), s)

def _strip_outer_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == "'") or (s[0] == s[-1] == '"')):
        return s[1:-1]
    return s

def _as_es_token(raw: str, phrase: bool = True) -> str:
    """양끝 따옴표 제거 → ES 특수문자 이스케이프 → 공백 있으면 "..." 로 감싸기"""
    x = _strip_outer_quotes(str(raw or ""))
    x = _escape_es(x)
    if phrase and any(ch.isspace() for ch in x):
        return f"\"{x}\""
    return x

# ===== 필드 매핑 (arXiv의 ti/abs/all 느낌을 OpenReview 경로로) =====
def _or_field_path(name: str) -> str:
    name = (name or "all").lower()
    mapping = {
        "title": "content.title.value",
        "abstract": "content.abstract.value",
        "authors": "content.authors.value",
        "authorids": "content.authorids.value",
        "keywords": "content.keywords.value",
        "venue": "content.venue.value",
        "venueid": "content.venueid.value",
        "all": ""  # 빈 문자열이면 필드 스코핑 없이 전역 검색
    }
    return mapping.get(name, name)

# ===== 단일 레벨 쿼리 빌더 (arXiv의 make_query_arxiv 스타일) =====
def make_query_openreview(keyword_list: list[str],
                          operator: list[str] = ["AND"],
                          field: list[str] = ["all"],
                          phrase: bool = True) -> str:
    """
    OpenReview v2 ES query-string 텀을 생성.
    - keyword_list: ["transformer", "attention"]
    - operator: ["AND"] 또는 ["AND","OR",...] (키워드-1 길이)
    - field: ["title"] 또는 ["title","abstract",...]
    """
    if not keyword_list:
        return ""

    n = len(keyword_list)

    # 1) operators 준비
    if len(operator) == 1:
        ops = [operator[0].upper()] * (n - 1)
    elif len(operator) == n - 1:
        ops = [op.upper() for op in operator]
    else:
        raise ValueError("operator 길이는 1 또는 (키워드 수 - 1)이어야 합니다.")

    # 2) fields 준비
    if len(field) == 1:
        fpaths = [_or_field_path(field[0])] * n
    elif len(field) == n:
        fpaths = [_or_field_path(f) for f in field]
    else:
        raise ValueError("field 길이는 1 또는 키워드 수와 같아야 합니다.")

    # 3) 단일 키워드 빠른 경로
    if n == 1:
        tok = _as_es_token(keyword_list[0], phrase=phrase)
        return f"{fpaths[0]}:{tok}" if fpaths[0] else tok

    # 4) 여러 키워드 조합
    terms = []
    for i, kw in enumerate(keyword_list):
        tok = _as_es_token(kw, phrase=phrase)
        scoped = f"{fpaths[i]}:{tok}" if fpaths[i] else tok
        terms.append(scoped)

    parts = [terms[0]]
    for i in range(n - 1):
        parts.append(f" {ops[i]} ")
        parts.append(terms[i + 1])

    return "".join(parts)

# ===== 조합 파서들 (네 arXiv용 hard/soft를 OR-v2로 포팅) =====
def hard_parsing_openreview(keyword_dict: dict, field: str = "all") -> str:
    """
    Main과 Optional을 모두 반드시 포함:
    ( (syn1 OR syn2) AND (synA OR synB) ) AND ( opt1 AND opt2 AND ... )
    """
    main_list = keyword_dict.get("main", [])        # 예상: [ [synonyms...], [synonyms...] ]
    optional_list = keyword_dict.get("optional", [])# 예상: [opt1, opt2, ...] (flat)

    # 1) Main 블록: 각 동의어 그룹은 OR로, 그룹끼리는 AND
    main_blocks = []
    for synonyms in main_list:
        sub = make_query_openreview(synonyms, operator=["OR"], field=[field])
        main_blocks.append(f"({sub})")
    main_query = " AND ".join(main_blocks)

    # 2) Optional 블록: 전체를 AND (너의 hard_parsing과 동일한 의도)
    opt_query = ""
    if optional_list:
        sub = make_query_openreview(optional_list, operator=["AND"], field=[field])
        opt_query = f"({sub})"

    # 3) 결합
    if main_query and opt_query:
        return f"({main_query}) AND ({opt_query})"
    elif main_query:
        return main_query
    else:
        return opt_query

def soft_parsing_openreview(keyword_dict: dict, field: str = "all") -> str:
    """
    Main 또는 Optional 중 하나만 만족해도 됨:
    ( (syn1 OR syn2) AND (synA OR synB) ) OR ( opt1 OR opt2 OR ... )
    """
    main_list = keyword_dict.get("main", [])
    optional_list = keyword_dict.get("optional", [])

    # 1) Main 블록: 동의어 그룹 OR, 그룹끼리 AND
    main_blocks = []
    for synonyms in main_list:
        sub = make_query_openreview(synonyms, operator=["OR"], field=[field])
        main_blocks.append(f"({sub})")
    main_query = " AND ".join(main_blocks)

    # 2) Optional 블록: 전체를 OR  (※ arXiv soft 버전의 의도 반영; 네 기존 코드의 AND는 버그였음)
    opt_query = ""
    if optional_list:
        sub = make_query_openreview(optional_list, operator=["OR"], field=[field])
        opt_query = f"({sub})"

    # 3) 결합은 OR
    if main_query and opt_query:
        return f"({main_query}) AND ({opt_query})"
    elif main_query:
        return main_query
    else:
        return opt_query