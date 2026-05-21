import os
from enum import Enum
from typing import Optional

class ModelStatus(Enum):
    OFFLINE = "local"
    ONLINE = "cloud"

class ModelManager:
    def __init__(self, preferred_mode: ModelStatus = ModelStatus.OFFLINE):
        self.mode = preferred_mode
        self.local_model = "gemma3:4b"
        self.cloud_model = "gemini-2.5-flash"
        
    def check_connectivity(self) -> ModelStatus:
        """Ping a reliable endpoint to detect GFW-status or internet health."""
        # Simple heuristic: if we can reach google, we are online. 
        # In the future, this can be more advanced (e.g., checking proxy tunnels).
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            return ModelStatus.ONLINE
        except OSError:
            return ModelStatus.OFFLINE

    def get_model(self):
        """Routing logic based on current system state."""
        current_status = self.check_connectivity()
        if current_status == ModelStatus.ONLINE:
            return self.cloud_model
        return self.local_model

    def execute_prompt(self, system_prompt: str, user_prompt: str, stream=True):
        """Transparent wrapper to handle the backend switch."""
        target = self.get_model()
        print(f"🧠 Routing to [{target}] based on status...")
        
        if target == self.cloud_model:
            # Call your Google GenAI implementation
            return self._call_gemini(system_prompt, user_prompt)
        else:
            # Call your local Ollama implementation
            return self._call_ollama(system_prompt, user_prompt)
