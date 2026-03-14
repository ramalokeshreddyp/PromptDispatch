# Questionnaire Answers

## 1) Explain the design choices behind one of your expert personas. Why did you choose its specific tone, constraints, and output style?

For the Code Expert persona, I intentionally used a direct, non-conversational tone because coding requests benefit from precision and low ambiguity. In my prompt configuration, this persona is constrained to produce production-quality code, include robust error handling, and follow idiomatic language patterns. I also constrained the output style to code blocks with brief technical explanations, which keeps responses actionable and easier to validate in testing.

I added a constraint to prefer well-known libraries over custom reinventions to improve reliability and reduce brittle code. The overall design goal was consistency: if users route to code intent, they should reliably get implementation-first answers rather than generic discussion.

## 2) Describe your process for developing the classifier prompt. What were some alternative phrasings you considered, and why did you choose the final version?

My classifier prompt was designed around output contract reliability first, then intent accuracy. Early prompt variants were more open-ended (for example, asking the model to explain its choice), but those often returned extra prose, markdown fences, or commentary that made parsing less reliable.

The final prompt explicitly does four things:

1. Restricts labels to a closed set: code, data, writing, career, unclear.
2. Requires a single JSON object.
3. Requires fixed keys: intent and confidence.
4. Forbids extra text.

This aligns with my parser logic, which expects structured JSON and gracefully falls back to {"intent": "unclear", "confidence": 0.0} on invalid output. I also run the classifier at temperature 0.0 to reduce variance and keep routing deterministic.

## 3) How does your system handle ambiguous user messages that could match multiple intents? Discuss the trade-offs of your approach.

Ambiguity is handled with two mechanisms in combination:

1. The classifier can return an explicit unclear label.
2. A confidence threshold is applied (default 0.7). If confidence is below threshold, the system forces unclear.

When intent is unclear, my router does not guess. It returns a deterministic clarifying question: "Are you asking for help with coding, data analysis, writing feedback, or career advice?" This behavior is intentional and tested.

The trade-off is precision versus friction. This approach reduces confident misrouting (better precision), but it may ask for clarification more often (more user turns). I chose this trade-off because incorrect expert routing usually harms answer quality more than one extra clarification step.

## 4) This task involves two LLM calls. Discuss your strategy for model selection for the classifier versus the response generator in a production environment.

In the submitted implementation, model choice is configurable via environment variables:

- CLASSIFIER_MODEL (default gpt-4o-mini)
- GENERATOR_MODEL (default gpt-4o-mini)

I used the same default for simplicity and predictable behavior during evaluation, but the architecture is intentionally split so production can optimize each stage independently.

Production strategy:

1. Classifier: use a smaller, faster, lower-cost model because output is short and schema-constrained.
2. Generator: use a stronger model for higher response quality, especially for complex coding/data/writing/career prompts.

This two-model strategy improves cost-performance balance: cheap routing at scale, premium generation only when needed.

## 5) Beyond malformed JSON, what are other potential failure modes for this prompt routing system, and how would you make it more resilient?

Beyond malformed JSON, key failure modes include:

1. Upstream API failures (timeouts, rate limits, transient 5xx).
2. Missing or invalid API credentials.
3. Persistent misclassification for certain phrasing patterns.
4. Prompt-injection-style user content that tries to override system behavior.
5. Distribution drift over time (new user intents not represented in current labels).

Current protections in my code already include:

- Safe fallback when classifier output cannot be parsed.
- Confidence-threshold fallback to unclear.
- Safe handling when API key is not configured.
- Per-request JSONL logging for observability.

For higher resilience in production, I would add:

1. Retries with exponential backoff and timeout budgets.
2. Circuit breaker and fallback responses during provider outages.
3. Intent quality monitoring (confusion matrix from labeled samples).
4. Prompt/version tracking and A/B testing.
5. Input guardrails and stricter system-policy enforcement.
6. Optional semantic pre-router for known high-risk ambiguous classes.
