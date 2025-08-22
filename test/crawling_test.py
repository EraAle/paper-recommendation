from crawler import *

print("--- arxiv 호출해서 가져오기 테스트 ---")
# 케이스 1: 기본 (단일 키워드)
# keyword_list1 = ["attention"]
# field_list1 = ["title"]
# operator_list1 = ["AND"]
# document = main_crawling(keyword_list1, operator_list1, field_list1, limit=500, date = None, accept = False)
# document_print(document)

# keyword_list2 = ["robotics", "computer vision", "AI"]
# field_list2 = ["all"]
# operator_list2 = ["AND", "OR"]
# document2 = main_crawling(keyword_list2, operator_list2, field_list2, limit=500, date = None, accept = False)
# document_print(document2)

# keyword_list3 = ["transformer", "google"]
# field_list3 = ["title", "abstract"]
# operator_list3 = ["AND"]
# document3 = main_crawling(keyword_list3, operator_list3, field_list3, limit=50, date = None, accept = False)
# document_print(document3)

# keyword_list4 = []
# field_list4 = []
# operator_list4 = []
# document4 = main_crawling(keyword_list4, operator_list4, field_list4, limit=50, date = None, accept = False)
# document_print(document4)

# print("\n--- make_query_openreview_search 테스트 ---")
keyword_list5 = ["reinforcement", "learning"]
field_list5 = ["title"]
operator_list5 = ["OR"]
# # document5 = main_crawling(keyword_list5, operator_list5, field_list5, limit=50, date = None, accept = False)
# # document_print(document5)
# query = make_query_openreview_search(keyword_list5, field_list5, operator_list5)
# print(query)
# document6 = crawling_openreview_v2(query, 50, None, False)
# document_print(document6)
query = make_query_openreview_v1(keyword_list5, field_list5)
print(query)

document7 = crawling_openreview_v1(query, 50,  False)
document_print(document7)