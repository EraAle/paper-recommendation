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

soft_document = main_crawling(soft_query, num=300)
document_print(soft_document)

# QUERY = '(all:"RL" OR all:"reinforcement learning")'
# docs = fetch_arxiv_bulk(QUERY, want=500, page_size=50, delay=3.0, sort_by="submittedDate")
# document_print(docs)