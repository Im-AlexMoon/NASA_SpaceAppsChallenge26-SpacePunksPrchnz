"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { gasTests, readings, type Reading, type Nearby } from "../lib/content";
import DecisionExport from "./DecisionExport";
import BurnChart from "./BurnChart";
import CoverageMap from "./CoverageMap";
import TierBadge from "./TierBadge";

const { xo2: GX, p_kpa: GP, points } = readings.grid;
const ORDER = ["iss_cabin", "exploration_8p2_34", "lunar_base_upper", "mars_surface_habitat", "spacesuit", "earth_sea_level"];
const SHORT: Record<string, string> = {
  iss_cabin: "ISS cabin", exploration_8p2_34: "Exploration", lunar_base_upper: "Lunar base",
  mars_surface_habitat: "Mars habitat", spacesuit: "Spacesuit", earth_sea_level: "Earth",
};
const nearest = (arr: number[], v: number) => arr.reduce((b, a, i) => (Math.abs(a - v) < Math.abs(arr[b] - v) ? i : b), 0);
const fmt = (v: number) => (v >= 10 || Number.isInteger(v) ? v.toFixed(0) : v.toFixed(1));
const pct = (v: number | null | undefined) => (v == null ? "—" : `${Math.round(v * 100)}%`);
const gravityName = (g: number) => (g === 0 ? "Microgravity" : g === 1 ? "Earth gravity" : g < 0.2 ? "Lunar gravity" : "Martian gravity");

export default function AtmosphereExplorer() {
  const presets = ORDER.map((k) => readings.references.find((r) => r.key === k)!).filter(Boolean);
  const [preset, setPreset] = useState<string | null>("lunar_base_upper");
  const [xi, setXi] = useState(nearest(GX, 0.3));
  const [pi, setPi] = useState(nearest(GP, 70.3));

  useEffect(() => {
    const restore = () => {
      const key = window.location.hash.slice(1);
      const found = readings.references.find((reading) => reading.key === key);
      if (found) {
        setPreset(found.key);
        setXi(nearest(GX, found.inputs.xo2));
        setPi(nearest(GP, found.inputs.p_kpa));
      } else if (/^grid-\d+-\d+$/.test(key)) {
        const [, x, p] = key.split("-").map(Number);
        if (GX[x] != null && GP[p] != null) {
          setPreset(null);
          setXi(x);
          setPi(p);
        }
      }
    };
    const frame = requestAnimationFrame(restore);
    window.addEventListener("hashchange", restore);
    return () => { cancelAnimationFrame(frame); window.removeEventListener("hashchange", restore); };
  }, []);

  const choose = (r: Reading) => {
    setPreset(r.key);
    setXi(nearest(GX, r.inputs.xo2));
    setPi(nearest(GP, r.inputs.p_kpa));
  };
  const ref = preset ? presets.find((r) => r.key === preset) : undefined;
  const xo2 = ref ? ref.inputs.xo2 : GX[xi];
  const p = ref ? ref.inputs.p_kpa : GP[pi];

  const grid = points[pi][xi];
  const prediction = ref?.prediction;
  const median = ref ? prediction?.median_burn_s : grid.median;
  const ci = ref ? prediction?.median_burn_s_90ci : grid.ci;
  const near: Nearby = ref?.nearby ?? grid.nearby;
  const tier = ref?.tier ?? grid.tier;
  const tad = ref ? ref.physics.tad_k : grid.tad;
  const chartSelection = xo2 >= GX[0] && xo2 <= GX.at(-1)! &&
    p >= GP[0] && p <= GP.at(-1)! + 0.1 ? xi : null;
  const horizons = ref ? [
    [30, prediction?.p_still_burning_30s, prediction?.p_still_burning_30s_90ci],
    [60, prediction?.p_still_burning_60s, prediction?.p_still_burning_60s_90ci],
  ] as const : [[30, grid.p30, grid.p30_ci], [60, grid.p60, grid.p60_ci]] as const;

  return (
    <div className="stack">
      <div className="grid-2">
        <section className="panel stack" aria-label="Atmosphere">
          <span className="label">Reference atmospheres</span>
          <div className="presets">
            {presets.map((r) => (
              <button key={r.key} className="preset" aria-pressed={preset === r.key} onClick={() => choose(r)}>
                <span>{SHORT[r.key] ?? r.label}</span>
                <small>{Math.round(r.inputs.xo2 * 100)}% oxygen at {r.inputs.p_kpa.toFixed(1)} kPa</small>
              </button>
            ))}
          </div>
          <div className="field">
            <div className="field-row">
              <label htmlFor="o2">Oxygen</label>
              <output htmlFor="o2" className="num">{(xo2 * 100).toFixed(xo2 < 1 && (xo2 * 100) % 1 ? 1 : 0)}%</output>
            </div>
            <input id="o2" type="range" min={0} max={GX.length - 1} step={1} value={xi}
              style={{ "--fill": `${(xi / (GX.length - 1)) * 100}%` } as React.CSSProperties}
              aria-valuetext={`${Math.round(xo2 * 100)} percent oxygen`}
              onChange={(e) => { setPreset(null); setXi(+e.target.value); }} />
          </div>
          <div className="field">
            <div className="field-row">
              <label htmlFor="p">Pressure</label>
              <output htmlFor="p" className="num">{p.toFixed(p < 60 ? 1 : 0)} kPa</output>
            </div>
            <input id="p" type="range" min={0} max={GP.length - 1} step={1} value={pi}
              style={{ "--fill": `${(pi / (GP.length - 1)) * 100}%` } as React.CSSProperties}
              aria-valuetext={`${p} kilopascals`}
              onChange={(e) => { setPreset(null); setPi(+e.target.value); }} />
          </div>
          <div className="stats" style={{ gridTemplateColumns: "repeat(2, minmax(0, 1fr))" }}>
            <div><span className="label">O₂ partial pressure</span><strong className="num">{(xo2 * p).toFixed(1)} kPa</strong></div>
            <div><span className="label">Flame temp. (calc.)</span><strong className="num">{tad ? `${Math.round(tad)} K` : "—"}</strong></div>
          </div>
        </section>

        <section className="panel reading" aria-live="polite" aria-label="Reading">
          <div className="reading-top">
            <TierBadge tier={tier} />
            <span className="label">Microgravity model</span>
          </div>
          <div className="stack" style={{ gap: 8 }}>
            <strong>Nearby CFI-G tests</strong>
            {near.n_tests === 0 ? <p>No tests fall inside the selected atmosphere window.</p> : <>
              <p>{near.n_tests} tests across {near.n_days} days. {near.n_ignited} of {near.n_known_ignition} tests with a known outcome ignited.</p>
              <p>Fuel composition: {Object.entries(near.fuel_counts).map(([fuel, count]) => count + " " + fuel).join(", ")}.
                {" "}{near.same_fuel_tests} used the reference fuel.</p>
              <p>{near.n_self_extinguished} flames went out on their own and {near.n_flow_cut} were still burning at fuel cutoff.</p>
              {near.median_burn_s_self_extinguished != null && <p>Observed median among self-extinguished flames: {fmt(near.median_burn_s_self_extinguished)} s.</p>}
              {tier !== "A" && <p>The nearby tests do not meet the coverage threshold.</p>}
            </>}
          </div>
          {median == null || !ci ? <div className="noread">
            <strong>No model reading</strong>
            <p className="muted">The conditions fall outside the supported model domain.</p>
            <Link className="link" href="/gaps">See which data are missing</Link>
          </div> : <div className="stack" style={{ gap: 8 }}>
            <span className="label">Model median for the reference propane flame</span>
            <div className="big num">{fmt(median)}<small>s</small></div>
            <p className="muted">The 90% estimation interval is {fmt(ci[0])} to {fmt(ci[1])} s.</p>
            <p>Estimated chance that an already-lit flame is still burning:</p>
            <ul>{horizons.map(([t, value, range]) => value != null && range &&
              <li key={t}>At {t} s: {pct(value)} with a 90% interval of {pct(range[0])} to {pct(range[1])}.</li>
            )}</ul>
          </div>}
          {ref?.gravity_effect && <div className="banner" role="note">
            <span>{gravityName(ref.gravity_g)}. {ref.gravity_effect.note}</span>
          </div>}
          <p className="muted">The estimate describes a spherical laboratory flame. It does not establish a fire response time.</p>
        </section>
      </div>

      <DecisionExport scenario={ref?.label ?? "Custom atmosphere"} selection={ref?.key ?? ["grid", xi, pi].join("-")}
        rows={[
          ["Oxygen mole fraction", String(xo2)],
          ["Total pressure (kPa)", String(p)],
          ["Nearby CFI-G tests", String(near.n_tests)],
          ["Operations days", String(near.n_days)],
          ["Tests using propane", String(near.same_fuel_tests)],
          ["Ignitions with known outcomes", near.n_ignited + " of " + near.n_known_ignition],
          ["Autoextinctions", String(near.n_self_extinguished)],
          ["Fuel cutoffs", String(near.n_flow_cut)],
          ["Observed median among autoextinctions (s)", String(near.median_burn_s_self_extinguished ?? "Unavailable")],
          ["Model median in microgravity (s)", String(median ?? "Unavailable")],
          ["Estimation interval, 90% (s)", ci?.join(" to ") ?? "Unavailable"],
          ["Gravity", ref?.gravity_effect?.note ?? "Microgravity"],
          ["Sources", "NASA PSI-159; M-01 v2; findings F-03 and F-04"],
        ]} />

      <section className="panel stack" aria-label="Burn time against oxygen">
        <div className="reading-top">
          <h2 style={{ fontSize: 22, letterSpacing: "-0.015em" }}>Burn time against oxygen at {GP[pi]} kPa</h2>
          <span className="label">M-01 v2 in microgravity</span>
        </div>
        <BurnChart xo2={GX} row={points[pi]} p={GP[pi]} selected={chartSelection} tests={gasTests} />
      </section>

      <section className="panel stack" aria-label="Where the evidence is">
        <div className="reading-top">
          <h2 style={{ fontSize: 22, letterSpacing: "-0.015em" }}>Where the evidence is</h2>
          <span className="label">Normal flames on the ISS</span>
        </div>
        <CoverageMap focus={{ xo2, p }} wide />
      </section>
    </div>
  );
}
