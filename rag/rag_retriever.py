import torch
from rag import model
import torch.nn.functional as F

class RAGRetriever:
    def __init__(self, model_name:str="all-MiniLM-L6-v2", use_cuda:bool=True):
        self.encoder = model.get_encoder(model_name).to("cuda") if use_cuda else model.get_encoder(model_name)

    def get_embedding(self, input_str: str):
        """
        Encode a single string into an embedding tensor.
        """
        return self.encoder.encode(input_str, convert_to_tensor=True)

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

    def run(self, query: str, refs: list, top_k: int = 3):
        """
        Full pipeline: encode query and references, compute similarities, return top-k matches.
        """
        query_emb = self.get_embedding(query)
        ref_embs = self.get_embeddings(refs)

        scores = self.compute_cosine_similarity(query_emb, ref_embs)

        top_k = min(top_k, len(refs))
        top_indices = torch.topk(torch.tensor(scores), k=top_k).indices.tolist()
        return top_indices