# Deployment Milestone Tracker

One place to see where every customer deployment stands: which milestones are done, which are late, what's blocking them and who owns the blocker. It also writes the weekly status update that would otherwise take Friday afternoon.

```
plan template (YAML) ──► new deployment ──► milestones with owners + due dates
                                                 │
                         update status / blocker ┤
                                                 ▼
                  health per deployment (green / amber / red) ──► weekly status (Markdown)
```

## Usage

```bash
pip install -e ".[dev]"
uvicorn tracker.api:app --reload                       # API + OpenAPI docs at /docs

curl -X POST localhost:8000/deployments -H 'content-type: application/json' \
     -d '{"customer": "Bank Rakyat", "start": "2026-11-02", "template": "standard"}'
curl -X PATCH localhost:8000/milestones/3 -H 'content-type: application/json' \
     -d '{"status": "blocked", "blocker": "Waiting on firewall change CR-4471", "blocker_owner": "customer"}'
curl localhost:8000/deployments/1/status.md             # the weekly update, ready to paste
```

## Health rules

Kept deliberately simple, so anyone can predict the colour:

| Health | When |
|---|---|
| **red** | any milestone overdue by more than 5 days, or blocked for more than 3 days |
| **amber** | anything overdue or blocked at all, or the go-live milestone due within 7 days and not on track |
| **green** | everything else |

The reason is always shown next to the colour, because a red with no explanation just starts a meeting.

## Layout

```
tracker/templates.py  standard milestone plans (offsets from start date)
tracker/db.py         SQLite schema and queries (stdlib sqlite3)
tracker/health.py     green/amber/red rules, pure functions
tracker/report.py     weekly Markdown status
tracker/api.py        FastAPI routes
tests/                health and report tests
```
