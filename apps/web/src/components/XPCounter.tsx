"use client";

import { useEffect, useState } from "react";

/** Rolls from 0 to `value` over ~900ms. Respects reduced motion by jumping straight there. */
export function XPCounter({ value, prefix = "+" }: { value: number; prefix?: string }) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    const reduce = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const dur = reduce || value === 0 ? 0 : 900;
    let start = 0;
    let raf = 0;
    const tick = (t: number) => {
      if (!start) start = t;
      const p = dur === 0 ? 1 : Math.min(1, (t - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setShown(Math.round(value * eased));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  return (
    <span className="font-display text-6xl font-bold tabular-nums text-ember">
      {prefix}
      {shown}
    </span>
  );
}
