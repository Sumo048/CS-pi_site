import { useEffect, useRef } from "react";
import { base, observeVideo } from "../lib/lazyMedia";

export interface VideoEntry {
  mp4: string;
  webm: string;
  poster: string;
  w?: number;
  h?: number;
}

/** Muted, inline, looping clip that loads near the viewport and pauses off it. */
export function LazyVideo({ entry, label }: { entry: VideoEntry; label: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    v.muted = true; // React does not reflect `muted` as an attribute
    return observeVideo(v);
  }, [entry.mp4]);
  return (
    <video
      key={entry.mp4}
      ref={ref}
      className="media"
      width={entry.w}
      height={entry.h}
      style={entry.w && entry.h ? { aspectRatio: `${entry.w} / ${entry.h}` } : undefined}
      autoPlay
      muted
      loop
      playsInline
      preload="none"
      aria-label={label}
      data-lazy=""
      data-poster={base(entry.poster)}
    >
      <source data-src={base(entry.mp4)} type="video/mp4" />
      <source data-src={base(entry.webm)} type="video/webm" />
    </video>
  );
}

export function OutcomeLabel({ ok, text }: { ok: boolean; text?: string }) {
  return (
    <span className={`outcome ${ok ? "ok" : "bad"}`}>
      <span className="mark" aria-hidden="true">{ok ? "✓" : "✗"}</span>
      {text ?? (ok ? "safe" : "fail")}
    </span>
  );
}
