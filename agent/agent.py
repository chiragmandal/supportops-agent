import json
from .triage import triage_ticket
from .retrieve import retrieve
from .router import route_from_triage
from .reply import draft_reply
from .checker import check_reply
from .schemas import AgentResponse, RetrievedChunk

def run_agent(ticket: str) -> AgentResponse:
    triage = triage_ticket(ticket)
    route = route_from_triage(triage)

    docs = retrieve(ticket, k=5)

    triage_str = triage.model_dump_json()
    reply_raw, snippets = draft_reply(ticket, triage_str, docs)

    # Build snippets blob for checker
    snippets_blob = "\n\n".join([f"[{s['chunk_id']} | {s['source']}]\n{s['text']}" for s in snippets])
    qc = check_reply(reply_raw, snippets_blob)

    final_answer = reply_raw
    if not qc.get("ok", True):
        # Append suggested fix (simple approach). You can also re-draft using suggested_fix.
        final_answer = reply_raw + "\n\n---\nQA NOTE: " + qc.get("suggested_fix", "")

    retrieved = [RetrievedChunk(**s) for s in snippets]
    citations = [{"chunk_id": s["chunk_id"], "source": s["source"]} for s in snippets]

    return AgentResponse(
        triage=triage,
        route=route,
        answer=final_answer,
        citations=citations,
        retrieved=retrieved,
        debug={"qc": qc},
    )
