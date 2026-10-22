# Viewer 3D/2D Guide

## 3D (React Three Fiber + drei)
- `<Canvas dpr={[1, 2]} frameloop="demand" camera={{ fov: 35, position: [0, 1.2, 3.2] }}>`; call `invalidate()` on interaction.
- Load with `useGLTF(url, true /* draco */)`; preload only on viewer route; wrap in `<Suspense>` with 2D placeholder.
- Build a `Map<region_code, Object3D>` once by traversing the scene (`obj.name`).
- Picking: R3F pointer events on meshes (`onPointerDown`) or a `Raycaster` against the region map; ignore hidden layers.
- Highlight: clone material per highlighted mesh (`MeshStandardMaterial` with severity colour, `emissive` low intensity, `opacity` from tokens); restore original on clear. Do not mutate shared materials.
- Outline selected region with drei `<Outlines>` or post-processing outline pass (watch perf on mobile).
- Layers: assign meshes to groups (skin, muscle, skeleton, organs, vessels, lymph); toggle `visible`; x-ray slider sets skin/muscle opacity.
- Camera presets: animate with `CameraControls` or lerp target/position over 300 ms (0 ms if reduced motion).
- Labels: drei `<Html>` sparingly (DOM cost); prefer side panel.
- Metastasis lines: `QuadraticBezierCurve3` from primary centroid to site centroid → `<Line>` (drei) width from tokens, purple; reference layer dashed grey.
- Dispose on unmount (geometries, materials, textures) to avoid GPU leaks.

## 2D (SVG)
- Inline SVG components with `id=region_code` paths; colour via `fill` from tokens, plus pattern/hatch overlay for colour-blind support.
- Keyboard: each region `<g role="button" tabIndex={0} aria-label="...">` only in the findings list mode; for full body SVG, provide list-based navigation instead of tabbing 200 paths.
- Dental chart: generated from FDI numbers; 5 surfaces per tooth as separate paths `tooth_36_O`, `tooth_36_M`…

## Fallback logic
```ts
const supportsWebGL = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; } })();
```
Use 2D if `!supportsWebGL`, if `navigator.hardwareConcurrency <= 2` on mobile, or if measured FPS < 25 for 3 s.

## Accessibility
Findings list (`<ul>` grouped by Unit → Region) is the primary accessible interface; selecting an item focuses the region in the viewer and opens details; `aria-live="polite"` announces selection ("Răng 36, sâu răng, mức nặng").
