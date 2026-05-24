from db.sqlite import get_conn

def main():
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO beats (name, description) VALUES (?, ?)",
            ("Foundation Model Labs",
             "Anthropic, OpenAI, Mistral, DeepSeek, xAI, Cohere, Meta AI, Google DeepMind, Qwen, Allen AI, Reka, Black Forest Labs, etc."),
        )
    print("Beat seeded.")

if __name__ == "__main__":
    main()