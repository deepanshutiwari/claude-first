# 🔧 Newsletter #3: Tool Use & Function Calling
### Claude Certified Architect Exam Prep | Day 3 of 10

---

## Today's Exam Hook

> "Claude is given 5 tools but keeps hallucinating results instead of calling them. What's wrong with the tool definitions?"

Vague descriptions. The exam tests whether you know that Claude decides WHEN and WHETHER to use a tool based entirely on the tool's description and parameter documentation — not on the function implementation.

---

## Tool Definition Architecture

```python
tools = [
    {
        "name": "get_weather",
        "description": """Get current weather conditions for a specific location.
        Use this tool whenever the user asks about weather, temperature, 
        conditions, or forecast for any city or region.
        Returns temperature in Celsius, humidity percentage, and conditions.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name and country code, e.g. 'London, UK' or 'Tokyo, JP'"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit. Default: celsius"
                }
            },
            "required": ["location"]
        }
    }
]
```

**The three-part description rule:**
1. What the tool does
2. When to use it (trigger conditions)
3. What it returns

---

## The Tool Use Flow

```python
import anthropic

client = anthropic.Anthropic()

# Step 1: Initial request with tools
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}]
)

# Step 2: Check if Claude wants to use a tool
if response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    tool_name = tool_use.name          # "get_weather"
    tool_input = tool_use.input        # {"location": "Paris, FR"}
    tool_use_id = tool_use.id          # needed for response

    # Step 3: Execute the tool
    result = get_weather(**tool_input)

    # Step 4: Return result to Claude
    final_response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": "What's the weather in Paris?"},
            {"role": "assistant", "content": response.content},  # full content block
            {
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": str(result)
                }]
            }
        ]
    )
```

**Exam gotchas:**
- `stop_reason == "tool_use"` not `"stop_sequence"`
- Return `response.content` (the full list), not just the text
- Tool results go in a `user` role message with type `tool_result`
- Must include `tool_use_id` matching the original tool call

---

## Tool Choice Control

```python
# Force Claude to use a specific tool
tools=tools,
tool_choice={"type": "tool", "name": "get_weather"}

# Force Claude to use any tool (not respond with text)
tool_choice={"type": "any"}

# Let Claude decide (default)
tool_choice={"type": "auto"}

# Prevent tool use entirely
tool_choice={"type": "none"}
```

**Exam scenario:** "You need to guarantee structured output on every call." Answer: `tool_choice={"type": "tool", "name": "your_schema_tool"}` — forces Claude to always call the tool, giving you structured JSON every time.

---

## Parallel Tool Calls

Claude can call multiple tools in one response:

```python
# Response may contain multiple tool_use blocks
for block in response.content:
    if block.type == "tool_use":
        results.append(execute_tool(block.name, block.input, block.id))

# Return ALL results in one user message
messages.append({
    "role": "user",
    "content": [
        {"type": "tool_result", "tool_use_id": r["id"], "content": r["result"]}
        for r in results
    ]
})
```

**When Claude parallelizes:** When tool calls are independent. When they're sequential (B depends on A), Claude calls them one at a time.

---

## 🧪 Quiz

**Q1:** After a tool call, Claude's response content includes both a `tool_use` block and a `text` block. The stop_reason is `tool_use`. What should you do with the text block?
<details><summary>Answer</summary>Include it in the messages when returning tool results (pass the full `response.content` as the assistant message), but don't display it to users yet — Claude hasn't finished its response.</details>

**Q2:** You want Claude to ALWAYS return a structured JSON schema, never free text. What's the most reliable approach?
<details><summary>Answer</summary>Define a tool with the desired schema and set `tool_choice={"type": "tool", "name": "your_tool"}`. This forces structured output on every call.</details>

**Q3:** What's wrong with this tool description: `"name": "search", "description": "Searches things"`?
<details><summary>Answer</summary>Too vague — no trigger conditions (when to use it), no specification of what it searches, no description of what it returns. Claude may not call it when appropriate or may hallucinate results.</details>

---

## Key Concept

**Tool definitions are the interface contract between your code and Claude's reasoning.** The description IS the documentation Claude uses to decide when and how to call the tool. Treat it like a well-written API spec, not a comment.

---

*Tomorrow: **Computer Use** — how Claude operates browsers and interfaces, and what the exam expects you to know about the beta API.*

*Progress: ██████░░░░ 3/10 complete*
