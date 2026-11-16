"use client";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { gasTests, ranking } from "../lib/content";

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
  const [comparison, setComparison] = useState<string[]>([]);
  const [open, setOpen] = useState<string | null>(null);
  const env = ranking.profiles[profile].environment;
  const custom = DIMS.some((d) => Math.abs((weights[d] ?? 0) - ranking.profiles[profile].weights[d]) > 1e-9);

  const rows = useMemo(() => {
    const total = DIMS.reduce((s, d) => s + (weights[d] ?? 0), 0);
    if (!total) return [];
    const scores = new Map(ranking.scores[env].map((row) => [row.psi_id, row]));
    return ranking.investigations
      .map((inv) => {
        const s = Object.fromEntries(DIMS.map((dimension) => [dimension, Number(scores.get(inv.psi_id)?.[dimension] ?? 0)]));
        const contrib = Object.fromEntries(DIMS.map((d) => [d, (s[d] * (weights[d] ?? 0)) / total]));
        return { ...inv, s, contrib, score: Object.values(contrib).reduce((a, b) => a + b, 0) };
      })
      .sort((a, b) => b.score - a.score || a.psi_id.localeCompare(b.psi_id, "en"));
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
        <summary>Adjust weights{custom ? " (custom)" : ""}</summary>
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

      {!custom && sens?.joint && <p className="small">Across {sens.joint.n_scenarios} joint weight scenarios, up to {sens.joint.max_changed} of the top {ranking.sensitivity.top_k} investigations changed.</p>}

      <section className="panel stack">
        <h2>Compare investigations</h2>
        <label>Add up to three investigations
          <select value="" disabled={comparison.length >= 3} onChange={(event) => {
            if (event.target.value) setComparison([...comparison, event.target.value]);
          }}>
            <option value="">Select an investigation</option>
            {ranking.investigations.filter((item) => !comparison.includes(item.psi_id)).map((item) =>
              <option value={item.psi_id} key={item.psi_id}>{item.psi_id}: {item.acronym ?? item.title}</option>)}
          </select>
        </label>
        {comparison.map((key) => {
          const item = ranking.investigations.find((row) => row.psi_id === key)!;
          const gas = gasTests.filter((test) => test.psi_id === key);
          const fuels = [...new Set(gas.map((test) => test.fuel).filter(Boolean))].sort();
          const pressure = gas.flatMap((test) => test.p_kpa == null ? [] : [test.p_kpa]);
          const oxygen = gas.flatMap((test) => test.xo2 == null ? [] : [test.xo2]);
          return <article key={key}>
            <h3>{item.acronym ?? item.title}</h3>
            <p>{key}. Hardware: {item.hardware_family ?? "Unspecified"}. Platform: {item.flight_platform ?? "Unspecified"}.</p>
            <p>Data access: {item.access_status.replaceAll("_", " ")}. Curated tests: {item.n_gold_tests ?? "Unavailable"}.</p>
            {gas.length > 0 && <p>Gas flame fuels: {fuels.join(", ")}.</p>}
            {pressure.length > 0 && <p>Recorded pressure: {Math.min(...pressure).toFixed(1)} to {Math.max(...pressure).toFixed(1)} kPa.</p>}
            {oxygen.length > 0 && <p>Recorded oxygen: {(100 * Math.min(...oxygen)).toFixed(1)}% to {(100 * Math.max(...oxygen)).toFixed(1)}%.</p>}
            {item.doi && <p><a className="link" href={"https://doi.org/" + encodeURI(item.doi)}>Open the source DOI</a></p>}
            <button type="button" className="btn btn-ghost" onClick={() => setComparison(comparison.filter((id) => id !== key))}>Remove {key}</button>
          </article>;
        })}
      </section>

      {rows.length === 0 && <p role="status">Set at least one weight above zero to rank investigations.</p>}
      <ol className="rank-list" ref={list}>
        {rows.map((r, i) => (
          <li key={r.psi_id} data-id={r.psi_id}>
            <div className="rank-row" data-top={i < 5 || undefined} onClick={() => setOpen(open === r.psi_id ? null : r.psi_id)} style={{ cursor: "pointer" }}>
              <span className="pos num">{String(i + 1).padStart(2, "0")}</span>
              <span className="name">
                <button className="rank-name" aria-expanded={open === r.psi_id} onClick={(e) => { e.stopPropagation(); setOpen(open === r.psi_id ? null : r.psi_id); }}>
                  {r.acronym ?? r.title.split(" ").slice(0, 6).join(" ") + "…"}
                </button>
                <span>{r.psi_id}: {r.title}</span>
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
