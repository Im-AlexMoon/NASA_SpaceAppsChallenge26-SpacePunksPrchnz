import type { Metadata } from "next";
import Link from "next/link";
import CoverageMap from "../../components/CoverageMap";
import { reference } from "../../lib/content";

export const metadata: Metadata = { title: "Knowledge gaps" };

export default function Page() {
  const lunar = reference("lunar_base_upper");
  const ci = lunar.prediction?.median_burn_s_90ci;
  return (
    <div className="page">
      <div className="wrap stack" style={{ gap: 40 }}>
        <header className="page-head" data-enter style={{ marginBottom: 0 }}>
          <p className="eyebrow">Gaps · Finding F-04</p>
          <h1>What NASA has not tested yet</h1>
          <p className="lede">The atmospheres planned for the Moon and Mars sit where the ISS flame record is thin or empty.</p>
        </header>

        <div className="gap-list">
          <div className="card">
            <strong className="num">0</strong>
            <h3>Normal flames near lunar-base air</h3>
            <p>No normal flame within ±5 points of O₂ and ±25% of pressure around 30% O₂ / 70 kPa.</p>
          </div>
          <div className="card">
            <strong className="num">0</strong>
            <h3>CFI-G normal flames at 24–33% O₂</h3>
            <p>Flame Design has 6 ethylene flames near 30% O₂, all at 1 atm and without a recorded burn time.</p>
          </div>
          <div className="card">
            <strong className="num">0</strong>
            <h3>Tests in partial gravity</h3>
            <p>Every PSI combustion test ran in microgravity. Lunar and Martian values are bounds, never measurements.</p>
          </div>
        </div>

        <section className="grid-gap panel" aria-label="Coverage map">
          <div className="section-head">
            <h2 style={{ fontSize: "clamp(26px,3vw,36px)" }}>The model fills the gap, with a warning</h2>
            <p className="muted">
              Inside the empty window M-01 v2 reads {lunar.prediction?.median_burn_s.toFixed(0)} s
              {ci ? ` (90% interval ${ci[0].toFixed(0)}–${ci[1].toFixed(0)} s)` : ""}, an interpolation at{" "}
              {lunar.support.distance_ratio_to_training?.toFixed(2)}× the typical distance between tests. Tier B, not a
              measurement.
            </p>
            <Link className="link" href="/atmosphere">Open the lunar-base reading</Link>
          </div>
          <CoverageMap />
        </section>

        <section className="stack" aria-labelledby="exp-title">
          <h2 id="exp-title" style={{ fontSize: "clamp(26px,3vw,36px)" }}>Experiments that would close it</h2>
          <ol className="steps">
            <li>
              <div className="card">
                <h3>Spherical flames at 30% O₂ / 70 kPa</h3>
                <p>With the ACME hardware on the ISS. Turns the lunar-base reading from tier B into tier A. (REC-02)</p>
              </div>
            </li>
            <li>
              <div className="card">
                <h3>A sweep across 24–33% O₂</h3>
                <p>At reduced pressure, where exploration habitats will actually operate. (REC-02, REC-03)</p>
              </div>
            </li>
            <li>
              <div className="card">
                <h3>The same set in partial gravity</h3>
                <p>Parabolic flights or an ISS centrifuge, to measure what buoyancy does at 0.165 g and 0.38 g. (REC-05)</p>
              </div>
            </li>
          </ol>
        </section>
      </div>
    </div>
  );
}
