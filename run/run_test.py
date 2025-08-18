from crawller import *
from rag.run import run

query = "I want to find paper related to transformer rag and mixure of experts."

keyword_list = ["transformer", "Mixture of experts"]

search_query = make_query(keyword_list, operator="AND", field="all")

operator_list = ["AND"]

field_list = ["title", "abstract"]

search_query2 = make_query(keyword_list, operator_list, field_list)

print("search_query:", search_query)
print("search_query2:", search_query2)


email = "ljjstar0714@naver.com"

documents = crawling_basic(search_query, num=10, sort_op="relevance")

filtered_documents = run(query, documents, top_k = 5, model_name = "all-MiniLM-L6-v2")
print("filtered_documents:")
document_print(filtered_documents)

citation_documents = sort_citation_crossref(filtered_documents, email)
print("citation_documents:")
document_print(citation_documents)
print(len(citation_documents))

citation_documents2 = sort_citation_openalex(filtered_documents, email)
print("citation_documents2:")
document_print(citation_documents2)

random_document = random_crawling(10, 5)
print("random_document:")
document_print(random_document)
