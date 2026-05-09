
from langchain_community.utilities import SearxSearchWrapper
from langchain.agents import create_agent
from datetime import date

# 1. Point LangChain directly at your LXC container's IP
searx = SearxSearchWrapper(searx_host="http://10.12.88.184:8080")

# 2. The new, bunker-grade search tool
def get_real_weather(city: str, date: str) -> str:
    """Use this tool to search the web for current weather in a given city."""
    print(f"\n[Bunker Log: Firing SearXNG engine for {city} on {date}...]\n")

    # .run() automatically queries your container and extracts the text snippets!
    return searx.run(f"weather in {city} on {date}")

# 3. Create the agent
agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[get_real_weather],
    system_prompt="""You are a helpful assistant.
    Always use your tools to answer questions about today's weather.""",
)

# 4. Execute
today = str(date.today())
content = f"What's the actual weather in Tokyo, {today}?"

result = agent.invoke(
    {"messages": [{"role": "user", "content": content}]}
)

print("\n--- Final Agent Response ---")
print(result["messages"][-1].content)
