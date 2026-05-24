import asyncio, httpx
from openai import AsyncOpenAI
from config import settings

async def check_openai_compat(name, base_url, api_key, model):
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    try:
        r = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'ok' and nothing else."}],
            max_tokens=10,
        )
        print(f"[OK]   {name}: {r.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")

async def check_jina():
    async with httpx.AsyncClient() as http:
        r = await http.post(
            "https://api.jina.ai/v1/embeddings",
            headers={"Authorization": f"Bearer {settings.jina_api_key}"},
            json={"model": "jina-embeddings-v3", "input": ["hello"]},
        )
        ok = r.status_code == 200
        print(f"[{'OK  ' if ok else 'FAIL'}] Jina embeddings: {r.status_code}")

async def check_tavily():
    from tavily import TavilyClient
    try:
        TavilyClient(api_key=settings.tavily_api_key).search("test", max_results=1)
        print("[OK]   Tavily")
    except Exception as e:
        print(f"[FAIL] Tavily: {e}")

async def main():
    # NOTE: model IDs change. Verify on each provider's docs page.
    await check_openai_compat("Cerebras", "https://api.cerebras.ai/v1",
                              settings.cerebras_api_key, "llama3.1-8b")
    await check_openai_compat("Groq", "https://api.groq.com/openai/v1",
                              settings.groq_api_key, "llama-3.3-70b-versatile")
    await check_openai_compat("SambaNova", "https://api.sambanova.ai/v1",
                              settings.sambanova_api_key, "Meta-Llama-3.3-70B-Instruct")
    await check_openai_compat("OpenRouter", "https://openrouter.ai/api/v1",
                              settings.openrouter_api_key, "nvidia/nemotron-3-super-120b-a12b:free")
    await check_jina()
    await check_tavily()

if __name__ == "__main__":
    asyncio.run(main())