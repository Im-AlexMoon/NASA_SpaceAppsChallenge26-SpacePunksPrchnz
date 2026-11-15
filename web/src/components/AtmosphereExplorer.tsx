"use client";
import Link from "next/link";
import { useState } from "react";
import { gasTests, readings, type Reading, type Tier } from "../lib/content";
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
const fmt = (v: number) => (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(0) : v.toFixed(1));
const pct = (v: number | null | undefined) => (v == null ? "—" : `${Math.round(v * 100)}%`);
const gravityName = (g: number) => (g === 0 ? "Microgravity" : g === 1 ? "Earth gravity" : g < 0.2 ? "Lunar gravity" : "Martian gravity");

type View = {
  tier: Tier; median: number | null; ci: [number, number] | null; p30: number | null; p60: number | null;
  nNear: number; nDays: number | null; obs: number | null; tad: number | null; gravity: number; reading?: Reading;
};

export default function AtmosphereExplorer() {
  const presets = ORDER.map((k) => readings.references.find((r) => r.key === k)!).filter(Boolean);
  const [preset, setPreset] = useState<string | null>("lunar_base_upper");
  const [xi, setXi] = useState(nearest(GX, 0.3));
  const [pi, setPi] = useState(nearest(GP, 70.3));

  const choose = (r: Reading) => {
    setPreset(r.key);
    setXi(nearest(GX, r.inputs.xo2));
    setPi(nearest(GP, r.inputs.p_kpa));
  };
  const ref = preset ? presets.find((r) => r.key === preset) : undefined;
  const xo2 = ref ? ref.inputs.xo2 : GX[xi];
  const p = ref ? ref.inputs.p_kpa : GP[pi];

  const view: View = (() => {
    if (ref) {
      const pr = ref.prediction;
      return {
        tier: ref.tier, median: pr?.median_burn_s ?? null, ci: pr?.median_burn_s_90ci ?? null,
        p30: pr?.p_still_burning_30s ?? null, p60: pr?.p_still_burning_60s ?? null, nNear: ref.nearby.n_tests,
        nDays: ref.nearby.n_days, obs: ref.nearby.median_burn_s_self_extinguished, tad: ref.physics.tad_k,
        gravity: ref.gravity_g, reading: ref,
      };
    }
    const g = points[pi][xi];
    return { tier: g.tier, median: g.median, ci: g.ci, p30: g.p30, p60: g.p60, nNear: g.n_near, nDays: null, obs: g.obs_median, tad: g.tad, gravity: 0 };
  })();

  const showObserved = view.tier === "A" && view.obs != null;
  const caveats = ref?.caveats ?? [
    ...(view.tier === "B" ? ["No real test near this atmosphere: the value is an interpolation of the model."] : []),
    "Microgravity only: PSI has no partial-gravity combustion data.",
    "Burn duration of a laboratory spherical gas flame, not the time available to respond to a fire.",
    "Tad is calculated (chemical equilibrium), not measured.",
  ];

  return (
    <div className="stack">
      <div className="grid-2">
        <section className="panel stack" aria-label="Atmosphere">
          <span className="label">Reference atmospheres</span>
          <div className="presets">
            {presets.map((r) => (
              <button key={r.key} className="preset" aria-pressed={preset === r.key} onClick={() => choose(r)}>
                <span>{SHORT[r.key] ?? r.label}</span>
                <small>{Math.round(r.inputs.xo2 * 100)}% · {r.inputs.p_kpa.toFixed(r.inputs.p_kpa < 60 ? 1 : 0)} kPa</small>
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
              aria-valuetext={`${Math.round(GX[xi] * 100)} percent oxygen`}
              onChange={(e) => { setPreset(null); setXi(+e.target.value); }} />
          </div>
          <div className="field">
            <div className="field-row">
              <label htmlFor="p">Pressure</label>
              <output htmlFor="p" className="num">{p.toFixed(p < 60 ? 1 : 0)} kPa</output>
            </div>
            <input id="p" type="range" min={0} max={GP.length - 1} step={1} value={pi}
              style={{ "--fill": `${(pi / (GP.length - 1)) * 100}%` } as React.CSSProperties}
              aria-valuetext={`${GP[pi]} kilopascals`}
              onChange={(e) => { setPreset(null); setPi(+e.target.value); }} />
          </div>
          <div className="stats" style={{ gridTemplateColumns: "1fr 1fr" }}>
            <div><span className="label">O₂ partial pressure</span><strong className="num">{(xo2 * p).toFixed(1)} kPa</strong></div>
            <div><span className="label">Flame temp. (calc.)</span><strong className="num">{view.tad ? `${Math.round(view.tad)} K` : "—"}</strong></div>
          </div>
        </section>

        <section className="panel reading" aria-live="polite" aria-label="Reading">
          <div className="reading-top">
            <TierBadge tier={view.tier} />
            <span className="label">{gravityName(view.gravity)} · propane burner</span>
          </div>

          {view.tier === "C" || (view.median == null && !showObserved) ? (
            <div className="noread">
              <strong>No reading</strong>
              <p className="muted">
                {ref?.reason ? `This atmosphere is ${ref.reason}.` : "Outside the tested range of the physical inputs, or too far from any tested flame."}{" "}
                FlameSafe shows no number where NASA has no evidence.
              </p>
              <Link className="link" href="/gaps">See the missing experiment</Link>
            </div>
          ) : (
            <div className="stack" style={{ gap: 8 }}>
              <span className="label">{showObserved ? "Observed median burn" : "Model median burn"}</span>
              <div className="big num">{fmt(showObserved ? view.obs! : view.median!)}<small>s</small></div>
              <p className="muted">
                {showObserved
                  ? `${view.nNear} real tests nearby${view.nDays ? ` from ${view.nDays} days` : ""}. Model: ${fmt(view.median!)} s (90% interval ${fmt(view.ci![0])}–${fmt(view.ci![1])}).`
                  : view.tier === "A"
                    ? `${view.nNear} real tests nearby. 90% interval ${fmt(view.ci![0])}–${fmt(view.ci![1])} s.`
                    : `90% interval ${fmt(view.ci![0])}–${fmt(view.ci![1])} s. No real test near this atmosphere.`}
              </p>
            </div>
          )}

          {view.tier !== "C" && view.p30 != null && (
            <div className="stats">
              <div><span className="label">Still burning at 30 s</span><strong className="num">{pct(view.p30)}</strong></div>
              <div><span className="label">Still burning at 60 s</span><strong className="num">{pct(view.p60)}</strong></div>
              <div><span className="label">Tests nearby</span><strong className="num">{view.nNear}</strong></div>
            </div>
          )}

          {view.gravity > 0 && ref?.gravity_effect && (
            <div className="banner" role="note">
              <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5 15 14H1z" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" /><path d="M8 6v4M8 11.6v.4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" /></svg>
              <span>
                No flame data exist at {gravityName(view.gravity).toLowerCase()}. Buoyancy feeds the flame, so the microgravity
                value is likely a lower bound on how long it persists.
              </span>
            </div>
          )}
          <ul className="caveats">{caveats.map((c) => <li key={c}>{c}</li>)}</ul>
        </section>
      </div>

      <section className="panel stack" aria-label="Burn time against oxygen">
        <div className="reading-top">
          <h2 style={{ fontSize: 22, letterSpacing: "-0.015em" }}>Burn time against oxygen at {GP[pi]} kPa</h2>
          <span className="label">M-01 v2 · microgravity</span>
        </div>
        <BurnChart xo2={GX} row={points[pi]} p={GP[pi]} selected={xi} tests={gasTests} />
      </section>

      <section className="panel stack" aria-label="Where the evidence is">
        <div className="reading-top">
          <h2 style={{ fontSize: 22, letterSpacing: "-0.015em" }}>Where the evidence is</h2>
          <span className="label">Normal flames · ISS</span>
        </div>
        <CoverageMap focus={{ xo2, p }} wide />
      </section>
    </div>
  );
}
