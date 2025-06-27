# main_promptpatterns.py
from pipeline_promptpatterns import build_pipeline
import os
from dotenv import load_dotenv
load_dotenv()

# Load your API key securely (from environment variable)
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Please set the GROQ_API_KEY environment variable.")

pipeline = build_pipeline(groq_api_key)

def generate_and_improve():
    task = input("\n📝 Enter your task description:\n> ").strip()

    patterns = ["None", "persona", "flipped", "n-shot", "directional", "template", "meta"]
    print("\n🎨 Available Prompt Design Patterns:")
    for idx, pattern in enumerate(patterns):
        print(f"  {idx}. {pattern}")
    choice = int(input("\nSelect pattern number (e.g., 0 for None): "))
    selected_pattern = patterns[choice]
    use_pattern = selected_pattern != "None"

    print(f"\n🚀 Generating prompt using pattern: {selected_pattern}...\n")
    result = pipeline.invoke({
        "mode": "generate",
        "task_description": task,
        "use_pattern": use_pattern,
        "selected_pattern": selected_pattern if use_pattern else None
    })

    print("✅ Prompt Generated!")
    print("\n🧾 Template Used:\n")
    print(result.get("base_template", "<None>"))

    print("\n🧠 Final Prompt:\n")
    print(result.get("prompt", "<None>"))

def improve_prompt():
    prompt = input("\nPaste your existing prompt:\n> ").strip()
    context = input("\nProvide improvement context:\n> ").strip()

    print("\n🔧 Improving prompt...")
    result = pipeline.invoke({
        "mode": "improve",
        "prompt": prompt,
        "context": context
    })

    print("\n✅ Improved Prompt:\n")
    print(result.get("improved_prompt", "<None>"))

def main():
    print("🧠 PromptCraft CLI")
    print("======================")
    print("1. Generate & Improve Prompt")
    print("2. Improve Existing Prompt")

    choice = input("\nChoose an option (1 or 2): ").strip()
    if choice == "1":
        generate_and_improve()
    elif choice == "2":
        improve_prompt()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
