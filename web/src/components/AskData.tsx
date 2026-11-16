"use client";
import { useState } from "react";
import type { components } from "../generated/api";

type Answer = components["schemas"]["AnswerResult"];
type Query = components["schemas"]["ToolRequest"];
type Tool = components["schemas"]["ToolResult"];

function ToolPanel({ result }: { result: Tool }) {
  const rows = result.results as Record<string, unknown>[];
  const columns = rows.length ? Object.keys(rows[0]) : [];
  return (
    <section className="panel stack">
      <h3>{result.tool_name.replaceAll("_", " ")}</h3>
      <p className="small">
        {result.n_rows} matching rows. Scope: {result.population_or_cohort}. Evidence version: {result.dataset_build_id}.
      </p>
      {rows.length ? (
        <div className="table-wrap">
          <table>
            <thead><tr>{columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {columns.map((c) => (
                    <td key={c}>{row[c] == null ? <em>Unknown</em> : typeof row[c] === "object" ? JSON.stringify(row[c]) : String(row[c])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="small">No observations match this scope.</p>
      )}
      {result.warnings?.length ? <ul className="caveats">{result.warnings.map((w) => <li key={w}>{w}</li>)}</ul> : null}
    </section>
  );
}

const PUBLIC_ASK = process.env.NEXT_PUBLIC_PUBLIC_ASK === "true";

const EXAMPLES = [
  "What are the 3 most relevant findings of the study?",
  "How does oxygen change how long a flame burns?",
  "Where does burn_time_s come from?",
];

export default function AskData() {
  const [token, setToken] = useState("");
  const [question, setQuestion] = useState(EXAMPLES[0]);
  const [language, setLanguage] = useState<"en" | "es">("en");
  const [generate, setGenerate] = useState(true);
  const [mode, setMode] = useState<"question" | "count" | "list">("question");
  const [campaign, setCampaign] = useState("");
  const [fuel, setFuel] = useState("");
  const [geometry, setGeometry] = useState<"normal" | "inverse" | "">("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [answer, setAnswer] = useState<Answer>();

  async function ask() {
    setBusy(true);
    setError("");
    setAnswer(undefined);
    const query: Query | undefined = mode === "question" ? undefined : {
      tool: mode === "count" ? "summarize_ignition_outcomes" : "list_gas_tests",
      arguments: { cohort: "raw_gold", limit: 30, campaign: campaign || undefined, fuel: fuel.trim() || undefined, flame_type: geometry || undefined },
    };
    try {
      const response = await fetch("/api/backend/chat", {
        method: "POST",
        headers: PUBLIC_ASK
          ? { "Content-Type": "application/json" }
          : { "x-dashboard-token": token, "Content-Type": "application/json" },
        body: JSON.stringify({ question: query ? "Gas flame evidence" : question, language, evidence_only: !!query || !generate, query }),
      });
      if (response.status === 409) throw new Error("This dashboard and the evidence service use different releases. Public findings remain available.");
      if (response.status === 429) throw new Error("Too many questions right now. Try again in a few minutes.");
      if (response.status === 503) throw new Error("The evidence service is unavailable or starting (503). Try again in a moment; public findings remain available.");
      if (!response.ok)
        throw new Error(
          response.status === 401
            ? "Enter your dashboard access token."
            : `Request unavailable (${response.status}). The evidence service may be starting; try again in a moment.`,
        );
      setAnswer(await response.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unavailable");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid-2">
      <section className="panel stack" aria-label="Question">
        <label>Request type <select value={mode} onChange={(event) => setMode(event.target.value as typeof mode)}>
          <option value="question">Ask a question</option><option value="count">Count ignition outcomes</option><option value="list">List gas tests</option>
        </select></label>
        {mode !== "question" && <fieldset className="stack"><legend>Query filters</legend>
          <label>Campaign <select value={campaign} onChange={(event) => setCampaign(event.target.value)}><option value="">All</option><option>CFI-G</option><option>Flame Design</option></select></label>
          <label>Flame geometry <select value={geometry} onChange={(event) => setGeometry(event.target.value as typeof geometry)}><option value="">All</option><option value="normal">Normal</option><option value="inverse">Inverse</option></select></label>
          <label>Fuel <input value={fuel} maxLength={80} onChange={(event) => setFuel(event.target.value)} /></label>
          <p>Population: curated Gold gas tests. Results report durations in seconds and pressure in kilopascals when available.</p>
        </fieldset>}
        {mode === "question" && <label>
          Question
          <textarea maxLength={2000} value={question} onChange={(e) => setQuestion(e.target.value)} />
        </label>}
        {mode === "question" && <div className="actions">
          {EXAMPLES.slice(1).map((q) => (
            <button key={q} className="btn btn-ghost" style={{ minHeight: 38, fontSize: 13, padding: "0 14px" }} onClick={() => setQuestion(q)}>
              {q}
            </button>
          ))}
        </div>}
        <label>
          Response language
          <select value={language} onChange={(e) => setLanguage(e.target.value as "en" | "es")}>
            <option value="en">English</option>
            <option value="es">Español</option>
          </select>
        </label>
        {!PUBLIC_ASK && <label>
          Dashboard access token
          <input type="password" autoComplete="off" value={token} onChange={(e) => setToken(e.target.value)} />
        </label>}
        <label className="checkbox">
          <input type="checkbox" checked={generate && mode === "question"} disabled={mode !== "question"} onChange={(e) => setGenerate(e.target.checked)} />
          Let Gemini select and organize source excerpts. This sends the question and excerpts to Google.
        </label>
        <button className="btn btn-primary" disabled={busy || (mode === "question" && !question.trim())} onClick={ask}>
          {busy ? "Retrieving…" : mode === "question" ? "Ask" : "Run query"}
        </button>
      </section>

      <section className="stack" aria-live="polite" aria-label="Answer">
        {error && <p role="alert" className="error panel">{error}</p>}
        {!answer && !error && (
          <div className="panel stack">
            <span className="label">Grounded answers</span>
            <p className="muted">
              Gemini selects and orders source excerpts. Exact queries show the calculated results with their filters and release.
            </p>
          </div>
        )}
        {answer && (
          <>
            <div className="panel stack">
              <span className="label">{answer.status.replaceAll("_", " ")}</span>
              <p>{answer.message}</p>
              <p className="small"><strong>{answer.evidence.source_mode.toUpperCase()}</strong> data. Evidence version {answer.evidence.build_id}.</p>
              {answer.claims?.map((claim, i) => {
                const cites = claim.evidence_ids.map((id) => (
                  <a key={id} className="link" href={`#${id}`}>[{answer.evidence.chunks?.findIndex((c) => c.chunk_id === id)! + 1}]</a>
                ));
                return claim.kind === "data" ? (
                  <blockquote key={i}>{claim.text} <span className="small">{cites}</span></blockquote>
                ) : (
                  <p key={i} style={{ fontSize: 17 }}>
                    {claim.kind === "limitation" && <span className="label">Limit: </span>}
                    {claim.text} <span className="small">{cites}</span>
                  </p>
                );
              })}
            </div>
            {answer.evidence.tools?.map((t) => <ToolPanel key={t.evidence_id} result={t} />)}
            <div className="panel">
              {answer.evidence.chunks?.map((chunk, i) => {
                const source = answer.evidence.sources?.find((s) => s.source_id === chunk.source_id);
                return (
                  <details key={chunk.chunk_id} id={chunk.chunk_id}>
                    <summary>Evidence {i + 1}: {source?.title} ({chunk.section})</summary>
                    <p className="excerpt">{chunk.text}</p>
                    <p className="small">{source?.review_status}. Source: {source?.locator}. SHA-256: {source?.sha256}.</p>
                  </details>
                );
              })}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
