import asyncio
import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

MODEL_NAME1 = "qwen3:8b"
MODEL_NAME2 = "mistral:7b"
MODEL_NAME3 = "llama3.1:8b"
OLLAMA_URL = "http://127.0.0.1:11434"

load_dotenv()

print(f"Connected to Ollama. Using local model: {MODEL_NAME3}")


async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": [os.path.join(base_dir, "mathserver.py")],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable-http",
            },
        }
    )

    tools = await client.get_tools()

    model = ChatOllama(
        model=MODEL_NAME3,
        base_url=OLLAMA_URL,
        temperature=0,
    )

    agent = create_react_agent(model, tools)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What is the year around weather in Paris and what is 12 + 5?"}]}
    )
    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
