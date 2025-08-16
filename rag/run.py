from rag.model import get_model
from rag.rag_retriever import RAGRetriever
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)


def retrieve_by_title(retriever: RAGRetriever, query: str, documents: list[dict]) -> list[dict]:
    if len(documents) <= 100:
        return documents

    title_list = [doc["title"] for doc in documents]
    top_indices = retriever.run(query, title_list, top_k=100)
    filtered_documents = [documents[i] for i in top_indices]

    return filtered_documents

def retrieve_by_title_and_abstract(retriever: RAGRetriever,
                         query: str,
                         filtered_documents: list[dict],
                         top_k: int) -> list[dict]:
    abstract_list = [doc["title"] + "\n" + doc["abstract"] for doc in filtered_documents]
    top_indices = retriever.run(query, abstract_list, top_k=top_k)
    filtered_documents = [filtered_documents[i] for i in top_indices]

    return filtered_documents


def run(query: str, documents: list[dict], top_k: int = 5, model_name: str = "all-MiniLM-L6-v2") -> list[dict]:
    """
    Retrieve the top-k most relevant documents for a given query.

    Args:
        query (str): Query string used for paper search.
        documents (list[dict]): List of document dictionaries.
            Each document should have the following format:
            {
                "title": str,
                "url": str,
                "abstract": str
            }
        top_k (int, optional): Number of top results to return. maximum=20, default=5.
        model_name (str, optional): model_name for BERT used in RAGRetriever. Defaults to "all-MiniLM-L6-v2".

    Returns:
        list[dict]: A list of tuples containing top-k documents sorted by score in descending order.
    """
    retriever = RAGRetriever(model_name)
    filtered_documents = retrieve_by_title(retriever, query, documents)
    filtered_documents = retrieve_by_title_and_abstract(retriever, query, filtered_documents, top_k)

    return filtered_documents