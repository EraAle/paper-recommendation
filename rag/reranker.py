import torch
from rag import model
import torch.nn.functional as F

class Reranker:
    def __init__(self, model_name: str="ms-marco-MiniLM-L-6-v2", use_cuda: bool=True):
        self.encoder = model.get_cross_encoder(model_name).to("cuda") if use_cuda else model.get_cross_encoder(model_name)

    def run(self, query: str, refs: list[str], top_k: int=10):
        pairs = [[query, ref] for ref in refs]
        scores = self.encoder.predict(pairs)

        top_k = min(top_k, len(refs))
        top_indices = torch.topk(torch.tensor(scores), k=top_k).indices.tolist()
        return top_indices