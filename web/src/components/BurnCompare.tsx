"use client";
import { useEffect, useRef, useState } from "react";

type Lane = { name: string; air: string; seconds: number; n: number };

// Two observed burn times drawn as burning tracks; played once, ten times faster than real time.
export default function BurnCompare({ lanes }: { lanes: Lane[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const [play, setPlay] = useState(false);
  const max = Math.max(...lanes.map((l) => l.seconds));
  useEffect(() => {
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) ref.current!.dataset.armed = "";
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setPlay(true);
          io.disconnect();
        }
      },
      { threshold: 0.5 },
    );
    io.observe(ref.current!);
    return () => io.disconnect();
  }, []);
  return (
    <div className="compare" ref={ref} data-play={play || undefined}>
      {lanes.map((l) => (
        <div className="lane" key={l.name}>
          <div className="lane-name">
            <strong>{l.name}</strong>
            <span className="label">{l.air}</span>
          </div>
          <div className="track" style={{ "--k": l.seconds / max, "--d": `${l.seconds / 10}s` } as React.CSSProperties}>
            <i />
          </div>
          <div className="lane-value num">
            {l.seconds}
            <small>s</small>
          </div>
        </div>
      ))}
    </div>
  );
}
