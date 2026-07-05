"""academy-services — the AI-service adapters the chains call.

Every adapter is **mock-first**: with no credentials it runs a deterministic
local implementation, so students see the *shape* of the service and exactly
where it plugs into the chain. Setting ``ACADEMY_RUNTIME=live`` (plus the
service's env vars) or ``ACADEMY_RUNTIME=maf`` upgrades individual adapters to
the real Azure AI service; anything unconfigured degrades gracefully to mock.
"""

from academy_services.hub import ServiceHub

__all__ = ["ServiceHub"]
