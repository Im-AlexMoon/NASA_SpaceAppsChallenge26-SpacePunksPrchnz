import type { Metadata } from "next";
import Dashboard from "../../components/dashboard/Dashboard";
import { meta } from "../../lib/content";

export const metadata: Metadata = { title: "Dashboard" };

export default function Page() {
  return (
    <div className="page">
      <div className="wrap">
        <header className="page-head" data-enter>
          <p className="eyebrow">{meta.counts.gas_flame_tests} flames on the ISS, one view</p>
          <h1>Evidence dashboard</h1>
          <p className="lede">Filter the flames, see how long they burned and how far each result can be trusted.</p>
        </header>
        <Dashboard />
      </div>
    </div>
  );
}
