# 🖥️ Newsletter #4: Computer Use
### Claude Certified Architect Exam Prep | Day 4 of 10

---

## Today's Exam Hook

> "A team wants to automate browser-based workflows using Claude. They implement computer use and Claude successfully clicks buttons — but fails on dynamic content that loads after 2 seconds. What's the architectural fix?"

Explicit wait strategies and state verification. Computer use requires you to architect around latency, not just actions. The exam tests whether you understand the operational constraints of the beta API.

---

## What Computer Use Actually Is

Computer use lets Claude control a computer by:
- Taking screenshots (seeing the screen)
- Moving/clicking the mouse
- Typing keyboard input
- Executing bash commands

It's **not** a magic "automate anything" feature — it's a perception-action loop that requires careful orchestration.

---

## The Three Computer Use Tools

```python
tools = [
    {
        "type": "computer_20241022",
        "name": "computer",
        "display_width_px": 1920,
        "display_height_px": 1080,
        "display_number": 1
    },
    {
        "type": "text_editor_20241022", 
        "name": "str_replace_editor"
    },
    {
        "type": "bash_20241022",
        "name": "bash"
    }
]
```

**Exam fact:** Computer use requires the `computer-use-2024-10-22` beta header:
```python
client.messages.create(
    model="claude-opus-4-5",  # Computer use requires Opus
    betas=["computer-use-2024-10-22"],
    ...
)
```

---

## The Perception-Action Loop

```python
messages = [{"role": "user", "content": "Go to github.com and star the anthropics/anthropic-sdk-python repo"}]

while True:
    response = client.beta.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        tools=tools,
        messages=messages,
        betas=["computer-use-2024-10-22"]
    )
    
    if response.stop_reason == "end_turn":
        break  # Claude is done
    
    # Execute tool actions and collect screenshots
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_computer_action(block)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result  # includes screenshot
            })
    
    # Feed results back
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})
```

---

## Critical Operational Constraints

| Constraint | Detail |
|-----------|--------|
| **Model** | Only Claude Opus supports computer use |
| **Beta header** | Required: `betas=["computer-use-2024-10-22"]` |
| **Screenshot timing** | Must wait for page load before taking screenshot |
| **Coordinate system** | Pixels from top-left (0,0) |
| **Safety** | Never run unmonitored on systems with sensitive data |

**The dynamic content fix (exam answer):** After actions that trigger loading (clicks, form submissions), add a wait + screenshot verification step before proceeding:

```python
def execute_computer_action(block):
    perform_action(block.input)
    time.sleep(2)  # Wait for dynamic content
    screenshot = take_screenshot()
    return [{"type": "image", "source": {"type": "base64", 
             "media_type": "image/png", "data": screenshot}}]
```

---

## What the Exam Tests on Computer Use

1. **Which model?** Only Opus (not Sonnet or Haiku)
2. **Beta header?** Always required — `computer-use-2024-10-22`
3. **Tool types?** Three tools: `computer`, `str_replace_editor`, `bash`
4. **Safety posture?** Human-in-the-loop for irreversible actions
5. **When NOT to use it?** When an API exists — always prefer APIs over UI automation

---

## 🧪 Quiz

**Q1:** A developer uses `claude-sonnet-4-5` for computer use tasks to save money. What happens?
<details><summary>Answer</summary>It won't work — computer use requires Claude Opus. Model capability is not negotiable here.</details>

**Q2:** What's the correct header to enable computer use?
<details><summary>Answer</summary>`betas=["computer-use-2024-10-22"]` in the API call parameters.</details>

**Q3:** When should you choose computer use over tool use?
<details><summary>Answer</summary>Only when no API or programmatic interface exists. Computer use is a last resort — APIs are faster, cheaper, and more reliable.</details>

---

## Key Concept

**Computer use is a fallback, not a first choice.** The exam tests whether you know the hierarchy: API integration > tool use > computer use. Choose computer use only for legacy systems or when no programmatic interface exists.

---

*Tomorrow: **Agents & Multi-Agent Systems** — orchestrators, subagents, and how to build systems that don't hallucinate their way through multi-step tasks.*

*Progress: ████████░░ 4/10 complete*
