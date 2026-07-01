# ⚙️ Newsletter #8: Claude API Best Practices
### Claude Certified Architect Exam Prep | Day 8 of 10

---

## Today's Exam Hook

> "A production system makes 1,000 Claude API calls per minute. During peak traffic, 15% of requests fail with status 529. The team adds retry logic — it makes things worse. Why?"

No backoff. Retrying immediately during overload amplifies the problem. The exam tests whether you know the production patterns that make Claude integrations resilient.

---

## Rate Limits — Know the Numbers

Rate limits operate on three axes:

| Limit Type | What It Counts |
|-----------|----------------|
| **RPM** | Requests per minute |
| **TPM** | Tokens per minute (input + output) |
| **TPD** | Tokens per day |

**Limits are per model, per workspace.** Haiku has higher TPM limits than Opus. Hitting Opus limits doesn't affect your Haiku budget.

---

## Error Handling — The Complete Pattern

```python
import anthropic
import time
import random

client = anthropic.Anthropic()

def call_with_retry(
    messages: list,
    model: str = "claude-sonnet-4-5",
    max_retries: int = 5
) -> anthropic.types.Message:
    
    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model=model,
                max_tokens=1024,
                messages=messages
            )
        
        except anthropic.RateLimitError as e:
            # 429 — too many requests
            wait = (2 ** attempt) + random.uniform(0, 1)  # Exponential + jitter
            print(f"Rate limited. Waiting {wait:.1f}s...")
            time.sleep(wait)
        
        except anthropic.APIStatusError as e:
            if e.status_code == 529:
                # Overloaded — same backoff
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
            elif e.status_code >= 500:
                # Server error — retry
                time.sleep(2 ** attempt)
            else:
                # 4xx client error — don't retry
                raise
        
        except anthropic.APIConnectionError:
            # Network error — retry with backoff
            time.sleep(2 ** attempt)
    
    raise Exception(f"Failed after {max_retries} attempts")
```

**The key insight:** Only retry on 429, 529, 5xx, and network errors. Never retry on 400 (bad request) or 401 (auth) — those need code fixes, not retries.

---

## Streaming — When and How

```python
# Streaming for real-time UX
with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a long essay..."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)  # Stream to UI
    
    # Get final message with usage stats
    final_message = stream.get_final_message()
    print(f"\nTokens: {final_message.usage}")
```

**When to stream:**
- Long responses (>500 tokens) — improves perceived performance
- Chat interfaces — users see typing effect
- Never for tool use — stream + tool use requires special handling

**When NOT to stream:**
- Batch processing — adds overhead
- Short responses — latency overhead exceeds benefit
- When you need the full response before processing

---

## Prompt Caching — Production Impact

```python
# Without caching: 50K token system prompt × 10K requests/day = 500M tokens
# With caching: 50K tokens first request + 5K × 9,999 = ~100M tokens
# Savings: ~80% on input costs

system_prompt_blocks = [
    {
        "type": "text",
        "text": large_knowledge_base,  # 50K tokens
        "cache_control": {"type": "ephemeral"}
    },
    {
        "type": "text", 
        "text": "Answer questions using the knowledge base above.",
        # No cache_control — short, no value in caching
    }
]
```

**Cache invalidation:** Ephemeral cache lasts 5 minutes. After 5 minutes of inactivity, the cache is cleared and the next request pays full input cost again.

---

## Token Counting Before You Send

```python
# Count tokens without making an inference call
token_count = client.messages.count_tokens(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": long_document}]
)

print(f"This will use {token_count.input_tokens} input tokens")

if token_count.input_tokens > 150_000:
    # Chunk or summarize before sending
    document = chunk_document(long_document)
```

---

## 🧪 Quiz

**Q1:** Your system gets 529 errors and you implement immediate retry (no delay). Traffic doubles. Why?
<details><summary>Answer</summary>Immediate retries during overload create a retry storm — every failed request immediately retries, doubling load on an already overloaded system. Exponential backoff with jitter is required.</details>

**Q2:** Should you retry a 400 Bad Request error?
<details><summary>Answer</summary>No — 400 means your request is malformed. Retrying won't fix it. Fix the code instead.</details>

**Q3:** Prompt cache lasts how long before requiring re-population?
<details><summary>Answer</summary>5 minutes of inactivity. Cache is ephemeral — if no requests use the cached content for 5 minutes, the next request pays full input token cost again.</details>

---

## Key Concept

**Production reliability requires: exponential backoff with jitter, only retrying retriable errors, streaming for long UX, and caching static content.** These aren't optimizations — they're baseline requirements for any system handling real traffic.

---

*Tomorrow: **Evaluation & Testing** — how to know your Claude integration actually works, and the evaluation frameworks the exam tests.*

*Progress: ████████████████░░░░ 8/10 complete*
