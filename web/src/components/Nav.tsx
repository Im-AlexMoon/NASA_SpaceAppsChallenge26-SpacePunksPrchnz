"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const links = [
  ["/dashboard", "Dashboard"],
  ["/findings", "Findings"],
  ["/atmosphere", "Atmospheres"],
  ["/gaps", "Gaps"],
  ["/investigations", "Investigations"],
  ["/methods", "Methods"],
  ["/ask", "Ask"],
] as const;

export default function Nav() {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
  }, [open]);
  return (
    <header className="nav" data-open={open || undefined}>
      <div className="wrap nav-row">
        <Link className="brand" href="/" aria-label="FlameSafe home" onClick={() => setOpen(false)}>
          <span className="brand-mark" aria-hidden="true" />
          FlameSafe
        </Link>
        <nav aria-label="Main" id="main-nav">
          {links.map(([href, label]) => (
            <Link key={href} href={href} aria-current={path === href ? "page" : undefined} onClick={() => setOpen(false)}>
              {label}
            </Link>
          ))}
        </nav>
        <button
          className="menu"
          aria-expanded={open}
          aria-controls="main-nav"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          <span />
          <span />
        </button>
      </div>
    </header>
  );
}
