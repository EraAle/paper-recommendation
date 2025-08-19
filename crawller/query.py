# Set search keywords and maximum number of results
# When using this, ask them to write keywords within the list using only double quotes (""), not single quotes ('').
# The sort options are relevance, lastupdate, and submitted.

def make_query(keyword_list: list[str], operator: str | list[str] ="AND", field: str | list[str] = "title") -> str:
    """
    Creates a query to use with the arXiv API.

    Args:
        keyword_list: A list of keywords extracted from the instruction.
            Keywords in the list must be enclosed in double quotes only.
            Using single quotes may cause issues.

        operator: A string or list representing the operator(s) used to connect keywords.
            If a single string is provided, that operator will be used between all keywords.
            If a list is provided, operators will be inserted between keywords in order.

        field: A string or list representing the search field(s) for each keyword.
            If a single string is provided, it will be used for all keywords.
            If a list is provided, each keyword will be assigned a field in order.

    Returns:
        The constructed query string.
    """

    # 1. Enclose all keywords in the list with double quotes (").
    #    This is essential for searching phrases like 'def gh'.

    prefix_map = {'title': 'ti', 'abstract': 'abs', 'all': 'all'}
    num_keywords = len(keyword_list)

    if isinstance(operator, str):
        operators = [operator] * (num_keywords - 1)
    else:
        operators = operator

    if isinstance(field, str):
        fields = [field] * num_keywords
    else:
        fields = field

    query_term = []
    for i, keyword in enumerate(keyword_list):
        field_prefix = prefix_map.get(fields[i])
        if not field_prefix:
            raise ValueError(f"Invalid field name: {fields[i]}")
        query_term.append(f'{field_prefix}:"{keyword}"')

    if not query_term:
        return ""

    query_parts = [query_term[0]]

    for i in range(num_keywords - 1):
        query_parts.append(f" {operators[i]} ")

        query_parts.append(query_term[i + 1])

    return "".join(query_parts)