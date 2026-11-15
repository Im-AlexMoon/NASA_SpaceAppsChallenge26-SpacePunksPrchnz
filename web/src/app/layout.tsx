import Link from "next/link";
import "./style.css";
export const metadata = {
  title: "FlameSafe | Evidence explorer",
  description: "Traceable space combustion evidence",
};
const links = [
  ["", "Overview"],
  ["mission", "Mission"],
  ["investigations", "Investigations"],
  ["compare", "Compare"],
  ["insights", "Insights"],
  ["habitat", "Habitat"],
  ["ask", "Ask the data"],
  ["methods", "Methods"],
];
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <Link className="brand" href="/">
            FLAME<span>SAFE</span>
          </Link>
          <p>Space combustion · evidence explorer</p>
        </header>
        <nav aria-label="Main navigation">
          {links.map(([route, label]) => (
            <Link key={route} href={`/${route}`}>
              {label}
            </Link>
          ))}
        </nav>
        <main>{children}</main>
        <footer>
          Descriptive evidence, not a habitat safety certification. Experimental
          populations remain separate.
        </footer>
      </body>
    </html>
  );
}
