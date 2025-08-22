from crawler import *

# keyword_data = {
#   "main": [
#     ["RL", "reinforcement learning"],
#     ["LLM", "large language model"],
#     ["MoE", "Mixture of experts", "Mixture of expert"]
#   ],
#   "optional": ["circular", "refine", "self-evolving"]
#
    # }

keyword_data = {
  "main": [
    ["LLM", "Large Language Model"]
  ],
  "optional": []

    }

# 함수 실행
hard_query = hard_parsing(keyword_data, field="all")
soft_query = soft_parsing(keyword_data, field="all")

print("--- Hard Parsing (AND) ---")
print(hard_query)
# 예상 출력:
# ((all:"RL" OR all:"reinforcement learning") AND (all:"LLM" OR all:"large language model")) AND ((all:"circular" OR all:"refine" OR all:"self-evolving"))

print("\n--- Soft Parsing (OR) ---")
print(soft_query)
# 예상 출력:
# ((all:"RL" OR all:"reinforcement learning") AND (all:"LLM" OR all:"large la

# soft_document = main_crawling(soft_query, num=300)
# document_print(soft_document)

# QUERY = '(all:"RL" OR all:"reinforcement learning")'
# docs = fetch_arxiv_bulk(QUERY, want=500, page_size=50, delay=3.0, sort_by="submittedDate")
# document_print(docs)

kw = {
    "main": [
        ["transformer", "attention is all you need"], # 동의어 그룹 1 (OR)
        ["reasoning", "chain of thought"]            # 동의어 그룹 2 (OR)
    ],
    "optional": ["long-context", "in-context learning"]
}

# 둘 다 반드시 포함
q_hard = hard_parsing_openreview(kw, field="title")
# → ( (content.title:transformer OR content.title:"attention is all you need")
#     AND (content.title:reasoning OR content.title:"chain of thought") )
#     AND (content.title:"long-context" AND content.title:"in-context learning")
print("q_hard: ", q_hard)

# 메인 또는 옵션 어느 한쪽만 충족
q_soft = soft_parsing_openreview(kw, field="abstract")
# → ( ...main AND ...main ) OR (content.abstract:"long-context" OR content.abstract:"in-context learning")
print("q_soft: ", q_soft)

# 실제 호출
# notes = client.search_notes(term=q_hard, limit=50, offset=0)
