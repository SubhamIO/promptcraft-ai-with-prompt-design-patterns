# pipeline.py
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import logging
logging.basicConfig(level=logging.INFO)


# Define the state structure
class UnifiedState(TypedDict, total=False):
    mode: Literal["generate", "improve"]
    task_description: str
    context: Optional[str]
    base_template: Optional[str]
    prompt: Optional[str]
    feedback: Optional[str]
    score: Optional[float]
    issue_found: Optional[bool]
    improved_prompt: Optional[str]
    use_pattern: Optional[bool]
    selected_pattern: Optional[str]

# Prompt pattern logic
def apply_prompt_pattern(task: str, pattern: Optional[str]) -> str:
    if not pattern:
        return f"Given the following task, create a useful prompt: {task}"

    normalized = pattern.strip().lower()

    patterns = {
        "persona": f'''
                    You are a prompt engineering specialist. Your goal is to create a **persona-style prompt** for the given task.

                    The **Persona Prompting Pattern** involves assigning the LLM a **specific role, identity, or point of view** (e.g., “act as a historian,” “respond like a 5-year-old,” or “you are a medical expert”).

                    Instructions:

                        1. Clearly define the **persona or role** the LLM should assume.
                        2. Define the **task** that persona is to complete.
                        3. Ensure the role aligns with the expected style, domain expertise, or tone of the output.
                        4. Keep the prompt clear and instruct the LLM to remain in-character.

                    Use the following task to generate a persona-style prompt:  
                    {task}

                    Return only the final persona-style prompt.


                    ''',
        "flipped": f'''
                    To use the Flipped Interaction Pattern, your prompt should
                    incorporate these fundamental contextual cues:
                        1. I would like you to ask me questions to achieve task {task}
                        2. You should ask questions (optionally about 1, 2, 3,...) until you have enough information about the topic
                        or you have enough information to do task {task} 
                        3. Ask these questions one by one
                    Let’s start with the first question
                    ''',
        "n-shot": f'''
                    Generate a new prompt using the **n-shot prompting pattern**.

                    The goal is to teach the model a behavior through a few input-output examples (shots), 
                    and then leave the final input for the model to complete.

                    Here's how to structure it:

                        1. Start with a brief instruction to the LLM about the task.
                        2. Include **3 example input-output pairs**.
                        3. Add a **4th input only**, prompting the LLM to generate the corresponding output.

                    The task for which you should build the prompt is: {task}
                    Make the prompt clear, concise, and optimized for best results.
                    Respond with only the final prompt.

                    ''',
        "directional": f'''
                    Your task is to generate a prompt that uses the **directional stimulus prompting pattern**.

                    This pattern gives **explicit instructions** on the type of 
                    response desired from the LLM (e.g., style, tone, length, structure, or reasoning approach).

                    Here’s how to structure the final prompt:

                        1. **Define the task clearly.**
                        2. **Provide explicit instructions** to guide the LLM's behavior — such as:
                        - "Respond concisely using bullet points"
                        - "Explain as if teaching a beginner"
                        - "Use analogies from sports"
                        - "Answer in formal tone with no subjective opinions"
                        3. Ensure the prompt avoids ambiguity and focuses the LLM's attention on **how** to respond, not just **what** to respond to.

                    The task for which you should create this directional prompt is:  
                    {task}

                    Respond with only the final directional prompt.

                    ''',
        "template": f'''
                    Your goal is to generate a **template-style prompt** for the given task.

                    The **Template Prompting Pattern** provides a reusable format or structure that can be filled in with specific inputs.

                    Follow these steps:
                        1. Identify the key components needed for the task (e.g., goal, input, output format).
                        2. Create a **prompt template** that includes placeholders like `input`, `goal`, or `style`.
                        3. Clearly describe how the placeholders will be used by the LLM when filled in.
                        4. Optionally, include an example with filled-in values to demonstrate the prompt in action.

                    Use the following task to generate a prompt template:
                    {task}

                    Return only the final template-style prompt.


                    ''',
        "meta": f'''

                    You are a professional prompt engineer. Your task is to create a **meta-language-style prompt** for the given task.

                    The **Meta Language Prompting Pattern** involves telling the LLM *how to think* or *how to approach solving* a task — not just *what* to do. 
                    
                    This uses instructions like:

                        - “Think step-by-step before answering”
                        - “Break the problem into sub-parts”
                        - “Reflect on assumptions before responding”

                    Instructions:

                        1. Define the task clearly.
                        2. Add explicit meta-cognitive instructions about how the LLM should **approach the problem**.
                        3. Guide the LLM’s internal reasoning or mental process.
                        4. The final prompt should encourage **structured thinking** and **self-correction**.

                    The task for which you should write this meta-style prompt is:  
                    {task}

                    Respond with only the final meta-style prompt.

                    '''
            }

    pattern_template = patterns.get(normalized)
    if not pattern_template:
        return f"Given the following task, create a useful prompt: {task}"

    return pattern_template



# Pipeline builder
def build_pipeline(groq_api_key: str):
    groq_llm = ChatGroq(groq_api_key=groq_api_key, model="llama-3.1-8b-instant", temperature=0)

    def dispatcher_node(state: UnifiedState) -> dict:
        return {}

    def dispatcher_router(state: UnifiedState) -> str:
        return "PromptImproverDirect" if state.get("mode") == "improve" else "ContextBuilder"

    def context_builder(state: UnifiedState) -> dict:
        return {"context": f"You are a helpful assistant. Task: {state['task_description']}"}

    def template_selector(state: UnifiedState) -> dict:
        task = state["task_description"]
        pattern = state.get("selected_pattern")
        base_template = apply_prompt_pattern(task, pattern)
        # print(">>> Template selector activated. Pattern:", pattern)
        # print(">>> Generated base_template:", base_template)
        
        # Fix: carry forward base_template in state
        state["base_template"] = base_template
        return state



    def prompt_generator(state: UnifiedState) -> dict:
        input_text = state["base_template"]
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert prompt engineer."),
            ("human", input_text)
        ])
        response = (prompt | groq_llm).invoke({})
        return {"prompt": response.content}


    def prompt_evaluator(state: UnifiedState) -> dict:
        eval_input = f"Evaluate this prompt: '{state['prompt']}'. Return only a float score between 0.0 and 1.0"
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Respond with only a float."),
            ("human", eval_input)
        ])
        response = (prompt | groq_llm).invoke({})
        try:
            score = float(''.join(c for c in response.content if c.isdigit() or c == '.'))
        except:
            score = 0.5
        return {"score": score, "issue_found": score < 0.7}

    def critique_node(state: UnifiedState) -> dict:
        critique_prompt = f"Critique and suggest improvements: {state['prompt']}"
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Be a constructive prompt critic."),
            ("human", critique_prompt)
        ])
        response = (prompt | groq_llm).invoke({})
        return {"feedback": response.content}

    def loop_improver(state: UnifiedState) -> dict:
        improve_input = f"Feedback: {state['feedback']}\nPrompt: {state['prompt']}"
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Improve this prompt based on feedback."),
            ("human", improve_input)
        ])
        response = (prompt | groq_llm).invoke({})
        return {"prompt": response.content}

    def prompt_improver_direct(state: UnifiedState) -> dict:
        improve_input = f"Prompt: {state['prompt']}\nContext: {state['context']}"
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Improve this prompt with the given context."),
            ("human", improve_input)
        ])
        response = (prompt | groq_llm).invoke({})
        return {"improved_prompt": response.content}

    workflow = StateGraph(UnifiedState)
    workflow.add_node("Dispatcher", dispatcher_node)
    workflow.add_node("ContextBuilder", context_builder)
    workflow.add_node("PromptTemplateSelector", template_selector)
    workflow.add_node("PromptGenerator", prompt_generator)
    workflow.add_node("PromptEvaluator", prompt_evaluator)
    workflow.add_node("CritiqueNode", critique_node)
    workflow.add_node("LoopImproverAgent", loop_improver)
    workflow.add_node("PromptImproverDirect", prompt_improver_direct)

    workflow.set_entry_point("Dispatcher")

    workflow.add_conditional_edges("Dispatcher", dispatcher_router, {
        "PromptImproverDirect": "PromptImproverDirect",
        "ContextBuilder": "ContextBuilder"
    })

    workflow.add_edge("ContextBuilder", "PromptTemplateSelector")
    workflow.add_edge("PromptTemplateSelector", "PromptGenerator")
    workflow.add_edge("PromptGenerator", "PromptEvaluator")

    def eval_router(state: UnifiedState) -> str:
        return "critique_and_improve" if state.get("issue_found") else END

    workflow.add_conditional_edges("PromptEvaluator", eval_router, {
        "critique_and_improve": "CritiqueNode",
        END: END
    })

    workflow.add_edge("CritiqueNode", "LoopImproverAgent")
    workflow.add_edge("LoopImproverAgent", "PromptEvaluator")
    workflow.add_edge("PromptImproverDirect", END)

    return workflow.compile()



