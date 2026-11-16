import { meta } from "../../lib/content";
import type { Metadata } from "next";
import AtmosphereExplorer from "../../components/AtmosphereExplorer";

export const metadata: Metadata = { title: "Atmosphere explorer" };

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">Evidence from ISS experiments and Model M-01 v2</p>
          <h1>How long does a flame last in this air?</h1>
          <p className="lede">Pick a habitat or set oxygen and pressure. Every reading carries its evidence level.</p>
        </header>
        {meta.publication.model_readings.enabled && meta.publication.model_readings.status !== "reviewed" && <p>Candidate model readings. Physics review is pending.</p>}
        {meta.publication.model_readings.enabled ? <AtmosphereExplorer /> : <p>This section is unavailable in the current release.</p>}
      </div>
    </div>
  );
}
