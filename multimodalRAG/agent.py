import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from langchain_ollama import ChatOllama

# Best general model: strong chat, instruction following, and tool calling.
MODEL_QWEN3_8B = "qwen3:8b"
# Good general-purpose alternative for chat, planning, and explanations.
MODEL_LLAMA31_8B = "llama3.1:8b"
# Good conversational and writing model with balanced speed and quality.
MODEL_MISTRAL_7B = "mistral:7b"
# Fast lightweight general model for simple questions and low latency.
MODEL_QWEN25_3B = "qwen2.5:3b"
# Fast lightweight chat model for simple agents and everyday tasks.
MODEL_LLAMA32_3B = "llama3.2:3b"
# Best coding model in this collection: code generation, debugging, and APIs.
MODEL_QWEN25_CODER_7B = "qwen2.5-coder:7b"
# Best reasoning-focused model: math, logic, and multi-step analysis; slower.
MODEL_DEEPSEEK_R1_7B = "deepseek-r1:7b"
# Compact general model with good instruction following.
MODEL_GEMMA3_4B = "gemma3:4b"
# Small reasoning/instruction model; useful when conserving VRAM.
MODEL_PHI4_MINI = "phi4-mini:latest"
# Fastest chat/agent model here; lower quality on complex tasks.
MODEL_LLAMA32_1B = "llama3.2:1b"
# Small Qwen model for fast lightweight prompts and classification.
MODEL_QWEN25_15B = "qwen2.5:1.5b"
# Vision model for image and screenshot understanding; not text-only chat.
MODEL_LLAVA_7B = "llava:7b"
# Embedding model for RAG/vector search; do not use as a chat model.
MODEL_NOMIC_EMBED_TEXT = "nomic-embed-text:latest"

# Change this one value to switch the chat model used below.
MODEL_NAME = MODEL_QWEN25_15B
OLLAMA_URL = "http://127.0.0.1:11434" 
LANGSMITH_PROJECT = "debugging-monitor"


for env_path in (
    Path(__file__).with_name(".env"),
    Path.cwd() / ".env",
    Path.cwd().parent / ".env",
):
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def configure_langsmith():
    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return None

    os.environ.update(
        LANGSMITH_API_KEY=api_key,
        LANGSMITH_TRACING="true",
        LANGCHAIN_TRACING_V2="true",
        LANGSMITH_ENDPOINT="https://apac.api.smith.langchain.com",
        LANGCHAIN_ENDPOINT="https://apac.api.smith.langchain.com",
        LANGSMITH_PROJECT=LANGSMITH_PROJECT,
    )
    from langchain_core.tracers import LangChainTracer

    return LangChainTracer(project_name=LANGSMITH_PROJECT)


def make_tool_graph():
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        raise ValueError("TAVILY_API_KEY is missing from the local .env file.")

    tavily_client = TavilySearch(api_key=tavily_key, max_results=3)

    @tool
    def add(a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b

    @tool
    def tavily_search(query: str) -> str:
        """Search the web for current information using a direct query string."""
        result = tavily_client.invoke({"query": query})
        if isinstance(result, dict):
            return str(result.get("results", result))
        return str(result)

    tools = [add, tavily_search]
    model = ChatOllama(model=MODEL_NAME, base_url=OLLAMA_URL, temperature=0)
    model_with_tools = model.bind_tools(tools)

    def call_llm_model(state: State):
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(State)
    builder.add_node("call_llm_model", call_llm_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_llm_model")
    builder.add_conditional_edges(
        "call_llm_model",
        tools_condition,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "call_llm_model")
    graph=builder.compile()
    return graph


tool_agent = make_tool_graph()




