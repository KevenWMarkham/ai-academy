"""The 9 HR Service Delivery (Tier-0) scenarios — importing this package registers them all.

Area pattern: a single grounded agent on a short **Sequential** MAF chain at
ZERO_TOUCH, escalating only the genuine edge cases. Teaching briefs live in
``scenarios/hr-service-delivery/``.
"""

from academy_hrsd import (  # noqa: F401  (import = registration)
    hrsd01_policy_qa,
    hrsd02_status_lookup,
    hrsd03_kb_search,
    hrsd04_life_event,
    hrsd05_leave_absence,
    hrsd06_doc_generation,
    hrsd07_data_correction,
    hrsd08_deflection,
    hrsd09_multilingual,
)

ALL_SCENARIO_IDS = tuple(f"hr-hrsd-0{n}" for n in range(1, 10))
