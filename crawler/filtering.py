from datetime import datetime
import re
from .query import *
from .openreview_crawling import *

def v1_accept_filter(documents: list[dict[str, any]]) -> list[dict[str, any]]:

    # Accept으로 간주할 키워드 패턴 (대소문자 무시)
    # Oral, Poster, Spotlight 발표도 Accept된 논문이므로 포함
    accept_pattern = re.compile('accept|oral|poster|spotlight', re.IGNORECASE)

    filtered_documents = [
        doc for doc in documents
        if accept_pattern.search(doc.get('decision_info', ''))
    ]

    return filtered_documents

# 최종 업데이트 기준
def arxiv_date_filter(documents: list[dict[str, any]], date: list[int]) -> list[dict[str, any]]:
    if not date or len(date) != 2:
        return documents

    start_year, end_year = date[0], date[1]
    filtered_documents = []

    for doc in documents:
        if 'updated_date' in doc and isinstance(doc['updated_date'], datetime):
            paper_year = doc['updated_date'].year
            if start_year <= paper_year <= end_year:
                filtered_documents.append(doc)

    return filtered_documents

from datetime import datetime, timezone
from typing import Any as any

def openreview_date_filter(documents: list[dict[str, any]], date: list[int]) -> list[dict[str, any]]:

# 우선순위: content.year(또는 year) > mdate(ms) > cdate(ms)

    if not date or len(date) != 2:
        return documents

    start_year, end_year = date[0], date[1]
    filtered_documents = []

    for doc in documents:
        paper_year = None

        # content.year 또는 year
        if isinstance(doc.get('year'), int):
            paper_year = doc['year']
        elif isinstance(doc.get('content_year'), int):
            paper_year = doc['content_year']

        # mdate(수정 시각, ms)
        if paper_year is None and isinstance(doc.get('mdate'), (int, float)):
            try:
                paper_year = datetime.fromtimestamp(doc['mdate'] / 1000, tz=timezone.utc).year
            except Exception:
                pass

        # cdate(생성 시각, ms)
        if paper_year is None and isinstance(doc.get('cdate'), (int, float)):
            try:
                paper_year = datetime.fromtimestamp(doc['cdate'] / 1000, tz=timezone.utc).year
            except Exception:
                pass

        # 필터 적용
        if paper_year is not None and start_year <= paper_year <= end_year:
            filtered_documents.append(doc)

    return filtered_documents



def na_filter(documents: list[dict[str, any]]) -> list[dict[str, any]]:
    filtered_documents = []
    for doc in documents:
        title = str(doc.get('title', '') or '').strip()
        abstract = str(doc.get('abstract', '') or '').strip()
        url = str(doc.get('url', '') or '').strip()

        ok_title = (title and title.upper() != 'N/A')
        ok_abstract = (abstract and abstract.upper() != 'N/A')
        ok_url = (url and url.upper() != 'N/A' and url.startswith(('http://', 'https://')))

        if ok_title and ok_abstract and ok_url:
            filtered_documents.append(doc)

    print(f"필터링 완료: 총 {len(documents)}개 중 {len(filtered_documents)}개 논문이 선택되었습니다.")
    return filtered_documents