'use client';

import { Canvas, useFrame, useThree, type ThreeEvent } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import { useEffect, useMemo, useRef } from 'react';
import { Box3, Color, MeshStandardMaterial, Vector3, type Mesh } from 'three';
import { FPS_WARMUP_S, FPS_WINDOW_S, MAX_DPR, MIN_FPS } from './budget';
import { NEUTRAL_COLOR, isLod1, regionOf, severityColor, type Region3D } from './logic';

// Bundler resolves these to hashed static assets served from 'self' (CSP connect-src).
const URLS = {
  body: new URL('../../../../../../packages/anatomy-assets/glb/body.glb', import.meta.url).toString(),
  heart: new URL('../../../../../../packages/anatomy-assets/glb/heart.glb', import.meta.url).toString(),
};

export type Scene3DProps = {
  model: 'body' | 'heart';
  regions: Region3D[];
  selected: string | null;
  onPick: (code: string | null) => void;
  /** Called once if average FPS stays below MIN_FPS after warm-up. */
  onLowFps?: () => void;
};

type Pose = { pos: Vector3; target: Vector3 };
type Orbit = { target: Vector3; update: () => void; addEventListener: (t: string, f: () => void) => void; removeEventListener: (t: string, f: () => void) => void };

function Model({ model, regions, selected, onPick }: Omit<Scene3DProps, 'onLowFps'>) {
  const { scene } = useGLTF(URLS[model]);
  const root = useMemo(() => scene.clone(true), [scene]);
  const meshes = useMemo(() => {
    const out: Mesh[] = [];
    root.traverse((o) => {
      const m = o as Mesh;
      if (!m.isMesh) return;
      if (isLod1(m.name)) m.visible = false; // shortcut: LOD1 hidden; switch to <Detailed> if FPS needs it
      m.material = new MeshStandardMaterial();
      out.push(m);
    });
    return out;
  }, [root]);

  // Materials are per-mesh (ours); geometry/textures belong to the shared, cached GLTF.
  useEffect(() => () => meshes.forEach((m) => (m.material as MeshStandardMaterial).dispose()), [meshes]);

  useEffect(() => {
    const sev = new Map(regions.map((r) => [r.region_code, r.severity]));
    for (const m of meshes) {
      const code = regionOf(m.name);
      const s = sev.get(code);
      const on = code === selected;
      const mat = m.material as MeshStandardMaterial;
      mat.color = new Color(s ? severityColor(s) : NEUTRAL_COLOR);
      mat.emissive = new Color(on ? '#FFFFFF' : '#000000');
      mat.emissiveIntensity = on ? 0.45 : 0;
      // The silhouette must not hide the organs inside it.
      const shell = model === 'body' && code === 'body';
      mat.transparent = shell;
      mat.opacity = shell ? 0.18 : 1;
      mat.depthWrite = !shell;
    }
  }, [meshes, regions, selected, model]);

  const listed = useMemo(() => new Set(regions.map((r) => r.region_code)), [regions]);
  const pick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    onPick(e.intersections.map((i) => regionOf(i.object.name)).find((c) => listed.has(c)) ?? null);
  };
  return <primitive object={root} onClick={pick} onPointerMissed={() => onPick(null)} />;
}

/** Eases orbit target + camera toward the selected region (or home); snaps under reduced motion. */
function Focus({ model, selected }: { model: string; selected: string | null }) {
  const camera = useThree((s) => s.camera);
  const scene = useThree((s) => s.scene);
  const controls = useThree((s) => s.controls) as unknown as Orbit | null;
  const home = useRef<Pose | null>(null);
  const goal = useRef<Pose | null>(null);

  useEffect(() => {
    if (!controls) return;
    home.current ??= { pos: camera.position.clone(), target: controls.target.clone() };
    if (!selected) {
      goal.current = { pos: home.current.pos.clone(), target: home.current.target.clone() };
      return;
    }
    const box = new Box3();
    scene.traverse((o) => {
      const m = o as Mesh;
      if (m.isMesh && m.visible && regionOf(m.name) === selected) box.expandByObject(m);
    });
    if (box.isEmpty()) return;
    const target = box.getCenter(new Vector3());
    const dist = Math.max(box.getSize(new Vector3()).length() * 2, 0.6);
    const dir = camera.position.clone().sub(controls.target).normalize();
    goal.current = { pos: target.clone().add(dir.multiplyScalar(dist)), target };
  }, [selected, controls, camera, scene, model]);

  useEffect(() => {
    // A manual orbit cancels the ease so the user is never fought.
    const stop = () => { goal.current = null; };
    controls?.addEventListener('start', stop);
    return () => controls?.removeEventListener('start', stop);
  }, [controls]);

  useFrame((_, dt) => {
    const g = goal.current;
    if (!g || !controls) return;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const k = reduce ? 1 : 1 - Math.exp(-6 * dt);
    camera.position.lerp(g.pos, k);
    controls.target.lerp(g.target, k);
    controls.update();
    if (camera.position.distanceTo(g.pos) < 0.001) goal.current = null;
  });
  return null;
}

/** Counts frames after warm-up; fires onLow once if the average is under MIN_FPS. */
function FpsGuard({ onLow }: { onLow: () => void }) {
  const s = useRef({ t: 0, frames: 0, done: false });
  useFrame((_, dt) => {
    const c = s.current;
    if (c.done || dt > 0.5) return; // a long stall (tab hidden) is not a rendering-speed signal
    c.t += dt;
    if (c.t < FPS_WARMUP_S) return;
    c.frames += 1;
    const span = c.t - FPS_WARMUP_S;
    if (span >= FPS_WINDOW_S) {
      c.done = true;
      if (c.frames / span < MIN_FPS) onLow();
    }
  });
  return null;
}

export default function Scene3D({ onLowFps, ...props }: Scene3DProps) {
  return (
    <Canvas camera={{ position: [0, 0.3, props.model === 'body' ? 4 : 2.2], fov: 40 }} dpr={[1, MAX_DPR]}>
      {onLowFps && <FpsGuard onLow={onLowFps} />}
      <ambientLight intensity={0.8} />
      <directionalLight position={[3, 4, 5]} intensity={1.4} />
      <Model {...props} />
      <OrbitControls makeDefault enablePan={false} />
      <Focus model={props.model} selected={props.selected} />
    </Canvas>
  );
}
