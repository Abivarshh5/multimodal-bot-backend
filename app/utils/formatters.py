def format_chat_history(messages) -> list:
    """Format Pydantic messages into a list of dicts for LLM prompt."""
    return [{"role": "user" if msg.role == "user" else "assistant", "content": msg.text} for msg in messages]
