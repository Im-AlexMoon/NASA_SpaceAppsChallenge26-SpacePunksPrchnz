"use client";
import Link from "next/link";
import { useState } from "react";
import { dashboard, findings, ranking } from "../../lib/content";
import { lin, r2 } from "./kit";

const TERM: Record<string, string> = {
  inv_tad: "1000 / flame temperature", log_p: "ln pressure", log_mtot: "ln fuel flow", log_L: "ln flame position L", is_fd: "Flame Design campaign",
};

// Interval plot: estimate and 95% interval against a reference line (1 for ratios, 0 for coefficients).
export function Forest() {
  const [tab, setTab] = useState<"effects" | "law">("effects");
  const coef = (dashboard.model?.coef_table ?? []).filter((c) => TERM[c.term]);
  const rows = tab === "effects"
    ? dashboard.effects.rows.map((r) => ({ name: r.name, v: r.value, lo: r.ci95[0], hi: r.ci95[1], ref: r.reference, note: `n = ${r.n} · ${r.ref}` }))
    : coef.map((c) => ({ name: TERM[c.term], v: c.coef, lo: c.ci_low, hi: c.ci_high, ref: 0, note: "M-01 v2" }));
  const log = tab === "effects";
  const vals = rows.flatMap((r) => [r.lo, r.hi, r.ref]);
  const d0 = log ? 0.1 : Math.min(...vals) - 0.5, d1 = log ? 4 : Math.max(...vals) + 0.5;
  const W = 640, rowH = 40, L = 300, R = 36, H = rows.length * rowH + 30;
  const x = log ? (v: number) => r2(L + (Math.log(v / d0) / Math.log(d1 / d0)) * (W - L - R)) : lin(d0, d1, L, W - R);
  const ticks = log ? [0.1, 0.25, 0.5, 1, 2, 4] : [-15, -10, -5, 0, 5].filter((t) => t >= d0 && t <= d1);
  return (
    <div className="stack" style={{ gap: 12 }}>
      <div className="seg" role="group" aria-label="Interval set">
        <button aria-pressed={tab === "effects"} onClick={() => setTab("effects")}>Oxygen effect</button>
        <button aria-pressed={tab === "law"} onClick={() => setTab("law")}>Burn-time law terms</button>
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={rows.map((r) => `${r.name} ${r.v} (95% ${r.lo} to ${r.hi})`).join("; ")}>
        <g className="grid">{ticks.map((t) => <g key={t}><line x1={x(t)} x2={x(t)} y1={6} y2={H - 24} /><text x={x(t)} y={H - 8} textAnchor="middle">{t}</text></g>)}</g>
        <line x1={x(rows[0]?.ref ?? 0)} x2={x(rows[0]?.ref ?? 0)} y1={6} y2={H - 24} stroke="var(--ink-3)" strokeDasharray="4 4" />
        {rows.map((r, i) => {
          const cy = 18 + i * rowH;
          return (
            <g key={r.name}>
              <text x={0} y={cy + 4} style={{ fill: "var(--ink-2)", fontFamily: "var(--font-sans)", fontSize: 13 }}>{r.name}</text>
              <line x1={x(r.lo)} x2={x(r.hi)} y1={cy} y2={cy} stroke="var(--accent)" strokeWidth={2} strokeLinecap="round" />
              <circle cx={x(r.v)} cy={cy} r={5} fill="var(--ink)" stroke="var(--surface)" strokeWidth={2} />
              <text x={x(r.hi) + 8} y={cy + 4}>{r.v}</text>
            </g>
          );
        })}
      </svg>
      <p className="dash-note">
        {log ? "A hazard ratio below 1 means fewer flames going out per second; a time ratio above 1 means longer burns. Neither interval crosses 1."
          : "Coefficients of ln(burn time) with 95% day-bootstrap intervals. No interval crosses 0."}
      </p>
    </div>
  );
}

// Predicted vs observed probability of still burning, by tercile, at 30 s and 60 s.
export function Calibration() {
  const S = 150, P = 22;
  const s = lin(0, 1, P, S - 6), sy = lin(0, 1, S - P, 6);
  return (
    <div className="calib">
      {dashboard.calibration.horizons.map((h) => (
        <figure key={h.t_s}>
          <svg className="chart" viewBox={`0 0 ${S} ${S}`} role="img" aria-label={`At ${h.t_s} s, predicted ${h.predicted.join(", ")} versus observed ${h.observed.join(", ")}`}>
            <rect x={P} y={6} width={S - P - 6} height={S - P - 6} fill="none" stroke="var(--line)" />
            <line x1={s(0)} y1={sy(0)} x2={s(1)} y2={sy(1)} stroke="var(--ink-3)" strokeDasharray="3 3" />
            {h.predicted.map((p, i) => <circle key={i} cx={s(p)} cy={sy(h.observed[i])} r={4.5} fill="var(--accent)" stroke="var(--surface)" strokeWidth={1.5} />)}
            <text x={P} y={S - 6}>0</text><text x={S - 10} y={S - 6}>1</text>
          </svg>
          <figcaption className="small">Still burning at {h.t_s} s</figcaption>
        </figure>
      ))}
    </div>
  );
}

// Out-of-sample log-likelihood of three models (less negative is better).
export function Baselines() {
  const rows = dashboard.baselines.rows;
  const lo = Math.min(...rows.map((r) => r.loglik));
  return (
    <div className="hbars static">
      {rows.map((r) => (
        <div key={r.model}>
          <span className="hb-label">{r.model}</span>
          <span className="hb-track"><i style={{ transform: `scaleX(${r2(1 - r.loglik / (lo * 1.15))})` }} /></span>
          <span className="num">{r.loglik.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
}

export function Research() {
  const [show, setShow] = useState<"all" | "negative">("all");
  const rows = dashboard.research.rows.filter((r) => show === "all" || r.outcome === "negative");
  return (
    <div className="stack" style={{ gap: 14 }}>
      <div className="seg" role="group" aria-label="Show tests">
        <button aria-pressed={show === "all"} onClick={() => setShow("all")}>All tests</button>
        <button aria-pressed={show === "negative"} onClick={() => setShow("negative")}>Negative results</button>
      </div>
      <ol className="research">
        {rows.map((r) => (
          <li key={r.ref} data-outcome={r.outcome}>
            <span className="num">{r.ref}</span>
            <div>
              <strong>{r.question}</strong>
              <p>{r.result}. <span className="num">{r.metric}</span></p>
            </div>
            <span className="chip">{r.outcome === "negative" ? "Ruled out" : "Kept"}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

export function Quality() {
  return (
    <div className="kpis" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))" }}>
      {dashboard.quality.rows.map((q) => (
        <div key={q.label} className="kpi">
          <strong className="num">{q.unit === "K" ? "+" : ""}{q.value}{q.unit === "%" ? "%" : q.unit ? ` ${q.unit}` : ""}</strong>
          <span>{q.label}</span>
          <span className="num small">n = {q.n} · {q.ref}</span>
        </div>
      ))}
    </div>
  );
}

const PROFILES = Object.entries(ranking.profiles);
export function RankingTop() {
  const [profile, setProfile] = useState(PROFILES[0][0]);
  const p = ranking.profiles[profile];
  const total = Object.values(p.weights).reduce((a, b) => a + b, 0);
  const scores = new Map(ranking.scores[p.environment].map((r) => [r.psi_id, r]));
  const rows = ranking.investigations.map((inv) => ({
    ...inv,
    score: ranking.dimension_order.reduce((s, d) => s + Number(scores.get(inv.psi_id)?.[d] ?? 0) * (p.weights[d] ?? 0), 0) / total,
  })).sort((a, b) => b.score - a.score || a.psi_id.localeCompare(b.psi_id)).slice(0, 10);
  return (
    <div className="stack" style={{ gap: 12 }}>
      <label className="small">Profile{" "}
        <select value={profile} onChange={(e) => setProfile(e.target.value)}>
          {PROFILES.map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
      </label>
      <div className="hbars static">
        {rows.map((r) => (
          <div key={r.psi_id}>
            <span className="hb-label" title={r.title}>{r.acronym ?? r.psi_id}</span>
            <span className="hb-track"><i style={{ transform: `scaleX(${r2(r.score / rows[0].score)})` }} /></span>
            <span className="num">{r.score.toFixed(2)}</span>
          </div>
        ))}
      </div>
      <Link className="link small" href="/investigations">Adjust the weights</Link>
    </div>
  );
}

export function FindingsStrip() {
  return (
    <div className="fstrip">
      {findings.map((f) => {
        const k = f.key_numbers[0];
        return (
          <Link key={f.id} href={`/findings#${f.id}`} className="fcard">
            <span className="num eyebrow">{f.id}</span>
            <strong>{f.title}</strong>
            {k && <span className="num small">{k.name}: {k.value}{k.unit && typeof k.value === "number" && k.unit !== "per 1000/K" ? ` ${k.unit}` : ""}</span>}
          </Link>
        );
      })}
    </div>
  );
}
