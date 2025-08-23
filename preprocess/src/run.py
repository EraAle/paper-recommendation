from preprocess.prompt.prompts import KEYWORD_EXTRACTION_PROMPT, \
    UNCERTAIN_KEYWORDS_DETECTION_PROMPT, INSTRUCTION_REFINE_PROMPT
import torch
import re

from preprocess.src.model import get_model_and_tokenizer

model = None
tokenizer = None

def parse_keywords(response: str):
    for line in response.splitlines():
        if "keywords" in line.lower():
            match = re.search(r"\[(.*?)\]", line)
            if match:
                return [kw.strip().strip('"').strip("'") for kw in match.group(1).split(",") if kw.strip()]

def parse_uncertain(response):
    uncertain = []
    for line in response.splitlines():
        if "abbreviations" in line.lower():
            match = re.search(r"\[(.*?)\]", line)
            if match:
                uncertain = [kw.strip().strip('"').strip("'") for kw in match.group(1).split(",") if kw.strip()]
            break
    return uncertain

def parse_query(response):
    match = re.search(r"<(.*?)>", response)
    if match:
        return match.group(1).strip()
    return ""

def extract_keywords(query: str, max_new_tokens: int = 128):
    global model, tokenizer

    prompt = KEYWORD_EXTRACTION_PROMPT.format(USER_INPUT=query)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.split("Output:")[-1]

    keywords = parse_keywords(response)

    return keywords

def detect_uncertainty(keywords: list[str], max_new_tokens: int = 128):
    global model, tokenizer

    prompt = UNCERTAIN_KEYWORDS_DETECTION_PROMPT.format(USER_INPUT=keywords)

    # LLM inference
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.split("Output:")[-1]
    uncertain = parse_uncertain(response)

    return uncertain


def refine_query(query: str, max_new_tokens: int = 128):
    global model, tokenizer

    prompt = INSTRUCTION_REFINE_PROMPT.format(USER_INPUT=query)

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.split("Output:")[-1]
    refined_query = parse_query(response)

    return refined_query

def setup(model_name: str="Qwen2.5-7B-Instruct", prefer_8bit=False):
    global model, tokenizer
    model, tokenizer = get_model_and_tokenizer(model_name, prefer_8bit=prefer_8bit)

def run(query: str):
    global model, tokenizer

    main_keywords = extract_keywords(query)
    return {
        "main": main_keywords,
        "optional": [],
    }

if __name__ == '__main__':
    setup()
    for _ in range(10):
        query = input("query: ")
        print(run(query))
