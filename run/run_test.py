from crawller.crawling import *
from rag.run import *
from rag.rag_retriever import RAGRetriever

query = "I want to find paper related to transformer rag and mixure of experts."

keyword_list = ["transformer", "Mixture of experts", "rag"]

search_query = make_query(keyword_list, operator="AND", field="title")

operator_list = ["AND", "OR"]

search_query2 = make_query_with_operator(keyword_list, operator_list, field="abstract")

print(search_query)
print(search_query2)
# documents = []
#
# email = "ljjstar0714@naver.com"
#
# documents = crawling_basic(keyword_list, num=10, operator="AND", sort_op="relevance")
#
#
# filltered_documents = run(query, documents, top_k = 5, model_name = "all-MiniLM-L6-v2")
# print(filltered_documents)
# # print(len(filltered_documents))
#
# citation_documents = sort_citation(filltered_documents, email)
# print(citation_documents)
# print(len(citation_documents))