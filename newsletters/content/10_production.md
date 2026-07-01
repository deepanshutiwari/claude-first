# 🚀 Newsletter #10: Production Deployment
### Claude Certified Architect Exam Prep | Day 10 of 10 — FINAL EDITION

---

## Today's Exam Hook

> "A Claude-powered application goes viral overnight. Costs spike 40x, latency triples, and some users see error messages. The team has no runbook. What three architectural decisions made this survivable vs catastrophic?"

Rate limit buffers, cost monitoring with alerts, and graceful degradation. The exam loves production readiness scenarios. This final newsletter ties everything together.

---

## The Production Architecture Checklist

```
✅ Rate limit management
✅ Cost monitoring & budgets  
✅ Error handling & retry logic
✅ Graceful degradation
✅ Prompt versioning
✅ Observability & logging
✅ Security & input validation
✅ Evaluation in CI/CD
```

---

## Cost Management

```python
class CostTracker:
    PRICES = {
        "claude-opus-4-5":   {"input": 15.00, "output": 75.00},  # per 1M tokens
        "claude-sonnet-4-5": {"input": 3.00,  "output": 15.00},
        "claude-haiku-4-5-20251001": {"input": 0.25, "output": 1.25}
    }
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = self.PRICES[model]
        return (
            (input_tokens / 1_000_000) * prices["input"] +
            (output_tokens / 1_000_000) * prices["output"]
        )
    
    def log_request(self, model: str, usage: dict, user_id: str):
        cost = self.calculate_cost(model, usage.input_tokens, usage.output_tokens)
        # Log to your metrics system
        metrics.increment("claude.cost", cost, tags={"model": model, "user": user_id})
        metrics.increment("claude.tokens.input", usage.input_tokens)
        metrics.increment("claude.tokens.output", usage.output_tokens)
```

**Cost optimization hierarchy:**
1. Use the cheapest model that meets quality bar
2. Cache static content (prompt caching)
3. Limit max_tokens appropriately
4. Batch similar requests where possible
5. Monitor per-user costs to catch abuse

---

## Graceful Degradation

```python
def get_claude_response(prompt: str, fallback: str = None) -> str:
    try:
        response = call_with_retry(prompt)
        return response.content[0].text
    
    except anthropic.RateLimitError:
        # Option 1: Queue for later
        task_queue.enqueue(prompt)
        return "Your request is queued. We'll notify you when complete."
    
    except anthropic.APIStatusError as e:
        if e.status_code == 529:  # Overloaded
            # Option 2: Use cached/static response
            if fallback:
                return fallback
            # Option 3: Downgrade to simpler model
            return call_with_retry(prompt, model="claude-haiku-4-5-20251001")
    
    except Exception:
        # Option 4: Fail gracefully
        return "Service temporarily unavailable. Please try again in a moment."
```

---

## Observability Pattern

```python
import time
import logging

def instrumented_claude_call(prompt: str, model: str) -> dict:
    start = time.time()
    
    try:
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )
        
        latency = time.time() - start
        
        logging.info("claude_call", extra={
            "model": model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "latency_ms": latency * 1000,
            "stop_reason": response.stop_reason,
            "cache_hit": hasattr(response.usage, 'cache_read_input_tokens')
        })
        
        return {"success": True, "response": response, "latency": latency}
    
    except Exception as e:
        logging.error("claude_error", extra={"error": str(e), "model": model})
        raise
```

---

## Prompt Versioning

```python
# prompts/v1/system_prompt.txt → original
# prompts/v2/system_prompt.txt → improved
# prompts/v3/system_prompt.txt → current

PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v3")

def load_prompt(name: str) -> str:
    path = f"prompts/{PROMPT_VERSION}/{name}.txt"
    return open(path).read()

# A/B test new prompts
def get_prompt_variant(user_id: str) -> str:
    if hash(user_id) % 10 < 2:  # 20% get new prompt
        return load_prompt("v4_experimental")
    return load_prompt("system_prompt")
```

---

## The Exam's Production Scenario Patterns

**"System goes down during peak traffic"**
→ Answer always involves: rate limit buffers + graceful degradation + queuing

**"Costs 10x higher than expected"**
→ Answer: model right-sizing + prompt caching + token limits + per-user monitoring

**"New prompt version causes regressions"**
→ Answer: eval suite in CI/CD + canary deployment + prompt versioning + rollback

**"Security incident from prompt injection"**
→ Answer: input validation + user input wrapping + output validation + system prompt constraints

---

## 🧪 Final Quiz — Comprehensive

**Q1:** You need to handle 10,000 requests/hour with a mix of simple and complex queries. What's the cost-optimal architecture?
<details><summary>Answer</summary>Route simple queries to Haiku, complex queries to Sonnet, reserve Opus only for tasks requiring its capabilities. Use prompt caching for shared system prompts. Implement request queuing to stay within rate limits.</details>

**Q2:** A prompt change ships without testing. How do you catch regressions before users?
<details><summary>Answer</summary>Run automated eval suite in CI/CD pipeline as a deployment gate. Fail the deployment if regression rate exceeds threshold (e.g., >5% of test cases regress).</details>

**Q3:** What's the difference between an operator adjustable behavior and a hardcoded behavior?
<details><summary>Answer</summary>Hardcoded behaviors (CBRN assistance, CSAM, etc.) cannot be changed by anyone — they're absolute limits in the model. Softcoded/adjustable behaviors are defaults that operators can turn on or off for legitimate business purposes.</details>

---

## You've Completed the Series 🎉

**10 newsletters. 10 exam domains. Here's your study map:**

| # | Topic | Exam Weight |
|---|-------|-------------|
| 1 | Models & API | High |
| 2 | Prompt Engineering | High |
| 3 | Tool Use | High |
| 4 | Computer Use | Medium |
| 5 | Agents | High |
| 6 | Safety | High |
| 7 | Context & Memory | Medium |
| 8 | API Best Practices | Medium |
| 9 | Evaluation | Medium |
| 10 | Production | High |

**Final study advice:** The exam tests architecture decisions, not syntax recall. For every scenario, ask: "What could go wrong? What's the minimum viable safeguard? What's the cost-quality tradeoff?" Those three questions unlock most exam answers.

Good luck. You've got this. 🏆

*Progress: ████████████████████ 10/10 complete*
