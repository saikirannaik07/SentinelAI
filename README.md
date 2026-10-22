# SentinelAI — AI Agent Security Gateway (MVP)

A hackathon MVP demonstrating policy-based control over proposed AI-agent actions. It evaluates each request and returns **ALLOW**, **BLOCK**, or **HUMAN APPROVAL**, with an audit trail.

> **Scope / honesty note:** This is a local demonstration prototype. It evaluates submitted action requests before the simulated action is executed. It does not automatically intercept third-party agents or protect real enterprise systems.

## Features
- FastAPI backend with request-evaluation endpoint
- Rule-based policy and risk evaluation
- Allow / Block / Human Approval decisions
- Human approval / rejection endpoint
- In-memory audit log (resets when server restarts)
- React-style single-page dashboard implemented as a lightweight static frontend
- Three demo scenarios

## Stack
- Python 3.10+
- FastAPI
- Uvicorn
- HTML/CSS/JavaScript frontend
- In-memory storage for fast setup (PostgreSQL can be added later)

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in `backend/`.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the API:
   ```bash
   uvicorn main:app --reload
   ```
5. Open `frontend/index.html` in your browser.
6. The frontend expects the API at `http://127.0.0.1:8000`. If opening the HTML directly causes browser CORS issues, run a local static server from the project root:
   ```bash
   python -m http.server 5500
   ```
   then open `http://127.0.0.1:5500/frontend/`.

## API
- `GET /` — health/status
- `GET /audit` — audit events
- `POST /evaluate` — evaluate a proposed action
- `POST /approval/{event_id}` — approve or reject a pending action

Example:
```json
{
  "agent": "Demo Agent",
  "action": "read_file",
  "resource": "public_report.pdf",
  "sensitivity": "low",
  "requested_by": "demo-user"
}
```

## Demo script (under 4 minutes)
1. Introduce SentinelAI (20 sec).
2. Submit a permitted read request and show **ALLOW** (35 sec).
3. Submit an unauthorized deletion and show **BLOCK** (35 sec).
4. Submit a sensitive data export and show **HUMAN APPROVAL**; approve/reject it (50 sec).
5. Show audit log and explain that this is a prototype using simulated actions (30 sec).

## Security / implementation notes
- The backend is a demo policy engine, not a production security boundary.
- The audit log is in memory and is not durable.
- Do not send real secrets or personal data to the demo.
- Before production, add authentication, durable storage, signed identities, policy administration, rate limiting, structured audit retention, and integration-specific enforcement.
