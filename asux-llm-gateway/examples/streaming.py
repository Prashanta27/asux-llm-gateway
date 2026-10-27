import asyncio
import os
from asux_llm_gateway.clients.llm_client import LLMClient
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.messages import Message

os.environ["DEFAULT_PROVIDER"] = "mock"

async def main():
    client = LLMClient()
    request = GatewayRequest(messages=[Message.user("Write a poem.")])
    
    print("Streaming response:")
    async for chunk in client.stream(request):
        print(chunk.content_delta, end="", flush=True)
    print("\n[Stream Complete]")

if __name__ == "__main__":
    asyncio.run(main())
