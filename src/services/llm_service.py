# src/services/llm_service.py
import os
import json
from dotenv import load_dotenv
load_dotenv()

# robust JSON extractor helper
def _extract_json(text: str):
    text = text.strip()
    # try direct load
    try:
        return json.loads(text)
    except Exception:
        # find first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
    raise ValueError("Failed to parse JSON from model output")

# attempt to import openai (optional)
_openai_available = False
try:
    import openai
    _openai_available = True
    openai.api_key = os.getenv("OPENAI_API_KEY")
except Exception:
    _openai_available = False

from utils.prompts import EVAL_SYSTEM, EVAL_USER_TEMPLATE

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")  # Fixed model name from "gpt-4o"

def evaluate_code_with_llm(code: str, question: dict, temperature=0.0, max_tokens=800, model=DEFAULT_MODEL):
    """
    Send prompt to LLM to evaluate code. Returns parsed JSON evaluation.
    If OpenAI key is not present, returns a deterministic mock evaluation.
    """
    tests_serialized = json.dumps(question.get("example_tests", []), indent=2)
    user_content = EVAL_USER_TEMPLATE.format(
        problem=question["description"],
        signature=question.get("function_signature", ""),
        tests_serialized=tests_serialized,
        code=code
    )

    if not _openai_available or not openai.api_key:
        # Mock evaluator (simple heuristics)
        passed_count = 0
        total = max(1, len(question.get("example_tests", [])))
        # naive heuristic: if builtin 'sum' used for sum_array, pass
        qid = question.get("id", "")
        if qid == "sum_array" and "sum(" in code:
            passed_count = total
        # basic mock scoring
        score = int(100 * passed_count / total)
        return {
            "score": max(score, 10),
            "breakdown": {"correctness": score, "style": 50, "efficiency": 50},
            "comments": f"Mock evaluator: {passed_count}/{total} example tests seem satisfied heuristically.",
            "suggested_improvements": ["Add input validation", "Consider built-in functions for brevity"],
            "potential_bugs": ["May fail for non-integer inputs"],
            "edge_cases": ["Empty list", "Large numbers"],
            "next_question": "How would you adapt your solution to streaming input?",
            "confidence": 0.35
        }

    # Real OpenAI call
    messages = [
        {"role":"system", "content": EVAL_SYSTEM},
        {"role":"user", "content": user_content}
    ]
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        text = resp["choices"][0]["message"]["content"]
        parsed = _extract_json(text)
        # ensure numeric types & fallbacks
        parsed.setdefault("score", int(parsed.get("score", 0)))
        parsed.setdefault("breakdown", parsed.get("breakdown", {}))
        parsed.setdefault("confidence", float(parsed.get("confidence", 0.0)))
        return parsed
    except Exception as e:
        return {
            "score": 0,
            "breakdown": {"correctness": 0, "style": 0, "efficiency": 0},
            "comments": f"LLM error: {str(e)}",
            "suggested_improvements": [],
            "potential_bugs": [],
            "edge_cases": [],
            "next_question": "",
            "confidence": 0.0
        }