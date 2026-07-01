# 🧩 Newsletter #7: Context & Memory Management
### Claude Certified Architect Exam Prep | Day 7 of 10

---

## Today's Exam Hook

> "A chatbot using Claude works perfectly for the first 20 messages, then starts 'forgetting' earlier parts of the conversation and giving inconsistent answers. Token budget is fine. What's the real problem?"

Context window management. Long conversations need summarization or selective context strategies — not just bigger context windows. The 200K token window helps, but architecture still matters.

---

## The Four Types of Memory

| Type | Where Stored | Persists? | Cost |
|------|-------------|-----------|------|
| **In-context** | Messages array | Session only | Token cost per request |
| **External (vector)** | Database | Permanent | Retrieval latency |
| **External (key-value)** | Database | Permanent | Lookup latency |
| **In-weights** | Model training | Permanent | Training cost |

**Exam rule:** Claude has no built-in persistent memory. Anything you need to remember must be stored externally and injected into context.

---

## In-Context Memory Patterns

### Full History (Simple, Expensive)
```python
messages = []  # Grows unbounded

def chat(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})
    response = client.messages.create(
        model="claude-sonnet-4-5",
        messages=messages,
        max_tokens=1024
    )
    messages.append({"role": "assistant", "content": response.content[0].text})
    return response.content[0].text
```
**Problem:** Cost grows quadratically. 100 turns × 500 tokens = 50K tokens per request by the end.

### Sliding Window (Better)
```python
MAX_HISTORY = 20  # Keep last N messages

def chat(user_input: str, history: list) -> str:
    recent = history[-MAX_HISTORY:]  # Trim old messages
    messages = recent + [{"role": "user", "content": user_input}]
    ...
```

### Summarization (Best for Long Sessions)
```python
def summarize_history(messages: list) -> str:
    return client.messages.create(
        model="claude-haiku-4-5-20251001",  # Cheap model for summarization
        system="Summarize this conversation, preserving key facts and decisions.",
        messages=[{"role": "user", "content": str(messages)}],
        max_tokens=500
    ).content[0].text

def chat_with_summary(user_input: str, history: list, summary: str) -> str:
    if len(history) > 30:
        summary = summarize_history(history)
        history = history[-5:]  # Keep only recent after summarizing
    
    system = f"Previous conversation summary:\n{summary}"
    ...
```

---

## External Memory with RAG

```python
import anthropic
from your_vector_db import search_similar

def rag_chat(user_input: str) -> str:
    # 1. Retrieve relevant memories
    relevant_docs = search_similar(user_input, top_k=3)
    
    # 2. Inject into context
    context = "\n\n".join([doc.content for doc in relevant_docs])
    
    system = f"""You are a helpful assistant with access to relevant information.

<retrieved_context>
{context}
</retrieved_context>

Use the retrieved context to inform your responses when relevant."""
    
    return client.messages.create(
        model="claude-sonnet-4-5",
        system=system,
        messages=[{"role": "user", "content": user_input}]
    ).content[0].text
```

---

## Prompt Caching for Memory Efficiency

```python
# Cache the static system prompt + knowledge base
response = client.messages.create(
    model="claude-sonnet-4-5",
    system=[
        {
            "type": "text",
            "text": "You are an expert assistant with access to our knowledge base.",
            "cache_control": {"type": "ephemeral"}  # Cache this block
        },
        {
            "type": "text", 
            "text": knowledge_base_content,  # Large static content
            "cache_control": {"type": "ephemeral"}  # Cache separately
        }
    ],
    messages=conversation_history
)
```

**Cache hit savings:** ~90% reduction on cached input tokens. For a 50K token knowledge base injected on every request, this is significant.

---

## 🧪 Quiz

**Q1:** A user asks Claude something discussed 200 messages ago. The context window has 200K tokens, so all messages fit. But Claude answers inconsistently. Why?
<details><summary>Answer</summary>Attention dilution — with very long contexts, Claude's attention to early content weakens. Architecture should use summarization or explicit memory injection for important facts, not rely on distance-from-end.</details>

**Q2:** What's the cheapest model to use for conversation summarization within a larger Claude system?
<details><summary>Answer</summary>Claude Haiku — use the smallest, fastest model for auxiliary tasks like summarization, reserving Sonnet/Opus for the primary task.</details>

**Q3:** An application needs to remember user preferences across sessions (not just within one conversation). What memory type is required?
<details><summary>Answer</summary>External storage (key-value or database) — in-context memory is session-scoped. Persistent cross-session memory must be stored externally and injected into each new session's context.</details>

---

## Key Concept

**Context is not free, and attention is not uniform.** Long contexts cost more, and older content gets less attention. Design memory architecture deliberately: summarize what's old, inject what's critical, cache what's static.

---

*Tomorrow: **Claude API Best Practices** — rate limits, error handling, streaming, and the production patterns that separate hobby projects from reliable systems.*

*Progress: ██████████████░░░░░░ 7/10 complete*
