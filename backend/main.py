from datetime import datetime, timezone
from itertools import count
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="SentinelAI API", version="0.1.0",
              description="Demo policy gateway for proposed AI-agent actions")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo only; restrict origins before deployment.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ids = count(1)
audit_log = []

class ActionRequest(BaseModel):
    agent: str = Field(default="Demo Agent", max_length=80)
    action: str = Field(..., min_length=1, max_length=80)
    resource: str = Field(..., min_length=1, max_length=160)
    sensitivity: Literal["low", "medium", "high"] = "low"
    requested_by: str = Field(default="demo-user", max_length=80)

class ApprovalRequest(BaseModel):
    approved: bool
    reviewer: str = Field(default="demo-reviewer", max_length=80)

def evaluate(req: ActionRequest):
    action = req.action.lower().strip()
    resource = req.resource.lower().strip()

    # Explicit deny rules take precedence.
    if action in {"delete_all", "delete_database", "disable_security", "exfiltrate"}:
        return "BLOCK", "Critical action is prohibited by policy.", "critical"
    if action in {"delete", "delete_file", "send_external", "modify_permissions"}:
        return "BLOCK", "Action is not permitted by the demo policy.", "high"
    if any(term in resource for term in ("secret", "credential", "password", "private_key")):
        return "BLOCK", "Resource appears to contain credentials or secrets.", "critical"

    # Sensitive operations are held for a human.
    if req.sensitivity == "high" or action in {"export_data", "send_email", "update_record"}:
        return "HUMAN APPROVAL", "Sensitive action requires explicit human review.", "high"

    if req.sensitivity == "medium":
        return "HUMAN APPROVAL", "Medium-sensitivity action requires review.", "medium"

    allowed = {"read_file", "search", "summarize", "list_records", "read_record"}
    if action in allowed and req.sensitivity == "low":
        return "ALLOW", "Action matches the permitted low-risk policy.", "low"

    return "BLOCK", "Action is not allowlisted by the demo policy.", "medium"

@app.get("/")
def root():
    return {"name": "SentinelAI", "status": "running", "mode": "demo prototype"}

@app.get("/audit")
def get_audit():
    return list(reversed(audit_log))

@app.post("/evaluate")
def evaluate_action(req: ActionRequest):
    decision, reason, risk = evaluate(req)
    event = {
        "id": next(ids),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "agent": req.agent,
        "action": req.action,
        "resource": req.resource,
        "sensitivity": req.sensitivity,
        "requested_by": req.requested_by,
        "decision": decision,
        "reason": reason,
        "risk": risk,
        "status": "PENDING" if decision == "HUMAN APPROVAL" else ("EXECUTED (SIMULATED)" if decision == "ALLOW" else "DENIED"),
    }
    audit_log.append(event)
    return event

@app.post("/approval/{event_id}")
def resolve_approval(event_id: int, req: ApprovalRequest):
    event = next((item for item in audit_log if item["id"] == event_id), None)
    if event is None:
        raise HTTPException(status_code=404, detail="Audit event not found")
    if event["decision"] != "HUMAN APPROVAL":
        raise HTTPException(status_code=400, detail="This event is not awaiting approval")
    if event["status"] != "PENDING":
        raise HTTPException(status_code=400, detail="This request has already been reviewed")

    event["status"] = "APPROVED (SIMULATED)" if req.approved else "REJECTED"
    event["reviewer"] = req.reviewer
    event["reviewed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return event
