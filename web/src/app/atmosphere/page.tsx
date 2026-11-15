import type { Metadata } from "next";
import AtmosphereExplorer from "../../components/AtmosphereExplorer";

export const metadata: Metadata = { title: "Atmosphere explorer" };

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">Predict · Model M-01 v2</p>
          <h1>How long does a flame last in this air?</h1>
          <p className="lede">Pick a habitat or set oxygen and pressure. Every reading carries its evidence level.</p>
        </header>
        <AtmosphereExplorer />
      </div>
    </div>
  );
}
