import { useEffect, useState } from "react";
import { api } from "../api";
import type { RunOut, ScenarioDetail } from "../types";
import { EMPLOYEES } from "../types";
import { LedgerTrace } from "./LedgerTrace";

interface Props {
  detail: ScenarioDetail | null;
}

/** Render the drafted answer: minimal **bold** + line-break support, nothing more. */
function Answer({ text }: { text: string }) {
  return (
    <div className="answer-body">
      {text.split("\n").map((line, i) => (
        <p key={i}>
          {line.split(/(\*\*[^*]+\*\*)/g).map((part, j) =>
            part.startsWith("**") && part.endsWith("**") ? (
              <strong key={j}>{part.slice(2, -2)}</strong>
            ) : (
              <span key={j}>{part}</span>
            ),
          )}
        </p>
      ))}
    </div>
  );
}

function GateStamp({ run }: { run: RunOut }) {
  const { gate } = run;
  const kind = gate.escalated ? "escalated" : gate.approved ? "approved" : "pending";
  const label = gate.escalated ? "★ Escalated" : gate.approved ? "✓ Approved" : "… Pending";
  return (
    <div className={`gate-stamp gate-${kind}`}>
      <span className="gate-mode">{gate.mode.replace("_", " ")} · gate 16</span>
      <span className="gate-verdict">{label}</span>
      <span className="gate-note">
        {gate.note}
        {run.escalation_route ? ` → ${run.escalation_route}` : ""}
      </span>
    </div>
  );
}

export function RunConsole({ detail }: Props) {
  const [employeeId, setEmployeeId] = useState(EMPLOYEES[0].id);
  const [text, setText] = useState("");
  const [run, setRun] = useState<RunOut | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!detail) return;
    setText(detail.sample_text);
    setEmployeeId(detail.scenario_id === "hr-hrsd-09" ? "E1003" : "E1001");
    setRun(null);
    setError(null);
  }, [detail]);

  if (!detail) return <main className="console console-empty">Loading scenario…</main>;

  const execute = async () => {
    setBusy(true);
    setError(null);
    try {
      setRun(await api.runScenario(detail.scenario_id, employeeId, text));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="console">
      <div className="scenario-head">
        <div className="scenario-title-row">
          <h2 className="scenario-title">{detail.name}</h2>
          <span className="scenario-agent">lead agent — {detail.lead_agent}</span>
        </div>
        <p className="scenario-tagline">{detail.tagline}</p>
        <div className="scenario-chips">
          {detail.azure_services.map((svc) => (
            <span key={svc} className="chip">
              {svc}
            </span>
          ))}
        </div>
      </div>

      <div className="composer">
        <label className="composer-label" htmlFor="employee">
          Asking as
        </label>
        <select
          id="employee"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          disabled={busy}
        >
          {EMPLOYEES.map((emp) => (
            <option key={emp.id} value={emp.id}>
              {emp.label}
            </option>
          ))}
        </select>
        <textarea
          aria-label="Employee request"
          value={text}
          rows={2}
          onChange={(e) => setText(e.target.value)}
          disabled={busy}
        />
        <button className="run-button" onClick={execute} disabled={busy || !text.trim()}>
          {busy ? "Running the chain…" : "Run the chain"}
        </button>
      </div>

      {error && <div className="run-error">Run failed: {error}</div>}

      {run && (
        <div className="run-result" key={run.ledger[0]?.seq + run.answer.length}>
          <GateStamp run={run} />

          <section className="answer">
            <h3 className="section-head">Answer · delivered in Teams</h3>
            <Answer text={run.answer} />
          </section>

          <section>
            <h3 className="section-head">Ledger · {run.ledger.length} × 14-field rows</h3>
            <LedgerTrace rows={run.ledger} />
          </section>

          <section>
            <h3 className="section-head">KPIs this run moves</h3>
            <table className="kpi-table">
              <tbody>
                {run.kpis.map((k) => (
                  <tr key={k.name}>
                    <td className="kpi-name">{k.name}</td>
                    <td className="kpi-delta">
                      {k.baseline} <span className="kpi-arrow">→</span> <strong>{k.target}</strong>
                    </td>
                    <td className="kpi-owner">{k.owner}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      )}
    </main>
  );
}
