
from langchain_core.tools import tool
import host_context # importing your script

# Cat One is network manager, help with tools to debug connections
# it also know how to gether terminal history and prepare all context for LLM

@tool
def get_machine_state() -> str:
    """Gets current machine context including IP address, OS version, and user info."""
    # This calls the function you just perfected!
    context_list = host_context.get_machine_info()
    return "\n".join(context_list)


