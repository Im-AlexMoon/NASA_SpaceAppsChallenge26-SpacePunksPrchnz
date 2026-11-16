"use client";
import { useState } from "react";
import type { GasTest } from "../../lib/content";
import { readings } from "../../lib/content";
import { BANDS, CAMPAIGN_COLOR, fmtS, km, lin, logScale, r2, survivalAt } from "./kit";

const T_MAX = 300;

// Fraction of flames still burning against time, one step curve per oxygen band (Kaplan-Meier, observed data).
export function SurvivalChart({ rows }: { rows: GasTest[] }) {
  const W = 640, H = 300, M = { l: 44, r: 16, t: 12, b: 34 };
  const x = logScale(1, T_MAX, M.l, W - M.r);
  const y = lin(0, 1, H - M.b, M.t);
  const [hover, setHover] = useState<number | null>(null);
  const curves = BANDS.map((b) => ({ ...b, ...km(rows.filter((t) => t.xo2 != null && b.test(t.xo2))) })).filter((c) => c.n >= 5);
  const path = (steps: { t: number; s: number }[]) => {
    let d = `M${x(1)},${y(1)}`;
    steps.slice(1).forEach((p) => { d += `H${x(p.t)}V${y(p.s)}`; });
    return d + `H${x(T_MAX)}`;
  };
  const onMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const box = e.currentTarget.getBoundingClientRect();
    const vx = ((e.clientX - box.left) / box.width) * W;
    if (vx < M.l || vx > W - M.r) return setHover(null);
    setHover(Math.exp(((vx - M.l) / (W - M.l - M.r)) * Math.log(T_MAX)));
  };
  return (
    <div className="chart-box">
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} onPointerMove={onMove} onPointerLeave={() => setHover(null)}
        role="img" aria-label="Fraction of flames still burning against time, by oxygen band">
        <g className="grid">
          {[0, 0.25, 0.5, 0.75, 1].map((s) => <g key={s}><line x1={M.l} x2={W - M.r} y1={y(s)} y2={y(s)} /><text x={M.l - 8} y={y(s) + 4} textAnchor="end">{s * 100}%</text></g>)}
          {[1, 3, 10, 30, 100, 300].map((t) => <text key={t} x={x(t)} y={H - 10} textAnchor="middle">{t}s</text>)}
        </g>
        <line x1={M.l} x2={W - M.r} y1={y(0.5)} y2={y(0.5)} stroke="var(--line-2)" strokeDasharray="4 4" />
        {curves.map((c) => <path key={c.key} d={path(c.steps)} fill="none" stroke={c.color} strokeWidth={2} strokeLinejoin="round" />)}
        {hover != null && <line className="cursor" x1={x(hover)} x2={x(hover)} y1={M.t} y2={H - M.b} />}
      </svg>
      {hover != null && curves.length > 0 && (
        <div className="tip" style={{ left: `${(x(hover) / W) * 100}%`, top: "8%" }}>
          At {fmtS(hover)} s: {curves.map((c) => `${c.label.replace("O₂ ", "")} ${Math.round(survivalAt(c.steps, hover) * 100)}%`).join(" · ")}
        </div>
      )}
      <div className="legend" style={{ marginTop: 10 }}>
        {curves.map((c) => <span key={c.key}><i style={{ background: c.color }} />{c.label}: median {c.median == null ? "not reached" : `${fmtS(c.median)} s`}, n = {c.n}</span>)}
      </div>
      {curves.length === 0 && <p role="status" className="small">Not enough flames with a recorded end in this selection.</p>}
    </div>
  );
}

// Burn duration against oxygen for every flame with a recorded duration; colour = campaign.
export function ScatterChart({ rows }: { rows: GasTest[] }) {
  const W = 640, H = 300, M = { l: 44, r: 16, t: 12, b: 34 };
  const x = lin(0.12, 0.5, M.l, W - M.r);
  const y = logScale(1, 400, H - M.b, M.t);
  const [hover, setHover] = useState<GasTest | null>(null);
  const pts = rows.filter((t) => t.burn_time_s != null && t.burn_time_s > 0 && t.xo2 != null);
  return (
    <div className="chart-box">
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Burn duration against oxygen mole fraction" onPointerLeave={() => setHover(null)}>
        <g className="grid">
          {[1, 3, 10, 30, 100, 300].map((t) => <g key={t}><line x1={M.l} x2={W - M.r} y1={y(t)} y2={y(t)} /><text x={M.l - 8} y={y(t) + 4} textAnchor="end">{t}s</text></g>)}
          {[0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45].map((v) => <text key={v} x={x(v)} y={H - 10} textAnchor="middle">{Math.round(v * 100)}%</text>)}
        </g>
        {pts.map((t) => (
          <circle key={t.campaign + t.test_id} cx={x(t.xo2!)} cy={y(t.burn_time_s!)} r={hover === t ? 6 : 3.5}
            fill={CAMPAIGN_COLOR[t.campaign] ?? "var(--ink-3)"} fillOpacity={t.extinction_mode === "self_extinguished" ? 0.9 : 0.25}
            stroke={t.extinction_mode === "self_extinguished" ? "var(--surface)" : CAMPAIGN_COLOR[t.campaign]} strokeWidth={1}
            onPointerEnter={() => setHover(t)} />
        ))}
      </svg>
      {hover && (
        <div className="tip" style={{ left: `${(x(hover.xo2!) / W) * 100}%`, top: `${(y(hover.burn_time_s!) / H) * 100}%` }}>
          {hover.campaign} {hover.test_id}: {hover.fuel}, {(hover.xo2! * 100).toFixed(1)}% O₂, {hover.p_kpa?.toFixed(0)} kPa, {fmtS(hover.burn_time_s)} s, {(hover.extinction_mode ?? "end not recorded").replace("_", " ")}
        </div>
      )}
      <div className="legend" style={{ marginTop: 10 }}>
        <span><i style={{ background: "var(--c1)" }} />Went out on its own</span>
        <span><i style={{ background: "transparent", border: "1px solid var(--c1)" }} />Flow cut while burning</span>
      </div>
    </div>
  );
}

const OUTCOMES = [
  { key: "self", label: "Went out on its own", color: "#4f8dff", test: (t: GasTest) => t.ignition_outcome === "yes" && t.extinction_mode === "self_extinguished" },
  { key: "cut", label: "Flow cut while burning", color: "#ffb04a", test: (t: GasTest) => t.ignition_outcome === "yes" && t.extinction_mode === "flow_terminated" },
  { key: "unk", label: "Ignited, end not recorded", color: "#5c6a7e", test: (t: GasTest) => t.ignition_outcome === "yes" && t.extinction_mode == null },
  { key: "no", label: "Did not ignite or flashed", color: "#2a3342", test: (t: GasTest) => t.ignition_outcome === "no" || t.ignition_outcome === "flash" },
  { key: "na", label: "Ignition not recorded", color: "transparent", test: (t: GasTest) => t.ignition_outcome == null },
];

// One horizontal 100% bar per campaign and flame type. Missing values stay a category of their own.
export function OutcomeBars({ rows }: { rows: GasTest[] }) {
  const groups = [...new Set(rows.map((t) => `${t.campaign} · ${t.flame_type}`))].sort();
  return (
    <div className="stack" style={{ gap: 14 }}>
      {groups.map((g) => {
        const sub = rows.filter((t) => `${t.campaign} · ${t.flame_type}` === g);
        return (
          <div key={g} className="outcome-row">
            <div className="outcome-head"><span>{g}</span><span className="num small">n = {sub.length}</span></div>
            <div className="outcome-bar" role="img" aria-label={`${g}: ` + OUTCOMES.map((o) => `${o.label} ${sub.filter(o.test).length}`).join(", ")}>
              {OUTCOMES.map((o) => {
                const k = sub.filter(o.test).length;
                return k ? <i key={o.key} title={`${o.label}: ${k}`} style={{ flexGrow: k, background: o.color, border: o.key === "na" ? "1px dashed var(--line-2)" : undefined }} /> : null;
              })}
            </div>
          </div>
        );
      })}
      <div className="legend">{OUTCOMES.map((o) => <span key={o.key}><i style={{ background: o.color, border: o.key === "na" ? "1px dashed var(--ink-3)" : undefined, borderRadius: 2 }} />{o.label}</span>)}</div>
    </div>
  );
}

// Test counts per fuel. Clicking a bar filters the whole dashboard to that fuel.
export function FuelBars({ rows, active, onPick }: { rows: GasTest[]; active: string; onPick: (fuel: string) => void }) {
  const counts = Object.entries(rows.reduce<Record<string, number>>((a, t) => ({ ...a, [t.fuel]: (a[t.fuel] ?? 0) + 1 }), {})).sort((a, b) => b[1] - a[1]);
  const max = counts[0]?.[1] ?? 1;
  return (
    <div className="hbars">
      {counts.map(([fuel, k]) => (
        <button key={fuel} type="button" aria-pressed={active === fuel} onClick={() => onPick(active === fuel ? "all" : fuel)}>
          <span className="hb-label">{fuel}</span>
          <span className="hb-track"><i style={{ transform: `scaleX(${r2(k / max)})` }} /></span>
          <span className="num">{k}</span>
        </button>
      ))}
    </div>
  );
}

const XE = [0.12, 0.16, 0.2, 0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.5];
const PE = [20, 45, 65, 85, 110, 140, 220, 320];
const REF: Record<string, string> = { iss_cabin: "ISS", exploration_8p2_34: "Expl.", lunar_base_upper: "Moon", mars_surface_habitat: "Mars" };

// Count of tests per oxygen x pressure cell, with reference habitats marked. Clicking a cell narrows the dashboard.
export function CoverageHeatmap({ rows, onPick }: { rows: GasTest[]; onPick: (o2: number, p: number) => void }) {
  const W = 1100, H = 300, M = { l: 52, r: 12, t: 10, b: 34 };
  const cw = (W - M.l - M.r) / (XE.length - 1), ch = (H - M.t - M.b) / (PE.length - 1);
  const grid = PE.slice(0, -1).map((p0, j) => XE.slice(0, -1).map((x0, i) =>
    rows.filter((t) => t.xo2 != null && t.p_kpa != null && t.xo2 >= x0 && t.xo2 < XE[i + 1] && t.p_kpa >= p0 && t.p_kpa < PE[j + 1]).length));
  const max = Math.max(1, ...grid.flat());
  const cellX = (v: number) => { const i = XE.findIndex((e, k) => v >= e && v < XE[k + 1]); return i < 0 ? null : M.l + (i + (v - XE[i]) / (XE[i + 1] - XE[i])) * cw; };
  const cellY = (v: number) => { const j = PE.findIndex((e, k) => v >= e && v < PE[k + 1]); return j < 0 ? null : H - M.b - (j + (v - PE[j]) / (PE[j + 1] - PE[j])) * ch; };
  const [hover, setHover] = useState<[number, number] | null>(null);
  return (
    <div className="chart-box">
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Number of tests per oxygen and pressure cell">
        {grid.map((row, j) => row.map((k, i) => (
          <rect key={`${i}-${j}`} x={r2(M.l + i * cw + 1)} y={r2(H - M.b - (j + 1) * ch + 1)} width={r2(cw - 2)} height={r2(ch - 2)} rx={4}
            fill={k ? `rgba(79,141,255,${r2(0.15 + 0.85 * Math.sqrt(k / max))})` : "transparent"} stroke={k ? "none" : "var(--line)"}
            style={{ cursor: k ? "pointer" : "default" }}
            onPointerEnter={() => setHover([i, j])} onPointerLeave={() => setHover(null)}
            onClick={() => k && onPick((XE[i] + XE[i + 1]) / 2, (PE[j] + PE[j + 1]) / 2)} />
        )))}
        <g className="grid">
          {XE.map((v, i) => <text key={v} x={M.l + i * cw} y={H - 12} textAnchor="middle">{Math.round(v * 100)}%</text>)}
          {PE.map((v, j) => <text key={v} x={M.l - 8} y={H - M.b - j * ch + 4} textAnchor="end">{v}</text>)}
        </g>
        {readings.references.filter((r) => REF[r.key]).map((r) => {
          const cx = cellX(r.inputs.xo2), cy = cellY(r.inputs.p_kpa);
          return cx == null || cy == null ? null : (
            <g key={r.key} pointerEvents="none">
              <circle cx={r2(cx)} cy={r2(cy)} r={6} fill="none" stroke={r.key === "lunar_base_upper" ? "var(--soot)" : "var(--ink)"} strokeWidth={2} />
              <text x={r2(cx + 9)} y={r2(cy - 7)} style={{ fill: "var(--ink)" }}>{REF[r.key]}</text>
            </g>
          );
        })}
      </svg>
      {hover && (
        <div className="tip" style={{ left: `${((M.l + (hover[0] + 0.5) * cw) / W) * 100}%`, top: `${((H - M.b - (hover[1] + 1) * ch) / H) * 100}%` }}>
          {Math.round(XE[hover[0]] * 100)}–{Math.round(XE[hover[0] + 1] * 100)}% O₂, {PE[hover[1]]}–{PE[hover[1] + 1]} kPa: {grid[hover[1]][hover[0]]} tests
        </div>
      )}
      <p className="small" style={{ marginTop: 8 }}>Pressure in kPa (uneven bins). Empty outlined cells: no tests.</p>
    </div>
  );
}
