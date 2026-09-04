"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

/**
 * In-app scanner (the secondary path; the phone's camera app is the primary one).
 * Uses the native BarcodeDetector when the browser has it, otherwise offers
 * manual code entry. No scanner library in the MVP.
 */
export function Scanner({ zoo }: { zoo: string }) {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [supported] = useState<boolean>(() => typeof window !== "undefined" && "BarcodeDetector" in window);
  const [camera, setCamera] = useState<"idle" | "on" | "denied">("idle");
  const [code, setCode] = useState("");

  useEffect(() => {
    if (camera !== "on" || !supported) return;
    let stream: MediaStream | null = null;
    let raf = 0;
    let stopped = false;
    const Detector = (window as unknown as { BarcodeDetector: new (o: { formats: string[] }) => { detect: (v: HTMLVideoElement) => Promise<{ rawValue: string }[]> } }).BarcodeDetector;
    const detector = new Detector({ formats: ["qr_code"] });
    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        const v = videoRef.current!;
        v.srcObject = stream;
        await v.play();
        const loop = async () => {
          if (stopped) return;
          try {
            const codes = await detector.detect(v);
            const hit = codes.find((c) => /\/s\/([A-Z0-9-]+)/i.test(c.rawValue) || /^[A-Z0-9-]{6,40}$/i.test(c.rawValue));
            if (hit) {
              const m = hit.rawValue.match(/\/s\/([A-Z0-9-]+)/i);
              stopped = true;
              router.push(`/s/${(m ? m[1] : hit.rawValue).toUpperCase()}`);
              return;
            }
          } catch {
            /* keep scanning */
          }
          raf = requestAnimationFrame(loop);
        };
        loop();
      } catch {
        setCamera("denied");
      }
    })();
    return () => {
      stopped = true;
      cancelAnimationFrame(raf);
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, [camera, supported, router]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const c = code.trim().toUpperCase();
    if (c) router.push(`/s/${c}`);
  };

  return (
    <div>
      <p className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-ember">Scanner</p>
      <h1 className="mt-1 text-5xl font-bold leading-none">Scan the quest marker</h1>
      <p className="mt-2 text-sand-dim">Tip: your phone&apos;s regular camera app reads these signs too.</p>

      {supported && camera !== "denied" && (
        <div className="mt-6 overflow-hidden rounded-card border border-line bg-canopy">
          {camera === "on" ? (
            <video ref={videoRef} playsInline muted className="aspect-[3/4] w-full object-cover" />
          ) : (
            <button onClick={() => setCamera("on")} className="btn btn-primary m-4 w-[calc(100%-2rem)]">
              Open camera
            </button>
          )}
        </div>
      )}
      {camera === "denied" && (
        <p className="mt-4 rounded-card border border-line bg-canopy p-4 text-sand-dim">
          Camera access was blocked. Type the code printed under the QR square instead.
        </p>
      )}

      <form onSubmit={submit} className="mt-6">
        <label className="font-display text-xs font-semibold uppercase tracking-[0.16em] text-sand-dim">
          Or type the code on the sign
        </label>
        <div className="mt-2 flex gap-2">
          <input
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="CHZ-GIRAFFE-001"
            autoCapitalize="characters"
            autoComplete="off"
            className="min-h-14 flex-1 rounded-2xl border border-line bg-canopy px-4 font-mono text-lg uppercase text-sand placeholder:text-sand-dim/50 focus:border-ember focus:outline-none"
          />
          <button type="submit" className="btn btn-primary px-5">
            Go
          </button>
        </div>
      </form>
      <p className="mt-4 text-center text-xs text-sand-dim">{zoo.replace(/-/g, " ")}</p>
    </div>
  );
}
