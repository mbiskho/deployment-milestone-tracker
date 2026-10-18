"""Green / amber / red, with the reason. Pure functions over plain dicts."""

from __future__ import annotations

from datetime import date

from .templates import GO_LIVE


def _d(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


def assess(milestones: list[dict], today: date) -> tuple[str, list[str]]:
    red, amber = [], []
    for m in milestones:
        if m["status"] == "done":
            continue
        late = (today - _d(m["due"])).days
        if late > 5:
            red.append(f"'{m['name']}' is {late} days overdue")
        elif late > 0:
            amber.append(f"'{m['name']}' is {late} days overdue")
        if m["status"] == "blocked":
            days = (today - (_d(m["blocked_since"]) or today)).days
            msg = f"'{m['name']}' blocked {days}d: {m['blocker'] or 'no reason given'} (owner: {m['blocker_owner'] or '?'})"
            (red if days > 3 else amber).append(msg)
        if m["name"] == GO_LIVE and 0 <= -late <= 7 and m["status"] != "in_progress":
            amber.append(f"go-live in {-late} days and not in progress")
    if red:
        return "red", red + amber
    if amber:
        return "amber", amber
    return "green", []


def progress(milestones: list[dict]) -> float:
    return sum(m["status"] == "done" for m in milestones) / len(milestones) if milestones else 0.0
