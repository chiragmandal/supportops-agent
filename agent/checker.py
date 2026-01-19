import json
import re
from string import Template
from langchain_ollama import ChatOllama

_llm = ChatOllama(model="llama3.1", temperature=0)

CHECK_PROMPT = Template("""You are a strict QA checker for Fintech SaaS support replies.
Return ONLY valid JSON (no markdown, no prose). Must start with '{' and end with '}'.

Detect:
- Unsupported claims (not grounded in snippets)
- Requests for sensitive data (full PAN/bank info)
- Missing critical follow-ups (e.g., request_id for API errors, invoice ID for verification)

JSON schema:
{
  "ok": true/false,
  "issues": ["..."],
  "suggested_fix": "..."
}

Reply:
$reply

Snippets:
$snippets
""")

def _clean_to_json(raw: str) -> str:
    raw = raw.strip()

    # Remove ```json ... ``` fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    # Extract first {...} block
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start:end+1]

    # If model returned a fragment like: "ok": true, ...
    if raw.lstrip().startswith('"ok"') or raw.lstrip().startswith("'ok'"):
        return "{" + raw.strip().strip(",") + "}"

    return raw

def check_reply(reply: str, snippets_blob: str):
    prompt = CHECK_PROMPT.substitute(reply=reply, snippets=snippets_blob)
    raw = _llm.invoke(prompt).content
    cleaned = _clean_to_json(raw)

    try:
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(
            f"Failed to parse checker JSON.\n\nRAW:\n{raw}\n\nCLEANED:\n{cleaned}\n\nERR:\n{e}"
        )
