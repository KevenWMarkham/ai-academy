# 07 · Surfacing in M365 Copilot — test on the Deloitte tenant, deploy at the customer

The persona rule from doc 03 becomes literal here: Raj meets the chains **only through
Copilot**. The surface is a **declarative agent** whose action is an **API plugin** calling
`academy-api`; the chain runtime is unchanged — Copilot is just a new front door.

```
M365 Copilot chat (Teams / copilot.microsoft.com)
  └─ Declarative agent "HR Service Delivery"          m365/appPackage/declarativeAgent.json (v1.7)
       └─ API plugin action (OpenAPI)                 m365/appPackage/ai-plugin.json (v2.4) + openapi.json
            └─ academy-api  (FastAPI)                 apps/academy-api → Azure Container Apps (infra/)
                 └─ ChainRunner → the 9 scenarios     unchanged: gate at 16, ledger, KPIs
```

The Copilot orchestrator plans against the three `operationId`s — `listScenarios`,
`getScenario`, `runScenario` — and the agent's instructions tell it which scenario id fits
which employee ask. The agent is told to present answers **faithfully** (citations, gate
outcomes, escalations) and never to answer HR policy from its own knowledge.

## Lifecycle: two tenants, one package pipeline

| | **Test — Deloitte tenant** | **Production — customer tenant** |
|---|---|---|
| Azure | Deloitte Azure instance, RG e.g. `rg-ai-academy-test` | Customer subscription, their landing zone |
| Data | **Synthetic only** (`data/`) — never real HR data on the test tenant | Customer's gold HR views behind the same API contract |
| API auth | `X-Api-Key` shared key (`ACADEMY_API_KEY`) | Entra ID — plugin auth `OAuthPluginVault`, API validates tokens |
| Agent distribution | Sideload / "Upload custom app" for the pilot group | Teams admin center → org-wide or targeted rollout |
| Package | `package.ps1 -ApiBaseUrl <deloitte ACA URL>` | Same script, customer URL — **only the URL and auth change** |

That last row is the design goal: the app package is tenant-portable. Rebuild with the
customer's base URL, switch the plugin `auth` block, upload.

## Part 1 — Deploy the API to the Deloitte tenant

Prereqs: Azure CLI logged into the Deloitte tenant (`az login --tenant <deloitte-tenant-id>`),
contributor on a test subscription/RG.

```powershell
az login --tenant <deloitte-tenant-id>
cd infra
./deploy.ps1 -ResourceGroup rg-ai-academy-test -Location eastus2 -ApiKey "<generate-a-key>"
```

The script what-if-validates, deploys ACA + ACR (managed-identity pull, no admin creds),
builds the image server-side (`az acr build` — no local Docker), rolls the app, smoke-tests
`/healthz`, and prints the API base URL. The API ships in `mock` runtime — deterministic
synthetic answers, ideal for tenant testing; flip `ACADEMY_RUNTIME` to `live`/`maf` once an
AOAI deployment exists in the test subscription.

## Part 2 — Package and sideload the agent

```powershell
python scripts/make_icons.py                      # once — generates the package icons
cd m365
./package.ps1 -ApiBaseUrl https://<the-url-from-part-1>
```

Sideload `m365/dist/hr-service-delivery-agent.zip` on the Deloitte tenant — pick one:

- **Microsoft 365 Agents Toolkit** (VS Code): sign in with your Deloitte test account →
  provision/preview the package. Best for iterating.
- **Teams → Apps → Manage your apps → Upload an app → Upload a custom app** (requires custom
  app upload enabled for your account).
- **Teams admin center** (tenant admin): Teams apps → Manage apps → Upload new app — then
  scope availability to the pilot group.

Requirements on the test tenant: an **M365 Copilot license** for each tester, and custom app
upload permitted by app-setup policy. Both typically need a tenant-admin request in a managed
tenant like Deloitte's.

## Part 3 — Validate on the tenant

Open Copilot (Teams or copilot.microsoft.com) → the **HR Service Delivery** agent → walk the
nine conversation starters (they are the nine scenarios). Verify against the briefs:

- **hr-hrsd-01** answer carries the `[source: …]` citation and the CA jurisdiction rider.
- **hr-hrsd-06** relays the letter and the ACK_ONLY framing.
- **hr-hrsd-08** (garnishment) reports the **escalation to Payroll Operations** — the agent
  must present it as routing-with-context, not failure.
- **hr-hrsd-09** answers in Spanish (mock mode shows the `[en→es]` tag — expected and honest).

Then the trust checks: ask the agent an HR question **without** naming a scenario (the
instructions must route it), and ask something the KB can't answer (it must escalate, not
invent). API-side evidence: `GET /runs` responses include the full ledger, so testers can
audit every answer.

## Part 4 — Promote to the customer site

1. Deploy `infra/` + image into the **customer's** subscription (their region, their RG).
2. Switch auth: register an Entra app in the customer tenant, change `ai-plugin.json`
   `runtimes[0].auth` to `{"type": "OAuthPluginVault", "reference_id": "<from admin center>"}`,
   and validate tokens in `academy_api.main.require_api_key`'s successor.
3. Swap the data plane: point the adapters at the customer's real gold views / ServiceNow —
   the `ServiceHub` interface is the seam; scenarios don't change.
4. Repackage with the customer URL, upload via their Teams admin center, scope the rollout.
5. Keep Purview/sensitivity, RAI review, and the customer's AI governance sign-off in the
   deployment checklist — the ledger (doc 04) is your evidence trail.

## Framing note (Independence)

In all materials, this is **Deloitte's own practice using Microsoft technology for clients
other than Microsoft** — no partner/alliance/JV language. The Deloitte tenant is used solely
as the engineering **test environment** with synthetic data.
