# Architecture

The AsuX LLM Gateway provides a unified interface for all AI agents to communicate with LLM providers.

## Core Flow

```mermaid
flowchart TD
    Agent[AI Agent] -->|Uses| Client[LLMClient]
    Client -->|HTTP/Direct| Gateway[Gateway Service]
    Gateway --> Router[Model Router]
    Router --> Provider[Provider Abstraction]
    Provider --> OpenAI[OpenAI API]
    Provider --> Local[Local Models]
```

## Future Project Integration

Future AsuX projects (e.g., Prompt Engine, Agent Runtime) must NEVER depend directly on the OpenAI SDK. Instead, they will depend on the `LLMClient` provided by this project.

- **Project 1**: LLM Gateway V1 (This project)
- **Project 2**: Prompt Engine (Builds on this Gateway)
