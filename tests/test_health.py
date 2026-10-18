from datetime import date

from tracker.health import assess
from tracker.report import weekly_status

TODAY = date(2026, 11, 20)


def m(name="Sandbox environment live", due="2026-11-25", status="not_started", **kw):
    base = {"name": name, "due": due, "status": status, "owner": "us", "blocker": None,
            "blocker_owner": None, "blocked_since": None, "done_on": None}
    return {**base, **kw}


def test_green_when_on_track():
    assert assess([m(), m(status="done", due="2026-11-01")], TODAY) == ("green", [])


def test_amber_when_slightly_late_red_when_very_late():
    assert assess([m(due="2026-11-18")], TODAY)[0] == "amber"
    assert assess([m(due="2026-11-10")], TODAY)[0] == "red"


def test_blocked_turns_red_after_three_days_and_says_who_owns_it():
    fresh = m(status="blocked", blocker="firewall CR", blocker_owner="customer", blocked_since="2026-11-19")
    stale = {**fresh, "blocked_since": "2026-11-10"}
    assert assess([fresh], TODAY)[0] == "amber"
    health, reasons = assess([stale], TODAY)
    assert health == "red" and "owner: customer" in reasons[0]


def test_go_live_close_and_not_started_is_amber():
    assert assess([m(name="Go-live", due="2026-11-24")], TODAY)[0] == "amber"


def test_status_report_lists_blockers():
    md = weekly_status({"customer": "Acme"}, [m(status="blocked", blocker="SSO metadata", blocker_owner="customer",
                                                 blocked_since="2026-11-19")], TODAY)
    assert "## Blockers" in md and "SSO metadata" in md and "AMBER" in md
