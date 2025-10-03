import streamlit as st
from streamlit_ace import st_ace
from pathlib import Path
import json, sys, uuid
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from services.llm_service import evaluate_code_with_llm
from services.llm_service import chat_with_llm



st.set_page_config(page_title="Interview Assist", layout="wide")

# ---------------- LOAD QUESTIONS ----------------
@st.cache_data
def load_questions():
    p = BASE_DIR / "data" / "questions.json"
    return json.loads(p.read_text())

questions = load_questions()
id2q = {q["id"]: q for q in questions}

# ---------------- SESSION ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- RENDER QUESTION ----------------
def render_question_card(question):
    st.markdown(
        f"""
        <div style="background-color:#1e1e1e; padding:20px; border-radius:12px; border:1px solid #333; margin-bottom:15px;">
            <h3 style="color:#58a6ff; margin-top:0;">📝 {question['title']}</h3>
            <p style="font-size:16px; line-height:1.5; color:#ddd;">
                <b>Problem:</b> {question['description']}
            </p>
        </div>
        """, unsafe_allow_html=True
    )
    st.code(question.get("function_signature", ""), language="python")

    tests = question.get("example_tests", [])
    if tests:
        df = pd.DataFrame([{"Input": str(t["input"]), "Expected": str(t["expected"])} for t in tests])
        st.table(df)
    else:
        st.info("No example tests provided.")

# ---------------- FEEDBACK ----------------
def render_feedback_card(result):
    st.markdown("### 📊 Evaluation Results")
    st.metric("Overall Score", f"{result.get('score',0)}/100")
    st.success(result.get("comments","No comments."))
    breakdown = result.get("breakdown",{})
    c1, c2, c3 = st.columns(3)
    c1.metric("Correctness", breakdown.get("correctness",0))
    c2.metric("Style", breakdown.get("style",0))
    c3.metric("Efficiency", breakdown.get("efficiency",0))


# ---------------- LAYOUT: 3 PANELS ----------------
col1, col2, col3 = st.columns([2,3,2])  # left, middle, right

# LEFT → QUESTION
with col1:
    st.header("📌 Question")
    q_choice = st.selectbox("Select Question", options=[q["id"] for q in questions], format_func=lambda x: id2q[x]["title"])
    question = id2q[q_choice]
    render_question_card(question)

# MIDDLE → CODE + FEEDBACK
with col2:
    st.header("💻 Code Editor & Evaluation")
    starter = f"{question.get('function_signature','def solve(...):')}\n    # your code here\n"
    code = st_ace(value=starter, language="python", theme="monokai", keybinding="vscode", min_lines=20, key="code_editor")
    if st.button("🚀 Evaluate Code", use_container_width=True):
        with st.spinner("Evaluating your code with LLM..."):
            result = evaluate_code_with_llm(code, question)
            st.session_state.last_result = result
            st.session_state.last_code = code

            # --- Show Evaluation Results in the middle panel ---
            with col2:  # or wherever your evaluation card lives
                render_feedback_card(result)

            # --- Push Improvements into Chat (only if code partially works) ---
            correctness = result.get("breakdown", {}).get("correctness", 0)

            # ✅ Only suggest improvements if code runs at least partially
            if correctness > 0 and result.get("suggested_improvements"):
                improvements_text = "\n".join([f"- {i}" for i in result["suggested_improvements"]])
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": f"🔧 Suggested Improvements:\n{improvements_text}"
                })

            # ✅ Only ask follow-up if solution was at least partially correct
            if correctness > 0 and result.get("next_question"):
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": f"🎯 Follow-up Question: {result['next_question']}"
                })

            # --- Push improvements into chat ---
            if result.get("suggested_improvements"):
                improvements_text = "\n".join([f"- {i}" for i in result["suggested_improvements"]])
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": f"🔧 Suggested Improvements:\n{improvements_text}"
                })

            # --- Push follow-up into chat ---
            if result.get("next_question"):
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": f"🎯 Follow-up Question: {result['next_question']}"
                })

# ✅ Results panel always shows latest evaluation
with col2:
    st.subheader("📊 Evaluation Results")
    if "last_result" in st.session_state and st.session_state.last_result:
        render_feedback_card(st.session_state.last_result)

# RIGHT → CHAT
with col3:
    st.header("💬 Chat with AI Interviewer")

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"🧑 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **AI:** {msg['content']}")

    # Input box for user
    user_msg = st.text_input("Type your question here...", key="chat_input")

    if st.button("Send", use_container_width=True):
        if user_msg.strip():
            # Save user message
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

            # Build message history for LLM
            messages = [{"role": "system", "content": "You are a helpful technical interviewer. Be concise and clear."}]
            messages.extend(st.session_state.chat_history)

            # Get AI reply
            ai_reply = chat_with_llm(messages)

            # Save AI reply
            st.session_state.chat_history.append({"role": "ai", "content": ai_reply})

            st.rerun()