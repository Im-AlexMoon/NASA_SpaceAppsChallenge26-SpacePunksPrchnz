import type { Metadata } from "next";
import Link from "next/link";
import { meta, findings, type KeyNumber } from "../../lib/content";
import Tex from "../../components/Tex";

export const metadata: Metadata = { title: "Findings" };

const PILLAR: Record<string, string> = { prevention: "Prevention", detection: "Detection", suppression: "Suppression" };

const plain = (s: string) => s.replace(/\s*(->|→)\s*/g, " to ");
const tex = (v: number) => String(v);
const UNIT_TEX: Record<string, string> = { s: String.raw`\,\mathrm{s}`, K: String.raw`\,\mathrm{K}` };
const interval = (a: number, b: number) => String.raw`\;[${tex(a)},\,${tex(b)}]`;

function Num({ k }: { k: KeyNumber }) {
  const ci = k.ci95 ?? k.ci90;
  const level = k.ci95 ? "95%" : "90%";
  const unit = k.unit ? UNIT_TEX[k.unit] ?? "" : "";
  const sub = [ci ? `${level} interval` : null, k.groups ?? null].filter(Boolean).join(", ");
  return (
    <div>
      {typeof k.value === "number" ? (
        <strong className="num">
          <Tex expr={`${tex(k.value)}${unit}${ci ? interval(ci[0], ci[1]) : ""}`} />
        </strong>
      ) : (
        <strong className="num" style={{ fontSize: 19, lineHeight: 1.3 }}>{plain(k.value)}</strong>
      )}
      <span>{plain(k.name)}</span>
      {(k.n || sub) && (
        <span className="num">
          {k.n ? <Tex expr={`n = ${k.n}`} /> : null}
          {k.n && sub ? ", " : null}
          {sub}
        </span>
      )}
    </div>
  );
}

const GLOSSARY: [string, string][] = [
  ["T_{ad}", "calculated adiabatic flame temperature: how hot the flame would be with no heat loss"],
  ["p", "chamber pressure"],
  [String.raw`\dot m`, "fuel flow supplied by the burner"],
  [String.raw`L = -\ln(1 - Z_{st})`, "flame position term from the stoichiometric mixture fraction: larger L means the flame sits closer to the burner"],
];

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">What the data say</p>
          <h1>Findings from ISS combustion experiments</h1>
          <p className="lede">Each finding states its numbers, the physics behind them and where they stop being valid.</p>
        </header>
        {findings.length === 0 && <p>Findings are unavailable in the current release.</p>}
        {findings.map((f) => (
          <article key={f.id} id={f.id} className="finding" style={{ scrollMarginTop: 90 }}>
            <div className="finding-id">
              <strong>{f.id}</strong>
              <span className="chip">{PILLAR[f.pillar] ?? f.pillar}</span>
              {(f.status !== "reviewed" || meta.publication.findings.status !== "reviewed") && <span className="chip">Candidate</span>}
              <span className="chip">{f.confidence} confidence</span>
            </div>
            <div className="finding-body">
              <h2>{plain(f.title)}</h2>
              {f.id === "F-02" ? (
                <>
                  <Tex
                    display
                    className="equation"
                    label="ln t equals 15.8 minus 13.4 times 1000 over T ad, minus 0.41 ln p, minus 1.20 ln m-dot, plus 2.12 ln L"
                    expr={String.raw`\ln t = 15.8 - 13.4\,\frac{1000}{T_{ad}} - 0.41\ln p - 1.20\ln\dot m + 2.12\ln L`}
                  />
                  <dl className="muted" style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "4px 14px", margin: "8px 0 12px" }}>
                    {GLOSSARY.map(([sym, text]) => (
                      <div key={sym} style={{ display: "contents" }}>
                        <dt><Tex expr={sym} /></dt>
                        <dd style={{ margin: 0 }}>{text}</dd>
                      </div>
                    ))}
                  </dl>
                  <p className="muted">
                    Fitted on CFI-G alone, it ranks the burn times of Flame Design ethylene flames it never saw (C-index 0.93,
                    calibration slope 1.16).
                  </p>
                </>
              ) : (
                <p className="muted" style={{ fontSize: 17 }}>{plain(f.claim)}</p>
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
