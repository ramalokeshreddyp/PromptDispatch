"""
Core Prompt Router — classify_intent & route_and_respond

Two-step LLM pipeline:
  1. classify_intent  → lightweight classification call
  2. route_and_respond → expert-persona generation call
"""

import json
import os
import re
from typing import Any

from openai import AsyncOpenAI, OpenAIError

from app.prompts import CLASSIFIER_PROMPT, CLARIFICATION_PROMPT, EXPERT_PROMPTS
from app.logger import log_route

# ---------------------------------------------------------------------------
# OpenAI client  (reads OPENAI_API_KEY from env automatically)
# ---------------------------------------------------------------------------
def _build_client() -> AsyncOpenAI | None:
    """Create an OpenAI client, returning None when API key is unavailable."""
    try:
        return AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except OpenAIError:
        return None


client = _build_client()

CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", "gpt-4o-mini")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "gpt-4o-mini")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

VALID_INTENTS = set(EXPERT_PROMPTS.keys()) | {"unclear"}
UNCLEAR_QUESTION = (
    "Are you asking for help with coding, data analysis, writing feedback, "
    "or career advice?"
)
GREETING_RESPONSE = (
    "Hi. I can help with coding, data analysis, writing feedback, or career advice. "
    "Tell me what you need, or start with @code, @data, @writing, or @career."
)

# Regex to detect manual override prefix like @code, @data, etc.
OVERRIDE_PATTERN = re.compile(
    r"^@(" + "|".join(re.escape(k) for k in EXPERT_PROMPTS) + r")\b\s*",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_classification(raw: str) -> dict[str, Any]:
    """
    Try to extract a JSON object from the LLM response.
    Falls back to {"intent": "unclear", "confidence": 0.0} on any failure.
    """
    default = {"intent": "unclear", "confidence": 0.0}
    try:
        # Strip markdown fences if the model wraps its answer
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        data = json.loads(cleaned)

        intent = str(data.get("intent", "unclear")).lower().strip()
        confidence = float(data.get("confidence", 0.0))

        if intent not in VALID_INTENTS:
            intent = "unclear"
            confidence = 0.0

        return {"intent": intent, "confidence": round(confidence, 4)}
    except (json.JSONDecodeError, TypeError, ValueError, KeyError, AttributeError):
        return default


def _is_greeting(message: str) -> bool:
    normalized = re.sub(r"[^a-z]+", "", message.lower())
    return normalized in {
        "hi",
        "hello",
        "hey",
        "heya",
        "hiya",
        "yo",
        "sup",
        "goodmorning",
        "goodafternoon",
        "goodevening",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def classify_intent(message: str) -> dict[str, Any]:
    """
    Call the LLM to classify a user message into one of the known intents.
    Returns {"intent": str, "confidence": float}.
    """
    if client is None:
        return {"intent": "unclear", "confidence": 0.0}

    try:
        response = await client.chat.completions.create(
            model=CLASSIFIER_MODEL,
            temperature=0.0,
            max_tokens=60,
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user", "content": message},
            ],
        )
        raw = response.choices[0].message.content or ""
        result = _parse_classification(raw)

        # Apply confidence threshold
        if result["intent"] != "unclear" and result["confidence"] < CONFIDENCE_THRESHOLD:
            result["intent"] = "unclear"

        return result

    except Exception:
        # Network / auth / rate-limit errors → safe fallback
        return {"intent": "unclear", "confidence": 0.0}


async def route_and_respond(message: str, intent: dict[str, Any]) -> str:
    """
    Select the expert prompt based on intent and generate the final response.
    Logs every decision to route_log.jsonl.
    """
    label = intent["intent"]
    confidence = intent["confidence"]

    if label == "unclear":
        final_text = GREETING_RESPONSE if _is_greeting(message) else UNCLEAR_QUESTION

        # Log every routing decision, including clarification fallbacks.
        log_route(
            intent=label,
            confidence=confidence,
            user_message=message,
            final_response=final_text,
        )
        return final_text

    system_prompt = EXPERT_PROMPTS.get(label, CLARIFICATION_PROMPT)

    if client is None:
        final_text = "Sorry, the AI service is not configured. Please set OPENAI_API_KEY and try again."
        log_route(
            intent=label,
            confidence=confidence,
            user_message=message,
            final_response=final_text,
        )
        return final_text

    try:
        response = await client.chat.completions.create(
            model=GENERATOR_MODEL,
            temperature=0.7,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
        )
        final_text = response.choices[0].message.content or ""
    except Exception as exc:
        final_text = f"Sorry, something went wrong while generating a response: {exc}"

    # Log every routing decision
    log_route(
        intent=label,
        confidence=confidence,
        user_message=message,
        final_response=final_text,
    )

    return final_text


async def handle_message(raw_message: str) -> dict[str, Any]:
    """
    End-to-end handler: detect override → classify → route → respond.
    Returns a dict with intent, confidence, and response.
    """
    message = raw_message.strip()

    # --- Manual override: @code, @data, @writing, @career ----------------
    override_match = OVERRIDE_PATTERN.match(message)
    if override_match:
        forced_intent = override_match.group(1).lower()
        message = message[override_match.end():].strip() or message
        intent_result = {"intent": forced_intent, "confidence": 1.0}
    else:
        intent_result = await classify_intent(message)

    response_text = await route_and_respond(message, intent_result)

    return {
        "intent": intent_result["intent"],
        "confidence": intent_result["confidence"],
        "response": response_text,
    }
