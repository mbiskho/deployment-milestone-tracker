from __future__ import annotations

import os
from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from . import db
from .health import assess, progress
from .report import weekly_status

app = FastAPI(title="Deployment Milestone Tracker", version="0.1.0")
conn = db.connect(os.environ.get("TRACKER_DB", "tracker.db"))


class NewDeployment(BaseModel):
    customer: str
    start: date
    template: str = "standard"


class MilestoneUpdate(BaseModel):
    status: Literal["not_started", "in_progress", "blocked", "done"] | None = None
    due: date | None = None
    blocker: str | None = None
    blocker_owner: Literal["us", "customer"] | None = None


def _load(dep_id: int):
    try:
        dep, ms = db.deployment(conn, dep_id)
    except KeyError:
        raise HTTPException(404, "no such deployment") from None
    return dict(dep), [dict(m) for m in ms]


@app.post("/deployments", status_code=201)
def create(body: NewDeployment) -> dict:
    try:
        return {"id": db.create_deployment(conn, body.customer, body.start, body.template)}
    except ValueError as e:
        raise HTTPException(400, str(e)) from None


@app.get("/deployments")
def list_deployments() -> list[dict]:
    out = []
    for row in conn.execute("SELECT id FROM deployments ORDER BY id").fetchall():
        dep, ms = _load(row["id"])
        health, reasons = assess(ms, date.today())
        out.append({**dep, "health": health, "reasons": reasons, "progress": progress(ms)})
    return out


@app.get("/deployments/{dep_id}")
def get_deployment(dep_id: int) -> dict:
    dep, ms = _load(dep_id)
    health, reasons = assess(ms, date.today())
    return {**dep, "health": health, "reasons": reasons, "progress": progress(ms), "milestones": ms}


@app.patch("/milestones/{mid}")
def update(mid: int, body: MilestoneUpdate) -> dict:
    if body.status == "blocked" and not body.blocker:
        raise HTTPException(422, "a blocked milestone needs a blocker description")
    try:
        changes = body.model_dump(exclude_none=True)
        if "due" in changes:
            changes["due"] = changes["due"].isoformat()
        return dict(db.update_milestone(conn, mid, date.today(), **changes))
    except KeyError:
        raise HTTPException(404, "no such milestone") from None


@app.get("/deployments/{dep_id}/status.md", response_class=PlainTextResponse)
def status_md(dep_id: int) -> str:
    dep, ms = _load(dep_id)
    return weekly_status(dep, ms, date.today())
