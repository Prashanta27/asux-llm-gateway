# HTTP API Reference

The Gateway exposes a FastAPI service.

## `GET /health`
Basic health check. Returns `{"status": "ok"}`.

## `GET /ready`
Readiness check. Ensures providers are configured. Returns `{"status": "ready"}`.

## `POST /v1/chat/completions`
Standard completion endpoint.

**Request:**
```json
{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "Hello"}],
  "temperature": 0.7
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "model": "gpt-4o",
  "provider": "openai",
  "message": {"role": "assistant", "content": "Hi!"},
  "usage": {"total_tokens": 10},
  "estimated_cost": 0.0001
}
```

## `POST /v1/chat/completions/stream`
Streaming completions via Server-Sent Events (SSE).
