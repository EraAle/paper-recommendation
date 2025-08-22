from crawler import *
from rag.run import run

# keyword_data = {
#   "main": [
#     ["RL", "reinforcement learning"],
#     ["LLM", "large language model"]
#   ],
#   "optional": ["circular", "refine", "self-evolving"]
#
#     }

# keyword_data = {
#     "main": [
#     ["transformer"]
#   ],
#   "optional": []
#   }

# keyword_data = {
#     "main": [
#         ["transformer", "attention is all you need"], # 동의어 그룹 1 (OR)
#         ["reasoning", "chain of thought"]            # 동의어 그룹 2 (OR)
#     ],
#     "optional": ["long-context", "in-context learning"]
# }
#
# instruction = "I want to read transformer paper. for example, attention is all you need. and reasoning long-context and in-context learning paper."
#

# keyword_data = {
#     "main": [
#         ["llm", "large language model"],          # 동의어 그룹 1 (OR)
#         ["alignment", "rlhf", "dpo"],             # 동의어 그룹 2 (OR)
#         ["retrieval", "rag"]                      # 동의어 그룹 3 (OR)
#     ],
#     "optional": ["efficiency", "quantization", "distillation"]
# }
#
# instruction = "I want to read llm paper. for example, large language model. and alignment rlhf dpo and retrieval rag efficiency quantization and distillation paper."

# keyword_data = {
#     "main": [
#         ["multimodal", "vision-language", "vlm"],   # 동의어 그룹 1 (OR)
#         ["reasoning", "chain of thought", "cot"],   # 동의어 그룹 2 (OR)
#         ["memory", "long-term memory"]              # 동의어 그룹 3 (OR)
#     ],
#     "optional": ["tool-use", "agent", "planning"]
# }
#
# instruction = "I want to read multimodal paper. for example, vision-language vlm. and reasoning chain of thought cot and memory long-term memory tool-use agent and planning paper."


# 함수 실행
# hard_query = hard_parsing_arxiv(keyword_data, field="all")
# soft_query = soft_parsing_arxiv(keyword_data, field="all")

# print("--- Hard Parsing (AND) ---")
# print(hard_query)
# 예상 출력:
# ((all:"RL" OR all:"reinforcement learning") AND (all:"LLM" OR all:"large language model")) AND ((all:"circular" OR all:"refine" OR all:"self-evolving"))

# print("\n--- Soft Parsing (OR) ---")
# print(soft_query)

# query = soft_parsing_openreview(keyword_data, field="all")
# print(query)
#
test_keyword_data = ["test1", "test2", "test3"]
operator = ["AND", "OR"]
field = ["title", "abstract", "all"]
#
query_open = make_query_v2(test_keyword_data, operator, field=field)
print("이거임", query_open)

# 100개 나왔음
# document_arxiv = main_crawling(keyword_data, field="all", num=150, date=None, accept=False)
# document_print(document_arxiv)
#
# document_arxiv_date = main_crawling(keyword_data, field="all", num=150, date=[2024, 2024], accept=False)
# document_print(document_arxiv_date)

# document_openreview = main_crawling(keyword_data, field="all", num=50, date=None, accept=True)

#
document_openreview_date = main_crawling(keyword_data, field="all", num=250, date=[2023, 2025], accept=True)
document_print(document_openreview_date)
# #
result = run(instruction, document_openreview_date, top_k=5)
document_print(result)



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
