"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { gasTests, readings, type Reading, type Nearby } from "../lib/content";
import DecisionExport from "./DecisionExport";
import BurnChart from "./BurnChart";
import CoverageMap from "./CoverageMap";
import TierBadge from "./TierBadge";
import css from "./AtmosphereExplorer.module.css";

const { xo2: GX, p_kpa: GP, points } = readings.grid;
const ORDER = ["iss_cabin", "exploration_8p2_34", "lunar_base_upper", "mars_surface_habitat", "spacesuit", "earth_sea_level"];
const SHORT: Record<string, string> = {
  iss_cabin: "ISS cabin", exploration_8p2_34: "Exploration", lunar_base_upper: "Lunar base",
  mars_surface_habitat: "Mars habitat", spacesuit: "Spacesuit", earth_sea_level: "Earth",
};
// caveats every reference reading carries; reused for custom grid atmospheres
const SHARED_CAVEATS = readings.references
  .map((r) => r.caveats)
  .reduce<string[]>((acc, list, i) => (i === 0 ? [...list] : acc.filter((c) => list.includes(c))), []);
const nearest = (arr: number[], v: number) => arr.reduce((b, a, i) => (Math.abs(a - v) < Math.abs(arr[b] - v) ? i : b), 0);
const fmt = (v: number) => (v >= 10 || Number.isInteger(v) ? v.toFixed(0) : v.toFixed(1));
const pct = (v: number | null | undefined) => (v == null ? "—" : `${Math.round(v * 100)}%`);
const gravityName = (g: number) => (g === 0 ? "Microgravity" : g === 1 ? "Earth gravity" : g < 0.2 ? "Lunar gravity" : "Martian gravity");

export default function AtmosphereExplorer() {
  const presets = ORDER.map((k) => readings.references.find((r) => r.key === k)!).filter(Boolean);
  const [preset, setPreset] = useState<string | null>("lunar_base_upper");
  const [xi, setXi] = useState(nearest(GX, 0.3));
  const [pi, setPi] = useState(nearest(GP, 70.3));
  const segRef = useRef<HTMLDivElement>(null);

  // keep the active preset visible when the segmented row scrolls sideways on narrow screens
  useEffect(() => {
    const row = segRef.current;
    const btn = row?.querySelector<HTMLElement>('[aria-pressed="true"]');
    if (!row || !btn) return;
    const left = btn.offsetLeft - row.offsetLeft;
    if (left < row.scrollLeft || left + btn.offsetWidth > row.scrollLeft + row.clientWidth) {
      row.scrollLeft = left - (row.clientWidth - btn.offsetWidth) / 2;
    }
  }, [preset]);

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
  const pickFromMap = (x: number, kpa: number) => {
    setPreset(null);
    setXi(nearest(GX, x));
    setPi(nearest(GP, kpa));
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
  const gravity = ref && ref.gravity_g !== 0 ? ref.gravity_g : null;
  const partialGravity = gravity != null && gravity !== 1;
  const limits = [...new Set([
    ...(near.n_tests === 0 ? ["There are no tests in the selected atmosphere window."] : []),
    ...(tier !== "A" ? ["The nearby tests do not meet the coverage threshold."] : []),
    ...(ref?.caveats ?? SHARED_CAVEATS),
  ])];

  return (
    <div className="stack">
      <div ref={segRef} className={`seg ${css.presets}`} role="group" aria-label="Reference atmospheres">
        {presets.map((r) => (
          <button key={r.key} type="button" aria-pressed={preset === r.key} onClick={() => choose(r)}
            title={`${r.label}: ${Math.round(r.inputs.xo2 * 100)}% oxygen at ${r.inputs.p_kpa.toFixed(1)} kPa`}>
            {SHORT[r.key] ?? r.label}
          </button>
        ))}
      </div>

      <div className="grid-2">
        <section className="panel stack" aria-label="Atmosphere">
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
          <div>
            <details className={`more ${css.details}`}>
              <summary>Physics</summary>
              <div className={css.kv}>
                <div><span className="label">O₂ partial pressure</span><strong className="num">{(xo2 * p).toFixed(1)} kPa</strong></div>
                <div><span className="label">Flame temp. (calc.)</span><strong className="num">{tad ? `${Math.round(tad)} K` : "—"}</strong></div>
              </div>
            </details>
            <details className={`more ${css.details}`}>
              <summary>Nearby CFI-G tests</summary>
              {near.n_tests === 0 ? <ul><li>No tests fall inside the selected atmosphere window.</li></ul> : <ul>
                <li>{near.n_tests} tests across {near.n_days} days; {near.n_ignited} of {near.n_known_ignition} with a known outcome ignited.</li>
                <li>Fuels: {Object.entries(near.fuel_counts).map(([fuel, count]) => count + " " + fuel).join(", ")}; {near.same_fuel_tests} used the reference fuel.</li>
                <li>{near.n_self_extinguished} went out on their own; {near.n_flow_cut} were still burning at fuel cutoff.</li>
                {near.median_burn_s_self_extinguished != null && <li>Observed median among self-extinguished flames: {fmt(near.median_burn_s_self_extinguished)} s.</li>}
              </ul>}
            </details>
          </div>
        </section>

        <section className={`panel ${css.reading}`} aria-live="polite" aria-label="Reading">
          <div className="reading-top">
            <TierBadge tier={tier} />
            <span className="label">Microgravity model</span>
          </div>
          {median == null || !ci ? <div className="noread">
            <strong>No model reading</strong>
            <p className="muted">The conditions fall outside the supported model domain.</p>
            <Link className="link" href="/gaps">See which data are missing</Link>
          </div> : <>
            <div>
              <span className="label">Median burn time, reference propane flame</span>
              <div className="big num">{fmt(median)}<small>s</small></div>
            </div>
            <p className={css.context}>
              90% interval <b className="num">{fmt(ci[0])}–{fmt(ci[1])} s</b> · <b className="num">{near.n_tests}</b> nearby {near.n_tests === 1 ? "test" : "tests"}
            </p>
            <div className={css.meter} role="group" aria-label="Chance an already-lit flame is still burning">
              <span className="label">Still burning</span>
              {horizons.map(([t, value, range]) => value != null && range && (
                <div key={t} className={css.meterRow}
                  aria-label={`At ${t} seconds: ${pct(value)}, 90% interval ${pct(range[0])} to ${pct(range[1])}`}>
                  <span>{t} s</span>
                  <div className={css.track} title={`90% interval ${pct(range[0])} to ${pct(range[1])}`}>
                    <i className={css.band} style={{ left: `${range[0] * 100}%`, width: `${(range[1] - range[0]) * 100}%` }} />
                    <i className={css.fill} style={{ transform: `scaleX(${value})` }} />
                  </div>
                  <strong>{pct(value)}</strong>
                </div>
              ))}
            </div>
          </>}
          {gravity != null && ref?.gravity_effect && <div className="banner" role="note">
            <span>
              {gravityName(gravity)}. {ref.gravity_effect.note}
              {partialGravity && " PSI has no partial-gravity data, so treat this reading as a bound or extrapolation, not a prediction."}
            </span>
          </div>}
          <details className={`more ${css.details}`}>
            <summary>Limits</summary>
            <ul>{limits.map((line) => <li key={line}>{line}</li>)}</ul>
          </details>
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
        <p className={css.hint}>Click a test or any point on the map to move the sliders to the nearest model grid point.</p>
        <CoverageMap focus={{ xo2, p }} wide onPick={pickFromMap} />
      </section>
    </div>
  );
}
