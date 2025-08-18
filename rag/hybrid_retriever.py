from rag import model
import torch
from rank_bm25 import BM25Okapi
import spacy
import torch.nn.functional as F


class HybridRetriever:
    def __init__(self, encoder_model_name: str="all-mpnet-base-v2", use_cuda: bool=True):
        if use_cuda:
            self.encoder = model.get_encoder(encoder_model_name).to("cuda")
        else:
            self.encoder = model.get_encoder(encoder_model_name)
        self.nlp = spacy.load("en_core_web_sm")
        self.bm25 = None

    def tokenize(self, text: str):
        return [token.lemma_.lower() for token in self.nlp(text) if not token.is_stop and token.is_alpha]

    def build_bm25(self, refs: list[str]):
        tokenized = [self.tokenize(ref) for ref in refs]
        self.bm25 = BM25Okapi(tokenized)

    def get_embeddings(self, input_list: list[str]):
        """
        Encode a list of strings into a tensor of embeddings.
        """
        return self.encoder.encode(input_list, convert_to_tensor=True)

    def compute_cosine_similarity(self, query_emb: torch.Tensor, ref_embs: torch.Tensor) -> list[float]:
        """
        Compute cosine similarity between a query embedding and reference embeddings.

        Args:
            query_emb (torch.Tensor): query embedding tensor (shape: [dim] or [1, dim])
            ref_embs (torch.Tensor): reference embeddings tensor (shape: [N, dim])

        Returns:
            list[float]: cosine similarity scores for each reference
        """
        if query_emb.dim() == 1:
            query_emb = query_emb.unsqueeze(0)

        cosine_scores = F.cosine_similarity(query_emb, ref_embs)

        return cosine_scores.tolist()

    def run(self, query: str, titles: list[str], abstracts: list[str], alpha: float = 0.7, top_k: int = 1000):
        """
        Hybrid retrieval using BM25 and cosine similarity.

        Args:
            query (str): query string
            titles (list[str]): titles of papers
            abstracts (list[str]): abstracts of papers
            alpha (float): weight for BM25 score (1-alpha for cosine similarity)
            top_k (int): number of top indices to return

        Returns:
            list[int]: indices of top-k documents ranked by hybrid score
        """
        if alpha < 0 or alpha > 1:
            raise ValueError("alpha must be in [0, 1]")

        documents = []
        for i in range(len(titles)):
            documents.append(titles[i] + "\n" + abstracts[i])

        self.build_bm25(documents)

        tokenized_query = self.tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query).tolist()

        query_emb = self.encoder.encode(query, convert_to_tensor=True)
        ref_embs = self.get_embeddings(titles)
        cosine_scores = self.compute_cosine_similarity(query_emb, ref_embs)

        bm25_tensor = torch.tensor(bm25_scores, dtype=torch.float32)
        cos_tensor = torch.tensor(cosine_scores, dtype=torch.float32)

        if bm25_tensor.max() > 0:
            bm25_tensor = (bm25_tensor - bm25_tensor.min()) / (bm25_tensor.max() - bm25_tensor.min() + 1e-8)
        if cos_tensor.max() > 0:
            cos_tensor = (cos_tensor - cos_tensor.min()) / (cos_tensor.max() - cos_tensor.min() + 1e-8)

        hybrid_scores = alpha * bm25_tensor + (1 - alpha) * cos_tensor

        top_k = min(top_k, len(titles))
        top_indices = torch.topk(hybrid_scores, k=top_k).indices.tolist()

        return top_indices