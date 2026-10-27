import asyncio
import os
from asux_llm_gateway.clients.llm_client import LLMClient
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.messages import Message

# Mock setup for example purposes
os.environ["DEFAULT_PROVIDER"] = "mock"

async def main():
    client = LLMClient()
    request = GatewayRequest(
        messages=[Message.user("Hello from AsuX LLM Gateway!")]
    )
    
    response = await client.complete(request)
    print("Response:", response.content)
    print("Tokens:", response.usage.total_tokens if response.usage else "Unknown")
    print("Cost:", response.estimated_cost)

if __name__ == "__main__":
    asyncio.run(main())
