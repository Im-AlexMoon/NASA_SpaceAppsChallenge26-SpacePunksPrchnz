"use client";

import { useMemo, useRef, useState, type KeyboardEvent, type MouseEvent } from "react";
import { gasTests, type GasTest } from "../lib/content";
import css from "./AtmosphereExplorer.module.css";

// Where NASA has flame data: every normal spherical flame tested on the ISS, by O2 mole fraction and total pressure.
const M = { l: 52, r: 16, t: 16, b: 40 };
const X0 = 0.14, X1 = 0.44, P0 = 40, P1 = 340;
const r2 = (v: number) => Math.round(v * 100) / 100; // identical server and client markup

const TARGETS = [
  { key: "iss", label: "ISS cabin", xo2: 0.21, p: 101.3 },
  { key: "exploration", label: "Exploration", xo2: 0.34, p: 56.5 },
  { key: "lunar", label: "Lunar base", xo2: 0.3, p: 70.3 },
];

const outcome = (t: GasTest) => {
  if (t.ignition_outcome === "no") return "Did not ignite";
  if (t.ignition_outcome === "flash") return "Flash, no sustained flame";
  if (t.extinction_mode === "self_extinguished") return "Went out on its own";
  if (t.extinction_mode === "flow_terminated") return "Burning at fuel cutoff";
  return t.ignition_outcome === "yes" ? "Ignited" : "Outcome not recorded";
};
const describe = (t: GasTest) =>
  `${t.campaign} test ${t.test_id}, ${t.fuel}, ${(t.xo2! * 100).toFixed(1)}% oxygen, ${t.p_kpa!.toFixed(0)} kPa, ${outcome(t)}` +
  (t.burn_time_s != null ? `, burned ${t.burn_time_s} s` : "");

type Props = {
  focus?: { xo2: number; p: number };
  compact?: boolean;
  wide?: boolean;
  /** Opt-in interactivity: tooltips, legend highlight, keyboard focus, and click-to-pick (oxygen fraction, kPa). */
  onPick?: (xo2: number, p: number) => void;
};

export default function CoverageMap({ focus, compact = false, wide = false, onPick }: Props) {
  const W = wide ? 1000 : 640, H = wide ? 420 : 400;
  const x = (v: number) => r2(M.l + ((v - X0) / (X1 - X0)) * (W - M.l - M.r));
  const y = (p: number) => r2(H - M.b - (Math.log(p / P0) / Math.log(P1 / P0)) * (H - M.t - M.b));
  const [campaign, setCampaign] = useState("");
  const [fuel, setFuel] = useState("");
  const [geometry, setGeometry] = useState("normal");
  const [hasDuration, setHasDuration] = useState(false);
  const pts = gasTests.filter((test) =>
    (geometry === "" || test.flame_type === geometry) && (!campaign || test.campaign === campaign) &&
    (!fuel || test.fuel === fuel) && (!hasDuration || test.burn_time_s != null) &&
    test.xo2 != null && test.xo2 >= X0 && test.xo2 <= X1 &&
    test.p_kpa != null && test.p_kpa >= P0 && test.p_kpa <= P1,
  );
  const lunar = TARGETS[2];
  const interactive = !!onPick;
  const svgRef = useRef<SVGSVGElement>(null);
  const [hover, setHover] = useState<number | null>(null);
  const [active, setActive] = useState<number | null>(null);
  const [highlight, setHighlight] = useState<string | null>(null);
  // keyboard order: left to right by oxygen, then bottom to top by pressure
  const order = useMemo(() => pts.map((_, i) => i).sort((a, b) => pts[a].xo2! - pts[b].xo2! || pts[a].p_kpa! - pts[b].p_kpa!), [pts]);
  const pick = (t: GasTest) => onPick?.(t.xo2!, t.p_kpa!);
  const pickArea = (event: MouseEvent<SVGSVGElement>) => {
    const box = svgRef.current?.getBoundingClientRect();
    if (!box || !onPick) return;
    const vx = ((event.clientX - box.left) / box.width) * W, vy = ((event.clientY - box.top) / box.height) * H;
    if (vx < M.l || vx > W - M.r || vy < M.t || vy > H - M.b) return;
    onPick(X0 + ((vx - M.l) / (W - M.l - M.r)) * (X1 - X0), P0 * Math.exp(((H - M.b - vy) / (H - M.t - M.b)) * Math.log(P1 / P0)));
  };
  const onKey = (event: KeyboardEvent<SVGCircleElement>, i: number) => {
    const at = order.indexOf(i);
    const step: Record<string, number> = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1, Home: -order.length, End: order.length };
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); pick(pts[i]); return; }
    if (!(event.key in step)) return;
    event.preventDefault();
    const next = order[Math.max(0, Math.min(order.length - 1, at + step[event.key]))];
    setActive(next);
    setHover(next);
    (svgRef.current?.querySelector(`[data-i="${next}"]`) as SVGCircleElement | null)?.focus();
  };
  const tip = interactive && hover != null ? pts[hover] : undefined;
  const tabStop = active != null && active < pts.length ? active : order[0];
  const inPlot = (f: { xo2: number; p: number }) => f.xo2 >= X0 && f.xo2 <= X1 && f.p >= P0 && f.p <= P1;
  return (
    <figure className={wide ? "coverage coverage-wide" : "coverage"} style={{ margin: 0 }}>
      {wide && <div className="actions" aria-label="Map filters">
        <label>Campaign <select value={campaign} onChange={(event) => setCampaign(event.target.value)}>
          <option value="">All campaigns</option><option>CFI-G</option><option>Flame Design</option>
        </select></label>
        <label>Fuel <select value={fuel} onChange={(event) => setFuel(event.target.value)}>
          <option value="">All fuels</option>
          {[...new Set(gasTests.map((test) => test.fuel).filter(Boolean))].sort().map((name) => <option key={name}>{name}</option>)}
        </select></label>
        <label>Geometry <select value={geometry} onChange={(event) => setGeometry(event.target.value)}>
          <option value="">All geometries</option><option value="normal">Normal</option><option value="inverse">Inverse</option>
        </select></label>
        <label><input type="checkbox" checked={hasDuration} onChange={(event) => setHasDuration(event.target.checked)} /> Recorded duration only</label>
      </div>}
      <div className={css.plot}>
      <svg ref={svgRef} className="chart" viewBox={`0 0 ${W} ${H}`} role={interactive ? "group" : "img"}
        aria-label={interactive
          ? "Gas-flame tests by oxygen fraction and pressure. Use arrow keys to move between tests and Enter to set the sliders to a test."
          : "Gas-flame tests by oxygen fraction and pressure, with the lunar reference window marked"}
        onClick={interactive ? pickArea : undefined} onMouseLeave={interactive ? () => setHover(null) : undefined}>
        <g className="grid">
          {[50, 70, 100, 200, 300].map((p) => (
            <g key={p}>
              <line x1={M.l} x2={W - M.r} y1={y(p)} y2={y(p)} />
              <text x={M.l - 10} y={y(p) + 4} textAnchor="end">{p}</text>
            </g>
          ))}
          {[0.15, 0.2, 0.25, 0.3, 0.35, 0.4].map((v) => (
            <text key={v} x={x(v)} y={H - M.b + 22} textAnchor="middle">{Math.round(v * 100)}%</text>
          ))}
        </g>
        <text x={M.l} y={H - 4} style={{ fill: "var(--ink-3)" }}>Oxygen mole fraction</text>
        <text x={12} y={M.t + 8} transform={`rotate(-90 12 ${M.t + 8})`} textAnchor="end">kPa</text>
        {/* CFI-G never tested normal flames between 24 % and 33 % O2 */}
        <rect x={x(0.24)} y={M.t} width={x(0.33) - x(0.24)} height={H - M.t - M.b} fill="rgba(255,255,255,0.025)" />
        {/* evidence window of the lunar-base reading: +-0.05 O2, +-25 % pressure */}
        <rect
          x={x(lunar.xo2 - 0.05)} y={y(lunar.p * 1.25)} width={x(lunar.xo2 + 0.05) - x(lunar.xo2 - 0.05)} height={y(lunar.p * 0.75) - y(lunar.p * 1.25)}
          fill="rgba(255,176,74,0.06)" stroke="var(--soot)" strokeDasharray="4 4" rx="6"
        />
        {pts.map((t, i) => interactive ? (
          <circle key={t.psi_id + t.test_id + i} data-i={i} className={`${css.point} ${highlight && t.campaign !== highlight ? css.dim : ""}`}
            cx={x(t.xo2!)} cy={y(t.p_kpa!)} r={hover === i ? 6 : 4.5} fill={t.campaign === "CFI-G" ? "var(--c1)" : "var(--c2)"} stroke="var(--bg)" strokeWidth={1.5}
            tabIndex={i === tabStop ? 0 : -1} role="button" aria-label={describe(t)}
            onMouseEnter={() => setHover(i)} onFocus={() => { setActive(i); setHover(i); }} onBlur={() => setHover(null)}
            onClick={(event) => { event.stopPropagation(); pick(t); }} onKeyDown={(event) => onKey(event, i)} />
        ) : (
          <circle key={t.test_id + t.campaign} cx={x(t.xo2!)} cy={y(t.p_kpa!)} r={4} fill={t.campaign === "CFI-G" ? "var(--c1)" : "var(--c2)"} stroke="var(--bg)" strokeWidth={1.5} opacity={0.9}>
            <title>{`${t.test_id}, ${t.campaign}, ${t.fuel}, ${(t.xo2! * 100).toFixed(1)}% O₂, ${t.p_kpa!.toFixed(0)} kPa`}</title>
          </circle>
        ))}
        {TARGETS.map((a) => (
          <g key={a.key}>
            <circle cx={x(a.xo2)} cy={y(a.p)} r={7} fill="none" stroke={a.key === "lunar" ? "var(--soot)" : "var(--ink)"} strokeWidth={2} />
            {!compact && (
              <text x={x(a.xo2) + (a.key === "exploration" ? -12 : 12)} y={y(a.p) + (a.key === "exploration" ? -12 : -12)} textAnchor={a.key === "exploration" ? "end" : "start"} style={{ fill: a.key === "lunar" ? "var(--soot)" : "var(--ink)", fontSize: 12 }}>
                {a.label}
              </text>
            )}
          </g>
        ))}
        {focus && (interactive ? inPlot(focus) : focus.xo2 >= X0 && focus.xo2 <= X1) && (
          <g>
            <line className="cursor" x1={x(focus.xo2)} x2={x(focus.xo2)} y1={M.t} y2={H - M.b} />
            <line className="cursor" x1={M.l} x2={W - M.r} y1={y(focus.p)} y2={y(focus.p)} />
            <circle cx={x(focus.xo2)} cy={y(focus.p)} r={6} fill="var(--ink)" />
          </g>
        )}
        {interactive && focus && !inPlot(focus) && (
          <text x={W - M.r} y={M.t + 12} textAnchor="end">Current atmosphere is outside this map</text>
        )}
      </svg>
      {tip && (() => {
        const fx = x(tip.xo2!) / W;
        const shift = fx < 0.2 ? "0%" : fx > 0.8 ? "-100%" : "-50%";
        return (
          <div className={css.tip} role="status" style={{ left: `${fx * 100}%`, top: `${(y(tip.p_kpa!) / H) * 100}%`, transform: `translate(${shift}, calc(-100% - 12px))` }}>
            <b>{tip.campaign} · {tip.fuel}</b>
            <span>{(tip.xo2! * 100).toFixed(1)}% O₂ · {tip.p_kpa!.toFixed(1)} kPa</span><br />
            {outcome(tip)}{tip.burn_time_s != null ? `, ${tip.burn_time_s} s` : ", no recorded duration"}
          </div>
        );
      })()}
      </div>
      <figcaption className="legend" style={{ marginTop: 12 }}>
        {interactive ? ["CFI-G", "Flame Design"].map((name, k) => (
          <button key={name} type="button" className={css.legendBtn} aria-pressed={highlight === name}
            onMouseEnter={() => setHighlight(name)} onMouseLeave={() => setHighlight(null)}
            onFocus={() => setHighlight(name)} onBlur={() => setHighlight(null)}>
            <i style={{ background: k ? "var(--c2)" : "var(--c1)" }} />{name}
          </button>
        )) : <>
          <span><i style={{ background: "var(--c1)" }} />CFI-G</span>
          <span><i style={{ background: "var(--c2)" }} />Flame Design</span>
        </>}
        <span><i style={{ border: "2px solid var(--soot)", background: "transparent" }} />Lunar-base window</span>
      </figcaption>
      {wide && <details className="more">
        <summary>View test records for the visible window</summary>
        <p>{pts.length} tests with these filters. {pts.filter((test) => test.burn_time_s == null).length} lack a recorded duration.</p>
        <div className="table-wrap">
          <table>
            <caption>First {Math.min(20, pts.length)} visible records</caption>
            <thead><tr><th>Test</th><th>Fuel</th><th>Oxygen</th><th>Pressure (kPa)</th><th>Duration (s)</th><th>Source</th></tr></thead>
            <tbody>{pts.slice(0, 20).map((test, i) => <tr key={test.psi_id + test.test_id + i}>
              <td>{test.psi_id} {test.test_id}</td><td>{test.fuel}</td>
              <td>{((test.xo2 ?? 0) * 100).toFixed(1)}%</td><td>{test.p_kpa?.toFixed(1)}</td>
              <td>{test.burn_time_s ?? "Unavailable"}</td>
              <td>{test.source_file ?? "Unavailable"}{test.source_row != null && ", row " + test.source_row}</td>
            </tr>)}</tbody>
          </table>
        </div>
      </details>}
    </figure>
  );
}
