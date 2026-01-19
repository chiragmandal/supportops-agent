from typing import List, Dict
from langchain_ollama import ChatOllama

_llm = ChatOllama(model="llama3.1", temperature=0.2)

REPLY_PROMPT = """You are a Fintech SaaS support agent.
Write a helpful response using ONLY the provided knowledge snippets.
If information is missing, ask targeted follow-up questions.
Never request full card numbers or full bank details (last 4 digits only).
Be concise and professional.

Ticket:
{ticket}

Triage:
{triage}

Knowledge snippets:
{snippets}

Return:
1) A customer-facing reply
2) A "CITATIONS" section listing which snippet ids you used (comma-separated).
"""

def build_snippets(docs) -> List[Dict[str, str]]:
    out = []
    for i, d in enumerate(docs):
        src = d.metadata.get("source", "kb")
        out.append({
            "chunk_id": f"kb_{i}",
            "source": str(src).split("/")[-1],
            "text": d.page_content
        })
    return out

def draft_reply(ticket: str, triage_str: str, docs):
    snippets = build_snippets(docs)
    blob = "\n\n".join([f"[{s['chunk_id']} | {s['source']}]\n{s['text']}" for s in snippets])

    prompt = REPLY_PROMPT.format(ticket=ticket, triage=triage_str, snippets=blob)
    raw = _llm.invoke(prompt).content.strip()
    return raw, snippets
