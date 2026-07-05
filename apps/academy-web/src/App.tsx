import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { Catalog } from "./components/Catalog";
import { RunConsole } from "./components/RunConsole";
import type { ScenarioDetail, ScenarioSummary } from "./types";

export default function App() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ScenarioDetail | null>(null);
  const [apiDown, setApiDown] = useState<string | null>(null);

  useEffect(() => {
    api
      .listScenarios()
      .then((list) => {
        setScenarios(list);
        setSelectedId((current) => current ?? list[0]?.scenario_id ?? null);
      })
      .catch((err: Error) => setApiDown(err.message));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setDetail(null);
    api.getScenario(selectedId).then(setDetail).catch((err: Error) => setApiDown(err.message));
  }, [selectedId]);

  const today = useMemo(
    () =>
      new Date().toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
    [],
  );

  return (
    <>
      <header className="topbar">
        <span className="wordmark">
          Deloitte<span className="wordmark-dot">.</span>
        </span>
        <span className="topbar-right">AI Academy · Tier-0 Operations Console · {today}</span>
      </header>
      <div className="page">
        <div className="masthead">
          <div className="masthead-kicker">HR Service Delivery</div>
          <h1 className="masthead-title">
            Scenario Chain Console<span className="title-dot">.</span>
          </h1>
          <div className="masthead-sub">
            <span>
              Nine scenario chains · Sequential MAF pattern · one HITL gate at step 16 · every
              step ledgered
            </span>
            <span className="masthead-figures">All figures are synthetic reference figures</span>
          </div>
        </div>

      {apiDown ? (
        <div className="api-down">
          <strong>academy-api unreachable.</strong> Start it with{" "}
          <code>npm run dev:api</code> (port 8000), then reload. <em>{apiDown}</em>
        </div>
      ) : (
        <div className="layout">
          <Catalog scenarios={scenarios} selectedId={selectedId} onSelect={setSelectedId} />
          <RunConsole detail={detail} />
        </div>
      )}

        <footer className="colophon">
          <span>
            Chain: Assess → Classify → Quantify → Decide → <strong>★ HITL (16)</strong> → Act →
            Learn
          </span>
          <span>docs/07 · test on the Deloitte tenant · deploy at the customer site</span>
        </footer>
      </div>
    </>
  );
}
