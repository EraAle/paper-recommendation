import arxiv
import requests
import re
import math
import random
import textwrap


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

    PREFIX_MAP = {'title': 'ti', 'abstract': 'abs', 'all': 'all'}
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
        field_prefix = PREFIX_MAP.get(fields[i])
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

# This function retrieves the citation count for a single paper title at a time.
# If the paper cannot be found via the Crossref API, it simply returns a citation count of 0.
def get_citation_crossref(title: str, email: str) -> int:
    """
    Searches for a paper using its title via the Crossref API and retrieves its citation count.

    Args:
        title: The title of the paper.
        email: An argument used for polite pool access.
            Providing an email allows for unrestricted API usage.

    Returns:
        The citation count of the paper found using the title.
    """

    BASE_URL = "https://api.crossref.org/works"

    params = {
        "query.title": title,
        "rows": 1,  # Request only the single most relevant result
        "mailto": email  # Use the Polite Pool
    }

    try:
        # The requests.get() function combines the URL and parameters to request data from the Crossref server.
        response = requests.get(BASE_URL, params=params)

        # Check the HTTP status code.
        # If the response is not successful (i.e., 4xx or 5xx error), raise an HTTPError exception.
        response.raise_for_status()

        # Convert the response body from JSON to a Python dictionary.
        data = response.json()

        # Check whether the data['message']['items'] list is not empty based on the Crossref data structure.
        if data['message']['items']:
            # Assign the first search result to a variable.
            item = data['message']['items'][0]

            # Extract the citation count ('is-referenced-by-count') value.
            # Use .get() to return 0 as the default if the key is missing.
            citation_count = item.get('is-referenced-by-count', 0)

            # Return the extracted citation count as the result of the function.
            return citation_count
        else:
            # Return 0 if there are no search results.
            return 0

    # Executed when a network error occurs during requests.get(), or when the JSON structure is not as expected.
    except (requests.exceptions.RequestException, KeyError, IndexError):
        return 0

import requests

def get_citation_openalex(title: str, email: str) -> int:
    """
    Searches for the citation count of a paper using its title via the OpenAlex API.

    Args:
        title: The title of the paper.
        email: An argument used for polite pool access.
            Providing an email allows for unrestricted API usage.

    Returns:
        The citation count of the paper found using the title.
    """

    base_url = "https://api.openalex.org/works"
    params = {
        'search': title,
        'per_page': 1, # Request only the single most relevant result
        'mailto': email  # Use the Polite Pool
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Handle exceptions when an HTTP error occurs
        data = response.json()

        # Check if there are search results and the result list is not empty
        if data.get('results') and len(data['results']) > 0:
            # Retrieve the citation count ('cited_by_count') from the first result
            citation_count = data['results'][0].get('cited_by_count', 0)
            return citation_count
        else:
            # In case there are no search results
            return 0

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return 0


def sort_citation_crossref(document: list[dict[str, str]], email: str) -> list[dict[str, str]]:
    """
    Sorts the documents by citation count using the Crossref API.

    Args:
        document: The list of documents to be sorted.
        email: An argument used for polite pool access.
            Providing an email allows for unrestricted API usage.

    Returns:
        The list of documents sorted by citation count.
    """

    BASE_URL = "https://api.crossref.org/works"

    title_list = [doc["title"] for doc in document]
    citation_list = []

    for title in title_list:
        citation_count = get_citation_crossref(title, email)
        citation_list.append(citation_count)

    print(citation_list)
    # Zip together title_list and citation_count
    paired_list = list(zip(document, citation_list))

    # Sort the zipped list in descending order based on the citation count (the second element of each pair).
    #     key=lambda item: item[1]  --> Sort by the value at index 1 (citation count) of each pair
    #     reverse=True              --> Descending order (larger numbers come first)
    sorted_pairs = sorted(paired_list, key=lambda item: item[1], reverse=True)

    # Extract only the titles (the first element of each pair) from the sorted list of pairs.
    sorted_target_list = [tar for tar, criteria in sorted_pairs]

    return sorted_target_list

def sort_citation_openalex(document: list[dict[str, str]], email: str) -> list[dict[str, str]]:
    """
    Sorts the documents by citation count using the OpenAlex API.

    Args:
        document: The list of documents to be sorted.
        email: An argument used for polite pool access.
            Providing an email allows for unrestricted API usage.

    Returns:
        The list of documents sorted by citation count.
    """

    BASE_URL = "https://api.openalex.org/works"

    title_list = [doc["title"] for doc in document]
    citation_list = []

    for title in title_list:
        citation_count = get_citation_openalex(title, email)
        citation_list.append(citation_count)

    print(citation_list)
    # Zip together title_list and citation_count
    paired_list = list(zip(document, citation_list))

    # Sort the zipped list in descending order based on the citation count (the second element of each pair).
    #     key=lambda item: item[1]  --> Sort by the value at index 1 (citation count) of each pair
    #     reverse=True              --> Descending order (larger numbers come first)
    sorted_pairs = sorted(paired_list, key=lambda item: item[1], reverse=True)

    # Extract only the titles (the first element of each pair) from the sorted list of pairs.
    sorted_target_list = [tar for tar, criteria in sorted_pairs]

    return sorted_target_list

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

def document_print(document: list[dict[str, str]]) -> None:
    """
    Takes a list of paper information and prints it in a human-readable format.

    Args:
        document: The list of documents to print.
    """

    if not document:
        print("document is empty")
        return

    # Print each document with a number
    for i, doc in enumerate(document, 1):
        print(f"\n{'=' * 25} Document {i} {'=' * 25}")

        print(f"Title: {doc.get('title', 'N/A')}")

        print(f"URL: {doc.get('url', 'N/A')}")

        print("Abstract:")

        abstract = doc.get('abstract', 'N/A')
        wrapped_abstract = textwrap.fill(
            abstract,
            width=80,
            initial_indent="    ",
            subsequent_indent="    "
        )
        print(wrapped_abstract)

    print(f"\n{'=' * 58}")