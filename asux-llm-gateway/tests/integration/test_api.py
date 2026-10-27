import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_create_completion(client: AsyncClient):
    payload = {"model": "mock-model", "messages": [{"role": "user", "content": "Hello"}]}
    response = await client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["model"] == "mock-model"
    assert data["provider"] == "mock"
    assert data["message"]["content"] == "Mock response"
    assert "usage" in data
    assert data["usage"]["total_tokens"] == 30


@pytest.mark.asyncio
async def test_create_completion_stream(client: AsyncClient):
    payload = {
        "model": "mock-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
    }

    chunks = []
    async with client.stream("POST", "/v1/chat/completions/stream", json=payload) as response:
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: ") and line != "data: [DONE]":
                chunks.append(line[6:])

    assert len(chunks) == 4
    import json

    first_chunk = json.loads(chunks[0])
    assert first_chunk["content_delta"] == "Mock "

    last_chunk = json.loads(chunks[-1])
    assert last_chunk["finish_reason"] == "stop"
    assert last_chunk["usage"]["total_tokens"] == 30
