from asux_llm_gateway.clients.llm_client import LLMClient


# Dependency to provide the client to routes
def get_llm_client() -> LLMClient:
    return LLMClient()
