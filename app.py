import json
import traceback
import gradio as gr
from agent.agent import run_agent

SYSTEM_HINT = """Fintech SaaS SupportOps Agent (local, free).
Describe your issue like a real support ticket. Optional metadata:
customer_tier=..., region=..., plan=...
"""

def respond(message, history):
    try:
        message = (message or "").strip()
        if not message:
            return "", history

        history = history or []

        # Convert Gradio "messages" history into a ticket thread string
        thread_lines = []
        for m in history:
            role = m.get("role", "")
            content = m.get("content", "")
            if role == "user":
                thread_lines.append(f"User: {content}")
            elif role == "assistant":
                thread_lines.append(f"Agent: {content}")
        thread = "\n".join(thread_lines)

        ticket = (thread + "\nUser: " + message).strip()

        result = run_agent(ticket)

        panel = {
            "category": result.triage.category,
            "priority": result.triage.priority,
            "sentiment": result.triage.sentiment,
            "confidence": result.triage.confidence,
            "missing_info": result.triage.missing_info,
            "route": result.route,
            "citations": result.citations,
            "qc": result.debug.get("qc") if result.debug else None,
        }

        answer = (
            result.answer
            + f"\n\n---\nRouting: {result.route}\n\n"
            + "```json\n"
            + json.dumps(panel, indent=2)
            + "\n```"
        )

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})

        return "", history

    except Exception:
        tb = traceback.format_exc()
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"⚠️ Backend error:\n\n```text\n{tb}\n```"})
        return "", history


with gr.Blocks() as demo:
    gr.Markdown("## 🏦 Fintech SaaS SupportOps Agent (Local, Free)\n" + SYSTEM_HINT)

    chatbot = gr.Chatbot(height=420, type="messages")

    with gr.Row():
        msg = gr.Textbox(placeholder="Describe your issue…", lines=3, show_label=False)
        send = gr.Button("Send", variant="primary")

    clear = gr.Button("Clear")

    send.click(respond, [msg, chatbot], [msg, chatbot])
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)

demo.launch(show_error=True)
