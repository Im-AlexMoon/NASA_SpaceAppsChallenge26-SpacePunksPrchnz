import type { Metadata } from "next";
import TierBadge from "../../components/TierBadge";
import Tex from "../../components/Tex";
import { dashboard, meta, ranking, readings } from "../../lib/content";

export const metadata: Metadata = { title: "Methods & sources" };

const STEPS = [
  ["Catalog and tables", "24 PSI investigations and their experimental tables, stored raw and immutable, then typed and harmonized. Missing values stay missing."],
  ["Sensor time series", "3,325 per-test files from the ACME rig. A detector re-derives each flame's end and agrees with NASA's labels on 99.6% of extinction modes."],
  ["ISS flame video", "All 335 CFI-G videos measured on Google Cloud Run. Video burn times match the table with Spearman 0.97 over 264 flames."],
  ["Burn-time law", `A log-logistic survival model on ${meta.counts.model_cohort} flames from ${meta.counts.model_days} days, validated by leaving one operations day out.`],
  ["Ranking", "Seven criteria scored from versioned inputs and combined with published weights. Every weight can be changed."],
  ["Physics review", "The release records physics review and identifies candidate content."],
];


const c = (term: string) => dashboard.model?.coef_table.find((row) => row.term === term)?.coef.toFixed(2) ?? "";
const MODELS = [
  {
    name: "M-01 v2 · Burn-time law", status: "Published",
    q: "How long does a spherical gas flame keep burning in a given air, and what is the chance it is still burning at 30 s or 60 s?",
    tex: `\\ln t = ${c("Intercept")} ${c("inv_tad")}\\,\\tfrac{1000}{T_{ad}} ${c("log_p")}\\ln p ${c("log_mtot")}\\ln \\dot m + ${c("log_L")}\\ln L + \\sigma\\,\\varepsilon`,
    how: "A survival model: the logarithm of burn time is a straight line in four physical groups plus a log-logistic error. Flames whose fuel flow was cut before they went out are censored, not dropped, so long-lived flames are not underestimated.",
    check: `Leave one operations day out: C-index ${readings.metrics.oof_c_index.toFixed(2)} on ${meta.counts.model_cohort} flames over ${meta.counts.model_days} days. Fitted on CFI-G alone it ranks unseen Flame Design flames with C ${dashboard.transfer.c_index}. 90% intervals from a day bootstrap.`,
    limit: "Microgravity, gas fuels, spherical burner flames, inside the tested range. Not a fire-response time.",
  },
  {
    name: "Oxygen effect · Cox and Weibull models", status: "Finding F-01",
    q: "How much does each extra 5 points of oxygen change the risk that a flame goes out?",
    tex: "h(t\\mid x) = h_0(t)\\,e^{\\beta x_{O_2}}",
    how: "A Cox proportional-hazards model with standard errors clustered by test day, and a Weibull time model as a cross-check. One reports the instantaneous risk of going out, the other how burn time stretches.",
    check: `Hazard ratio ${dashboard.effects.rows[0].value} (95% ${dashboard.effects.rows[0].ci95.join("–")}) and time ratio ${dashboard.effects.rows[1].value} per +0.05 O₂, n = ${dashboard.effects.rows[0].n}.`,
    limit: "CFI-G normal flames tested at two oxygen regimes only; nothing measured between them.",
  },
  {
    name: "Evidence levels · Readings by atmosphere", status: "Every reading",
    q: "How much should a number for this air be trusted?",
    tex: "d = \\min_i \\lVert z - z_i \\rVert",
    how: "Each requested air is placed in the same standardized physical space as the tested flames. Real tests nearby give tier A, the model inside its support gives tier B, and anything farther gives tier C with no number.",
    check: "The distance is reported as a multiple of the typical spacing between tested flames, so the reader sees how far the model is reaching.",
    limit: "Partial gravity is outside every tier: lunar and Martian values are microgravity bounds.",
  },
  {
    name: "Thermochemistry and flame geometry", status: "Calculated inputs",
    q: "How hot can this mixture burn, and where does the flame sit around the burner?",
    tex: "L = -\\ln(1 - Z_{st}), \\quad r_f \\propto \\dfrac{\\dot m}{L}",
    how: "Adiabatic flame temperature and stoichiometric mixture fraction come from chemical equilibrium (Cantera, NASA gas data). The flame-position group L follows the classical quasi-steady picture of a porous spherical burner.",
    check: `Calculated temperatures match the investigators' values with a median difference of +${dashboard.quality.rows.find((q) => q.unit === "K")?.value} K over ${dashboard.quality.rows.find((q) => q.unit === "K")?.n} tests.`,
    limit: "Calculated, not measured. Real ISS flames are transient and lose heat by radiation.",
  },
  {
    name: "Extinction detector and video measurement", status: "Data quality",
    q: "When did each flame really go out, and did it go out on its own?",
    tex: `\\rho_s = ${dashboard.quality.rows[1].value}`,
    how: "A detector re-derives the end of each flame from the sensor time series, and every CFI-G video is measured on Google Cloud Run to track the flame's size over time.",
    check: `${dashboard.quality.rows[0].value}% agreement with NASA's extinction labels; video burn times agree with the table (Spearman ${dashboard.quality.rows[1].value}, n = ${dashboard.quality.rows[1].n}). Flame shrinking warns of self-extinction 5 to 10 s ahead (AUC 0.76).`,
    limit: "The shrinking signal is retrospective; a real-time alarm still needs false-alarm testing.",
  },
  {
    name: "Investigation ranking · MCDA", status: "Investigations page",
    q: `Which of the ${meta.counts.investigations} PSI investigations matter most for a given mission?`,
    tex: "S = \\dfrac{\\sum_d w_d\\, s_d}{\\sum_d w_d}",
    how: "Seven criteria (prevention, detection, suppression, environment, evidence quality, modeling value, maturity) are scored from versioned inputs and combined with published, editable weights.",
    check: `Each single weight is moved by ±${Math.round(ranking.sensitivity.perturbation * 100)}% and the change in the top ${ranking.sensitivity.top_k} is reported, along with joint weight scenarios.`,
    limit: "Scores rank relevance for fire safety, not scientific quality.",
  },
  {
    name: "Ask · Grounded answers", status: "Ask page",
    q: "Can anyone ask a question in plain words and get an answer tied to sources?",
    tex: "\\text{answer} \\subseteq \\text{cited passages}",
    how: "Lexical search (BM25) retrieves reviewed passages; Gemini writes the answer, and every claim must cite a retrieved passage. Any number not found word for word in the cited text is rejected.",
    check: "If an answer cannot be fully verified, the app shows the relevant passages instead.",
    limit: "Answers cover the reviewed documents only.",
  },
  {
    name: "Earlier and exploratory models", status: "Superseded",
    q: "What did we try before, and why did it change?",
    tex: "\\ell_{\\text{Weibull}} = -1.55 \\;<\\; \\ell_{\\text{log-logistic}} = -1.34",
    how: "M1 v1 combined a penalized logistic ignition model with Weibull and Cox duration models; an exploratory Cox model with Kaplan-Meier curves checked proportional hazards. Descriptive effect sizes (Cliff's delta, PCA) are exploratory only.",
    check: "Out of sample, the Weibull error was overconfident (log-likelihood per test shown above), so the published law uses a log-logistic error.",
    limit: "Kept for transparency; not used for readings.",
  },
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


        <section className="stack" aria-labelledby="models-title">
          <h2 id="models-title" style={{ fontSize: "clamp(26px,3vw,36px)" }}>The models, one by one</h2>
          <p className="muted">What each model answers, how it works, how it was checked and where it stops.</p>
          <div className="models">
            {MODELS.map((m) => (
              <article key={m.name} className="model-card">
                <div className="model-top"><h3>{m.name}</h3><span className="chip">{m.status}</span></div>
                <p className="model-q">{m.q}</p>
                <Tex expr={m.tex} display className="model-tex" />
                <dl>
                  <dt>How it works</dt><dd>{m.how}</dd>
                  <dt>How we checked it</dt><dd>{m.check}</dd>
                  <dt>Where it stops</dt><dd>{m.limit}</dd>
                </dl>
              </article>
            ))}
          </div>
        </section>

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
