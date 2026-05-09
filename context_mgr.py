from langchain_ollama import OllamaLLM

CM_SYS_PROMPT = """You are an elite Network Diagnostic AI Copilot.
Your job is to help the user debug their Linux network step-by-step.

RULES:
1. Analyze the context and suggest ONE bash command to diagnose the issue.
2. You MUST wrap your command in a bash block like this:
```bash
<command>
```
3. NEVER suggest interactive or infinite commands (e.g., 
   use `ping -c 4` instead of `ping`, never use `top`, `vim`, or `nano`).
4. Keep your explanations extremely brief (1-2 sentences).
"""

class ContextManager:
    """Singleton-style State Holder for the HITL Loop"""
    _instance = None

    # THE LSP FIX: Declare the attributes so Pyright knows they exist
    history: list[str]
    system_prompt: str
    llm: OllamaLLM | None
    lalamo: OllamaLLM | None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextManager, cls).__new__(cls)
            cls._instance.history = []
            cls._instance.system_prompt = CM_SYS_PROMPT

            # python LLM model instance
            cls._instance.llm = OllamaLLM(
                    model="gemma3:4b", 
                    base_url="http://127.0.0.1:11434"
            )

            # llm is tongue twisting to pronounce, so there's lalamo :)
            cls._instance.lalamo = cls._instance.llm 
        return cls._instance

    def add_user_event(self, event_text: str):
        """Adds terminal output or human feedback to the context."""
        self.history.append(f"USER/SYSTEM: {event_text}")

    def add_ai_event(self, event_text: str):
        """Records what the AI previously decided."""
        self.history.append(f"AI: Suggested command -> {event_text}")

    def get_full_context(self) -> str:
        """Compiles the clean history for the LLM."""
        return "\n".join(self.history)
