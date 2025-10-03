import streamlit as st
from streamlit_ace import st_ace
from pathlib import Path
import json, sys, uuid

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from services.llm_service import evaluate_code_with_llm

st.set_page_config(page_title="Interview Assist", layout="wide")

@st.cache_data
def load_questions():
    p = BASE_DIR / "data" / "questions.json"
    return json.loads(p.read_text())

questions = load_questions()
id2q = {q["id"]: q for q in questions}

# ---- HEADER ----
st.title("💼 Interview Assist — Mock Technical Interview")
st.markdown("Practice technical coding interviews with instant AI-powered feedback.")

# ---- Session ----
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

col1, col2 = st.columns([3, 2])

# ---------------- LEFT: QUESTION + EDITOR ----------------
with col1:
    q_choice = st.selectbox("📌 Select Question", options=[q["id"] for q in questions], format_func=lambda x: id2q[x]["title"])
    question = id2q[q_choice]

    with st.container():
        st.subheader(f"📝 {question['title']}")
        st.markdown(f"**Problem:** {question['description']}")
        st.code(question.get("function_signature",""), language="python")
        with st.expander("🔍 Example tests"):
            st.json(question.get("example_tests", []))

    st.markdown("### 💻 Write your solution")
    code = st_ace(
        value=f"{question['function_signature']}\n    # your code here\n",
        language="python",
        theme="monokai",
        keybinding="vscode",
        min_lines=15,
        key="code_editor"
    )

    if st.button("🚀 Evaluate with LLM", use_container_width=True):
        with st.spinner("Evaluating your code..."):
            result = evaluate_code_with_llm(code, question)
            st.session_state.last_result = result
            st.session_state.last_code = code

# ---------------- RIGHT: EVALUATION ----------------
with col2:
    st.subheader("📊 Evaluation Results")

    if "last_result" in st.session_state:
        r = st.session_state.last_result

        # Big score
        st.metric("Overall Score", f"{r.get('score',0)}/100")

        # Comments
        st.markdown("#### 💡 Feedback")
        st.success(r.get("comments","No comments."))

        # Breakdown
        st.markdown("#### 📈 Breakdown")
        breakdown = r.get("breakdown",{})
        c1, c2, c3 = st.columns(3)
        c1.metric("Correctness", breakdown.get("correctness",0))
        c2.metric("Style", breakdown.get("style",0))
        c3.metric("Efficiency", breakdown.get("efficiency",0))

        # Improvements
        if r.get("suggested_improvements"):
            st.markdown("#### 🔧 Suggested Improvements")
            for i in r["suggested_improvements"]:
                st.write(f"- {i}")

        # Bugs & edge cases
        if r.get("potential_bugs") or r.get("edge_cases"):
            st.markdown("#### ⚠️ Potential Bugs & Edge Cases")
            for e in (r.get("potential_bugs",[]) + r.get("edge_cases",[])):
                st.write(f"- {e}")

        # Follow-up
        if r.get("next_question"):
            st.markdown("#### 🎯 Follow-up Question")
            st.info(r["next_question"])

    else:
        st.info("✍️ Write your code and click **Evaluate with LLM** to see feedback.")