import asyncio
from llm.router import complete, AGENT_CHAINS

async def main():
    for agent in AGENT_CHAINS.keys():
        r = await complete(
            agent=agent,
            messages=[
                {"role": "system", "content": "Reply in exactly 5 words."},
                {"role": "user", "content": "Describe foundation models."},
            ],
            max_tokens=50,
        )
        print(f"[{agent}] via {r['provider']}: {r['message'].content}")

asyncio.run(main())