import asyncio
from llm.router import complete
from tools.registry import TOOL_SCHEMAS, execute_tool

async def main():
    messages = [
        {"role": "system", "content": "You are a research assistant. Use tools to answer."},
        {"role": "user", "content": "Find one recent article about Mistral AI's latest model release."},
    ]

    for turn in range(4):
        r = await complete(agent="reporter", messages=messages, tools=TOOL_SCHEMAS, max_tokens=512)
        msg = r["message"]
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            print("FINAL:", msg.content)
            break

        for call in msg.tool_calls:
            print(f"-> tool: {call.function.name}({call.function.arguments})")
            result = execute_tool(call.function.name, call.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

asyncio.run(main())