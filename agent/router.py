from .schemas import TriageResult, Route

def route_from_triage(triage: TriageResult) -> Route:
    if triage.category == "SECURITY" or triage.priority == "P0":
        return "ESCALATE_SECURITY"
    if triage.category == "BILLING":
        return "ESCALATE_BILLING" if triage.priority in ("P0", "P1") else "AUTO_REPLY"
    if triage.category in ("BUG_REPORT",):
        return "ESCALATE_TECH" if triage.priority in ("P0", "P1", "P2") else "NEEDS_INFO"
    if triage.missing_info:
        return "NEEDS_INFO"
    return "AUTO_REPLY"
