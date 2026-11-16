import Link from "next/link";
import type { Metadata } from "next";
import AskData from "../../components/AskData";

export const metadata: Metadata = { title: "Ask the data" };

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">Evidence and queries</p>
          <h1>Ask the data</h1>
          <p className="lede">Explore the study through cited passages or run a filtered query against the curated data.</p>
        </header>
        <p className="muted">The <Link href="/findings">public findings</Link> and <Link href="/atmosphere">atmosphere evidence</Link> are available without a dashboard token.</p>
        <AskData />
      </div>
    </div>
  );
}
