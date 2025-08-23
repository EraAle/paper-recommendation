from sentence_transformers import SentenceTransformer, CrossEncoder

bi_encoder_name_dict = {
    "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "msmarco-distilbert-base-v3": "sentence-transformers/msmarco-distilbert-base-v3",
    "msmarco-MiniLM-L-6-v3": "sentence-transformers/msmarco-MiniLM-L-6-v3",
    "ko-sroberta-multitask": "jhgan/ko-sroberta-multitask",
    "KoSimCSE-roberta-multitask": "BM-K/KoSimCSE-roberta-multitask"
}

cross_encoder_name_dict = {
    "ms-marco-MiniLM-L-6-v2": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "ms-marco-TinyBERT-L-6": "cross-encoder/ms-marco-TinyBERT-L-6",
    "ms-marco-electra-base": "cross-encoder/ms-marco-electra-base",
}

def get_encoder(model_name: str) -> SentenceTransformer:
    if model_name in bi_encoder_name_dict.keys():
        return SentenceTransformer(bi_encoder_name_dict[model_name])
    else:
        return SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def get_cross_encoder(model_name: str) -> CrossEncoder:
    if model_name in cross_encoder_name_dict.keys():
        return CrossEncoder(cross_encoder_name_dict[model_name])
    else:
        return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")