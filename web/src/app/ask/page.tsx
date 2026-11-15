import type { Metadata } from "next";
import AskData from "../../components/AskData";

export const metadata: Metadata = { title: "Ask the data" };

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">Ask · Retrieval over reviewed sources</p>
          <h1>Ask the data</h1>
          <p className="lede">Answers come with the exact passage or query behind them, or not at all.</p>
        </header>
        <AskData />
      </div>
    </div>
  );
}
