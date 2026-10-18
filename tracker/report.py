from __future__ import annotations

from datetime import date, timedelta

from .health import assess, progress

ICON = {"green": "🟢", "amber": "🟠", "red": "🔴"}
STATUS = {"done": "✅", "in_progress": "🔄", "blocked": "⛔", "not_started": "⬜"}


def weekly_status(dep: dict, milestones: list[dict], today: date) -> str:
    health, reasons = assess(milestones, today)
    week_ago = today - timedelta(days=7)
    done_this_week = [m for m in milestones if m["done_on"] and date.fromisoformat(m["done_on"]) > week_ago]
    upcoming = [m for m in milestones if m["status"] != "done"
                and date.fromisoformat(m["due"]) <= today + timedelta(days=14)]
    blocked = [m for m in milestones if m["status"] == "blocked"]

    out = [f"# {dep['customer']}: weekly status, {today.isoformat()}", "",
           f"**Health:** {ICON[health]} {health.upper()} · **Progress:** {progress(milestones):.0%} of milestones done", ""]
    if reasons:
        out += ["**Why:**", *[f"- {r}" for r in reasons], ""]
    out += ["## Done this week", *([f"- {m['name']}" for m in done_this_week] or ["- Nothing completed"]), ""]
    out += ["## Next two weeks", *([f"- {m['name']} (due {m['due']}, {m['owner']})" for m in upcoming] or ["- Nothing due"]), ""]
    if blocked:
        out += ["## Blockers (need action)",
                *[f"- **{m['name']}**: {m['blocker']} (owner: {m['blocker_owner']}, since {m['blocked_since']})" for m in blocked], ""]
    out += ["## Full plan", "", "| | Milestone | Owner | Due |", "|---|---|---|---|",
            *[f"| {STATUS[m['status']]} | {m['name']} | {m['owner']} | {m['due']} |" for m in milestones]]
    return "\n".join(out) + "\n"
