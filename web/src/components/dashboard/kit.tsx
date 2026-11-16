// Shared pieces of the executive dashboard: panel frame, scales, Kaplan-Meier and filters over the test table.
import type { GasTest } from "../../lib/content";

export const r2 = (v: number) => Math.round(v * 100) / 100;
export const lin = (d0: number, d1: number, r0: number, r1: number) => (v: number) => r2(r0 + ((v - d0) / (d1 - d0)) * (r1 - r0));
export const logScale = (d0: number, d1: number, r0: number, r1: number) => (v: number) =>
  r2(r0 + (Math.log(Math.min(Math.max(v, d0), d1) / d0) / Math.log(d1 / d0)) * (r1 - r0));
export const median = (xs: number[]) => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};
export const fmtS = (v: number | null) => (v == null ? "—" : v >= 10 ? v.toFixed(0) : v.toFixed(1));

// Oxygen bands follow the two regimes CFI-G actually tested (F-01) plus the gap between them.
export const BANDS = [
  { key: "low", label: "O₂ below 25%", test: (x: number) => x < 0.25, color: "#6f87ad" },
  { key: "mid", label: "O₂ 25–33%", test: (x: number) => x >= 0.25 && x < 0.33, color: "#4f8dff" },
  { key: "high", label: "O₂ 33% and above", test: (x: number) => x >= 0.33, color: "#b9d2ff" },
] as const;

export const CAMPAIGN_COLOR: Record<string, string> = { "CFI-G": "var(--c1)", "Flame Design": "var(--c2)" };

export type Filters = { campaign: string; flame: string; fuel: string; o2: string; p: string };
export const NO_FILTERS: Filters = { campaign: "all", flame: "all", fuel: "all", o2: "all", p: "all" };
export const P_BANDS: Record<string, [number, number]> = { low: [0, 80], ambient: [80, 120], high: [120, 1000] };
export const P_LABEL: Record<string, string> = { low: "Below 80 kPa", ambient: "80–120 kPa", high: "Above 120 kPa" };

export function applyFilters(rows: GasTest[], f: Filters) {
  return rows.filter((t) =>
    (f.campaign === "all" || t.campaign === f.campaign) &&
    (f.flame === "all" || t.flame_type === f.flame) &&
    (f.fuel === "all" || t.fuel === f.fuel) &&
    (f.o2 === "all" || (t.xo2 != null && BANDS.find((b) => b.key === f.o2)!.test(t.xo2))) &&
    (f.p === "all" || (t.p_kpa != null && t.p_kpa >= P_BANDS[f.p][0] && t.p_kpa < P_BANDS[f.p][1])));
}

// Kaplan-Meier on observed flames: event = self-extinguished, censored = flow terminated. Tests with no recorded
// extinction mode are left out, never counted as either.
export function km(rows: GasTest[]) {
  const obs = rows
    .filter((t) => t.ignition_outcome === "yes" && t.burn_time_s != null && (t.extinction_mode === "self_extinguished" || t.extinction_mode === "flow_terminated"))
    .map((t) => ({ t: t.burn_time_s!, e: t.extinction_mode === "self_extinguished" }))
    .sort((a, b) => a.t - b.t);
  const steps: { t: number; s: number; atRisk: number }[] = [{ t: 0, s: 1, atRisk: obs.length }];
  let s = 1, i = 0, n = obs.length;
  while (i < obs.length) {
    const t = obs[i].t;
    let d = 0, c = 0;
    while (i < obs.length && obs[i].t === t) { if (obs[i].e) d++; else c++; i++; }
    if (d) { s *= 1 - d / n; steps.push({ t, s, atRisk: n }); }
    n -= d + c;
  }
  const med = steps.find((p) => p.s <= 0.5)?.t ?? null;
  return { steps, n: obs.length, events: obs.filter((o) => o.e).length, median: med };
}
export const survivalAt = (steps: { t: number; s: number }[], t: number) => {
  let s = 1;
  for (const p of steps) { if (p.t > t) break; s = p.s; }
  return s;
};

export function Panel({ title, note, span = 6, children, id }: { title: string; note?: string; span?: number; children: React.ReactNode; id?: string }) {
  return (
    <section className="dash-panel" style={{ gridColumn: `span ${span}` }} aria-labelledby={id}>
      <h3 id={id}>{title}</h3>
      {children}
      {note && <p className="dash-note">{note}</p>}
    </section>
  );
}
