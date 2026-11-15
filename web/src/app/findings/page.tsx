import type { Metadata } from "next";
import Link from "next/link";
import { findings, type KeyNumber } from "../../lib/content";

export const metadata: Metadata = { title: "Findings" };

const PILLAR: Record<string, string> = { prevention: "Prevention", detection: "Detection", suppression: "Suppression" };

function Num({ k }: { k: KeyNumber }) {
  const ci = k.ci95 ?? k.ci90;
  const level = k.ci95 ? "95%" : "90%";
  return (
    <div>
      <strong className="num" style={typeof k.value === "string" ? { fontSize: 19, lineHeight: 1.3 } : undefined}>
        {k.value}
        {k.unit && typeof k.value === "number" ? <span style={{ fontSize: 15, color: "var(--ink-3)", marginLeft: 3 }}>{k.unit === "per 1000/K" ? "" : k.unit}</span> : null}
      </strong>
      <span>{k.name}</span>
      {ci && <span className="num">{level} CI {ci[0]} – {ci[1]}{k.n ? ` · n = ${k.n}` : ""}</span>}
      {!ci && k.n ? <span className="num">n = {k.n}{k.groups ? ` · ${k.groups}` : ""}</span> : null}
    </div>
  );
}

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">Understand · Reviewed by PHY</p>
          <h1>Five things the ISS flames show</h1>
          <p className="lede">Each finding states its numbers, the physics behind them and where they stop being valid.</p>
        </header>
        {findings.map((f) => (
          <article key={f.id} id={f.id} className="finding" style={{ scrollMarginTop: 90 }}>
            <div className="finding-id">
              <strong>{f.id}</strong>
              <span className="chip">{PILLAR[f.pillar] ?? f.pillar}</span>
              <span className="chip">{f.confidence} confidence</span>
            </div>
            <div className="finding-body">
              <h2>{f.title}</h2>
              {f.id === "F-02" ? (
                <>
                  <div className="equation" aria-label="ln t equals 15.8 minus 13.4 times 1000 over Tad, minus 0.41 ln p, minus 1.20 ln m-dot, plus 2.12 ln L">
                    ln t = 15.8 − 13.4·(1000/T<sub>ad</sub>) − 0.41·ln p − 1.20·ln ṁ + 2.12·ln L
                  </div>
                  <p className="muted">
                    Fitted on CFI-G alone, it ranks the burn times of Flame Design ethylene flames it never saw (C-index 0.93,
                    calibration slope 1.16). T<sub>ad</sub> is calculated, p is pressure, ṁ the burner flow and L = −ln(1 − Z<sub>st</sub>).
                  </p>
                </>
              ) : (
                <p className="muted" style={{ fontSize: 17 }}>{f.claim}</p>
              )}
              <div className="kn">{f.key_numbers.slice(0, 4).map((k) => <Num key={k.name} k={k} />)}</div>
              <details className="more">
                <summary>Physics and limits</summary>
                <div className="more-body">
                  <p><span className="label">Physics</span><br />{f.physics}</p>
                  <p><span className="label">Limits</span><br />{f.limits}</p>
                  {f.next_experiment && <p><span className="label">Next experiment</span><br />{f.next_experiment}</p>}
                </div>
              </details>
              {f.id === "F-04" && <Link className="link" href="/gaps">See the gap on the map</Link>}
              {f.id === "F-03" && <Link className="link" href="/atmosphere">Try both atmospheres</Link>}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
