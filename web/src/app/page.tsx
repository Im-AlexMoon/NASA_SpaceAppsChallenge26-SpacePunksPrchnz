import Link from "next/link";
import BurnCompare from "../components/BurnCompare";
import CoverageMap from "../components/CoverageMap";
import FlameCanvas from "../components/FlameCanvas";
import { meta, reference } from "../lib/content";

const glyphs = {
  atmosphere: (
    <svg viewBox="0 0 200 96" width="100%" height="96" aria-hidden="true">
      <path d="M8 84 C60 82 90 70 120 44 S170 10 192 8" fill="none" stroke="currentColor" strokeWidth="2" />
      <path d="M8 80 C60 76 90 60 120 34 S170 2 192 2 L192 16 C170 18 150 34 120 54 S60 88 8 88Z" fill="currentColor" opacity="0.14" />
      <circle cx="120" cy="44" r="5" fill="#f4f6f9" />
    </svg>
  ),
  findings: (
    <svg viewBox="0 0 200 96" width="100%" height="96" aria-hidden="true">
      {[0, 1, 2, 3, 4].map((i) => (
        <g key={i}>
          <rect x={8} y={8 + i * 18} width={184} height={10} rx={5} fill="currentColor" opacity={0.1} />
          <rect x={8} y={8 + i * 18} width={[150, 120, 96, 70, 40][i]} height={10} rx={5} fill="currentColor" opacity={i === 0 ? 1 : 0.55} />
        </g>
      ))}
    </svg>
  ),
  investigations: (
    <svg viewBox="0 0 200 96" width="100%" height="96" aria-hidden="true">
      {[82, 70, 58, 50, 41, 33, 26].map((h, i) => (
        <rect key={i} x={10 + i * 27} y={92 - h} width={18} height={h} rx={4} fill="currentColor" opacity={i < 3 ? 1 : 0.35} />
      ))}
    </svg>
  ),
  gaps: (
    <svg viewBox="0 0 200 96" width="100%" height="96" aria-hidden="true">
      {[[20, 60], [32, 52], [28, 72], [44, 64], [40, 40], [150, 30], [162, 44], [172, 26], [158, 60], [180, 52]].map(([cx, cy], i) => (
        <circle key={i} cx={cx} cy={cy} r={4} fill="currentColor" />
      ))}
      <rect x={70} y={22} width={58} height={52} rx={6} fill="none" stroke="#ffb04a" strokeDasharray="4 4" strokeWidth="1.5" />
    </svg>
  ),
};

export default function Home() {
  const iss = reference("iss_cabin");
  const exploration = reference("exploration_8p2_34");
  return (
    <>
      <section className="hero" aria-labelledby="hero-title">
        <FlameCanvas />
        <div className="wrap hero-copy" data-enter>
          <p className="eyebrow">NASA PSI combustion experiments in microgravity</p>
          <h1 id="hero-title">Fire safety evidence for space habitats</h1>
          <p className="lede">
            Choose the air of a future habitat and see how long a flame lasts, read from real flames on the ISS and
            graded by how much evidence stands behind the number.
          </p>
          <div className="actions">
            <Link className="btn btn-primary" href="/dashboard">
              Open the dashboard
            </Link>
            <Link className="btn btn-ghost" href="/atmosphere">
              Explore an atmosphere
            </Link>
          </div>
          <div className="hero-facts">
            <div>
              <strong className="num">{meta.counts.investigations}</strong>
              <span className="label">Investigations</span>
            </div>
            <div>
              <strong className="num">{meta.counts.gas_flame_tests}</strong>
              <span className="label">Flame tests</span>
            </div>
            <div>
              <strong className="num">0</strong>
              <span className="label">Partial-gravity tests</span>
            </div>
          </div>
        </div>
      </section>

      <section className="screen" aria-labelledby="why-title">
        <div className="wrap stack" style={{ gap: 36 }}>
          <div className="section-head">
            <p className="eyebrow">Why it matters</p>
            <h2 id="why-title">A fire in space has nowhere to go</h2>
            <p className="lede">
              Crews cannot step outside, and the air of future habitats is planned with more oxygen at lower pressure
              than the ISS cabin. How flames behave in that air has barely been measured.
            </p>
          </div>
          <ol className="story">
            <li>
              <span className="num">01</span>
              <h3>What we did</h3>
              <p>Read {meta.counts.investigations} NASA combustion investigations and {meta.counts.gas_flame_tests} flame tests flown on the ISS, and turned them into one consistent, versioned dataset.</p>
            </li>
            <li>
              <span className="num">02</span>
              <h3>What we measure</h3>
              <p>How long a flame keeps burning in a given air, and the chance it is still burning after 30 or 60 seconds, each with an evidence level.</p>
            </li>
            <li>
              <span className="num">03</span>
              <h3>Why that helps</h3>
              <p>It lets designers compare candidate habitat atmospheres, decide where detection and suppression matter most, and see which experiment is still missing.</p>
            </li>
            <li>
              <span className="num">04</span>
              <h3>How it scales</h3>
              <p>Every number traces back to a NASA file through the same open pipeline, so a new PSI campaign can be added and checked the same way.</p>
            </li>
          </ol>
          <div className="actions">
            <Link className="btn btn-primary" href="/dashboard">See the evidence</Link>
            <Link className="link" href="/methods">How every number is made</Link>
          </div>
        </div>
      </section>

      {meta.publication.findings.enabled && meta.publication.model_readings.enabled && (
      <section className="screen" aria-labelledby="air-title">
        <div className="wrap">
          <div className="section-head">
            <p className="eyebrow">Finding F-03 from ISS measurements</p>
            <h2 id="air-title">Nearby tests had longer burn durations under exploration conditions</h2>
            <p className="lede">Median duration among flames that went out on their own. The two groups used different mixes of fuels.</p>
          </div>
          {iss && exploration && <BurnCompare lanes={[iss, exploration].flatMap((reading) => {
            const seconds = reading.nearby.median_burn_s_self_extinguished;
            return seconds == null ? [] : [{
              name: reading.key === "iss_cabin" ? "ISS cabin" : "Exploration atmosphere",
              air: Math.round(reading.inputs.xo2 * 100) + "% oxygen at " + reading.inputs.p_kpa.toFixed(1) + " kPa",
              seconds, n: reading.nearby.n_self_extinguished,
            }];
          })} />}
          <div className="actions">
            <Link className="link" href="/findings#F-03">
              Read the comparison and its limits
            </Link>
          </div>
        </div>
      </section>
      )}

      <section className="screen" aria-labelledby="ways-title">
        <div className="wrap">
          <div className="section-head">
            <p className="eyebrow">Go deeper</p>
            <h2 id="ways-title">Compare conditions, rank studies and find what is missing</h2>
          </div>
          <div className="cards">
            <Link className="card" href="/atmosphere">
              <div className="glyph">{glyphs.atmosphere}</div>
              <span className="label">Predict</span>
              <h3>Atmosphere explorer</h3>
              <p>Oxygen and pressure in, burn duration out, with its evidence level.</p>
              <span className="go">Open explorer</span>
            </Link>
            <Link className="card" href="/findings">
              <div className="glyph">{glyphs.findings}</div>
              <span className="label">Understand</span>
              <h3>Five findings</h3>
              <p>Physical laws with confidence intervals, one negative result included.</p>
              <span className="go">Read findings</span>
            </Link>
            <Link className="card" href="/investigations">
              <div className="glyph">{glyphs.investigations}</div>
              <span className="label">Find</span>
              <h3>Ranked investigations</h3>
              <p>All 24 PSI studies, ordered for your role and your own weights.</p>
              <span className="go">Rank them</span>
            </Link>
            <Link className="card" href="/gaps">
              <div className="glyph">{glyphs.gaps}</div>
              <span className="label">Gaps</span>
              <h3>Where the analyzed evidence is limited</h3>
              <p>See where the reference conditions lack nearby measurements.</p>
              <span className="go">See the gaps</span>
            </Link>
          </div>
        </div>
      </section>

      {meta.publication.findings.enabled && <section className="screen" aria-labelledby="gap-title">
        <div className="wrap grid-gap">
          <div className="section-head">
            <p className="eyebrow">Evidence gap in Finding F-04</p>
            <h2 id="gap-title">The analyzed dataset has no normal-flame tests near the lunar reference atmosphere</h2>
            <p className="lede">
              Every dot is a normal flame tested on the ISS. The dashed window around the lunar-base atmosphere is
              empty. The analyzed tests do not measure the effect of lunar or Martian gravity.
            </p>
            <div className="actions">
              <Link className="btn btn-ghost" href="/gaps">
                See the gaps
              </Link>
            </div>
          </div>
          <div className="panel">
            <CoverageMap />
          </div>
        </div>
      </section>}
    </>
  );
}
