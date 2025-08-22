import arxiv
import time
import random
from .openreview_crawling import *

import arxiv
import time

import time, urllib.parse, requests, feedparser
from typing import Any, List, Dict


ID_PAT = re.compile(r"/abs/([^/]+)$")  # YYMM.NNNNNvX 추출

def _short_id(entry_id: str) -> str:
    m = ID_PAT.search(entry_id or "")
    return m.group(1) if m else (entry_id or "")

def crawling_basic(search_query: str, num: int = 50, sort_op: str = "submitted") -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    seen_ids = set()  # ← dedup 핵심

    try:
        sort_criterion_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastupdate": arxiv.SortCriterion.LastUpdatedDate,
            "submitted": arxiv.SortCriterion.SubmittedDate
        }
        sort_criterion = sort_criterion_map.get(sort_op, arxiv.SortCriterion.SubmittedDate)

        client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=5)
        print(f"총 {num}개의 논문 검색을 시작합니다.")

        max_empty_retries = 5
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
                        'arxiv_id': sid,  # (옵션) 저장해두면 편함
                    })
                    got += 1

                    # 500개마다만 쿨다운 (client가 이미 3초 쉬어줌)
                    if len(documents) % 500 == 0 and len(documents) < num:
                        print(f"현재 {len(documents)}개. 7초 대기…")
                        time.sleep(7)

                if got == 0:
                    empty_retries += 1
                    print(f"[warn] 빈 페이지/새 항목 0건 → {empty_retries}/5 재시도 (5초 대기)")
                    time.sleep(5)
                else:
                    empty_retries = 0

            except Exception as e:
                if "unexpectedly empty" in str(e).lower():
                    empty_retries += 1
                    print(f"[warn] 빈 페이지 예외 → {empty_retries}/5 재시도 (5초 대기)")
                    time.sleep(5)
                    continue
                else:
                    print(f"[stop] 알 수 없는 오류: {e}")
                    break

        print(f"총 {len(documents)}개의 논문 검색을 완료했습니다.")

    except Exception as e:
        print(f"\n[!] 검색 중 치명적 오류: {e}")
        print(f"지금까지 수집된 {len(documents)}개 반환")

    return documents[:num]


def main_crawling(search_query,
                  num: int = 50,
                  sort_op: str = "sumitted",
                  date: list[int] = None) -> list[dict[str, any]]:

    if date is None:
        documents = crawling_basic(search_query, num, sort_op)
    else:
        new_num = 3 * num
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

BASE = "https://export.arxiv.org/api/query"

def fetch_arxiv_bulk(query: str, want: int = 3000, page_size: int = 50,
                     delay: float = 3.0, max_retries: int = 3,
                     sort_by: str = "submittedDate", sort_order: str = "descending") -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    seen = set()
    start = 0
    consecutive_empty = 0

    def entry_to_doc(e):
        title = (getattr(e, "title", "") or "").strip()
        pdf_url = getattr(e, "pdf_url", None)
        entry_id = getattr(e, "id", "") or getattr(e, "entry_id", "")
        if not pdf_url:
            pdf_url = entry_id.replace("/abs/", "/pdf/") + ".pdf" if "/abs/" in entry_id else entry_id
        return title, {
            "title": title,
            "url": pdf_url,
            "abstract": getattr(e, "summary", ""),
            "updated_date": getattr(e, "updated", None),
            "published_date": getattr(e, "published", None),
            "id": entry_id,
            "authors": [a.name for a in getattr(e, "authors", [])] if hasattr(e, "authors") else [],
        }

    print(f"총 {want}개의 논문 검색을 시작합니다.")
    while len(docs) < want:
        params = {
            "search_query": query,
            "start": start,
            "max_results": page_size,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
        url = f"{BASE}?{urllib.parse.urlencode(params)}"

        feed = None
        last_exc = None
        for attempt in range(1, max_retries + 1):
            try:
                r = requests.get(url, timeout=30)
                if r.status_code in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"HTTP {r.status_code}")
                r.raise_for_status()
                feed = feedparser.parse(r.text)
                if feed.entries:
                    break
                last_exc = ValueError("Empty page")
            except Exception as e:
                last_exc = e
            sleep_s = delay * (1.5 ** (attempt - 1))
            print(f"[warn] {last_exc} → {sleep_s:.1f}s 대기 후 재시도({attempt}/{max_retries})")
            time.sleep(sleep_s)

        if feed is None or not feed.entries:
            consecutive_empty += 1
            if consecutive_empty >= 3:
                print("[error] 빈 페이지 3회 연속. 중단.")
                break
            # ★ 경계 우회: start를 반 페이지 뒤로 되돌림
            start = max(0, start - page_size // 2)
            time.sleep(delay)
            continue
        else:
            consecutive_empty = 0

        added = 0
        for e in feed.entries:
            title, d = entry_to_doc(e)
            key = (title, d["url"])
            if key in seen:
                continue
            seen.add(key)
            docs.append(d)
            added += 1
            if len(docs) >= want:
                break

        print(f"[page] start={start} got={added} have={len(docs)}/{want}")
        start += page_size

        # 장거리 예의상 쿨다운
        if len(docs) % 500 == 0 and len(docs) < want:
            print("장거리 예의상 7초 휴식…")
            time.sleep(7)

        time.sleep(delay)

    print(f"총 {len(docs)}개의 논문 검색을 완료했습니다.")
    return docs
