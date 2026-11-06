// Results: head-to-head comparison. Pick a task and a scenario, then any two
// methods (and outcome, where the task has one); their rollouts play side by
// side. Uses the same manifest as the qualitative explorer, plus the filmed
// real-world runs.
import { useMemo, useState } from "react";
import type { Method, Task } from "../data/site";
import { base } from "../lib/lazyMedia";
import { LazyVideo, OutcomeLabel, type VideoEntry } from "./LazyVideo";

type Outcome = "success" | "fail" | "rollout";
interface StillEntry { img: string; w?: number; h?: number; thumb?: string }
type Entry = VideoEntry | StillEntry;
const isStill = (e: Entry): e is StillEntry => "img" in e;
type Cell = Partial<Record<Outcome, Entry>>;
type Manifest = Record<string, Record<string, Record<string, Cell>>>;
interface Side { method: string; outcome: Outcome }

function absence(task: Task, method: string, outcome: Outcome) {
  const a = task.absence ?? {};
  if (method === "amr" && outcome === "fail") return a.amrFail ?? "CS-Pi is collision-free here, so no failure rollout exists.";
  if (outcome === "success") return a.success ?? "This method never succeeds here, so there is no successful rollout.";
  if (outcome === "rollout") return "No rollout was rendered for this method.";
  return a.fail ?? "This method never fails here, so there is no failure rollout.";
}

export default function Compare({ tasks, methods, manifest }: { tasks: Task[]; methods: Method[]; manifest: Manifest }) {
  const byKey = useMemo(() => Object.fromEntries(methods.map((m) => [m.key, m])), [methods]);
  const [taskKey, setTaskKey] = useState(tasks[0]!.key);
  const task = tasks.find((t) => t.key === taskKey)!;
  const cell = (t: string, s: string, m: string): Cell => manifest[t]?.[s]?.[m] ?? {};
  const label = (t: Task, k: string) => t.methodLabels?.[k] ?? byKey[k]?.label ?? k;

  const defaultOutcome = (t: Task, s: string, m: string, prefer: Outcome = "success"): Outcome => {
    if (!t.outcomes) return "rollout";
    const c = cell(t.key, s, m);
    if (c[prefer]) return prefer;
    return c.success ? "success" : c.fail ? "fail" : prefer;
  };
  // CS-Pi on the left; on the right the first baseline with a clip here,
  // preferring one that fails (the contrast a visitor most wants to see).
  const defaults = (t: Task, s: string): [Side, Side] => {
    const left: Side = { method: "amr", outcome: defaultOutcome(t, s, "amr") };
    const others = t.methods.filter((k) => k !== "amr");
    const has = (k: string) => Object.keys(cell(t.key, s, k)).length > 0;
    const pick = others.find((k) => cell(t.key, s, k).fail) ?? others.find(has) ?? others[0]!;
    return [left, { method: pick, outcome: defaultOutcome(t, s, pick, "fail") }];
  };

  const [scen, setScen] = useState(task.scenarios[0]!.key);
  const [sides, setSides] = useState<[Side, Side]>(() => defaults(task, task.scenarios[0]!.key));

  function selectTask(k: string) {
    const t = tasks.find((x) => x.key === k)!;
    const s = t.scenarios[0]!.key;
    setTaskKey(k); setScen(s); setSides(defaults(t, s));
  }
  function selectScen(s: string) { setScen(s); setSides(defaults(task, s)); }
  function setSide(i: 0 | 1, patch: Partial<Side>) {
    setSides((prev) => {
      const next = [...prev] as [Side, Side];
      const merged = { ...next[i], ...patch };
      if (patch.method) merged.outcome = defaultOutcome(task, scen, patch.method, next[i].outcome);
      next[i] = merged;
      return next;
    });
  }

  const scenario = task.scenarios.find((s) => s.key === scen)!;

  return (
    <div className="compare wide">
      <div className="ctl-row" role="group" aria-label="Task">
        {tasks.map((t) => (
          <button key={t.key} type="button" className="ctl" aria-pressed={t.key === taskKey} onClick={() => selectTask(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {task.scenarios.length > 1 && (
        <div className="compare-scen" role="group" aria-label="Scenario">
          {task.scenarios.map((s) => (
            <button key={s.key} type="button" className="chip" aria-pressed={s.key === scen} onClick={() => selectScen(s.key)}>
              {s.label}
            </button>
          ))}
        </div>
      )}

      <div className="compare-grid">
        {sides.map((side, i) => {
          const entry = cell(taskKey, scen, side.method)[side.outcome];
          const has = (o: Outcome) => !!cell(taskKey, scen, side.method)[o];
          const name = label(task, side.method);
          const m = byKey[side.method];
          const view = `${name}, ${scenario.label}${task.outcomes ? (side.outcome === "success" ? ", safe" : ", fail") : ""}`;
          return (
            <div className="compare-side" key={i}>
              <div className="compare-head">
                <label className="visually-hidden" htmlFor={`cmp-${i}`}>{i === 0 ? "Left method" : "Right method"}</label>
                <span className="swatch" style={{ ["--sw" as string]: m?.color }} aria-hidden="true" />
                <select id={`cmp-${i}`} value={side.method} onChange={(e) => setSide(i as 0 | 1, { method: e.target.value })}>
                  {task.methods.map((k) => (
                    <option key={k} value={k}>{label(task, k)}{byKey[k]?.ours ? " (ours)" : ""}</option>
                  ))}
                </select>
                {task.outcomes && (
                  <span className="seg" role="group" aria-label="Outcome">
                    <button type="button" aria-pressed={side.outcome === "success"} disabled={!has("success")}
                      onClick={() => setSide(i as 0 | 1, { outcome: "success" })}>✓ safe</button>
                    <button type="button" aria-pressed={side.outcome === "fail"} disabled={!has("fail")}
                      onClick={() => setSide(i as 0 | 1, { outcome: "fail" })}>✗ fail</button>
                  </span>
                )}
              </div>
              {entry ? (
                isStill(entry) ? (
                  <img key={entry.img} className="media still" src={base(entry.img)} width={entry.w} height={entry.h}
                    alt={view} loading="lazy" decoding="async" />
                ) : (
                  <LazyVideo entry={entry} label={view} />
                )
              ) : (
                <div className="empty">
                  <div>
                    <div className="t">No rollout</div>
                    <div className="why">{absence(task, side.method, side.outcome)}</div>
                  </div>
                </div>
              )}
              {entry && task.outcomes && (
                <div className="clip-cap"><span className="who">{name}</span><OutcomeLabel ok={side.outcome === "success"} /></div>
              )}
            </div>
          );
        })}
      </div>
      <p className="compare-note">{task.blurb}</p>
    </div>
  );
}
