// Head-to-head: CS-Pi's safe rollout next to the strongest baseline that
// fails the same shelf scenario. Cycles every 5.2 s while on screen, as before.
import { useEffect, useRef, useState } from "react";
import type { Method, Task } from "../data/site";
import { LazyVideo, OutcomeLabel, type VideoEntry } from "./LazyVideo";

type Cell = Partial<Record<"success" | "fail", VideoEntry>>;
type Manifest = Record<string, Record<string, Record<string, Cell>>>;

export default function FaceOff({ task, methods, manifest }: { task: Task; methods: Method[]; manifest: Manifest }) {
  const label = (k: string) => methods.find((m) => m.key === k)?.label ?? k;
  const cell = (s: string, m: string): Cell => manifest[task.key]?.[s]?.[m] ?? {};
  const scens = task.scenarios.filter((s) => cell(s.key, "amr").success);
  const baselineFail = (s: string) => {
    for (const k of ["tweedie", "trust", "projection"]) {
      const c = cell(s, k);
      if (c.fail) return { method: k, entry: c.fail };
    }
    return null;
  };

  const [idx, setIdx] = useState(0);
  const [visible, setVisible] = useState(false);
  const [tick, setTick] = useState(0); // restarts the timer after a manual pick
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const io = new IntersectionObserver(([e]) => setVisible(!!e?.isIntersecting), { threshold: 0.15 });
    if (root.current) io.observe(root.current);
    return () => io.disconnect();
  }, []);
  useEffect(() => {
    if (!visible || scens.length < 2) return;
    const t = setInterval(() => setIdx((i) => (i + 1) % scens.length), 5200);
    return () => clearInterval(t);
  }, [visible, tick, scens.length]);

  if (!scens.length) return null;
  const scen = scens[idx]!;
  const amr = cell(scen.key, "amr").success!;
  const base = baselineFail(scen.key);

  return (
    <div className="faceoff wide" ref={root}>
      <p className="col">
        Shelf pick-and-place with a deployment-time obstacle. Left is <span className="cs">CS-Pi</span>; right
        is the strongest baseline that fails this scenario. Currently showing: <b>{scen.label}</b>.
      </p>
      <div className="grid2 faceoff-stage">
        <figure className="clip">
          <LazyVideo entry={amr} label={`CS-Pi, ${scen.label}, safe`} />
          <figcaption className="clip-cap">
            <span className="who">CS-Pi (ours)</span>
            <OutcomeLabel ok />
          </figcaption>
        </figure>
        {base && (
          <figure className="clip">
            <LazyVideo entry={base.entry} label={`${label(base.method)}, ${scen.label}, fail`} />
            <figcaption className="clip-cap">
              <span className="who">{label(base.method)}</span>
              <OutcomeLabel ok={false} />
            </figcaption>
          </figure>
        )}
      </div>
      <div className="ctl-row" role="group" aria-label="Scenario">
        {scens.map((s, i) => (
          <button key={s.key} type="button" className="ctl" aria-pressed={i === idx}
            onClick={() => { setIdx(i); setTick((t) => t + 1); }}>
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
