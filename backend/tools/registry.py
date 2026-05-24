from typing import Callable, Any
import json
from tools.tavily_client import web_search, web_fetch
from tools.kb_tools import kb_query_facts, kb_search_prose, kb_check_source

# Descriptions are the single most important field — agents pick tools based on these.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use for finding new facts, recent events, or sources you don't already have in the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, 3–8 words is best."},
                    "max_results": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10},
                    "depth": {"type": "string", "enum": ["basic", "advanced"], "default": "basic"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch the cleaned text content of a specific URL. Use after web_search when you want to read a result in full.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "kb_query_facts",
            "description": "Query the beat's structured knowledge base for verified facts. Always use this BEFORE web_search to check if we already know something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beat_id": {"type": "integer"},
                    "entity": {"type": "string", "description": "An entity name like 'Anthropic' or 'Mistral 3.1'."},
                    "query": {"type": "string", "description": "Free-text query about facts you want."},
                },
                "required": ["beat_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "kb_search_prose",
            "description": "Semantic search over prior articles, notes, and extracted passages on this beat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beat_id": {"type": "integer"},
                    "query": {"type": "string"},
                    "k": {"type": "integer", "default": 5},
                },
                "required": ["beat_id", "query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "kb_check_source",
            "description": "Get the reliability score and history for a source domain (e.g. 'techcrunch.com').",
            "parameters": {
                "type": "object",
                "properties": {"domain": {"type": "string"}},
                "required": ["domain"],
            },
        },
    },
]

REGISTRY: dict[str, Callable[..., Any]] = {
    "web_search": web_search,
    "web_fetch": web_fetch,
    "kb_query_facts": kb_query_facts,
    "kb_search_prose": kb_search_prose,
    "kb_check_source": kb_check_source,
}

def execute_tool(name: str, arguments_json: str) -> str:
    """Run a tool and return JSON string (what the LLM expects in tool messages)."""
    if name not in REGISTRY:
        return json.dumps({"error": f"unknown tool: {name}"})
    try:
        args = json.loads(arguments_json) if arguments_json else {}
        result = REGISTRY[name](**args)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})