
import os
import json
from typing import TypedDict, List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY missing. Please add it to your .env file."
    )


# ==========================================
# 2. INITIALIZE GEMINI MODEL
# ==========================================

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=API_KEY,
    timeout=120,
    max_retries=1
)

# ==========================================
# 3. DEFINE LANGGRAPH STATE
# ==========================================

class TaskState(TypedDict):
    user_input: str
    tasks: List[Dict[str, Any]]
    organized_tasks: List[Dict[str, Any]]
    result: str


# ==========================================
# HELPER: PARSE GEMINI JSON RESPONSE
# ==========================================

def parse_json_response(response):
    content = response.content

    if isinstance(content, list):
        content = "".join(
            item.get("text", "") if isinstance(item, dict)
            else str(item)
            for item in content
        )

    content = str(content).strip()
    content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)


# ==========================================
# NODE 1: TASK EXTRACTION
# ==========================================

def extract_tasks(state: TaskState):
    prompt = f"""
    You are an AI task extraction assistant.

    Extract all individual tasks from the user's message.

    Return ONLY a valid JSON array.
    Each task must contain:
    - task: a short task description
    - deadline: deadline mentioned by the user, or "Not specified"

    Do not invent tasks or deadlines.
    Preserve the original meaning.

    User message:
    {state["user_input"]}
    """

    response = llm.invoke(prompt)
    tasks = parse_json_response(response)

    if not isinstance(tasks, list):
        raise ValueError("Task extraction did not return a JSON array.")

    return {"tasks": tasks}


# ==========================================
# NODE 2: TASK PRIORITIZATION
# ==========================================

def prioritize_tasks(state: TaskState):
    prompt = f"""
    You are an AI task prioritization assistant.

    Assign a priority to every task.

    Allowed priorities:
    - High
    - Medium
    - Low

    Guidelines:
    - High: urgent or very near deadlines.
    - Medium: important but less urgent tasks.
    - Low: tasks with low urgency.

    Consider the user's stated deadlines and urgency.
    Do not invent extra tasks or deadlines.

    Return ONLY a valid JSON array.
    Each object must contain:
    - task
    - deadline
    - priority

    Tasks:
    {json.dumps(state["tasks"], ensure_ascii=False)}
    """

    response = llm.invoke(prompt)
    organized_tasks = parse_json_response(response)

    if not isinstance(organized_tasks, list):
        raise ValueError("Prioritization did not return a JSON array.")

    # Validate priorities
    for task in organized_tasks:
        priority = str(task.get("priority", "Medium")).title()

        if priority not in {"High", "Medium", "Low"}:
            priority = "Medium"

        task["priority"] = priority
        task.setdefault("task", "Untitled task")
        task.setdefault("deadline", "Not specified")

    return {"organized_tasks": organized_tasks}


# ==========================================
# NODE 3: FORMAT RESULTS
# ==========================================

def format_results(state: TaskState):
    tasks = state["organized_tasks"]

    if not tasks:
        result = "No tasks were found in your message."
    else:
        lines = [
            "YOUR ORGANIZED TO-DO LIST",
            "=" * 30
        ]

        for number, task in enumerate(tasks, start=1):
            lines.append(f"\n{number}. {task['task']}")
            lines.append(f"   Deadline: {task['deadline']}")
            lines.append(f"   Priority: {task['priority']}")

        result = "\n".join(lines)

    return {"result": result}


# ==========================================
# 4. BUILD LANGGRAPH WORKFLOW
# ==========================================

workflow = StateGraph(TaskState)

workflow.add_node("task_extraction", extract_tasks)
workflow.add_node("task_prioritization", prioritize_tasks)
workflow.add_node("format_results", format_results)

workflow.add_edge(START, "task_extraction")
workflow.add_edge("task_extraction", "task_prioritization")
workflow.add_edge("task_prioritization", "format_results")
workflow.add_edge("format_results", END)

task_graph = workflow.compile()


# ==========================================
# 5. CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="AI Task Organizer",
    description=(
        "An AI assistant that extracts tasks, "
        "assigns priorities, and formats a to-do list "
        "using Gemini and LangGraph."
    ),
    version="1.0.0"
)


# ==========================================
# 6. DEFINE REQUEST MODEL
# ==========================================

class TaskRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10000,
        description="Describe your tasks in natural language."
    )


# ==========================================
# 7. HOME ENDPOINT
# ==========================================

@app.get("/")
def home():
    return {
        "message": "AI Task Organizer is running!",
        "model": MODEL_NAME,
        "docs": "/docs"
    }


# ==========================================
# 8. ORGANIZE TASKS ENDPOINT
# ==========================================

@app.post("/organize")
def organize_tasks(request: TaskRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a task description."
        )

    try:
        result = task_graph.invoke({
            "user_input": request.message.strip(),
            "tasks": [],
            "organized_tasks": [],
            "result": ""
        })

        return {
            "success": True,
            "tasks": result["organized_tasks"],
            "formatted_list": result["result"]
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned invalid JSON. Please try again."
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Task organization failed: {str(error)}"
        )
