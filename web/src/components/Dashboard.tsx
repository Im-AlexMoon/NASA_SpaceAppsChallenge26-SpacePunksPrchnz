"use client";
import Link from "next/link";
import { useState } from "react";
import type { components } from "../generated/api";
type Answer = components["schemas"]["AnswerResult"];
type Query = components["schemas"]["ToolRequest"];
type Tool = components["schemas"]["ToolResult"];
type Status = {
  build_id: string;
  source_mode: string;
  retrieval_mode: string;
  row_counts: Record<string, number>;
  generation_enabled: boolean;
};
const titles: Record<string, string> = {
  "": "Evidence overview",
  mission: "Mission brief",
  investigations: "Investigation explorer",
  compare: "Compare experimental conditions",
  insights: "Reviewed findings",
  habitat: "Habitat evidence coverage",
  ask: "Ask the data",
  methods: "Methods & sources",
};

function Table({ rows }: { rows: Record<string, unknown>[] }) {
  if (!rows.length)
    return <p className="notice">No observations match this scope.</p>;
  const columns = Object.keys(rows[0]);
  return (
    <div className="table">
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((c) => (
                <td key={c}>
                  {row[c] == null ? (
                    <em>Unknown</em>
                  ) : typeof row[c] === "object" ? (
                    JSON.stringify(row[c])
                  ) : (
                    String(row[c])
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function ToolPanel({ result }: { result: Tool }) {
  return (
    <section className="card">
      <h3>{result.tool_name.replaceAll("_", " ")}</h3>
      <p>
        <strong>{result.n_rows} rows</strong> ·{" "}
        {result.n_unique_tests ?? "Unknown"} unique tests ·{" "}
        {result.n_operations ?? "Unknown"} operations
      </p>
      <p>
        Scope: {result.population_or_cohort} · Build: {result.dataset_build_id}
      </p>
      <p>
        Units:{" "}
        {Object.entries(result.units || {})
          .map(([key, value]) => `${key}: ${value}`)
          .join("; ") || "Not applicable"}
      </p>
      <Table rows={result.results} />
      <details>
        <summary>Filters, missingness & provenance</summary>
        <pre>
          {JSON.stringify(
            {
              filters: result.normalized_parameters,
              valid: result.n_valid_by_variable,
              missing: result.n_missing_by_variable,
              provenance: result.provenance_reference,
              hash: result.result_hash,
            },
            null,
            2,
          )}
        </pre>
      </details>
      <ul>
        {result.warnings?.map((w) => (
          <li key={w}>{w}</li>
        ))}
      </ul>
    </section>
  );
}
export default function Dashboard({ route }: { route: string }) {
  const [token, setToken] = useState("");
  const [status, setStatus] = useState<Status>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [results, setResults] = useState<Tool[]>([]);
  const [answer, setAnswer] = useState<Answer>();
  const [question, setQuestion] = useState("Where does burn_time_s come from?");
  const [language, setLanguage] = useState<"en" | "es">("en");
  const [generate, setGenerate] = useState(false);
  const [campaign, setCampaign] = useState("CFI-G");
  const [geometry, setGeometry] = useState<"normal" | "inverse">("normal");
  const [variable, setVariable] = useState("xo2");
  const [fuel, setFuel] = useState("");
  const [secondFuel, setSecondFuel] = useState("");
  const [search, setSearch] = useState("");
  const [cohort, setCohort] = useState<
    "raw_gold" | "audited_unique" | "audited_verified_dates"
  >("raw_gold");
  async function api<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`/api/backend/${path}`, {
      method: body ? "POST" : "GET",
      headers: {
        "x-dashboard-token": token,
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok)
      throw new Error(
        response.status === 401
          ? "Enter your dashboard access token."
          : `Request unavailable (${response.status}). Check the backend and selected scope.`,
      );
    return response.json();
  }
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await action();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unavailable");
    } finally {
      setBusy(false);
    }
  }
  const query = (selectedFuel = fuel): Query => ({
    tool: "summarize_gas_tests",
    arguments: {
      campaign,
      flame_type: geometry,
      variable,
      cohort,
      limit: 30,
      ...(selectedFuel ? { fuel: selectedFuel } : {}),
    },
  });
  function filters() {
    return (
      <div className="controls">
        <label>
          Campaign
          <select
            value={campaign}
            onChange={(e) => setCampaign(e.target.value)}
          >
            <option>CFI-G</option>
            <option>Flame Design</option>
          </select>
        </label>
        <label>
          Geometry
          <select
            value={geometry}
            onChange={(e) =>
              setGeometry(e.target.value as "normal" | "inverse")
            }
          >
            <option value="normal">Normal</option>
            <option value="inverse">Inverse</option>
          </select>
        </label>
        <label>
          Variable
          <select
            value={variable}
            onChange={(e) => setVariable(e.target.value)}
          >
            {[
              "xo2",
              "p_kpa",
              "x_fuel",
              "m_fuel_mg_s",
              "m_o2_mg_s",
              "m_n2_mg_s",
              "burn_time_s",
              "peak_burner_t_k",
              "po2_kpa",
              "zst",
              "tad_k",
            ].map((v) => (
              <option key={v}>{v}</option>
            ))}
          </select>
        </label>
        <label>
          Cohort
          <select
            value={cohort}
            onChange={(e) => setCohort(e.target.value as typeof cohort)}
          >
            <option value="raw_gold">Raw gold</option>
            <option value="audited_unique">Audited unique</option>
            <option value="audited_verified_dates">Verified dates</option>
          </select>
        </label>
        <label>
          Fuel (exact name, optional)
          <input value={fuel} onChange={(e) => setFuel(e.target.value)} />
        </label>
      </div>
    );
  }
  return (
    <>
      <p className="eyebrow">RESEARCH WORKSPACE</p>
      <h1>{titles[route]}</h1>
      <section className="connection">
        <label>
          Dashboard access token
          <input
            type="password"
            autoComplete="off"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
        </label>
        <button
          disabled={busy}
          onClick={() =>
            run(async () => setStatus(await api<Status>("status")))
          }
        >
          Connect
        </button>
        {status && (
          <p>
            <strong>{status.source_mode.toUpperCase()} DATA</strong> ·{" "}
            {status.retrieval_mode} · {status.build_id}
          </p>
        )}
      </section>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {busy && <p role="status">Retrieving and validating evidence…</p>}
      {route === "" && (
        <>
          <p>
            Explore the experiment catalog, compare conditions and inspect the
            evidence behind an answer. Connect to display the current snapshot.
          </p>
          <div className="metrics">
            {Object.entries(status?.row_counts || {}).map(([name, n]) => (
              <section className="card" key={name}>
                <strong>{n}</strong>
                <p>{name.replaceAll("_", " ")}</p>
              </section>
            ))}
          </div>
        </>
      )}
      {route === "mission" && (
        <section className="card">
          <h2>Evidence for combustion research</h2>
          <p>
            FlameSafe organizes PSI experiment metadata and harmonized gas and
            droplet observations. The goal is traceable exploration of ignition,
            burning and extinction under the conditions actually studied.
          </p>
          <p>
            Normal and inverse flames have different meanings for oxygen and
            flow. Flame Design event labels are not interchangeable with CFI-G
            experimental ignition outcomes. Partial-gravity predictions are not
            measured evidence.
          </p>
          <p>
            Use Methods to inspect definitions, and Ask the Data to retrieve
            their sources.
          </p>
        </section>
      )}
      {route === "investigations" && (
        <section>
          <label>
            Search catalog or bibliography
            <input value={search} onChange={(e) => setSearch(e.target.value)} />
          </label>
          <div className="actions">
            <button
              disabled={busy}
              onClick={() =>
                run(async () =>
                  setResults([
                    await api<Tool>("data/query", {
                      tool: "find_investigations",
                      arguments: { text: search },
                    }),
                  ]),
                )
              }
            >
              Search investigations
            </button>
            <button
              disabled={busy}
              onClick={() =>
                run(async () =>
                  setResults([
                    await api<Tool>("data/query", {
                      tool: "find_publications",
                      arguments: { text: search },
                    }),
                  ]),
                )
              }
            >
              Search publications
            </button>
          </div>
          <p>
            Bibliographic records do not establish an article’s conclusions.
            Results are bounded previews; full matched counts appear separately.
          </p>
        </section>
      )}
      {(route === "compare" || route === "habitat") && (
        <>
          {filters()}
          {route === "compare" && (
            <label>
              Second fuel (optional)
              <input
                value={secondFuel}
                onChange={(e) => setSecondFuel(e.target.value)}
              />
            </label>
          )}
          <button
            disabled={busy}
            onClick={() =>
              run(async () => {
                const a = await api<Tool>("data/query", query());
                const b =
                  secondFuel && route === "compare"
                    ? await api<Tool>("data/query", query(secondFuel))
                    : null;
                setResults(b ? [a, b] : [a]);
              })
            }
          >
            Inspect coverage
          </button>
          <p>
            Summaries remain separated by campaign, geometry and fuel. Shared
            ranges alone do not establish experimental comparability; dilution,
            protocol and operational dependence can confound comparisons.
          </p>
          {route === "habitat" && (
            <aside className="notice">
              <h2>Model readings: disabled</h2>
              <p>
                ADR-0007 defines measured-nearby, interpolation and no-evidence
                tiers. The model publication block remains active pending
                reviewed model artifacts and validation. No numeric habitat risk
                or evacuation time is available here.
              </p>
            </aside>
          )}
        </>
      )}
      {route === "insights" && (
        <section className="notice">
          <h2>No reviewed findings published in this release</h2>
          <p>
            Candidate results require scientific review of the exact source
            version. Catalog descriptions and retrieved excerpts are not
            approved project findings.
          </p>
        </section>
      )}
      {route === "methods" && (
        <>
          <p>
            Retrieval uses local multilingual E5 embeddings and BM25, fused by
            reciprocal rank. Exact numbers come from bounded Python database
            tools. Missing values remain unknown. Generated excerpts must match
            a cited chunk; they are not causal conclusions.
          </p>
          <label>
            Variable definition
            <input
              value={variable}
              onChange={(e) => setVariable(e.target.value)}
            />
          </label>
          <button
            disabled={busy}
            onClick={() =>
              run(async () =>
                setResults([
                  await api<Tool>(`variables/${encodeURIComponent(variable)}`),
                ]),
              )
            }
          >
            Inspect definition
          </button>
          <p>
            Source locators, hashes, units and population filters accompany each
            result. Sample data must not be interpreted as full-experiment
            coverage.
          </p>
        </>
      )}
      {route === "ask" && (
        <>
          <label>
            Question
            <textarea
              maxLength={2000}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </label>
          <div className="controls">
            <label>
              Response language
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as "en" | "es")}
              >
                <option value="en">English</option>
                <option value="es">Español</option>
              </select>
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={generate}
                onChange={(e) => setGenerate(e.target.checked)}
              />
              Use configured generation provider
            </label>
          </div>
          <p>
            Generation sends your question and eligible retrieved text to the
            configured provider and may consume its quota. Evidence-only mode
            stays local. Quotations retain their source language.
          </p>
          <button
            disabled={busy || !question.trim()}
            onClick={() =>
              run(async () => {
                setAnswer(undefined);
                setAnswer(
                  await api<Answer>("chat", {
                    question,
                    language,
                    evidence_only: !generate,
                  }),
                );
              })
            }
          >
            Ask
          </button>
          <details>
            <summary>Exact query without generation</summary>
            {filters()}
            <button
              disabled={busy}
              onClick={() =>
                run(async () =>
                  setAnswer(
                    await api<Answer>("chat", {
                      question,
                      language,
                      evidence_only: true,
                      query: query(),
                    }),
                  ),
                )
              }
            >
              Run selected query
            </button>
          </details>
        </>
      )}
      {results.map((r, i) => (
        <ToolPanel key={`${r.evidence_id}-${i}`} result={r} />
      ))}
      {answer && (
        <section aria-live="polite">
          <h2>{answer.status.replaceAll("_", " ")}</h2>
          <p>{answer.message}</p>
          <p>
            <strong>{answer.evidence.source_mode.toUpperCase()}</strong> ·{" "}
            {answer.evidence.build_id}
          </p>
          {answer.claims?.map((claim, i) => (
            <blockquote key={i}>
              {claim.text}
              <p>
                {claim.evidence_ids.map((id) => (
                  <a key={id} href={`#${id}`}>
                    [Evidence{" "}
                    {answer.evidence.chunks?.findIndex(
                      (c) => c.chunk_id === id,
                    )! + 1}
                    ]{" "}
                  </a>
                ))}
              </p>
            </blockquote>
          ))}
          {answer.evidence.tools?.map((t) => (
            <ToolPanel key={t.evidence_id} result={t} />
          ))}
          {answer.evidence.chunks?.map((chunk, i) => {
            const source = answer.evidence.sources?.find(
              (s) => s.source_id === chunk.source_id,
            );
            return (
              <details key={chunk.chunk_id} id={chunk.chunk_id}>
                <summary>
                  Evidence {i + 1}: {source?.title} · {chunk.section}
                </summary>
                <p className="excerpt">{chunk.text}</p>
                <p>
                  {source?.review_status} · {source?.locator}
                </p>
                <p>SHA-256: {source?.sha256}</p>
              </details>
            );
          })}
          {answer.navigation === "/habitat" && (
            <Link href="/habitat">Open habitat evidence coverage</Link>
          )}
        </section>
      )}
    </>
  );
}
