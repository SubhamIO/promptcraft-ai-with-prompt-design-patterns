import streamlit as st
import os
from dotenv import load_dotenv
from pipeline_promptpatterns import build_pipeline

# Load API Key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("Please set the GROQ_API_KEY in your .env file.")
    st.stop()

# Build the LangGraph pipeline
pipeline = build_pipeline(groq_api_key)

# Page config
st.set_page_config(page_title="🧠 PromptCraft Chat", layout="centered")
st.title("🧠 PromptCraft Chat")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mode" not in st.session_state:
    st.session_state.mode = "Generate Prompt"
if "pattern" not in st.session_state:
    st.session_state.pattern = "None"
if "context" not in st.session_state:
    st.session_state.context = ""

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.mode = st.radio("Choose Mode", ["Generate Prompt", "Improve Prompt"])
    if st.session_state.mode == "Generate Prompt":
        st.session_state.pattern = st.selectbox("Prompt Pattern", ["None", "persona", "flipped", "n-shot", "directional", "template", "meta"])
    if st.session_state.mode == "Improve Prompt":
        st.session_state.context = st.text_area("Provide context for improvement", key="context_input")

# Chat input
user_input = st.chat_input("Enter your task or prompt...")

if user_input:
    # Store user message
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    # Handle mode logic
    if st.session_state.mode == "Generate Prompt":
        use_pattern = st.session_state.pattern != "None"
        response = pipeline.invoke({
            "mode": "generate",
            "task_description": user_input,
            "use_pattern": use_pattern,
            "selected_pattern": st.session_state.pattern if use_pattern else None
        })

        base_template = response.get("base_template", "<None>")
        final_prompt = response.get("prompt", "<None>")

        ai_reply = f"""
### 🎯 Prompt Generated (Pattern: `{st.session_state.pattern}`)

**🧾 Template Used:**
```text
{base_template}
```

**🧠 Final Prompt:**
```text
{final_prompt}
```
"""
    else:  # Improve Prompt
        response = pipeline.invoke({
            "mode": "improve",
            "prompt": user_input,
            "context": st.session_state.context
        })

        improved = response.get("improved_prompt", "<None>")

        ai_reply = f"""
### 🔧 Improved Prompt
```text
{improved}
```
"""

    # Store AI response
    st.session_state.chat_history.append({"role": "assistant", "text": ai_reply})

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message("User" if message["role"] == "user" else "PromptCraft AI"):
        st.markdown(message["text"], unsafe_allow_html=True)
