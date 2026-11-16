"use client";

import { useState } from "react";
import { gasTests } from "../lib/content";

// Where NASA has flame data: every normal spherical flame tested on the ISS, by O2 mole fraction and total pressure.
const M = { l: 52, r: 16, t: 16, b: 40 };
const X0 = 0.14, X1 = 0.44, P0 = 40, P1 = 340;
const r2 = (v: number) => Math.round(v * 100) / 100; // identical server and client markup

const TARGETS = [
  { key: "iss", label: "ISS cabin", xo2: 0.21, p: 101.3 },
  { key: "exploration", label: "Exploration", xo2: 0.34, p: 56.5 },
  { key: "lunar", label: "Lunar base", xo2: 0.3, p: 70.3 },
];

export default function CoverageMap({ focus, compact = false, wide = false }: { focus?: { xo2: number; p: number }; compact?: boolean; wide?: boolean }) {
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
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Gas-flame tests by oxygen fraction and pressure, with the lunar reference window marked">
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
        {pts.map((t) => (
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
        {focus && focus.xo2 >= X0 && focus.xo2 <= X1 && (
          <g>
            <line className="cursor" x1={x(focus.xo2)} x2={x(focus.xo2)} y1={M.t} y2={H - M.b} />
            <line className="cursor" x1={M.l} x2={W - M.r} y1={y(focus.p)} y2={y(focus.p)} />
            <circle cx={x(focus.xo2)} cy={y(focus.p)} r={6} fill="var(--ink)" />
          </g>
        )}
      </svg>
      <figcaption className="legend" style={{ marginTop: 12 }}>
        <span><i style={{ background: "var(--c1)" }} />CFI-G</span>
        <span><i style={{ background: "var(--c2)" }} />Flame Design</span>
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
