// Performance budget for the 3D viewer (see README.md in this folder).
export const MAX_GLB_BYTES = 1.5 * 1024 * 1024;
export const MAX_DPR = 2;
export const MIN_FPS = 30;
export const FPS_WARMUP_S = 1; // ignore shader compile / first paint
export const FPS_WINDOW_S = 3;
export const MIN_CORES = 4;
export const MIN_MEMORY_GB = 4;

export type Capabilities = {
  webgl: boolean;
  saveData: boolean;
  cores?: number;
  memoryGb?: number;
};
export type Decision = { mode: '3d' | '2d'; reason: 'ok' | 'noWebgl' | 'saveData' | 'lowCores' | 'lowMemory' };

/** Capabilities -> initial viewer. Unknown cores/memory (undefined) do not block 3D. */
export function decideViewer(c: Capabilities): Decision {
  if (!c.webgl) return { mode: '2d', reason: 'noWebgl' };
  if (c.saveData) return { mode: '2d', reason: 'saveData' };
  if (c.cores !== undefined && c.cores < MIN_CORES) return { mode: '2d', reason: 'lowCores' };
  if (c.memoryGb !== undefined && c.memoryGb < MIN_MEMORY_GB) return { mode: '2d', reason: 'lowMemory' };
  return { mode: '3d', reason: 'ok' };
}

export function detectCapabilities(): Capabilities {
  const nav = navigator as Navigator & { deviceMemory?: number; connection?: { saveData?: boolean } };
  let webgl = false;
  try {
    const c = document.createElement('canvas');
    webgl = !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    webgl = false;
  }
  return {
    webgl,
    saveData: !!nav.connection?.saveData || window.matchMedia?.('(prefers-reduced-data: reduce)').matches === true,
    cores: nav.hardwareConcurrency || undefined,
    memoryGb: nav.deviceMemory,
  };
}
