# src/services/llm_service.py

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from utils.prompts import EVAL_SYSTEM, EVAL_USER_TEMPLATE

# ---------------- CONFIG ----------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ---------------- HELPERS ----------------
def _extract_json(text: str):
    """
    Attempt to extract valid JSON from a model response.
    Falls back to substring search if extra text is included.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
    raise ValueError("Failed to parse JSON from model output")

# ---------------- MAIN FUNCTIONS ----------------
def evaluate_code_with_llm(code: str, question: dict, model: str = DEFAULT_MODEL):
    """
    Evaluates candidate code using LLM.
    Returns structured feedback (score, breakdown, comments, follow-up).
    """
    try:
        # Build user message
        user_prompt = EVAL_USER_TEMPLATE.format(
            problem=question.get("description", ""),
            signature=question.get("function_signature", ""),
            tests_serialized=json.dumps(question.get("example_tests", []), indent=2),
            code=code,
        )

        messages = [
            {"role": "system", "content": EVAL_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
        )

        reply = resp.choices[0].message.content

        # Try to parse JSON
        try:
            return _extract_json(reply)
        except Exception:
            return {
                "score": 0,
                "comments": f"LLM reply (not JSON): {reply}",
                "breakdown": {"correctness": 0, "style": 0, "efficiency": 0},
                "suggested_improvements": [],
                "potential_bugs": [],
                "edge_cases": [],
                "next_question": "",
            }

    except Exception as e:
        return {
            "score": 0,
            "comments": f"LLM error: {str(e)}",
            "breakdown": {"correctness": 0, "style": 0, "efficiency": 0},
            "suggested_improvements": [],
            "potential_bugs": [],
            "edge_cases": [],
            "next_question": "",
        }

def chat_with_llm(chat_history, model: str = DEFAULT_MODEL):
    """
    Interactive chat with the AI interviewer.
    chat_history should be a list of messages in format:
        [{"role":"system","content":"..."}, {"role":"user","content":"..."}]
    Returns AI reply string.
    """
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=chat_history,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"(LLM error: {str(e)})"