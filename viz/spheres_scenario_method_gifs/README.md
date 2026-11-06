# Sphere-Avoid GIFs — CS-Pi vs Guidance vs Trust vs Projection (2026-11-06)

Rendered from the EXACT samples of the camera-ready release run
`/grogu/datasets/rollout/cspi_release/results/tab_spheres/<Method>/{id,ood}.pt`
(same checkpoint `assets/checkpoints/spheres.pt`, same 120 tasks, best configs from
`configs/tab_spheres.yaml`). No re-sampling. Decoded with the release `spheres.trajectory`
and checked with the release `MPDCost` (collision-free iff cost < 1e-3).

| Method | Config | Table Safe-SR L1/ID | L2/OOD |
|---|---|---|---|
| CS-Pi | k=50, K_max=20, τ=1e-3 | 99.9% | 91.8% |
| Gradient guidance | α=0.01 | 23.6% | 4.7% |
| Trust sampling | w=0.3, J=5 | 77.0% | 38.7% |
| Projection | Newton projection | 88.2% | 62.1% |
| Unguided (reference) | — | 8.9% | 0.8% |

L1/ID = EnvSpheres3D (10 red spheres); L2/OOD = EnvSpheres3DExtraObjectsV00 (+6 orange).
Green dot = start EE, blue dot = goal EE. Top-down camera.

## Tasks (illustrative, NOT typical)
Auto-picked: tasks where the shown CS-Pi sample is collision-free and the shown sample of
every other method collides. They show the failure modes; the table above is the typical rate.
Each panel shows sample 0 of the 8; "task: k/8 samples safe" in the header is over all 8.

| unit | task | CS-Pi | Guidance | Trust | Projection | Unguided |  (collision waypoints /64 of shown sample; k/8 safe) |
|---|---|---|---|---|---|---|---|
| id  | 58 | 0 · 8/8 | 14 · 0/8 | 1 · 6/8 | 2 · 4/8 | 38 · 0/8 | |
| id  | 86 | 0 · 8/8 | 20 · 1/8 | 3 · 6/8 | 1 · 6/8 | 33 · 0/8 | |
| id  | 98 | 0 · 8/8 | 6 · 0/8 | 7 · 3/8 | 3 · 4/8 | 24 · 1/8 | |
| ood | 41 | 0 · 7/8 | 38 · 0/8 | 14 · 0/8 | 5 · 4/8 | 53 · 0/8 | |
| ood | 44 | 0 · 7/8 | 42 · 0/8 | 27 · 0/8 | 5 · 1/8 | 49 · 0/8 | |
| ood | 60 | 0 · 8/8 | 33 · 0/8 | 18 · 0/8 | 1 · 5/8 | 62 · 0/8 | |

## Files per task (`<unit>/task<N>/`)
- `grid.gif` — 2×2: CS-Pi | Guidance / Trust | Projection, synchronized
- `CS-Pi.gif`, `Guidance.gif`, `Trust.gif`, `Projection.gif`, `Unguided.gif` — single panels
- `filmstrip.png` — 6 evenly spaced frames per method (static snapshot)
- `info.json` — per-method trajectory cost, collision waypoints, goal error, k/8 safe
Frames with a red border / "IN COLLISION" are waypoints whose MPD cost ≥ 1e-3.

Reproduce: `sbatch submit_spheres_gifs.sh` (branch `worktree-orient-gifs`,
`render_spheres_methods.py`; `--tasks "id:58,86;ood:44"` to choose tasks, `--sample` for
another of the 8 samples, `--cam` for the view).
