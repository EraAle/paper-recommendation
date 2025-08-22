# llm/glue.py
from __future__ import annotations
from typing import List, Dict, Any
from .base_model import BaseLocalLLM, LocalLLMConfig
from .prompt_builder import PromptBuilder

def generate_research_cards_markdown(
    docs: List[Dict[str,Any]],
    query: str,
    model_id: str = "Qwen/Qwen3-0.6B",
    device: str = "cpu",
    dtype: str = "auto",
    style: str = "standard",
    max_new_tokens: int = 2048,
    load_in_4bit: bool = False,
    load_in_8bit: bool = False,
) -> str:
    cfg = LocalLLMConfig(
        model_id=model_id, device=device, dtype=dtype,
        max_new_tokens=max_new_tokens,
        temperature=0.2, top_p=0.9, do_sample=True,
        load_in_4bit=load_in_4bit, load_in_8bit=load_in_8bit,
    )
    llm = BaseLocalLLM(cfg)
    prompts = PromptBuilder(style=style).research_cards(
        user_instruction=query, docs=docs, show_scores=True
    )
    return llm.generate(system=prompts["system"], user=prompts["user"])
