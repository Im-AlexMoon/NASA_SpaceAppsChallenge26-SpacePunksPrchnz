"use client";
import { useState } from "react";
import type { GasTest, GridPoint } from "../lib/content";

// Model median burn time (with its 90 % interval) against O2 at one pressure; tier-C stretches are left blank.
const W = 720, H = 300, M = { l: 48, r: 16, t: 14, b: 34 };
const T0 = 2, T1 = 400;

export default function BurnChart({ xo2, row, p, selected, tests }: {
  xo2: number[]; row: GridPoint[]; p: number; selected: number | null; tests: GasTest[];
}) {
  const [hover, setHover] = useState<number | null>(null);
  const X0 = xo2[0], X1 = xo2[xo2.length - 1];
  const x = (v: number) => Math.round(100 * (M.l + ((v - X0) / (X1 - X0))* (W - M.l - M.r))) / 100;
  const y = (t: number) => Math.round(100 * (H - M.b - (Math.log(Math.min(Math.max(t, T0), T1) / T0) / Math.log(T1 / T0)) * (H - M.t - M.b))) / 100;

  // Split into runs of consecutive points that have a model reading.
  const runs: number[][] = [];
  row.forEach((pt, i) => {
    if (pt.tier === "C" || pt.median == null) return;
    const last = runs[runs.length - 1];
    if (last && last[last.length - 1] === i - 1) last.push(i);
    else runs.push([i]);
  });
  const near = tests.filter(
    (t) => t.flame_type === "normal" && t.extinction_mode === "self_extinguished" && t.burn_time_s != null &&
      t.xo2 != null && t.p_kpa != null && Math.abs(t.p_kpa / p - 1) <= 0.25 && t.xo2 >= X0 && t.xo2 <= X1,
  );
  const hi = hover ?? selected;
  const hp = hi == null ? undefined : row[hi];

  const onMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const box = e.currentTarget.getBoundingClientRect();
    const vx = ((e.clientX - box.left) / box.width) * W;
    const v = X0 + ((vx - M.l) / (W - M.l - M.r)) * (X1 - X0);
    const i = Math.round((v - X0) / (xo2[1] - xo2[0]));
    setHover(i >= 0 && i < xo2.length ? i : null);
  };

  return (
    <div className="chart-box">
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} onPointerMove={onMove} onPointerLeave={() => setHover(null)}
        role="img" aria-label={`Model burn time against oxygen at ${p} kilopascals, with observed flames near this pressure`}>
        <g className="grid">
          {[3, 10, 30, 100, 300].map((t) => (
            <g key={t}>
              <line x1={M.l} x2={W - M.r} y1={y(t)} y2={y(t)} />
              <text x={M.l - 8} y={y(t) + 4} textAnchor="end">{t}s</text>
            </g>
          ))}
          {[0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5].map((v) => (
            <text key={v} x={x(v)} y={H - 10} textAnchor="middle">{Math.round(v * 100)}%</text>
          ))}
        </g>
        {runs.map((r) => (
          <g key={r[0]}>
            <path className="band" d={
              r.map((i, k) => `${k ? "L" : "M"}${x(xo2[i])},${y(row[i].ci![1])}`).join("") +
              r.slice().reverse().map((i) => `L${x(xo2[i])},${y(row[i].ci![0])}`).join("") + "Z"} />
            <path className="curve" d={r.map((i, k) => `${k ? "L" : "M"}${x(xo2[i])},${y(row[i].median!)}`).join("")} />
          </g>
        ))}
        {near.map((t) => (
          <circle key={t.campaign + t.test_id} cx={x(t.xo2!)} cy={y(t.burn_time_s!)} r={4}
            fill={t.campaign === "CFI-G" ? "var(--c1)" : "var(--c2)"} stroke="var(--surface)" strokeWidth={2} opacity={0.85} />
        ))}
        {hi != null && <line className="cursor" x1={x(xo2[hi])} x2={x(xo2[hi])} y1={M.t} y2={H - M.b} />}
        {hi != null && hp && hp.median != null && hp.tier !== "C" && <circle cx={x(xo2[hi])} cy={y(hp.median)} r={5} fill="var(--ink)" />}
      </svg>
      {hover != null && hp && (
        <div className="tip" style={{ left: `${(x(xo2[hover]) / W) * 100}%`, top: `${((hp.median != null && hp.tier !== "C" ? y(hp.median) : M.t + 20) / H) * 100}%` }}>
          {(xo2[hover] * 100).toFixed(0)}% oxygen: {hp.tier === "C" || hp.median == null ? "no reading" : `${hp.median.toFixed(0)} s (${hp.ci![0].toFixed(0)}–${hp.ci![1].toFixed(0)})`} (tier {hp.tier})
        </div>
      )}
      <div className="legend" style={{ marginTop: 10 }}>
        <span><i style={{ background: "var(--accent)", borderRadius: 2, height: 3 }} />Model median, 90% interval</span>
        <span><i style={{ background: "var(--c1)" }} />CFI-G flames ±25% pressure</span>
        <span><i style={{ background: "var(--c2)" }} />Flame Design flames</span>
      </div>
    </div>
  );
}
