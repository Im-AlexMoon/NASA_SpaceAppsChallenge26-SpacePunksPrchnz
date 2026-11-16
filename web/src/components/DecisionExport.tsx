"use client";

import { meta } from "../lib/content";

type Props = {
  scenario: string;
  selection: string;
  rows: [string, string][];
};

export default function DecisionExport({ scenario, selection, rows }: Props) {
  const fields: [string, string][] = [
    ["Scenario", scenario], ["Evidence version", meta.build_id], ...rows,
    ["Decision", "Review whether the evidence supports a comparable experiment before transferring the result to a new environment."],
    ["Next step", "Check material, geometry, ventilation, fuel and gravity coverage. Record the conditions and reasons for termination."],
  ];

  function save(format: "txt" | "csv") {
    const quote = (value: string) => '"' + value.replaceAll('"', '""') + '"';
    const data = format === "csv"
      ? ["Field,Value", ...fields.map((pair) => pair.map(quote).join(","))].join("\r\n")
      : fields.map(([label, value]) => label + ": " + value).join("\n");
    const url = URL.createObjectURL(new Blob([data], { type: format === "csv" ? "text/csv;charset=utf-8" : "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "flamesafe-decision." + format;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return (
    <section className="panel stack" aria-labelledby="decision-title">
      <h2 id="decision-title">Evidence for the next experiment</h2>
      <p>Use this record to identify which fuel, material, ventilation and gravity conditions still need comparable measurements.</p>
      <div className="actions">
        <a className="btn btn-ghost" href={"#" + selection}>Link to this scenario</a>
        <button className="btn btn-ghost" type="button" onClick={() => save("txt")}>Download brief</button>
        <button className="btn btn-ghost" type="button" onClick={() => save("csv")}>Download CSV</button>
      </div>
    </section>
  );
}
