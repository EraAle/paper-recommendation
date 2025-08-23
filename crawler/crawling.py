import arxiv
import time
import random

from .parsing import *
from .openreview_crawling import *

import urllib.parse, requests, feedparser
from typing import Any, List, Dict


ID_PAT = re.compile(r"/abs/([^/]+)$")  # YYMM.NNNNNvX 추출

def _short_id(entry_id: str) -> str:
    m = ID_PAT.search(entry_id or "")
    return m.group(1) if m else (entry_id or "")

def crawling_basic(search_query: str, num: int = 50, sort_op: str = "submitted") -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    seen_ids = set()

    try:
        sort_criterion_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastupdate": arxiv.SortCriterion.LastUpdatedDate,
            "submitted": arxiv.SortCriterion.SubmittedDate
        }
        sort_criterion = sort_criterion_map.get(sort_op, arxiv.SortCriterion.SubmittedDate)

        client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=5)

        max_empty_retries = 2
        empty_retries = 0

        while len(documents) < num and empty_retries < max_empty_retries:
            try:
                search = arxiv.Search(
                    query=search_query,
                    max_results=num - len(documents),  # 남은 만큼만
                    sort_by=sort_criterion
                )
                got = 0
                for result in client.results(search):
                    if len(documents) >= num:
                        break

                    entry_id = getattr(result, "entry_id", "") or getattr(result, "id", "")
                    sid = _short_id(entry_id)  # 예: '2408.12345v2'
                    if sid in seen_ids:
                        continue
                    seen_ids.add(sid)

                    pdf_url = getattr(result, "pdf_url", None)
                    if not pdf_url and "/abs/" in entry_id:
                        pdf_url = entry_id.replace("/abs/", "/pdf/") + ".pdf"

                    documents.append({
                        'title': result.title,
                        'url': pdf_url or entry_id,
                        'abstract': result.summary,
                        'updated_date': result.updated,
                        'arxiv_id': sid,
                    })
                    got += 1

                    if len(documents) % 500 == 0 and len(documents) < num:
                        print(f"document: {len(documents)}. waiting 7 seconds…")
                        time.sleep(7)

                if got == 0:
                    empty_retries += 1
                    print(f"[warn] empty page error → {empty_retries}/5 try (waiting 5 secondes)")
                    time.sleep(5)
                else:
                    empty_retries = 0

            except Exception as e:
                if "unexpectedly empty" in str(e).lower():
                    empty_retries += 1
                    print(f"[warn] empty page error → {empty_retries}/5 try (waiting 5 secondes)")
                    time.sleep(5)
                    continue
                else:
                    print(f"[stop] error: {e}")
                    break


    except Exception as e:
        print(f"\n[!] stop error and return: {e}")

    return documents[:num]


def main_crawling(keyword_dict: dict,
                  field: str = "all",
                  num: int = 50,
                  sort_op: str = "sumitted",
                  date: list[int] = None, accept = False, openreview: bool = False) -> list[dict[str, any]]:

    if openreview:
        search_query = soft_parsing_openreview(keyword_dict, field=field)
        documents = crawling_openreview_v2(search_query, num, accept)
        if date is None:
            return documents
        else:
            documents = openreview_date_filter(documents, date)
            return documents

    if date is None:
        if accept == True:
            search_query = soft_parsing_arxiv(keyword_dict, field)
            documents = crawling_openreview_v2(search_query, num, accept)
        else:
            search_query = soft_parsing_openreview(keyword_dict, field)
            documents = crawling_basic(search_query, num, sort_op)
    else:
        if accept == True:
            new_num = 3 * num
            search_query = soft_parsing_openreview(keyword_dict, field)
            documents = crawling_openreview_v2(search_query, num, accept)
            documents = openreview_date_filter(documents, date)
        else:
            new_num = 3 * num
            search_query = soft_parsing_arxiv(keyword_dict, field)
            documents = crawling_basic(search_query, new_num, sort_op)
            documents = arxiv_date_filter(documents, date)

    if len(documents) > num:
        documents = documents[:num]

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

