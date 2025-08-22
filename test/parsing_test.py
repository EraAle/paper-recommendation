from crawler import *

# keyword_data = {
#   "main": [
#     ["RL", "reinforcement learning"],
#     ["LLM", "large language model"]
#   ],
#   "optional": ["circular", "refine", "self-evolving"]
#
#     }

keyword_data = {
    "main": [
    ["transformer"]
  ],
  "optional": []
  }


# 함수 실행
hard_query = hard_parsing_arxiv(keyword_data, field="all")
soft_query = soft_parsing_arxiv(keyword_data, field="all")

print("--- Hard Parsing (AND) ---")
print(hard_query)
# 예상 출력:
# ((all:"RL" OR all:"reinforcement learning") AND (all:"LLM" OR all:"large language model")) AND ((all:"circular" OR all:"refine" OR all:"self-evolving"))

print("\n--- Soft Parsing (OR) ---")
print(soft_query)

query = soft_parsing_openreview(keyword_data, field="title")
print(query)

# 100개 나왔음
# document_arxiv = main_crawling(keyword_data, field="all", num=150, date=None, accept=False)
# document_print(document_arxiv)
#
# document_arxiv_date = main_crawling(keyword_data, field="all", num=150, date=[2024, 2024], accept=False)
# document_print(document_arxiv_date)
#
document_openreview = main_crawling(keyword_data, field="title", num=50, date=None, accept=True)
document_print(document_openreview)
#
# document_openreview_date = main_crawling(keyword_data, field="all", num=50, date=[2024, 2024], accept=True)
# document_print(document_openreview_date)

#
#
# kw = {
#     "main": [
#         ["transformer", "attention is all you need"], # 동의어 그룹 1 (OR)
#         ["reasoning", "chain of thought"]            # 동의어 그룹 2 (OR)
#     ],
#     "optional": ["long-context", "in-context learning"]
# }
#
# # 둘 다 반드시 포함
# q_hard = hard_parsing_openreview(kw, field="title")
# # → ( (content.title:transformer OR content.title:"attention is all you need")
# #     AND (content.title:reasoning OR content.title:"chain of thought") )
# #     AND (content.title:"long-context" AND content.title:"in-context learning")
# print("q_hard: ", q_hard)
#
# # 메인 또는 옵션 어느 한쪽만 충족
# q_soft = soft_parsing_openreview(kw, field="abstract")
# # → ( ...main AND ...main ) OR (content.abstract:"long-context" OR content.abstract:"in-context learning")
# print("q_soft: ", q_soft)

# 실제 호출
# notes = client.search_notes(term=q_hard, limit=50, offset=0)
