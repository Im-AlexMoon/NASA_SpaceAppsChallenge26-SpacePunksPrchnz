"use client";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { ranking } from "../lib/content";

// MCDA ranking (configs/ranking.yaml): score = sum(w_d * s_d) / sum(w_d), the same formula as the API.
const DIMS = ranking.dimension_order;
const SHORT: Record<string, string> = {
  pillar_prevencion: "Prevention", pillar_deteccion: "Detection", pillar_supresion: "Suppression",
  environment: "Environment", evidence: "Evidence quality", modeling: "Modeling value", maturity: "Maturity",
};
const ENV: Record<string, string> = { nave: "spacecraft", estacion: "station", base_lunar: "lunar base", rover: "rover", marte: "Mars" };
const PROFILES = Object.entries(ranking.profiles);

export default function RankingBoard() {
  const [profile, setProfile] = useState(PROFILES[0][0]);
  const [weights, setWeights] = useState<Record<string, number>>(ranking.profiles[PROFILES[0][0]].weights);
  const [open, setOpen] = useState<string | null>(null);
  const env = ranking.profiles[profile].environment;
  const custom = DIMS.some((d) => Math.abs((weights[d] ?? 0) - ranking.profiles[profile].weights[d]) > 1e-9);

  const rows = useMemo(() => {
    const total = DIMS.reduce((s, d) => s + (weights[d] ?? 0), 0) || 1;
    return ranking.investigations
      .map((inv, i) => {
        const s = ranking.scores[env][i];
        const contrib = Object.fromEntries(DIMS.map((d) => [d, (s[d] * (weights[d] ?? 0)) / total]));
        return { ...inv, s, contrib, score: Object.values(contrib).reduce((a, b) => a + b, 0) };
      })
      .sort((a, b) => b.score - a.score || a.psi_id.localeCompare(b.psi_id, "en", { numeric: true }));
  }, [env, weights]);

  // FLIP: rows glide from their old position to the new one when the order changes.
  const list = useRef<HTMLOListElement>(null);
  const last = useRef<Map<string, number>>(new Map());
  useLayoutEffect(() => {
    const els = Array.from(list.current?.children ?? []) as HTMLElement[];
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const next = new Map<string, number>();
    els.forEach((el) => {
      const id = el.dataset.id!;
      const top = el.getBoundingClientRect().top;
      next.set(id, top);
      const prev = last.current.get(id);
      if (!reduce && prev != null && Math.abs(prev - top) > 1) {
        el.animate([{ transform: `translateY(${prev - top}px)` }, { transform: "none" }], {
          duration: 300, easing: "cubic-bezier(0.77, 0, 0.175, 1)",
        });
      }
    });
    last.current = next;
  }, [rows]);

  const max = rows[0]?.score || 1;
  const sens = ranking.sensitivity.by_profile[profile];

  return (
    <div className="stack" style={{ gap: 28 }}>
      <div className="seg" role="group" aria-label="Profile">
        {PROFILES.map(([k, v]) => (
          <button key={k} aria-pressed={profile === k} onClick={() => { setProfile(k); setWeights(v.weights); setOpen(null); }}>
            {v.label.replace(" (balanced)", "")}
          </button>
        ))}
      </div>

      <details className="more panel" style={{ padding: "4px 24px" }}>
        <summary>Adjust weights{custom ? " · custom" : ""}</summary>
        <div className="weights" style={{ paddingBottom: 18 }}>
          {DIMS.map((d) => (
            <div className="field" key={d}>
              <div className="field-row">
                <label htmlFor={`w-${d}`} title={ranking.dimensions[d]}>{SHORT[d]}</label>
                <output htmlFor={`w-${d}`} className="num">{Math.round((weights[d] ?? 0) * 100)}</output>
              </div>
              <input id={`w-${d}`} type="range" min={0} max={0.5} step={0.01} value={weights[d] ?? 0}
                style={{ "--fill": `${((weights[d] ?? 0) / 0.5) * 100}%` } as React.CSSProperties}
                onChange={(e) => setWeights({ ...weights, [d]: +e.target.value })} />
            </div>
          ))}
          <button className="btn btn-ghost" style={{ alignSelf: "end" }} onClick={() => setWeights(ranking.profiles[profile].weights)} disabled={!custom}>
            Reset weights
          </button>
        </div>
      </details>

      <p className="small">
        Target environment: {ENV[env] ?? env}.{" "}
        {!custom && sens
          ? `Moving any single weight by ±${Math.round(ranking.sensitivity.perturbation * 100)}% changes the top ${ranking.sensitivity.top_k} by at most ${sens.max_changed} investigation${sens.max_changed === 1 ? "" : "s"}.`
          : "Custom weights: scores recomputed with the published formula."}
      </p>

      <ol className="rank-list" ref={list}>
        {rows.map((r, i) => (
          <li key={r.psi_id} data-id={r.psi_id}>
            <div className="rank-row" data-top={i < 5 || undefined} onClick={() => setOpen(open === r.psi_id ? null : r.psi_id)} style={{ cursor: "pointer" }}>
              <span className="pos num">{String(i + 1).padStart(2, "0")}</span>
              <span className="name">
                <button className="rank-name" aria-expanded={open === r.psi_id} onClick={(e) => { e.stopPropagation(); setOpen(open === r.psi_id ? null : r.psi_id); }}>
                  {r.acronym ?? r.title.split(" ").slice(0, 6).join(" ") + "…"}
                </button>
                <span>{r.psi_id} · {r.title}</span>
              </span>
              <span className="bar"><i style={{ transform: `scaleX(${r.score / max})` }} /></span>
              <span className="score num">{r.score.toFixed(2)}</span>
            </div>
            {open === r.psi_id && (
              <div className="breakdown">
                {DIMS.map((d) => (
                  <div key={d}>
                    <span className="label">{SHORT[d]}</span>
                    <span className="mini"><i style={{ transform: `scaleX(${r.s[d]})` }} /></span>
                    <span className="num small">{r.s[d].toFixed(2)} × {Math.round((weights[d] ?? 0) * 100)}</span>
                  </div>
                ))}
              </div>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
