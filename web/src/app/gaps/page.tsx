import type { Metadata } from "next";
import Link from "next/link";
import GravityLadder from "../../components/GravityLadder";
import { meta, reference } from "../../lib/content";

export const metadata: Metadata = { title: "Knowledge gaps" };

export default function Page() {
  if (!meta.publication.findings.enabled) return <div className="page wrap"><h1>Evidence gaps</h1><p>This section is unavailable in the current release.</p></div>;
  const lunar = reference("lunar_base_upper");
  const ci = lunar?.prediction?.median_burn_s_90ci;
  return (
    <div className="page">
      <div className="wrap stack" style={{ gap: 40 }}>
        <header className="page-head" data-enter style={{ marginBottom: 0 }}>
          <p className="eyebrow">What nobody has measured yet</p>
          <h1>Gaps in the analyzed combustion data</h1>
          <p className="lede">The reference atmospheres help identify where the analyzed flame records are sparse and what measurements would be useful.</p>
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
            <p>The analyzed data do not establish how flame behavior changes in lunar or Martian gravity.</p>
          </div>
        </div>

        <section className="panel stack" aria-labelledby="gravity-title" style={{ gap: 18 }}>
          <div className="section-head">
            <h2 id="gravity-title" style={{ fontSize: "clamp(26px,3vw,36px)" }}>Every flame was burned in orbit</h2>
            <p className="muted">Lunar and Martian habitats sit between orbit and Earth, where no flame data exist. Buoyancy returns there, so any value for the Moon or Mars is a bound, not a measurement.</p>
          </div>
          <GravityLadder />
          {lunar?.prediction && <p className="small">
            For the lunar-base air, M-01 v2 reads {lunar.prediction.median_burn_s.toFixed(0)} s in microgravity
            {ci ? ` (90% interval ${ci[0].toFixed(0)}–${ci[1].toFixed(0)} s)` : ""}, an interpolation at{" "}
            {lunar.support.distance_ratio_to_training?.toFixed(2)}× the typical distance between tests. Tier B, not a measurement.{" "}
            <Link className="link" href="/atmosphere#lunar_base_upper">Oxygen–pressure coverage in the explorer</Link>
          </p>}
        </section>

        <section className="stack" aria-labelledby="exp-title">
          <h2 id="exp-title" style={{ fontSize: "clamp(26px,3vw,36px)" }}>Experiments that would close it</h2>
          <ol className="steps">
            <li>
              <div className="card">
                <h3>Spherical flames at 30% O₂ / 70 kPa</h3>
                <p>With the ACME hardware on the ISS. This would provide measured evidence near the lunar reference. See REC-02.</p>
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
