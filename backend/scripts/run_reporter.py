import asyncio, json
from agents.reporter import run_reporter

async def main():
    out = await run_reporter(beat_id=1, beat_name="Foundation Model Labs")
    print(f"Turns: {out['turns']}")
    print(f"Tool calls: {len(out['tool_log'])}")
    print("\n--- DRAFT ---\n")
    print(json.dumps(out["draft"], indent=2)[:3000])

asyncio.run(main())