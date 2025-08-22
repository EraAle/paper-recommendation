# test_pipeline.py
# 목적: HybridRetriever → RAGRetriever → Reranker 삼단계 파이프라인을
#       더미 문서로 빠르게 검증하고, 최종 Top-k를 '리서치 카드' 형태로 출력합니다.

import logging
from rich.logging import RichHandler

# 여러분의 모듈 경로 그대로 사용
from rag.hybrid_retriever import HybridRetriever
from rag.rag_retriever import RAGRetriever
from rag.reranker import Reranker


from llm.generater_research_cards import generate_research_cards_markdown


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)

# -------------------------
# 더미 문서 코퍼스 (8개 샘플)
# -------------------------
DOCUMENTS = [
    {
        "title": "A Simple Baseline for Multimodal RAG",
        "url": "https://example.org/paper1",
        "abstract": "We present a baseline that fuses image and text evidence for retrieval-augmented generation (RAG) on QA benchmarks."
    },
    {
        "title": "Improving Text-only RAG with Reranking",
        "url": "https://example.org/paper2",
        "abstract": "We analyze retriever quality and propose a cross-encoder reranking pipeline to improve text-only RAG."
    },
    {
        "title": "Contrastive Vision-Language Pretraining for Open-VQA",
        "url": "https://example.org/paper3",
        "abstract": "A contrastive pretraining approach aligns vision and language for visual question answering tasks."
    },
    {
        "title": "Long-Context Memory for Dialogue Assistants",
        "url": "https://example.org/paper4",
        "abstract": "We introduce memory mechanisms for long-context assistants with efficient attention."
    },
    {
        "title": "Graph-Augmented Retrieval for Complex Reasoning",
        "url": "https://example.org/paper5",
        "abstract": "We add graph structure to retrieval to support multi-hop reasoning over entities."
    },
    {
        "title": "Audio-RAG: Integrating Speech Evidence into Generative QA",
        "url": "https://example.org/paper6",
        "abstract": "We incorporate ASR transcripts and acoustic cues to improve RAG for spoken question answering."
    },
    {
        "title": "Efficient Indexing for Large-Scale Corpora",
        "url": "https://example.org/paper7",
        "abstract": "We propose an indexing method that improves latency and memory footprint for million-scale corpora."
    },
    {
        "title": "Domain Adaptation for Biomedical QA",
        "url": "https://example.org/paper8",
        "abstract": "A method to adapt general QA models to biomedical corpora using weak supervision and retrieval calibration."
    },
]

QUERY = "RAG"

def pretty_print_cards(docs):
    md = generate_research_cards_markdown(
        docs=docs,
        query=QUERY,
        model_id="Qwen/Qwen3-1.7B",        # "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B-Instruct-2507"
        device="cpu",                       # GPU 있으면 "cuda"
        dtype="auto",
        style="standard",
        max_new_tokens=2048,
        load_in_4bit=False,                 # GPU면 True 권장
        load_in_8bit=False,
    )
    print("\n============================")
    print(" 최종 Top-k 리서치 카드 (Qwen3) ")
    print("============================\n")
    print(md)

def main():
    # 개별 모듈 로딩(선택적 검증)
    logging.info("Loading models for manual stage checks...")
    hybrid = HybridRetriever("all-MiniLM-L6-v2", use_cuda=False)
    dense = RAGRetriever("all-MiniLM-L6-v2", use_cuda=False)
    rerank = Reranker("ms-marco-MiniLM-L-6-v2", use_cuda=False)

    # 1단계: 하이브리드 검색 (상위 200개)
    logging.info("Stage1: HybridRetriever...")
    stage1_docs = (lambda query, docs: [
        docs[i] for i in hybrid.run(
            query,
            [d.get("title","") for d in docs],
            [d.get("abstract","") for d in docs],
            alpha=0.6, top_k=min(200, len(docs))
        )
    ])(QUERY, DOCUMENTS)

    # 2단계: 임베딩 기반 재정렬 (상위 50개)
    logging.info("Stage2: RAGRetriever...")
    refs = [f"{d.get('title','')}\n{d.get('abstract','')}" for d in stage1_docs]
    top_dense_idx = dense.run(QUERY, refs, top_k=min(50, len(stage1_docs)))
    stage2_docs = [stage1_docs[i] for i in top_dense_idx]

    # 3단계: 크로스엔코더 리랭킹 (최종 Top-k)
    logging.info("Stage3: Reranker...")
    refs2 = [f"{d.get('title','')}\n{d.get('abstract','')}" for d in stage2_docs]
    top_ce_idx = rerank.run(QUERY, refs2, top_k=min(2, len(stage2_docs)))
    final_docs_manual = [stage2_docs[i] for i in top_ce_idx]

    # 수동 단계 결과 출력
    pretty_print_cards(final_docs_manual)

if __name__ == "__main__":
    main()
