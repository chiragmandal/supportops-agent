import json
import re
from string import Template
from langchain_ollama import ChatOllama
from .schemas import TriageResult

# print("✅ LOADED triage.py (Template version)")

_llm = ChatOllama(model="llama3.1", temperature=0)

TRIAGE_PROMPT = Template("""You are a senior Fintech SaaS support triage system.
Return ONLY valid JSON matching this schema (no markdown, no backticks, no explanation):

{
  "category": "BILLING|ACCOUNT_ACCESS|BUG_REPORT|FEATURE_REQUEST|SECURITY|OTHER",
  "priority": "P0|P1|P2|P3",
  "sentiment": "NEGATIVE|NEUTRAL|POSITIVE",
  "confidence": 0.0-1.0,
  "missing_info": ["..."],
  "reason": "short explanation"
}

Rules:
- P0: security incident, suspected fraud/AML, data breach, customer can't access funds
- P1: payment failures, chargebacks, locked out with urgent business impact
- P2: degraded functionality, webhook issues, pending transactions beyond typical window
- P3: how-to questions, feature requests

Ticket:
\"\"\"$ticket\"\"\"
""")

TRIAGE_PROMPT_RETRY = Template("""Return ONLY a JSON object (no markdown, no prose). Must start with '{' and end with '}'.
Use the schema exactly.

Ticket:
\"\"\"$ticket\"\"\"
""")

def _clean_to_json(raw: str) -> str:
    raw = raw.strip()

    # Remove ```json ... ``` fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    # Try to extract the first {...} block
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start:end + 1]

    # If model returned a JSON fragment like: "category": "BILLING", ...
    if raw.lstrip().startswith('"category"') or raw.lstrip().startswith("'category'"):
        return "{" + raw.strip().strip(",") + "}"

    return raw

def triage_ticket(ticket: str) -> TriageResult:
    prompt = TRIAGE_PROMPT.substitute(ticket=ticket)
    raw = _llm.invoke(prompt).content
    cleaned = _clean_to_json(raw)

    try:
        data = json.loads(cleaned)
        return TriageResult(**data)
    except Exception:
        prompt2 = TRIAGE_PROMPT_RETRY.substitute(ticket=ticket)
        raw2 = _llm.invoke(prompt2).content
        cleaned2 = _clean_to_json(raw2)

        try:
            data2 = json.loads(cleaned2)
            return TriageResult(**data2)
        except Exception as e:
            raise ValueError(
                f"Failed to parse triage JSON.\n\nRAW1:\n{raw}\n\nCLEAN1:\n{cleaned}\n\nRAW2:\n{raw2}\n\nCLEAN2:\n{cleaned2}\n\nERR:\n{e}"
            )
