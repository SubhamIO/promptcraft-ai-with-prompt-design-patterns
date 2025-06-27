# streamlit_app.py

import streamlit as st
import os
from pipeline_promptpatterns import build_pipeline

# Load environment variables
# groq_api_key = os.getenv("GROQ_API_KEY")
groq_api_key = st.secrets['GROQ_API_KEY']

if not groq_api_key:
    st.error("Please set the GROQ_API_KEY environment variable.")
    st.stop()

pipeline = build_pipeline(groq_api_key)

st.title("🧠 PromptCraft AI - The Prompt Wizard")
st.subheader("LLM Prompt Generator & Improver using LangGraph + Groq and Prompt Design Patterns")
st.sidebar.header("Choose Task")
mode = st.sidebar.selectbox("Select Mode", ["Generate & Improve Prompt", "Improve Existing Prompt"])

if mode == "Generate & Improve Prompt":
    st.header("📝 Generate Prompt from Task Description")

    task = st.text_area("Enter your task description:")

    patterns = ["None", "persona", "flipped", "n-shot", "directional", "template", "meta"]
    selected_pattern = st.selectbox("Select a prompt design pattern", patterns)

    if st.button("🚀 Generate Prompt"):
        if not task.strip():
            st.warning("Please enter a task description.")
        else:
            use_pattern = selected_pattern != "None"
            result = pipeline.invoke({
                "mode": "generate",
                "task_description": task,
                "use_pattern": use_pattern,
                "selected_pattern": selected_pattern if use_pattern else None
            })

            st.success("✅ Prompt Generated!")
            st.subheader("🧾 Template Used:")
            st.code(result.get("base_template", "<None>"), language="text")

            st.subheader("🧠 Final Prompt:")
            st.code(result.get("prompt", "<None>"), language="text")

elif mode == "Improve Existing Prompt":
    st.header("🔧 Improve Your Prompt")

    prompt = st.text_area("Paste your existing prompt:")
    context = st.text_area("Provide improvement context:")

    if st.button("✨ Improve Prompt"):
        if not prompt.strip() or not context.strip():
            st.warning("Please fill in both prompt and context.")
        else:
            result = pipeline.invoke({
                "mode": "improve",
                "prompt": prompt,
                "context": context
            })

            st.success("✅ Improved Prompt:")
            st.code(result.get("improved_prompt", "<None>"), language="text")
