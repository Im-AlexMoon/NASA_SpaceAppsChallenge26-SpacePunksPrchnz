"use client";
import { useEffect, useMemo, useState } from "react";
import { dashboard, gasTests, meta } from "../../lib/content";
import { CoverageHeatmap, FuelBars, OutcomeBars, ScatterChart, SurvivalChart } from "./charts";
import { Baselines, Calibration, FindingsStrip, Forest, Quality, RankingTop, Research } from "./evidence";
import { applyFilters, BANDS, fmtS, km, median, NO_FILTERS, P_BANDS, P_LABEL, Panel, type Filters } from "./kit";

const FUELS = [...new Set(gasTests.map((t) => t.fuel))].sort();
const KEYS = Object.keys(NO_FILTERS) as (keyof Filters)[];

export default function Dashboard() {
  const [f, setF] = useState<Filters>(NO_FILTERS);

  // Shareable view: filters live in the URL query.
  useEffect(() => {
    const restore = () => {
      const q = new URLSearchParams(window.location.search);
      setF(Object.fromEntries(KEYS.map((k) => [k, q.get(k) ?? "all"])) as Filters);
    };
    restore();
  }, []);
  const set = (patch: Partial<Filters>) => {
    const next = { ...f, ...patch };
    setF(next);
    const q = new URLSearchParams(KEYS.filter((k) => next[k] !== "all").map((k) => [k, next[k]]));
    window.history.replaceState(null, "", q.size ? `?${q}` : window.location.pathname);
  };

  const rows = useMemo(() => applyFilters(gasTests, f), [f]);
  const ignited = rows.filter((t) => t.ignition_outcome === "yes").length;
  const known = rows.filter((t) => t.ignition_outcome != null).length;
  const selfOut = rows.filter((t) => t.extinction_mode === "self_extinguished" && t.burn_time_s != null).map((t) => t.burn_time_s!);
  const surv = km(rows);
  const active = KEYS.filter((k) => f[k] !== "all").length;
  const m = dashboard.model;

  const select = (key: keyof Filters, label: string, options: [string, string][]) => (
    <label>
      <span className="label">{label}</span>
      <select value={f[key]} onChange={(e) => set({ [key]: e.target.value })}>
        <option value="all">All</option>
        {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
      </select>
    </label>
  );

  return (
    <div className="dash">
      <div className="dash-filters" role="group" aria-label="Filters">
        {select("campaign", "Campaign", [["CFI-G", "CFI-G"], ["Flame Design", "Flame Design"]])}
        {select("flame", "Flame", [["normal", "Normal"], ["inverse", "Inverse"]])}
        {select("fuel", "Fuel", FUELS.map((x) => [x, x]))}
        {select("o2", "Oxygen", BANDS.map((b) => [b.key, b.label.replace("O₂ ", "")]))}
        {select("p", "Pressure", Object.keys(P_BANDS).map((k) => [k, P_LABEL[k]]))}
        <button type="button" className="btn btn-ghost" disabled={!active} onClick={() => set(NO_FILTERS)}>Clear{active ? ` (${active})` : ""}</button>
      </div>

      <div className="kpis">
        <div className="kpi"><strong className="num">{rows.length}</strong><span>Flame tests selected</span><span className="num small">of {meta.counts.gas_flame_tests}</span></div>
        <div className="kpi"><strong className="num">{known ? Math.round((100 * ignited) / known) : 0}%</strong><span>Ignited</span><span className="num small">{ignited} of {known} with a recorded outcome</span></div>
        <div className="kpi"><strong className="num">{fmtS(median(selfOut))}<small> s</small></strong><span>Median burn, flames that went out alone</span><span className="num small">n = {selfOut.length}</span></div>
        <div className="kpi"><strong className="num">{surv.median == null ? "> 50%" : `${fmtS(surv.median)} s`}</strong><span>{surv.median == null ? "Still burning at the last recorded time" : "Half the flames had gone out by"}</span><span className="num small">Kaplan-Meier, n = {surv.n}</span></div>
        {m && <div className="kpi"><strong className="num">{m.metrics.oof_c_index.toFixed(2)}</strong><span>Model ranking accuracy (C-index)</span><span className="num small">{m.cohort.n} flames, {m.cohort.days} days held out one by one</span></div>}
      </div>

      <h2 className="dash-h">What the flames did</h2>
      <div className="dash-grid">
        <Panel id="p-surv" span={7} title="How many flames are still burning"
          note="Each step is a flame going out on its own; flames whose fuel flow was cut count until the cut. More oxygen keeps flames alight far longer. Durations come from CFI-G: Flame Design tests have no burn time in the published test table.">
          <SurvivalChart rows={rows} />
        </Panel>
        <Panel id="p-out" span={5} title="How each test ended" note="Missing records stay visible as their own category, never as zero.">
          <OutcomeBars rows={rows} />
        </Panel>
        <Panel id="p-scatter" span={7} title="Burn duration against oxygen" note="Hover a point for its test. Filled points went out on their own. CFI-G only, for the same reason.">
          <ScatterChart rows={rows} />
        </Panel>
        <Panel id="p-fuel" span={5} title="Tests by fuel" note="Click a fuel to filter every chart.">
          <FuelBars rows={applyFilters(gasTests, { ...f, fuel: "all" })} active={f.fuel} onPick={(fuel) => set({ fuel })} />
        </Panel>
        <Panel id="p-heat" span={12} title="Where the tests are" note="Click a cell to narrow the dashboard to its oxygen and pressure band. The lunar-base reference sits in an empty region.">
          <CoverageHeatmap rows={applyFilters(gasTests, { ...f, o2: "all", p: "all" })} onPick={(x, p) => set({
            o2: BANDS.find((b) => b.test(x))!.key,
            p: Object.keys(P_BANDS).find((k) => p >= P_BANDS[k][0] && p < P_BANDS[k][1]) ?? "all",
          })} />
        </Panel>
      </div>

      <h2 className="dash-h">How sure we are</h2>
      <div className="dash-grid">
        <Panel id="p-forest" span={7} title="Effects with 95% intervals"><Forest /></Panel>
        <Panel id="p-cal" span={5} title="Do predicted chances match reality?"
          note="Out of sample, by thirds of predicted probability. Points near the dashed line mean honest probabilities.">
          <Calibration />
          <div className="kpis" style={{ marginTop: 14 }}>
            <div className="kpi"><strong className="num">{dashboard.transfer.c_index}</strong><span>C-index on an unseen fuel and campaign</span><span className="num small">95% {dashboard.transfer.c_index_ci95.join("–")}</span></div>
            <div className="kpi"><strong className="num">{dashboard.transfer.slope}</strong><span>Calibration slope there (1 is ideal)</span><span className="num small">95% {dashboard.transfer.slope_ci95.join("–")}</span></div>
          </div>
        </Panel>
        <Panel id="p-base" span={5} title="Better than simpler models" note={dashboard.baselines.note}><Baselines /></Panel>
        <Panel id="p-qual" span={7} title="Checks on the data itself"><Quality /></Panel>
        <Panel id="p-res" span={12} title="Hypotheses we tested, kept and ruled out"><Research /></Panel>
      </div>

      <h2 className="dash-h">What it means</h2>
      <div className="dash-grid">
        <Panel id="p-find" span={7} title="Reviewed findings"><FindingsStrip /></Panel>
        <Panel id="p-rank" span={5} title="Most useful investigations" note="Weighted score across seven criteria, from configs/ranking.yaml."><RankingTop /></Panel>
      </div>
      <p className="small">Microgravity data only: no flame tests exist at lunar or Martian gravity. Evidence version {meta.build_id}.</p>
    </div>
  );
}
