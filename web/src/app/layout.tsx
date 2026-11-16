import type { Metadata, Viewport } from "next";
import { DM_Mono, Inter } from "next/font/google";
import Link from "next/link";
import Nav from "../components/Nav";
import "katex/dist/katex.min.css";
import "./style.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const mono = DM_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://127.0.0.1:3000"),
  title: { default: "FlameSafe: Space fire evidence", template: "%s | FlameSafe" },
  description:
    "How long a flame lasts in the air of future space habitats, read from 660 NASA flame tests on the ISS, so crews and designers can compare atmospheres, prioritize fire detection and know which experiment is still missing.",
  openGraph: {
    title: "FlameSafe: Space fire evidence",
    description: "24 NASA combustion investigations, ranked, read and tested against the atmospheres of future habitats.",
    type: "website",
  },
  icons: { icon: "/icon.svg" },
};

export const viewport: Viewport = { themeColor: "#05070b", colorScheme: "dark" };

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body>
        <a className="skip" href="#main">
          Skip to content
        </a>
        <Nav />
        <main id="main">{children}</main>
        <footer className="site-footer">
          <div className="wrap footer-grid">
            <Link className="brand" href="/" aria-label="FlameSafe home">
              <span className="brand-mark" aria-hidden="true" />
              FlameSafe
            </Link>
            <p>
              Data: NASA Physical Sciences Informatics (PSI-159 ACME CFI-G, PSI-10 ACME Flame Design and 22 more
              investigations). Flame video frames: NASA, CC0. Microgravity results only; no partial-gravity data exist.
            </p>
            <p>
              Team SpacePunks, NASA Space Apps Challenge 2026.{" "}
              <a href="https://github.com/Im-AlexMoon/NASA_SpaceAppsChallenge26-SpacePunksPrchnz">Source code</a>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
