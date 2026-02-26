# app/chatbot.py

from app.retriever import Retriever

import re

STRICT_NO_ANSWER = "I do not have verified information."


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\u0900-\u097F.,:/()-]", "", text)  # keep Hindi + English
    return text.strip()


def extract_relevant_sentences(query, context):
    sentences = re.split(r'(?<=[.?!])\s+', context)
    q_words = set(query.lower().split())

    scored = []
    for s in sentences:
        words = set(s.lower().split())
        score = len(q_words & words)
        if score > 0:
            scored.append((score, s))

    scored.sort(reverse=True)
    return " ".join([s for _, s in scored[:5]])


def answer_query(query, retriever):
    chunks = retriever.search(query, top_k=5)

    if not chunks:
        return STRICT_NO_ANSWER

    context = " ".join([c["text"] for c in chunks])
    context = clean_text(context)

    if not context:
        return STRICT_NO_ANSWER

    answer = extract_relevant_sentences(query, context)

    return answer if answer else STRICT_NO_ANSWER


def run_cli():
    print("\nBilingual RAG Chatbot (Strict Mode)")
    print("Type 'exit' to quit.\n")

    retriever = Retriever()

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        response = answer_query(query, retriever)
        print("\nBot:", response, "\n")


if __name__ == "__main__":
    run_cli()