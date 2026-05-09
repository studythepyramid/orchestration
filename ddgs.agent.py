
# pip install duckduckgo-search
#from duckduckgo_search import DDGS
from ddgs import DDGS
from langchain.agents import create_agent

from datetime import date

# 1. We write a REAL tool that touches the internet
def get_real_weather(city: str, date: str) -> str:
    """Use this tool to search the web for current weather in a given city."""
    print(f"\n[Bunker Log: Searching the web for {city} weather...]\n")



    print("--- Testing Network Connection ---")
    try:
        with DDGS() as ddgs:
            # Asking for just 1 result to test the pipe
            results = ddgs.text(f"weather in {city} on {date}", max_results=1)

        if results:
            print("SUCCESS! The wall is breached. Data received:")
            print(results[0]['body'])
            return results[0]['body']
        else:
            return """FAILED: 
                  Connection went through, 
                  but DuckDuckGo returned nothing 
                  (Possible rate-limit or proxy block)."""



    except Exception as e:
        print(f"FAILED: Network crashed. Error: {e}")
        return f"FAILED: Network crashed. Error: {e}"


# 2. We hand our real tool to the agent
agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[get_real_weather],
    system_prompt="""You are a helpful assistant. 
    Always use your tools to answer questions about today's weather.""",
)

today = str(date.today())
content = f"What's the actual weather in Tokyo,  {today}?"

# 3. Trigger the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": content}]}
)

print("\n--- Final Agent Response ---")
print(result["messages"][-1].content)
