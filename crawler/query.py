
import re
from typing import Sequence, Union, Optional

def make_query_arxiv(keyword_list: list[str], operator: list[str] = ["AND"], field: list[str] = ["title"]) -> str:

    if not keyword_list:
        return ""

    prefix_map = {'title': 'ti', 'abstract': 'abs', 'all': 'all'}
    num_keywords = len(keyword_list)

    if num_keywords == 1:
        keyword = keyword_list[0]
        field_name = field[0]
        field_prefix = prefix_map.get(field_name)
        if not field_prefix:
            raise ValueError(f"Invalid field name: {field_name}")
        return f'{field_prefix}:"{keyword}"'


    if len(operator) == 1:
        operators = operator * (num_keywords - 1)
    else:
        # 순차 연산자일 경우 개수 검증
        if len(operator) != num_keywords - 1:
            raise ValueError("operator len error.")
        operators = operator

    if len(field) == 1:
        fields = field * num_keywords
    else:
        if len(field) != num_keywords:
            raise ValueError("operator len error.")
        fields = field

    query_terms = []
    for i, keyword in enumerate(keyword_list):
        field_prefix = prefix_map.get(fields[i])
        if not field_prefix:
            raise ValueError(f"Invalid field name: {fields[i]}")
        query_terms.append(f'{field_prefix}:"{keyword}"')

    query_parts = [query_terms[0]]
    for i in range(num_keywords - 1):
        query_parts.append(f" {operators[i]} ")
        query_parts.append(query_terms[i + 1])

    return "".join  (query_parts)



_ES_SPECIALS = r'[\+\-\=\&\|\>\<\!\(\)\{\}\[\]\^"~\*\?:\\\/]'

def _escape_es(text: str) -> str:
    return re.sub(_ES_SPECIALS, lambda m: '\\' + m.group(0), text)

def _normalize_ops(ops: Union[str, Sequence[str]], n_terms: int) -> list[str]:
    if isinstance(ops, str):
        return [ops.upper()] * (n_terms - 1)
    ops = [o.upper() for o in ops]
    if len(ops) == n_terms - 1:
        return ops
    raise ValueError("operators len error")

def _to_field_path(name: str) -> str:
    mapping = {
        "title": "content.title.value",
        "abstract": "content.abstract.value",
        "all": ""
    }
    return mapping.get(name.lower(), name)

def make_query_v2(
    keywords: Sequence[str],
    operators: Union[str, Sequence[str]] = "AND",
    field: Union[str, Sequence[str]] = "all",
    negative_keywords: Optional[Sequence[str]] = None,
    phrase: bool = True
) -> str:

    if not keywords:
        raise ValueError("keywords empty")
    if isinstance(field, str):
        fields = [_to_field_path(field)] * len(keywords)
    else:
        if len(field) != len(keywords):
            raise ValueError("field len error")
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