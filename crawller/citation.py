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

    base_url = "https://api.crossref.org/works"

    params = {
        "query.title": title,
        "rows": 1,  # Request only the single most relevant result
        "mailto": email  # Use the Polite Pool
    }

    try:
        # The requests.get() function combines the URL and parameters to request data from the Crossref server.
        response = requests.get(base_url, params=params)

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