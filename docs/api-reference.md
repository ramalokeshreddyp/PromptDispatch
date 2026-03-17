# API Reference

## Endpoints

### `POST /api/chat`

Main endpoint. Classifies user intent, routes to the right expert, returns the response.

**Request Body**

```json
{
  "message": "How do I sort a list in Python?"
}
```

**Response**

```json
{
  "intent": "code",
  "confidence": 0.92,
  "response": "Here's how to sort a list in Python..."
}
```

| Field        | Type   | Description                                    |
|------------- |--------|------------------------------------------------|
| `intent`     | string | One of: `code`, `data`, `writing`, `career`, `unclear` |
| `confidence` | float  | 0.0 – 1.0 confidence score from the classifier |
| `response`   | string | Generated expert response                      |

---

### `GET /api/health`

Health check.

**Response**

```json
{ "status": "ok", "version": "1.0.0" }
```

---

### `GET /`

Serves the web UI (glassmorphism chat interface).

For GitHub Pages hosting, the repository root `index.html` provides a static frontend that calls the deployed backend `/api/chat` endpoint.

---

## Manual Override

Prefix your message with `@intent` to skip the classifier:

```
@code Fix this bug: for i in range(10) print(i)
@data What's the median of 5, 10, 15?
@writing This sentence feels awkward.
@career Should I switch jobs?
```

## Log Format

Each request is appended to `route_log.jsonl` as a single JSON line:

```json
{
  "timestamp": "2026-03-12T10:30:00.000000+00:00",
  "intent": "code",
  "confidence": 0.92,
  "user_message": "How do I sort a list in Python?",
  "final_response": "..."
}
```
