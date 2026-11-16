import type { Metadata } from "next";
import TierBadge from "../../components/TierBadge";
import { meta, readings } from "../../lib/content";

export const metadata: Metadata = { title: "Methods & sources" };

const STEPS = [
  ["Catalog and tables", "24 PSI investigations and their experimental tables, stored raw and immutable, then typed and harmonized. Missing values stay missing."],
  ["Sensor time series", "3,325 per-test files from the ACME rig. A detector re-derives each flame's end and agrees with NASA's labels on 99.6% of extinction modes."],
  ["ISS flame video", "All 335 CFI-G videos measured on Google Cloud Run. Video burn times match the table with Spearman 0.97 over 264 flames."],
  ["Burn-time law", `A log-logistic survival model on ${meta.counts.model_cohort} flames from ${meta.counts.model_days} days, validated by leaving one operations day out.`],
  ["Ranking", "Seven criteria scored from versioned inputs and combined with published weights. Every weight can be changed."],
  ["Physics review", "The release records physics review and identifies candidate content."],
];

export default function Page() {
  return (
    <div className="page">
      <div className="wrap stack" style={{ gap: 48 }}>
        <header className="page-head" data-enter style={{ marginBottom: 0 }}>
          <p className="eyebrow">Evidence version {meta.build_id}</p>
          <h1>How every number is made</h1>
          <p className="lede">From NASA&apos;s public files to a reading on screen, each step is versioned and checked.</p>
        </header>

        <ol className="steps">
          {STEPS.map(([t, d]) => (
            <li key={t}>
              <div className="card" style={{ height: "100%" }}>
                <h3>{t}</h3>
                <p>{d}</p>
              </div>
            </li>
          ))}
        </ol>

        <section className="stack" aria-labelledby="tiers-title">
          <h2 id="tiers-title" style={{ fontSize: "clamp(26px,3vw,36px)" }}>Three evidence levels</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Level</th><th>When</th><th>What you see</th></tr></thead>
              <tbody>
                <tr><td><TierBadge tier="A" /></td><td>At least 5 real tests from 2 or more days within ±0.05 O₂ and ±25% pressure</td><td>Observations are shown separately. A model estimate appears only within its supported domain.</td></tr>
                <tr><td><TierBadge tier="B" /></td><td>Inside the tested range of every physical input and close enough to tested flames</td><td>The model median with its 90% interval</td></tr>
                <tr><td><TierBadge tier="C" /></td><td>Outside the tested range of any physical input, or too far from every tested flame</td><td>No number, and the experiment that is missing</td></tr>
              </tbody>
            </table>
          </div>
          <p className="small">The analyzed tests do not establish the effect of lunar or Martian gravity. The estimate uses microgravity at the selected atmosphere.</p>
        </section>

        {meta.publication.model_readings.enabled && <section className="stack" aria-labelledby="model-title">
          <h2 id="model-title" style={{ fontSize: "clamp(26px,3vw,36px)" }}>Model M-01 v2</h2>
          <div className="stats" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            <div><span className="label">Out-of-sample C-index</span><strong className="num">{readings.metrics.oof_c_index.toFixed(2)}</strong></div>
            <div><span className="label">Flames and days</span><strong className="num">{meta.counts.model_cohort} flames over {meta.counts.model_days} days</strong></div>
            <div><span className="label">Interval</span><strong className="num">90%, day bootstrap</strong></div>
            <div><span className="label">Reviewed</span><strong>{readings.review.phy_reviewer}</strong></div>
          </div>
          <p className="small">Domain: readings for spherical ethane, propane and butane flames in microgravity, inside the tested range. Model card M-01 in the repository.</p>
        </section>}

        <section className="stack" aria-labelledby="src-title">
          <h2 id="src-title" style={{ fontSize: "clamp(26px,3vw,36px)" }}>Sources</h2>
          <div className="table-wrap">
            <table>
              <tbody>
                <tr><td>NASA Physical Sciences Informatics</td><td>PSI-159 ACME CFI-G and PSI-10 ACME Flame Design tables, sensor files and video; catalog of 24 combustion investigations</td></tr>
                <tr><td>NASA Technical Reports Server</td><td>Habitat atmosphere studies behind the reference atmospheres</td></tr>
                <tr><td>Thermochemistry</td><td>Flame temperature and stoichiometric mixture fraction calculated with Cantera (NASA gas data)</td></tr>
                <tr><td>Code</td><td>Python pipeline, FastAPI evidence service and this Next.js app, open source on GitHub</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
