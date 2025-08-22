# llm/prompt_builder.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import json, re

def _clip(s: str, n: int) -> str:
    if s is None: return ""
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s[:n] + "…" if len(s) > n else s

def _coerce_doc(d: Dict[str,Any], tmax=180, amax=1200) -> Dict[str,Any]:
    return {
        "title": _clip(d.get("title",""), tmax),
        "url": d.get("url",""),
        "abstract": _clip(d.get("abstract",""), amax),
        "venue": _clip(d.get("venue",""), 80),
        "year": d.get("year",""),
        "authors": d.get("authors", [])[:10],
        "keywords": d.get("keywords", [])[:8],
        "scores": d.get("scores", {}),      # {"hybrid":..,"dense":..,"ce":..}
        "evidence": d.get("evidence", {}),  # {"numbers":[...], "code":"...", "pdf":"..."}
    }

@dataclass
class PromptBuilder:
    style: str = "standard"  # "concise"|"standard"|"detailed"

    @property
    def system_ko(self) -> str:
        return (
            "당신은 정확한 연구 요약가입니다. 출력은 GitHub‑Flavored Markdown으로 작성합니다. "
            "사적 추론(<think> ... </think>)은 절대 출력하지 마세요. "
            "최종 답변은 <final> ... </final> 로 감싸서 출력하라"
            "오직 최종결과만 한국어로 작성합니다. "
            "숫자/성능치는 입력 JSON의 evidence.numbers에 있는 값만 사용하고, 없으면 '원문에 수치 미기재'라고 명시합니다. "
            "링크는 입력 url만 사용하고, '~입니다' 톤으로 간결하게 작성합니다."
        )

    def _docs_json(self, docs: List[Dict[str,Any]]) -> str:
        safe = [_coerce_doc(d) for d in docs]
        return json.dumps({"papers": safe}, ensure_ascii=False, indent=2)

    def research_cards(self, user_instruction: str, docs: List[Dict[str,Any]], show_scores: bool=True) -> Dict[str,str]:
        length = {
            "concise": "TL;DR 20–30자, 카드당 불릿 4–6개.",
            "standard": "TL;DR 30–50자, 카드당 불릿 6–9개.",
            "detailed": "TL;DR 50–80자, 카드당 불릿 8–12개."
        }[self.style]
        score_hint = "- (선택) scores.hybrid/dense/ce 중 2개까지 '(CE=0.91, Dense=0.83)' 형태로 표기합니다.\n" if show_scores else ""
        user = f"""아래 JSON의 user_instruction과 papers를 바탕으로,
각 논문을 '리서치 카드' 형식으로 요약하고, 맨 마지막에 Top‑k 비교표 1개를 추가하세요.

요구사항:
- 카드 필수 항목:
  1) 제목(연도, venue, 링크) 2) TL;DR 3) 왜 관련? (2–3개) 4) 핵심 기여(3–4불릿)
  5) 한계/주의(1–2불릿) 6) 난이도(초/중/고), 예상 읽기 시간(분) 7) 해시태그 3–5개
{score_hint}- 숫자/성능치는 evidence.numbers만 사용하고 없으면 '원문에 수치 미기재'라고 씁니다.
- 문장은 간결하게, 불릿 위주. {length}
- 마지막 비교표(테이블) 열:
  | 순위 | 제목 | 방법(한줄) | 데이터/스케일 | 핵심성능(있으면) | 관련성(0–5) | 난이도 | 링크 |

입력 JSON:
```
json{{
  "user_instruction": "{_clip(user_instruction, 400)}",
  "papers": []
}}
papers 데이터:

{self._docs_json(docs)}
"""
        
        return {"system": self.system_ko, "user": user}
