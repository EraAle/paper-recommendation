import arxiv
import random


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

