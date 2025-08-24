from rag.hybrid_retriever import HybridRetriever
from rag.model import get_encoder
from rag.rag_retriever import RAGRetriever
from rich.logging import RichHandler
import logging

from rag.reranker import Reranker

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)

hybrid_retriever = None
rag_retriever = None
reranker = None

def hybrid_retrieve(model: HybridRetriever,
                    query: str,
                    documents: list[dict],
                    alpha: float=0.7,
                    top_k: int=1000):
    if len(documents) <= top_k:
        return documents

    titles = [doc['title'] for doc in documents]
    abstracts = [doc['abstract'] for doc in documents]

    top_indices = model.run(query, titles, abstracts, alpha=alpha, top_k=top_k)
    retrieved_documents = [documents[i] for i in top_indices]

    return retrieved_documents

def rag_retrieve(model: RAGRetriever,
                 query: str,
                 documents: list[dict],
                 top_k: int=100):
    if len(documents) <= top_k:
        return documents

    refs = [doc['title'] + "\n" + doc['abstract'] for doc in documents]

    top_indices = model.run(query, refs, top_k=top_k)
    retrieved_documents = [documents[i] for i in top_indices]

    return retrieved_documents

def rerank(model: Reranker,
           query: str,
           documents: list[dict],
           top_k: int=10):
    refs = [doc['title'] + "\n" + doc['abstract'] for doc in documents]

    top_indices = model.run(query, refs, top_k=top_k)
    retrieved_documents = [documents[i] for i in top_indices]

    return retrieved_documents

def setup(encoder_model_name: str = "all-MiniLM-L6-v2",
          cross_encoder_model_name: str = "ms-marco-MiniLM-L-6-v2",
          use_cuda: bool = True) -> None:
    global hybrid_retriever, rag_retriever, reranker

    logging.info("Loading Hybrid Retriever...")
    hybrid_retriever = HybridRetriever(encoder_model_name, use_cuda=use_cuda)
    logging.info("Loading RAG Retriever...")
    rag_retriever = RAGRetriever(encoder_model_name, use_cuda=use_cuda)
    logging.info("Loading Reranker...")
    reranker = Reranker(cross_encoder_model_name, use_cuda=use_cuda)

def run(query: str,
        documents: list[dict],
        alpha: float=0.7,
        top_k: int = 10,
        encoder_model_name: str = "all-MiniLM-L6-v2",
        cross_encoder_model_name: str = "ms-marco-MiniLM-L-6-v2",
        use_cuda: bool = True) -> list[dict]:
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
        alpha (float, optional): weight for BM25 score (1-alpha for cosine similarity)
        top_k (int, optional): Number of top results to return. maximum=20, default=5.
        encoder_model_name (str, optional): model_name for BERT used in RAGRetriever. Defaults to "all-MiniLM-L6-v2".
        cross_encoder_model_name (str, optional): model_name for Reranker. Defaults to "ms-marco-MiniLM-L-6-v2".
        use_cuda (bool, optional): Whether to use CUDA or not. Defaults to True.

    Returns:
        list[dict]: A list of tuples containing top-k documents sorted by score in descending order.
    """
    global hybrid_retriever, rag_retriever, reranker

    logging.info("Running Hybrid Retriever...")
    retrieved_documents = hybrid_retrieve(hybrid_retriever, query, documents, alpha=alpha)
    logging.info("Running RAG Retriever...")
    retrieved_documents = rag_retrieve(rag_retriever, query, retrieved_documents)
    logging.info("Running Reranker...")
    retrieved_documents = rerank(reranker, query, retrieved_documents, top_k=top_k)

    return retrieved_documents