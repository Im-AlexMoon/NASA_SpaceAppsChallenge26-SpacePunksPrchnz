import type { Tier } from "../lib/content";

const LABEL: Record<Tier, string> = { A: "Measured nearby", B: "Model interpolation", C: "Outside model support" };

export default function TierBadge({ tier }: { tier: Tier }) {
  return (
    <span className={`tier tier-${tier}`}>
      <b>{tier}</b>
      {LABEL[tier]}
    </span>
  );
}
