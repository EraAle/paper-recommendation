from crawler import *

import re
from typing import Any as any, List, Dict
import openreview




# 1. 제목에 transformer, 초록에 attention 둘 다 포함
q1 = build_search_notes_query_v2(
    keywords=["transformer", "attention"],
    operators="AND",
    field=["title", "abstract"]
)
# -> '(content.title:transformer AND content.abstract:attention)'
print("q1:", q1)

# 2. 전체에서 transformer OR llm, 단 survey 제외
q2 = build_search_notes_query_v2(
    keywords=["transformer", "llm"],
    operators="OR",
    field="all",
    negative_keywords=["survey"]
)
# -> '("transformer" OR llm) NOT survey'
print("q2:", q2)

q2 = build_search_notes_query_v2(
    keywords=["transformer"],
    field="all"
)
print("q2:", q2)

# 실제 호출
document = crawling_openreview_v2(q2, 50, False)
document_print(document)

