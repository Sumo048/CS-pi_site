// Spheres-environment clips (viz/spheres_env_gifs). Every clip is a
// side-by-side render. The outcome of each side is read off the clip's final
// frame, where the renderer prints "cost=… OK" or "cost=… collision".
// (The folder README's success/failure prefixes do not always match the
// final frame, so the labels below follow the frame, not the file name.)

export type Outcome = "safe" | "collides";
export interface Side { method: string; outcome: Outcome }
export interface SphereClip { name: string; left: Side; right: Side }

const U = "Unconstrained";
const s = (method: string, outcome: Outcome): Side => ({ method, outcome });

export const SPHERE_GROUPS: { key: "in_distribution" | "out_of_distribution"; title: string; blurb: string; clips: SphereClip[] }[] = [
  {
    key: "in_distribution",
    title: "In distribution",
    blurb: "The 10-sphere environment the policy was trained on.",
    clips: [
      { name: "amr_vs_guidance_sample00", left: s("Gradient Guidance (α=0.5)", "collides"), right: s("CS-Pi (k=10)", "safe") },
      { name: "amr_vs_guidance_sample01", left: s("Gradient Guidance (α=0.5)", "safe"), right: s("CS-Pi (k=10)", "safe") },
      { name: "amr_success_sample00", left: s(U, "safe"), right: s("CS-Pi (k=10)", "safe") },
      { name: "amr_success_sample01", left: s(U, "collides"), right: s("CS-Pi (k=10)", "safe") },
      { name: "amr_success_sample02", left: s(U, "collides"), right: s("CS-Pi (k=10)", "collides") },
      { name: "amr_success_sample03", left: s(U, "collides"), right: s("CS-Pi (k=10)", "collides") },
      { name: "amr_success_sample04", left: s(U, "collides"), right: s("CS-Pi (k=10)", "collides") },
      { name: "amr_failure_sample00", left: s(U, "safe"), right: s("CS-Pi (k=0.5)", "safe") },
      { name: "amr_failure_sample01", left: s(U, "collides"), right: s("CS-Pi (k=0.5)", "collides") },
      { name: "amr_failure_sample02", left: s(U, "safe"), right: s("CS-Pi (k=0.5)", "safe") },
      { name: "amr_failure_sample03", left: s(U, "safe"), right: s("CS-Pi (k=0.5)", "collides") },
      { name: "amr_failure_sample04", left: s(U, "collides"), right: s("CS-Pi (k=0.5)", "collides") },
      { name: "unguided_vs_amr_sample00", left: s(U, "collides"), right: s("CS-Pi", "collides") },
      { name: "unguided_vs_amr_sample01", left: s(U, "collides"), right: s("CS-Pi", "collides") },
      { name: "unguided_vs_amr_sample02", left: s(U, "collides"), right: s("CS-Pi", "collides") },
    ],
  },
  {
    key: "out_of_distribution",
    title: "Out of distribution",
    blurb: "The same 10 spheres plus 6 extra obstacles the policy never saw.",
    clips: [
      { name: "amr_vs_guidance_sample00", left: s("Gradient Guidance (α=0.5)", "collides"), right: s("CS-Pi (k=10)", "safe") },
      { name: "amr_vs_guidance_sample01", left: s("Gradient Guidance (α=0.5)", "safe"), right: s("CS-Pi (k=10)", "safe") },
      { name: "unguided_vs_amr_sample00", left: s(U, "collides"), right: s("CS-Pi", "collides") },
      { name: "unguided_vs_amr_sample01", left: s(U, "collides"), right: s("CS-Pi", "collides") },
      { name: "unguided_vs_amr_sample02", left: s(U, "collides"), right: s("CS-Pi", "collides") },
    ],
  },
];
