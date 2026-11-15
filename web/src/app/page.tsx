import Link from "next/link";
import BurnCompare from "../components/BurnCompare";
import CoverageMap from "../components/CoverageMap";
import FlameCanvas from "../components/FlameCanvas";
import { meta } from "../lib/content";

const Arrow = () => (
  <svg className="arrow" width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
    <path d="M2 7h9M7.5 3.5 11 7l-3.5 3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

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
  return (
    <>
      <section className="hero" aria-labelledby="hero-title">
        <FlameCanvas />
        <div className="wrap hero-copy" data-enter>
          <p className="eyebrow">NASA PSI · Combustion in microgravity</p>
          <h1 id="hero-title">Fire safety evidence for space habitats</h1>
          <p className="lede">
            Choose the air of a future habitat and see how long a flame lasts, read from real flames on the ISS and
            graded by how much evidence stands behind the number.
          </p>
          <div className="actions">
            <Link className="btn btn-primary" href="/atmosphere">
              Explore an atmosphere <Arrow />
            </Link>
            <Link className="btn btn-ghost" href="/findings">
              Read the findings
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

      <section className="screen" aria-labelledby="air-title">
        <div className="wrap">
          <div className="section-head">
            <p className="eyebrow">Finding F-03 · Measured on the ISS</p>
            <h2 id="air-title">Exploration air keeps a flame alive seven times longer</h2>
            <p className="lede">Same spherical flame, less nitrogen around it. Median burn before it went out on its own.</p>
          </div>
          <BurnCompare
            lanes={[
              { name: "ISS cabin", air: "21% O₂ · 101 kPa", seconds: 9, n: 21 },
              { name: "Exploration habitat", air: "34% O₂ · 56.5 kPa", seconds: 62.5, n: 12 },
            ]}
          />
          <div className="actions">
            <Link className="link" href="/findings#F-03">
              21 and 12 self-extinguished flames · see the evidence
            </Link>
          </div>
        </div>
      </section>

      <section className="screen" aria-labelledby="ways-title">
        <div className="wrap">
          <div className="section-head">
            <p className="eyebrow">Four ways in</p>
            <h2 id="ways-title">Find, understand and predict, then see what is missing</h2>
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
              <h3>What NASA has not tested</h3>
              <p>The conditions a lunar base needs and no experiment has covered.</p>
              <span className="go">See the gaps</span>
            </Link>
          </div>
        </div>
      </section>

      <section className="screen" aria-labelledby="gap-title">
        <div className="wrap grid-gap">
          <div className="section-head">
            <p className="eyebrow">Finding F-04 · Knowledge gap</p>
            <h2 id="gap-title">No normal flame has been tested in lunar-base air</h2>
            <p className="lede">
              Every dot is a normal flame tested on the ISS. The dashed window around the lunar-base atmosphere is
              empty, and no test anywhere was run in lunar or Martian gravity.
            </p>
            <div className="actions">
              <Link className="btn btn-ghost" href="/gaps">
                See the gaps <Arrow />
              </Link>
            </div>
          </div>
          <div className="panel">
            <CoverageMap />
          </div>
        </div>
      </section>
    </>
  );
}
