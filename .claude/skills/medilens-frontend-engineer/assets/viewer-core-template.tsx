// features/viewer/core/BodyCanvas.tsx — core 3D viewer skeleton
'use client';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, useGLTF, Line } from '@react-three/drei';
import { Suspense, useEffect, useMemo } from 'react';
import * as THREE from 'three';
import type { Finding } from '../types';
import { severityColor } from '@/lib/tokens';

type Props = { glbUrl: string; findings: Finding[]; selected?: string; xray: number; onSelect(code: string): void };

function Model({ glbUrl, findings, selected, xray, onSelect }: Props) {
  const { scene } = useGLTF(glbUrl, true);
  const { invalidate } = useThree();
  const regions = useMemo(() => {
    const map = new Map<string, THREE.Mesh>();
    scene.traverse(o => { if ((o as THREE.Mesh).isMesh) map.set(o.name, o as THREE.Mesh); });
    return map;
  }, [scene]);

  useEffect(() => {
    const originals = new Map<THREE.Mesh, THREE.Material | THREE.Material[]>();
    for (const f of findings) {
      const mesh = regions.get(f.regionCode);
      if (!mesh || !f.severity) continue;
      originals.set(mesh, mesh.material);
      mesh.material = new THREE.MeshStandardMaterial({
        color: severityColor(f.severity), transparent: true, opacity: 0.75,
        emissive: new THREE.Color(severityColor(f.severity)), emissiveIntensity: selected === f.regionCode ? 0.4 : 0.1,
      });
    }
    regions.forEach((m, code) => { if (code.startsWith('skin') || code.startsWith('muscle')) {
      (m.material as THREE.MeshStandardMaterial).transparent = true;
      (m.material as THREE.MeshStandardMaterial).opacity = 1 - xray;
    }});
    invalidate();
    return () => { originals.forEach((mat, mesh) => { (mesh.material as THREE.Material).dispose(); mesh.material = mat; }); };
  }, [findings, selected, xray, regions, invalidate]);

  const metastasisLines = useMemo(() => {
    const primary = findings.find(f => !f.isMetastasis && regions.has(f.regionCode));
    if (!primary) return [];
    const centroid = (code: string) => new THREE.Box3().setFromObject(regions.get(code)!).getCenter(new THREE.Vector3());
    return findings.filter(f => f.isMetastasis && regions.has(f.regionCode)).map(f => {
      const a = centroid(primary.regionCode), b = centroid(f.regionCode);
      const mid = a.clone().add(b).multiplyScalar(0.5).add(new THREE.Vector3(0.15, 0.1, 0.2));
      return new THREE.QuadraticBezierCurve3(a, mid, b).getPoints(32);
    });
  }, [findings, regions]);

  return (
    <group onPointerDown={e => { e.stopPropagation(); onSelect(e.object.name); }}>
      <primitive object={scene} />
      {metastasisLines.map((pts, i) => <Line key={i} points={pts} color={severityColor('spread')} lineWidth={3} />)}
    </group>
  );
}

export default function BodyCanvas(props: Props) {
  return (
    <Canvas dpr={[1, 2]} frameloop="demand" camera={{ fov: 35, position: [0, 1.2, 3.2] }}>
      <ambientLight intensity={0.6} />
      <directionalLight position={[2, 4, 3]} intensity={0.8} />
      <Suspense fallback={null}>
        <Model {...props} />
      </Suspense>
      <OrbitControls enableDamping minDistance={0.8} maxDistance={6} makeDefault />
    </Canvas>
  );
}
