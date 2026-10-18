"""Standard deployment plans: milestone name, owner side, days after start."""

TEMPLATES: dict[str, list[tuple[str, str, int]]] = {
    "standard": [
        ("Kick-off and success criteria signed", "us", 3),
        ("Security review and DPA signed", "customer", 14),
        ("Network access and SSO configured", "customer", 21),
        ("Sandbox environment live", "us", 28),
        ("Data onboarding: first full load", "us", 35),
        ("Integration tests passing", "us", 45),
        ("User acceptance testing sign-off", "customer", 55),
        ("Go-live", "us", 60),
        ("Hypercare complete", "us", 75),
    ],
    "pilot": [
        ("Kick-off and success criteria signed", "us", 2),
        ("Sandbox environment live", "us", 10),
        ("Pilot users onboarded", "customer", 14),
        ("Pilot review against success criteria", "us", 30),
    ],
}

GO_LIVE = "Go-live"
