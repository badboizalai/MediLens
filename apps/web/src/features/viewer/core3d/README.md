# core3d performance budget

Constants live in `budget.ts`. `BodyViewer` (one level up) picks 3D or 2D.

- GLB <= 1.5 MB each (`MAX_GLB_BYTES`; current body/heart are ~150 KB / ~120 KB). Add Draco/meshopt only if a model nears the cap.
- Render at device pixel ratio <= 2 (`MAX_DPR`).
- LOD1 (`*__lod1`) meshes are hidden; only full-detail meshes render.
- three.js is loaded lazily (`BodyViewer3DLazy`), never in the initial bundle.
- Per-mesh materials are disposed on unmount / model change.
- 2D fallback when: no WebGL, Save-Data / `prefers-reduced-data`, < 4 cores, < 4 GB memory, a thrown error (GLB load, context loss), or measured FPS < 30 over a 3 s window after a 1 s warm-up. The user can switch manually; a manual 3D choice disables the FPS auto-fallback.

Manual check (no numbers recorded here): open a document on a weak or CPU-throttled machine, confirm the viewer drops to 2D with an announced reason, and the toggle returns to 3D.
