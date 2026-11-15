// Reviewed content snapshot written by `flamesafe web-content` (ADR-0011). Regenerate, never edit by hand.
import findingsJson from "../content/findings.json";
import metaJson from "../content/meta.json";
import rankingJson from "../content/ranking.json";
import readingsJson from "../content/readings.json";
import testsJson from "../content/tests.json";

export type Tier = "A" | "B" | "C";

export type KeyNumber = {
  name: string;
  value: number | string;
  unit?: string;
  ci95?: number[];
  ci90?: number[];
  n?: number;
  groups?: string;
  method?: string;
};

export type Finding = {
  id: string;
  title: string;
  claim: string;
  pillar: string;
  confidence: string;
  status: string;
  key_numbers: KeyNumber[];
  evidence: Record<string, unknown>;
  physics: string;
  limits: string;
  page: string;
  next_experiment?: string;
};

export type NearbyTest = {
  test_id: string;
  test_day: number;
  fuel: string;
  xo2: number;
  p_kpa: number;
  ignition_outcome: string;
  burn_time_s: number | null;
  extinction_mode: string | null;
};

export type Reading = {
  key: string;
  label: string;
  gravity_g: number;
  inputs: { xo2: number; p_kpa: number; po2_kpa: number; fuel: string; gravity: string };
  tier: Tier;
  tier_label: string;
  prediction: {
    median_burn_s: number;
    median_burn_s_90ci: [number, number];
    p_still_burning_30s: number;
    p_still_burning_60s: number;
  } | null;
  nearby: {
    n_tests: number;
    n_days: number;
    ignition_rate: number | null;
    median_burn_s_self_extinguished: number | null;
    tests: NearbyTest[];
  };
  physics: { tad_k: number | null; zst: number | null };
  support: { distance_ratio_to_training: number | null };
  caveats: string[];
  gravity_effect?: { note: string; tier?: string } | null;
  reason?: string;
};

export type GridPoint = {
  tier: Tier;
  median: number | null;
  ci: [number, number] | null;
  p30: number | null;
  p60: number | null;
  n_near: number;
  obs_median: number | null;
  tad: number | null;
  dist: number | null;
};

export type GasTest = {
  psi_id: string;
  campaign: string;
  test_id: string;
  test_day: number;
  flame_type: string;
  fuel: string;
  xo2: number | null;
  p_kpa: number | null;
  ignition_outcome: string | null;
  extinction_mode: string | null;
  burn_time_s: number | null;
  cool_flame: boolean | null;
};

export const findings = findingsJson.findings as Finding[];
export const meta = metaJson;
export const ranking = rankingJson as unknown as {
  dimensions: Record<string, string>;
  dimension_order: string[];
  environments: string[];
  profiles: Record<string, { label: string; environment: string; weights: Record<string, number> }>;
  sensitivity: {
    perturbation: number;
    top_k: number;
    by_profile: Record<string, { n_perturbations: number; perturbations_changing_top_k: number; max_changed: number }>;
  };
  investigations: {
    psi_id: string;
    acronym: string | null;
    title: string;
    tier: number;
    access_status: string;
    n_gold_tests: number | null;
  }[];
  scores: Record<string, Record<string, number>[]>;
};
export const readings = readingsJson as unknown as {
  model_id: string;
  review: { date: string; phy_reviewer: string; status: string };
  metrics: { oof_c_index: number };
  references: Reading[];
  grid: { xo2: number[]; p_kpa: number[]; points: GridPoint[][] };
};

const cols = testsJson.columns as (keyof GasTest)[];
export const gasTests: GasTest[] = (testsJson.rows as unknown[][]).map((row) =>
  Object.fromEntries(cols.map((c, i) => [c, row[i]])) as GasTest,
);

export const finding = (id: string) => findings.find((f) => f.id === id)!;
export const reference = (key: string) => readings.references.find((r) => r.key === key)!;
