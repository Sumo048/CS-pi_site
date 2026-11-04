// Interactive explorer: task → scenario → method (→ success / fail).
// A React port of the explorer in the old js/explorer.js, with the same data,
// controls, captions, absence reasons and ?task= / ?scen= deep links.
import { useEffect, useMemo, useState } from "react";
import type { Method, Task } from "../data/site";
import { base } from "../lib/lazyMedia";
import { LazyVideo, OutcomeLabel, type VideoEntry } from "./LazyVideo";

type Outcome = "success" | "fail" | "rollout";
type Cell = Partial<Record<Outcome, VideoEntry>>;
type Manifest = Record<string, Record<string, Record<string, Cell>>>;

interface Props {
  tasks: Task[];
  methods: Method[];
  manifest: Manifest;
}

const OUTCOME_CAPTION: Record<string, string> = {
  success: "Safe and successful: collision-free, the gripper picks the cube and places it.",
  fail: "Failure: a collision, or the gripper clears the obstacle but loses the cube.",
};

function absenceReason(method: string, outcome: Outcome) {
  if (method === "amr" && outcome === "fail")
    return "CS-Pi is collision-free on all five scenarios, so no failure rollout exists.";
  if (outcome === "success")
    return "This method scores 0% safe-success in this scenario, so there is no successful rollout to show.";
  if (outcome === "rollout") return "No rollout was rendered for this cell.";
  return "This method is safe on every trial in this scenario, so there is no failure rollout to show.";
}

const csName = (t: string) => t.replace(/CS-Pi/g, '<span class="cs">CS-Pi</span>');

export default function Explorer({ tasks, methods, manifest }: Props) {
  const available = tasks.filter((t) => t.available);
  const byKey = useMemo(() => Object.fromEntries(methods.map((m) => [m.key, m])), [methods]);
  const [taskKey, setTaskKey] = useState(available[0]!.key);
  const task = available.find((t) => t.key === taskKey)!;
  const [scen, setScen] = useState(task.scenarios[0]!.key);
  const [method, setMethod] = useState(task.methods[0]!);
  const [outcome, setOutcome] = useState<Outcome>(task.outcomes ? "success" : "rollout");

  const cell = (t: string, s: string, m: string): Cell => manifest[t]?.[s]?.[m] ?? {};
  const has = (o: Outcome, s = scen, m = method) => !!cell(taskKey, s, m)[o];
  const defaultOutcome = (t: Task, s: string, m: string): Outcome => {
    if (!t.outcomes) return "rollout";
    const c = cell(t.key, s, m);
    return c.success ? "success" : c.fail ? "fail" : "success";
  };

  function selectTask(k: string, wantScen?: string) {
    const t = available.find((x) => x.key === k)!;
    const s = (wantScen && t.scenarios.find((x) => x.key === wantScen)?.key) || t.scenarios[0]!.key;
    const m = t.methods.includes(method) ? method : t.methods[0]!;
    setTaskKey(k);
    setScen(s);
    setMethod(m);
    setOutcome(defaultOutcome(t, s, m));
  }
  function selectScen(s: string) {
    setScen(s);
    setOutcome(defaultOutcome(task, s, method));
  }
  function selectMethod(m: string) {
    setMethod(m);
    setOutcome(defaultOutcome(task, scen, m));
  }

  // Deep links: ?task=3dorient&scen=config2
  useEffect(() => {
    const q = new URLSearchParams(location.search);
    const t = q.get("task");
    const s = q.get("scen");
    if (t && available.some((x) => x.key === t)) selectTask(t, s ?? undefined);
    else if (s && task.scenarios.some((x) => x.key === s)) selectScen(s);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const m = byKey[method]!;
  const label = task.methodLabels?.[method] ?? m.label;
  const entry = cell(taskKey, scen, method)[outcome];
  const scenario = task.scenarios.find((s) => s.key === scen)!;
  const caption = !entry
    ? absenceReason(method, outcome)
    : task.outcomes
      ? OUTCOME_CAPTION[outcome]!
      : (task.rolloutCaption ?? "");
  const thumb = (s: string) => {
    const c = cell(taskKey, s, task.methods[0]!);
    const e = c.success ?? c.rollout ?? c.fail ?? Object.values(manifest[taskKey]?.[s] ?? {}).flatMap((x) => Object.values(x))[0];
    return e?.poster;
  };

  return (
    <div className="explorer wide">
      <div className="ctl-row" role="group" aria-label="Task">
        {tasks.map((t) => (
          <button key={t.key} type="button" className="ctl" disabled={!t.available}
            aria-pressed={t.key === taskKey} onClick={() => selectTask(t.key)}>
            {t.label}{t.available ? "" : " (soon)"}
          </button>
        ))}
      </div>
      <p className="blurb">{task.blurb}</p>

      <div className="exp-grid">
        <div>
          <p className="exp-label" id="exp-scen">Scenario</p>
          <div className="scen-list" role="group" aria-labelledby="exp-scen">
            {task.scenarios.map((s) => {
              const p = thumb(s.key);
              return (
                <button key={s.key} type="button" className="scen" aria-pressed={s.key === scen}
                  onClick={() => selectScen(s.key)}>
                  {p ? <img src={base(p)} alt="" loading="lazy" decoding="async" /> : <span className="ph" />}
                  <span>
                    <span className="name" style={{ display: "block" }}>{s.label}</span>
                    <span className="desc" style={{ display: "block" }}>{s.desc}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <p className="exp-label" id="exp-method">Method</p>
          <div className="ctl-row" role="group" aria-labelledby="exp-method">
            {task.methods.map((k) => {
              const mm = byKey[k];
              if (!mm) return null;
              return (
                <button key={k} type="button" className="ctl" aria-pressed={k === method} onClick={() => selectMethod(k)}>
                  <span className="swatch" style={{ ["--sw" as string]: mm.color }} aria-hidden="true" />
                  {task.methodLabels?.[k] ?? mm.label}{mm.ours ? " (ours)" : ""}
                </button>
              );
            })}
          </div>

          <div className="stage-head">
            <span className="who">
              <span className="swatch" style={{ ["--sw" as string]: m.color }} aria-hidden="true" />
              {label}{m.ours ? " · ours" : ""}
              {entry && task.outcomes && <OutcomeLabel ok={outcome === "success"} />}
            </span>
            {task.outcomes && (
              <span className="seg" role="group" aria-label="Outcome">
                <button type="button" aria-pressed={outcome === "success"} disabled={!has("success")}
                  onClick={() => setOutcome("success")}>✓ safe</button>
                <button type="button" aria-pressed={outcome === "fail"} disabled={!has("fail")}
                  onClick={() => setOutcome("fail")}>✗ fail</button>
              </span>
            )}
          </div>

          <div aria-live="polite">
            {entry ? (
              <LazyVideo entry={entry} label={`${label}, ${scenario.label}${task.outcomes ? (outcome === "success" ? ", safe" : ", fail") : ""}`} />
            ) : (
              <div className="empty">
                <div>
                  <div className="t">No rollout for this cell</div>
                  <div className="why">{absenceReason(method, outcome)}</div>
                </div>
              </div>
            )}
          </div>

          <div className="stage-note">
            <span className="interp">{caption}</span>
            {scenario.note && <span className="scennote">{scenario.note}</span>}
            {m.blurb && (<><br /><span dangerouslySetInnerHTML={{ __html: csName(m.blurb) }} /></>)}
          </div>
        </div>
      </div>
    </div>
  );
}
