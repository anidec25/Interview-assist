# 🤖 Interview Assist — Mock Technical Interview Platform

Interview Assist is an **AI-powered technical interview assistant** built with **Streamlit** and **OpenAI LLMs**.  
It helps users practice **mock coding interviews** by solving problems, writing code in the browser, and receiving **instant evaluation, structured feedback, and follow-up interview questions** — just like in a real interview.

---

## ✨ Features

- 📝 **Interactive Coding Questions**  
  - Questions are displayed in a LeetCode/HackerRank-style problem card.  
  - Includes problem description, function signature, and example test cases.  

- 💻 **Code Editor**  
  - Users can write and edit Python solutions directly in the browser using **Streamlit Ace Editor**.  

- 📊 **Automated Code Evaluation (LLM-based)**  
  - LLM evaluates code correctness, efficiency, and style without running user code in a sandbox.  
  - Provides **scores and structured feedback**.  

- 🔧 **Suggested Improvements**  
  - AI highlights improvements in coding style, efficiency, and edge-case handling.  

- 🎯 **Follow-up Questions**  
  - AI interviewer generates follow-up questions **only when the base solution is partially or fully correct**.  
  - No follow-ups are asked if the code has critical errors.  

- 💬 **Chat with AI Interviewer**  
  - Users can chat with the interviewer for hints, clarifications, or deeper discussions.  
  - Chat history is shown in a **WhatsApp-style bubble UI** (green for user, blue for AI).  
  - If the user is idle too long or explicitly asks for a "hint", AI provides a contextual hint.  

- ⚡ **Three-Panel Layout**  
  - **Left** → Question details  
  - **Middle** → Code editor + Evaluation results  
  - **Right** → Interactive chat with AI interviewer  

---

## 🛠️ Tech Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/)  
- **Code Editor**: [Streamlit Ace](https://github.com/okld/streamlit-ace)  
- **LLM Integration**: [OpenAI Python SDK](https://github.com/openai/openai-python) (`>=1.0`)  
- **Environment**: Conda + Python 3.10  
- **Utilities**: dotenv for API key management  

---

## 📂 Project Structure
Interview-Assist/
│── src/
│   ├── app/
│   │   ├── pages/
│   │   │   ├── interview_simulator.py   # Main Streamlit app (3-panel layout)
│   │   │   ├── resume_review.py         # (planned) Resume review module
│   │   │   ├── feedback_dashboard.py    # (planned) Feedback analytics dashboard
│   │   ├── main.py                      # Streamlit entrypoint
│   │   ├── config.py                    # Configs
│   │
│   ├── models/
│   │   ├── feedback_model.py
│   │   ├── interview_model.py
│   │   ├── resume_model.py
│   │
│   ├── services/
│   │   ├── llm_service.py               # OpenAI API integration
│   │
│   ├── utils/
│   │   ├── ai_utils.py
│   │   ├── helpers.py
│
│── requirements.txt
│── README.md
│── .env   # Store API key


---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/interview-assist.git
cd interview-assist
```


### 2. Create and activate conda environment
```bash
conda create -n interview-assist python=3.10 -y
conda activate interview-assist
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
