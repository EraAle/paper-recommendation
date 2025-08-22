from crawler import *
from crawler.query import make_query_openreview_search
from rag.run import run

######### arxiv query test #########

# 테스트 user instruction
query = "I want to find paper related to transformer rag and mixure of experts."

# 키워드 뽑았다 치고 리스트
keyword_list1 = ["Mixture of experts"]
keyword_list = ["transformer", "Mixture of experts"]

# arxiv 쿼리 제작 함수
search_query = make_query_arxiv(keyword_list1, field=["all"])

operator_list = ["AND"]

field_list = ["title", "abstract"]

search_query2 = make_query_arxiv(keyword_list, operator_list, field_list)

# 만들어진 arxiv 쿼리
print("search_query:", search_query)
print("search_query2:", search_query2)

######### openreview search_notes() query form test #########
api_keyword = ["Mixture of experts"]
api_field = ["abstract"]

api_query = make_query_openreview_search(api_keyword, api_field)

print("api_query:", api_query)

document = crawling_openreview_v2("transformer AND attention", 50, False)
document_print(document)

######### api v1 query test #########

# api_v1_keyword = "Mixture of experts"
# api_v1_field = "abstract"
#
# api_v1_query = make_query_openreview_v1(api_v1_keyword, api_v1_field)
#
# print("api_v1_query:", api_v1_query)


######### api v2 query test #########

### 한 개 ###
# api_v2_keyword_one = ["Mixture of experts"]
# api_v2_field_one = ["title"]
#
# api_v2_query_one = make_query_openreview_v2(api_v2_keyword_one, api_v2_field_one)
#
# print("api_v2_query_one:", api_v2_query_one)

### 여러 개 ###
# api_v2_keyword = ["Mixture of experts", "transformer", "rag"]
# api_v2_field = ["title", "title", "title"]
# api_v2_operator = ["and"]
#
# api_v2_query = make_query_openreview_v2(keyword_list=api_v2_keyword,operator=api_v2_operator, field=api_v2_field)
#
# print("api_v2_query:", api_v2_query)

#
# email = "ljjstar0714@naver.com"
#
# documents = crawling_basic(search_query, num=10, sort_op="relevance")
#
# filtered_documents = run(query, documents, top_k = 5, model_name = "all-MiniLM-L6-v2")
# print("filtered_documents:")
# document_print(filtered_documents)
#
# citation_documents = sort_citation_crossref(filtered_documents, email)
# print("citation_documents:")
# document_print(citation_documents)
# print(len(citation_documents))
#
# citation_documents2 = sort_citation_openalex(filtered_documents, email)
# print("citation_documents2:")
# document_print(citation_documents2)
#
# random_document = random_crawling(10, 5)
# print("random_document:")
# document_print(random_document)
