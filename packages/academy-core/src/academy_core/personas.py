"""The HR persona roster — ten personas recur across every HR area.

Every one of them meets the platform only through a Copilot surface — never
the agents, the schema, or the ledger directly.
"""

from __future__ import annotations

from academy_core.models import Persona

PERSONAS: dict[str, Persona] = {
    p.name: p
    for p in (
        Persona("Maya Chen", "Talent Acquisition Partner (Recruiter)", "Recruiting",
                "Copilot Studio agent"),
        Persona("David Okafor", "Hiring / People Manager", "Across the business",
                "Copilot in Teams"),
        Persona("Raj Patel", "Employee / New Hire", "Front line", "Copilot in Teams"),
        Persona("Priya Sharma", "HR Business Partner (HRBP)", "Embedded in the business",
                "Copilot in Teams"),
        Persona("Sofia Ramos", "HR Operations Specialist", "HR shared services",
                "custom Copilot / HRSD"),
        Persona("Aisha Bello", "Employee Relations Specialist", "ER & compliance",
                "Copilot Studio agent"),
        Persona("Marcus Lee", "Total Rewards / Comp Analyst", "Compensation & Benefits",
                "custom Copilot"),
        Persona("Nina Kowalski", "Learning & Development Lead", "Talent / L&D",
                "Copilot + Viva Learning"),
        Persona("Tom Becker", "People Analytics Lead", "People Analytics",
                "Power BI + Copilot"),
        Persona("Elena Vasquez", "CHRO", "Executive", "Power BI + Copilot"),
    )
}


def get_persona(name: str) -> Persona | None:
    return PERSONAS.get(name)
