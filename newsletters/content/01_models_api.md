# 🧠 Newsletter #1: Claude Models & the Anthropic API
### Claude Certified Architect Exam Prep | Day 1 of 10

---

## Today's Exam Hook

> "A candidate is asked which Claude model to use for a task requiring nuanced reasoning with a 50-page document. They choose Haiku for speed. Will this pass the exam?"

**Almost certainly no.** The exam tests whether you can match model capabilities to task requirements. Speed ≠ right answer when context window and reasoning depth matter. By the end of this newsletter, you'll know exactly how to answer questions like this.

---

## The Model Landscape You Must Know

### Claude 3 Family (Current Generation)

| Model | Strength | Context Window | When to Use |
|-------|----------|----------------|-------------|
| **Opus** | Best reasoning, most capable | 200K tokens | Complex analysis, nuanced tasks, production where quality > cost |
| **Sonnet** | Balanced speed + intelligence | 200K tokens | Most production use cases — the "default" choice |
| **Haiku** | Fastest, cheapest | 200K tokens | High-volume, simple tasks, real-time applications |

**Exam gotcha:** All three models share the same 200K context window. Don't confuse model size with context size.

---

## The Messages API — Architecture You Must Understand

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system="You are a helpful assistant.",  # system prompt is SEPARATE
    messages=[
        {"role": "user", "content": "Explain token pricing."},
        {"role": "assistant", "content": "Token pricing works by..."},  # multi-turn
        {"role": "user", "content": "Give me an example."}
    ]
)

print(message.content[0].text)
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")
```

**Key architecture points:**
- `system` parameter is top-level, NOT inside `messages[]`
- `messages` must alternate user/assistant (no consecutive same roles)
- Response is `message.content[0].text` — it's a list because of multi-modal
- Always track `usage` for cost management in production

---

## Token Economics (Exam Loves This)

```
Cost = (input_tokens × input_price) + (output_tokens × output_price)
```

**Output tokens cost more than input tokens.** This is architecturally significant — it means:
- Caching input is valuable (prompt caching reduces input costs by ~90%)
- Verbose system prompts are cheap compared to verbose outputs
- Streaming doesn't change cost — it changes latency

**Exam scenario:** You have a 10K token system prompt used in every API call. What's the most impactful optimization? → Prompt caching with `cache_control: {"type": "ephemeral"}`.

---

## What the Exam Tests on Models

1. **Model selection logic:** Given a scenario (cost constraint, latency requirement, task complexity), choose the right model
2. **API structure:** Know the difference between `system`, `messages`, and `content`
3. **Token counting:** Understand what contributes to input vs output tokens
4. **Rate limits:** Know that rate limits are per-model, per-workspace
5. **Versioning:** Know that `claude-3-opus-20240229` is a pinned version; `claude-opus-4-5` may point to latest

---

## 🧪 Quiz: Test Yourself

**Q1:** A real-time customer chat application needs responses in under 2 seconds for simple FAQ queries. 10,000 requests per day. Which model?
<details><summary>Answer</summary>**Haiku** — speed and cost optimization for simple, high-volume tasks.</details>

**Q2:** Your system prompt is 8,000 tokens and stays constant across all requests. What API feature cuts your input costs by ~90%?
<details><summary>Answer</summary>**Prompt caching** — use `cache_control: {"type": "ephemeral"}` on the system prompt block.</details>

**Q3:** A `messages` array has two consecutive `user` role entries. What happens?
<details><summary>Answer</summary>**API error** — messages must strictly alternate between `user` and `assistant` roles.</details>

---

## Key Concept to Remember

**The model selection framework:** Start with Sonnet as default. Move to Haiku only when latency or cost is the primary constraint AND the task is simple. Move to Opus only when quality is non-negotiable and the task requires deep reasoning.

This framework will answer ~40% of model-selection exam questions correctly.

---

*Tomorrow: **Prompt Engineering** — system prompts, few-shot examples, chain-of-thought, and the XML structuring patterns the exam loves.*

*Progress: ██░░░░░░░░ 1/10 newsletters complete*
