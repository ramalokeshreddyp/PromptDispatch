# Architecture Overview

How the Prompt Router works under the hood.

## High-Level Flow

```mermaid
flowchart TD
    A([User Message]) --> B{Manual Override?<br/>e.g. @code ...}
    B -->|Yes| D[Skip Classifier]
    B -->|No| C[Classifier LLM Call<br/>gpt-4o-mini · temp 0]
    C --> E{Parse JSON}
    E -->|Valid| F{Confidence ≥ 0.7?}
    E -->|Malformed| G[Default: unclear / 0.0]
    F -->|Yes| H[Use detected intent]
    F -->|No| G
    D --> H
    G --> I
    H --> I{Select Expert Prompt}
    I -->|code| J[🧑‍💻 Code Expert]
    I -->|data| K[📊 Data Analyst]
    I -->|writing| L[✍️ Writing Coach]
    I -->|career| M[💼 Career Advisor]
    I -->|unclear| N[🤔 Clarification]
    J --> O[Generator LLM Call<br/>gpt-4o-mini · temp 0.7]
    K --> O
    L --> O
    M --> O
    N --> O
    O --> P[Final Response]
    P --> Q[(Log to route_log.jsonl)]
    Q --> R([Return to User])
```

## Component Diagram

```mermaid
graph LR
    subgraph Client
        UI[Web UI<br/>Glassmorphism SPA]
    end

    subgraph Server[FastAPI Server]
        API[/api/chat]
        RT[router.py<br/>classify_intent<br/>route_and_respond]
        PM[prompts.py<br/>Expert Prompts]
        LG[logger.py<br/>JSONL Logger]
    end

    subgraph External
        OAI[OpenAI API]
    end

    UI -->|POST /api/chat| API
    API --> RT
    RT --> PM
    RT -->|2 LLM calls| OAI
    RT --> LG
    LG -->|append| LOG[(route_log.jsonl)]
    API -->|JSON| UI
```

## Request Sequence

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Web UI
    participant API as FastAPI
    participant CL as classify_intent
    participant RR as route_and_respond
    participant LLM as OpenAI API
    participant LOG as route_log.jsonl

    U->>UI: Type message
    UI->>API: POST /api/chat {message}
    API->>CL: classify_intent(message)
    CL->>LLM: Chat completion (classifier prompt)
    LLM-->>CL: {"intent":"code","confidence":0.92}
    CL-->>API: intent dict
    API->>RR: route_and_respond(message, intent)
    RR->>LLM: Chat completion (expert prompt)
    LLM-->>RR: Generated expert response
    RR->>LOG: Append log entry
    RR-->>API: final response text
    API-->>UI: {intent, confidence, response}
    UI-->>U: Render with intent badge
```
