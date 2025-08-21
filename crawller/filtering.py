from datetime import datetime

# 만약 년도 상한은 필터로 쓰고 싶지 않고 accept여부만 쓰고 싶다면
# 년도 상한에는 None을 입력
# accept 여부는 필터링에 사용하지 않을거면 False로 두기
# openreview api는 두 가지로 나뉘어서, 년도 상한이 있다면 그걸 고려해야 할듯.
# 년도 상한에 맞게 crawling_openreview로 논문 가져와야겠다
# 최대한 num에 맞게 retry해서 사용하되, 에러 나도 3번 정도 시도하고 그래도 실패하면 그냥 거기서 끝내자

# api2는 날짜별 필터링 검색을 지원하지만
# api1은 지원하지 않아서 따로 filtering하자
def crawling_filtering_api_v1(document: list[dict[str, str]], date: list[int], sort_op: str="relevance", accept = True) -> list[dict[str, str]]:
    """
        crawling_openreview (API v1)로부터 받은 결과 리스트를 연도(date)에 맞게 필터링합니다.

        Args:
            documents: 'cdate' (Unix timestamp in ms)를 포함하는 논문 딕셔너리 리스트.
            date: 필터링할 시작 연도와 종료 연도. 예: [2021, 2022]

        Returns:
            지정된 연도 범위에 해당하는 논문 딕셔너리 리스트.
        """
    if not date or len(date) != 2:
        # 날짜 정보가 없으면 필터링 없이 그대로 반환
        return document

    start_year, end_year = date
    filtered_documents = []

    for paper in document:
        # 'cdate' 키가 없는 경우를 대비한 예외 처리
        if 'cdate' not in paper or not paper['cdate']:
            continue

        # 1. Unix 타임스탬프(ms)를 datetime 객체로 변환
        timestamp_ms = paper['cdate']
        creation_date = datetime.fromtimestamp(timestamp_ms / 1000)

        # 2. 연도를 추출하여 범위 내에 있는지 확인
        publication_year = creation_date.year
        if start_year <= publication_year <= end_year:
            filtered_documents.append(paper)

    return filtered_documents