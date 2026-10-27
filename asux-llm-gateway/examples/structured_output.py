import asyncio
import os
from pydantic import BaseModel
from asux_llm_gateway.clients.llm_client import LLMClient
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.messages import Message

os.environ["DEFAULT_PROVIDER"] = "mock"

class Recommendation(BaseModel):
    product_name: str
    reason: str
    price_estimate: float

async def main():
    client = LLMClient()
    request = GatewayRequest(messages=[Message.user("Recommend a laptop.")])
    
    # Normally this would call the mock provider which returns {"product_name": "Mock", ...}
    # For a real provider, this uses json_schema response_format.
    try:
        recommendation = await client.complete_structured(request, Recommendation)
        print("Got structured recommendation:")
        print(f"Product: {recommendation.product_name}")
        print(f"Reason: {recommendation.reason}")
    except Exception as e:
        print(f"Error (expected with basic mock provider): {e}")

if __name__ == "__main__":
    asyncio.run(main())
