import logging
from llm.router import complete
from tools.registry import TOOL_SCHEMAS, execute_tool

log = logging.getLogger(__name__)

async def run_agent(
    agent_name: str,
    system_prompt: str,
    user_prompt: str,
    *,
    tools: list[dict] | None = TOOL_SCHEMAS,
    max_turns: int = 10,
    temperature: float = 0.4,
    max_tokens: int = 2048,
    response_format: dict | None = None,
) -> dict:
    """Generic agent loop. Returns {'content': str, 'turns': int, 'tool_log': [...]}.
    """
    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]
    tool_log = []

    for turn in range(max_turns):
        kwargs = {"tools": tools} if tools else {}
        if response_format:
            kwargs["response_format"] = response_format

        r = await complete(
            agent=agent_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        msg = r["message"]
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return {"content": msg.content or "", "turns": turn + 1, "tool_log": tool_log}

        for call in msg.tool_calls:
            log.info(f"[{agent_name}] tool: {call.function.name} args={call.function.arguments}")
            result = execute_tool(call.function.name, call.function.arguments)
            tool_log.append({
                "tool": call.function.name,
                "args": call.function.arguments,
                "result_preview": result[:300],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    return {"content": "[max turns reached]", "turns": max_turns, "tool_log": tool_log}