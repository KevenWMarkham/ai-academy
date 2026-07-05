import type { LedgerRow } from "../types";

/** The audit trail as a typeset register: step rail, stage, evidence, confidence. */
export function LedgerTrace({ rows }: { rows: LedgerRow[] }) {
  return (
    <ol className="ledger">
      {rows.map((row, i) => {
        const isGate = row.stage === "hitl-gate";
        return (
          <li
            key={row.seq}
            className={`ledger-row${isGate ? " is-gate" : ""} outcome-${row.outcome}`}
            style={{ animationDelay: `${i * 70}ms` }}
          >
            <span className="ledger-step">{isGate ? "★16" : row.step}</span>
            <span className="ledger-stage">{row.stage}</span>
            <span className="ledger-detail">
              {row.detail}
              {row.confidence != null && (
                <span className="ledger-conf"> conf {row.confidence.toFixed(2)}</span>
              )}
            </span>
            <span className={`ledger-outcome outcome-${row.outcome}`}>{row.outcome}</span>
          </li>
        );
      })}
    </ol>
  );
}
