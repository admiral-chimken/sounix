
"""
education.py
------------------------
Feature #4 for Sounix: general step-by-step teaching, on any topic.

Ask it to teach you something -- Python, algebra, how to change your
oil, how to cook something -- and it breaks the answer down into
clear, numbered steps instead of a short one-line answer.
"""

from ollama_client import ask_ollama


def explain_topic(topic):
    if not topic or not topic.strip():
        return "Sounix: Use: explain <topic>  (example: explain how to change car oil)"

    prompt = (
        f"Teach me about this, step by step: {topic}\n\n"
        "Format your answer as:\n"
        "1. A one-sentence plain-language definition or overview.\n"
        "2. Numbered steps that actually walk through how to do it or "
        "understand it -- be specific and concrete (exact tools, exact "
        "terms, exact actions), not vague generalities.\n"
        "3. A short 'Why this matters' or 'Common mistakes' section at "
        "the end if relevant.\n"
        "Keep it beginner-friendly -- avoid unexplained jargon, and "
        "explain any technical term the first time you use it."
    )

    return ask_ollama(prompt)


if __name__ == "__main__":
    print(explain_topic("how to check tire pressure"))

