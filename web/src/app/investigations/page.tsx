import { meta } from "../../lib/content";
import type { Metadata } from "next";
import RankingBoard from "../../components/RankingBoard";

export const metadata: Metadata = { title: "Investigations" };

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">NASA PSI combustion investigations</p>
          <h1>Which studies matter for your mission?</h1>
          <p className="lede">Seven transparent criteria, weighted for your role. Open any row to see why it ranks there.</p>
        </header>
        {meta.publication.ranking.enabled ? <RankingBoard /> : <p>This section is unavailable in the current release.</p>}
      </div>
    </div>
  );
}
