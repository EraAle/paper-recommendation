from sentence_transformers import SentenceTransformer

model_name_dict = {
    "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "msmarco-distilbert-base-v3": "sentence-transformers/msmarco-distilbert-base-v3",
    "msmarco-MiniLM-L-6-v3": "sentence-transformers/msmarco-MiniLM-L-6-v3",
    "ko-sroberta-multitask": "jhgan/ko-sroberta-multitask",
    "KoSimCSE-roberta-multitask": "BM-K/KoSimCSE-roberta-multitask"
}

def get_model(model_name: str) -> SentenceTransformer:
    full_model_name = model_name_dict[model_name]
    if full_model_name:
        return SentenceTransformer(full_model_name)
    else:
        return SentenceTransformer("sentence-transformers/all-mpnet-base-v2")