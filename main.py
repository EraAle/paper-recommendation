from rag.run import setup as setup_rag
from preprocess.src.run import setup as setup_preprocess, get_model

from rag.run import run as run_rag
from preprocess.src.run import run as run_preprocess

from crawler import *

from llm.generater_research_cards import generate_research_cards_markdown


def print_guidelines():
    print()
    print("=== Real-time Web-based Research Paper Search Tool ===")
    print("This tool allows you to input a query sentence and retrieve relevant research papers in real time.")
    print()
    print("Query Sentence Guidelines:")
    print("- Write short and concise sentence-style queries.")
    print("- Do not use abbreviations; always write terms in full form.")
    print()
    print("Examples:")
    print("- Bad: find me a paper about survey on MAS")
    print("- Good: survey on multi-agent system")

def pretty_print_cards(docs, qu, model, tokenizer):
    for doc in docs:
        md = generate_research_cards_markdown(
            docs=[doc],
            query=qu,
            model_id="Qwen/Qwen3-1.7B",        # "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B-Instruct-2507"
            device="cpu",                       # GPU 있으면 "cuda"
            dtype="auto",
            style="standard",
            max_new_tokens=2048,
            load_in_4bit=False,                 # GPU면 True 권장
            load_in_8bit=False,
            model=model,
            tokenizer=tokenizer,
        )
        print("\n============================")
        print(" 최종 Top-k 리서치 카드 (Qwen3) ")
        print("============================\n")
        print(md)

def setups():
    setup_rag()
    setup_preprocess()

def main():
    setups()

    # print guidelines
    print_guidelines()

    # receive user query input
    query = input("Input a query sentence for paper search: ")
    # receive top_k
    top_k = int(input("Input the number of top-k papers: "))

    # extract keywords
    keywords = run_preprocess(query)
    print(keywords)

    # --- search

    queryss = soft_parsing_openreview(keywords, field="all")
    print(queryss)
    documents = main_crawling(keywords, field="all", num=50, sort_op="relevance", date=None, accept = False, openreview = True)
    document_print(documents)

    # filter documents
    filtered_documents = run_rag(query, documents, top_k=top_k)

    # --- pretty print
    model, tokenizer = get_model()
    pretty_print_cards(filtered_documents, query, model, tokenizer)


if __name__ == '__main__':
    main()