# promptcraft-ai-with-prompt-design-patterns
Streamlit web application for generating and improving AI prompts using various prompt design patterns.

Here's a complete **`README.md`** file for your project — written from the perspective of a **professional content writer** and **Generative AI developer**.

---

## 🧠 PromptCraft AI — Intelligent Prompt Generator & Improver - powerd by Prompt Design Patterns

> A multi-node LangGraph-based agent pipeline that **generates, evaluates, critiques**, and **improves LLM prompts** dynamically using Groq's blazing-fast **LLaMA 3.1 8B** model.
> Built for developers, researchers, and prompt engineers who demand **high-quality prompts**.

---
---

## 🚀 Features

- 🎯 **Prompt Generation** from task descriptions
- 🔧 **Prompt Improvement** with context
- 🎨 Choose from different **Prompt Design Patterns**:
  - Persona Pattern
  - Flipped Interaction
  - N-Shot Prompting
  - Directional Stimulus
  - Template Pattern
  - Meta Language Pattern
- 📜 View the **base template** used behind the scenes
- 🔐 Uses `.env` file for secure API key management

---

### 📸 Project Architecture

```mermaid
flowchart TD
    A[Dispatcher Node] -->|mode == generate| B[ContextBuilder]
    A -->|mode == improve| I[PromptImproverDirect]

    B --> C[PromptTemplateSelector]
    C --> D[PromptGenerator]
    D --> E[PromptEvaluator]

    E -->|score < 0.7| F[CritiqueNode]
    E -->|score >= 0.7| Z[END]

    F --> G[LoopImproverAgent]
    G --> E

    I --> Z[END]
```

---

## ✨ Features

* 🔁 **Graph-based modular pipeline** using LangGraph
* 🚀 Powered by **Groq's LLaMA 3.1 8B-Instant** (ultra-low latency)
* 🧠 Supports both:

  * `generate`: full prompt generation with iterative refinement
  * `improve`: direct enhancement of existing prompts using context
* ✅ Automatic prompt **evaluation, scoring, and feedback loop**
* 🛠️ Easily extensible (e.g., add scoring history, memory, fine-tuned prompt templates)

---

## 📌 Node Descriptions

- **Dispatcher**  
  Entry point of the LangGraph. It routes the input based on the selected `mode`:  
  - `"generate"` → goes through the full prompt creation and evaluation loop  
  - `"improve"` → directly improves the given prompt using context

- **ContextBuilder**  
  Adds default context to the task description to provide grounding for prompt generation.

- **PromptTemplateSelector**  
  Applies the selected **prompt design pattern** (e.g., persona, flipped, n-shot) to create a base template prompt.

- **PromptGenerator**  
  Takes the generated base template and invokes the LLM to produce a first draft of the prompt.

- **PromptEvaluator**  
  Evaluates the quality of the generated prompt using a scoring mechanism (0.0 to 1.0).  
  If the score is below 0.7, the graph continues into critique mode.

- **CritiqueNode**  
  Provides critical feedback on the prompt and suggests how it could be improved.

- **LoopImproverAgent**  
  Uses the feedback from `CritiqueNode` to refine the prompt. The new prompt is re-evaluated in a loop until it meets quality standards.

- **PromptImproverDirect**  
  Used only in `"improve"` mode. Enhances the user's existing prompt based on additional context without scoring or iteration.


## 📦 Tech Stack

| Tool                 | Role                           |
| -------------------- | ------------------------------ |
| **LangGraph**        | Multi-node graph orchestration |
| **LangChain**        | Prompt templates, chaining     |
| **Groq + LLaMA 3.1** | Lightning-fast inference       |
| **Python**           | Core logic & orchestration     |
| **Dotenv**           | Secure API key management      |

---

## 🧑‍💻 How It Works

### 🔹 1. Prompt Generation Mode (`mode: generate`)

* Builds context based on task
* Creates a base template based on the prompt design pattern selected
* Generates prompt using LLM
* Evaluates and scores prompt quality
* If score < 0.7, it:

  * Critiques the prompt
  * Refines it using feedback
  * Re-evaluates until threshold met

### 🔹 2. Prompt Improvement Mode (`mode: improve`)

* Accepts user-defined prompt + improvement context
* Directly sends to an LLM for enhancement

---

## 🛠 Installation

1. **Clone the Repo**

```bash
git clone https://github.com/SubhamIO/promptcraft-ai-with-prompt-design-patterns.git
cd promptcraft-ai-with-prompt-design-patterns
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Add Environment Variables**

Create a `.env` file with your Groq API key:

```
GROQ_API_KEY=your-groq-api-key-here
```

---

## 🚀 Usage

Run the script:

```bash
app_promptpatterns_pythonapp.py or streamlit run app_promptpatterns.py
```

Expected output:

```bash
Running: Full Prompt Generation and Iterative Improvement
--- Evaluator: Score = 0.55, Issue Found = True ---
--- Critique Generated ---
--- Prompt Improved in Loop ---
--- Final Generated Prompt ---
"Explain the theory of relativity to a 10-year-old using a story about two children playing catch on a moving train..."

...

Running: Direct Prompt Improvement with Context
--- Final Improved Prompt ---
"Explain relativity using a train and ball analogy that a child can understand."
```

---

## 📂 Directory Structure

```
📦 promptcraft-ai/
 ┣ 📄 app_promptpatterns.py
 ┣ 📄 pipeline_promptpatterns.py
 ┣ 📄 README.md
 ┣ 📄 requirements.txt
 ┣ 📄 .streamlit/secrets.toml
```

---

---

## 🌱 Future Enhancements

* 🧠 Add memory-aware prompt history using `LangChain Memory`
* 📊 Dashboard for prompt score tracking
* 🔗 API endpoints to use in other apps
* 🧪 Custom fine-tuning of evaluation thresholds

---

## 🙌 Contributing

Feel free to fork, suggest improvements, or raise issues.
This project is designed to be a plug-and-play module for **any LLM-powered workflow.**

---

## 📄 License

MIT License © 2025 \[Subham Sarkar]


