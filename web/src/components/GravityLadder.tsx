import { meta, ranking } from "../lib/content";

// Where the analyzed flame tests sit on the gravity axis. Stops are placed at their true gravity (0 to 1 g).
const W = 1000, H = 340, L = 60, R = 60, BASE = 250, TOP = 40;
const x = (g: number) => Math.round(L + g * (W - L - R));

export default function GravityLadder() {
  const orbit = ranking.investigations.filter((i) => /ISS|Cygnus/.test(i.flight_platform ?? "")).length;
  const stops = [
    { g: 0, name: "Orbit (ISS)", value: `${meta.counts.gas_flame_tests} flame tests`, sub: `${orbit} investigations`, kind: "data" },
    { g: 0.165, name: "Moon", value: "0 tests", sub: "0.165 g", kind: "gap" },
    { g: 0.38, name: "Mars", value: "0 tests", sub: "0.38 g", kind: "gap" },
    { g: 1, name: "Earth", value: "Not in this dataset", sub: "1 g, ground reference", kind: "context" },
  ];
  return (
    <figure className="ladder" style={{ margin: 0 }}>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img"
        aria-label={stops.map((s) => `${s.name}: ${s.value}`).join("; ")}>
        <defs>
          <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="8" stroke="var(--line-2)" strokeWidth="2" />
          </pattern>
        </defs>
        <line x1={L} x2={W - R} y1={BASE} y2={BASE} stroke="var(--line-2)" strokeWidth={2} />
        <rect x={x(0) + 18} y={BASE - 8} width={x(1) - x(0) - 36} height={16} rx={8} fill="rgba(255,176,74,0.06)" stroke="var(--soot)" strokeDasharray="5 5" opacity={0.7} />
        <text x={(x(0.165) + x(0.38)) / 2} y={BASE + 74} textAnchor="middle" style={{ fill: "var(--soot)" }}>No flame data between orbit and Earth</text>
        {stops.map((s, i) => {
          const cx = x(s.g);
          const h = s.kind === "data" ? BASE - TOP : 90;
          return (
            <g key={s.name} className="ladder-stop" style={{ animationDelay: `${i * 80}ms` }}>
              {s.kind === "data" && <rect x={cx - 26} y={BASE - h} width={52} height={h} rx={8} fill="var(--accent)" className="ladder-bar" />}
              {s.kind === "gap" && <rect x={cx - 26} y={BASE - h} width={52} height={h} rx={8} fill="none" stroke="var(--soot)" strokeDasharray="5 5" />}
              {s.kind === "context" && <rect x={cx - 26} y={BASE - h} width={52} height={h} rx={8} fill="url(#hatch)" stroke="var(--line-2)" />}
              <circle cx={cx} cy={BASE} r={7} fill={s.kind === "data" ? "var(--accent)" : "var(--bg)"} stroke={s.kind === "gap" ? "var(--soot)" : "var(--ink-2)"} strokeWidth={2} />
              <text x={cx} y={BASE - h - 26} textAnchor="middle" style={{ fill: "var(--ink)", fontSize: 15, fontFamily: "var(--font-sans)", fontWeight: 600 }}>{s.value}</text>
              <text x={cx} y={BASE - h - 8} textAnchor="middle">{s.kind === "data" ? s.sub : ""}</text>
              <text x={cx} y={BASE + 30} textAnchor="middle" style={{ fill: "var(--ink)", fontSize: 14, fontFamily: "var(--font-sans)" }}>{s.name}</text>
              <text x={cx} y={BASE + 48} textAnchor="middle">{s.kind === "data" ? "≈ 0 g" : s.sub}</text>
            </g>
          );
        })}
      </svg>
    </figure>
  );
}
