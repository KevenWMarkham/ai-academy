import type { ScenarioSummary } from "../types";

interface Props {
  scenarios: ScenarioSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

/** The scenario register — grouped by productized service, like a course index. */
export function Catalog({ scenarios, selectedId, onSelect }: Props) {
  const services = [...new Set(scenarios.map((s) => s.service))];
  return (
    <aside className="catalog">
      <div className="catalog-head">Scenario register</div>
      {services.map((service) => (
        <section key={service} className="catalog-group">
          <h2 className="catalog-service">{service.replace("HR-HRSD-0", "Service 0").replace(" · ", " — ")}</h2>
          {scenarios
            .filter((s) => s.service === service)
            .map((s) => (
              <button
                key={s.scenario_id}
                className={`catalog-card${s.scenario_id === selectedId ? " is-selected" : ""}`}
                onClick={() => onSelect(s.scenario_id)}
              >
                <span className="catalog-id">{s.scenario_id}</span>
                <span className="catalog-name">{s.name}</span>
                <span className="catalog-meta">
                  <span className="catalog-chain">{s.chain_focus}</span>
                  <span className={`hitl-badge hitl-${s.hitl_mode.toLowerCase()}`}>
                    {s.hitl_mode.replace("_", " ")}
                  </span>
                </span>
              </button>
            ))}
        </section>
      ))}
    </aside>
  );
}
