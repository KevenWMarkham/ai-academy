"""academy-api — the REST surface the M365 Copilot declarative agent calls.

Copilot's orchestrator reads the OpenAPI description of this API (packaged in
``m365/appPackage/openapi.json``) and calls it as an **API plugin action**.
The chain runtime stays exactly the same — this is only a new front door.
"""
