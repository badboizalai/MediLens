import { z } from 'zod';

/**
 * Typed client for the upload flow (BR-010), matching apps/api document router:
 *   POST /v1/profiles/{profile_id}/documents  {content_type,size_bytes} -> presigned PUT (one document per file)
 *   PUT  <upload_url>                          -> bytes go straight to storage
 *   POST /v1/documents/{id}/complete           -> DocumentOut, starts processing
 *   GET  /v1/documents/{id}                    -> DocumentOut (+ retake_reason from the worker)
 */

export const RETAKE_REASONS = ['blurry', 'too_dark', 'not_a_document'] as const;
export type RetakeReason = (typeof RETAKE_REASONS)[number];

const createResponse = z.object({
  document_id: z.string().uuid(),
  upload_url: z.string().url(),
  method: z.string().default('PUT'),
  headers: z.record(z.string()).default({}),
  expires_in: z.number(),
});
const documentOut = z.object({
  id: z.string().uuid(),
  profile_id: z.string().uuid(),
  status: z.string(),
  // Set by the worker together with status "needs_retake" (codes from the quality gate).
  retake_reason: z.enum(RETAKE_REASONS).nullish(),
});
export type DocumentOut = z.infer<typeof documentOut>;
export type UploadTarget = z.infer<typeof createResponse>;

/** Coarse UI stage derived from the backend/worker document status. */
export type Stage = 'queued' | 'reading' | 'extracting' | 'ready' | 'needs_retake' | 'failed';
const STAGE: Record<string, Stage> = {
  'uploaded-pending': 'queued',
  uploaded: 'queued',
  validated: 'reading',
  preprocessed: 'reading',
  classified: 'reading',
  ocr_done: 'extracting',
  extracted: 'extracting',
  needs_review: 'ready',
  confirmed: 'ready',
  needs_retake: 'needs_retake',
  failed: 'failed',
};
export const stageOf = (status: string): Stage => STAGE[status] ?? 'queued';

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly title?: string,
  ) {
    super(title ?? `HTTP ${status}`);
  }
}

const base = () => process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

async function call(path: string, init: RequestInit): Promise<unknown> {
  const res = await fetch(`${base()}${path}`, {
    ...init,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init.headers },
  });
  if (!res.ok) {
    // RFC 7807 Problem Details: keep only the title, never the detail.
    const problem = (await res.json().catch(() => ({}))) as { title?: string };
    throw new ApiError(res.status, problem.title);
  }
  return res.json();
}

/** One document per file (one page = one document). */
export async function createDocument(profileId: string, file: { content_type: string; size_bytes: number }) {
  const body = await call(`/v1/profiles/${encodeURIComponent(profileId)}/documents`, {
    method: 'POST',
    body: JSON.stringify(file),
  });
  return createResponse.parse(body);
}

export async function putToPresignedUrl(target: UploadTarget, file: Blob, signal?: AbortSignal) {
  const res = await fetch(target.upload_url, { method: target.method, body: file, headers: target.headers, signal });
  if (!res.ok) throw new ApiError(res.status);
}

export async function completeDocument(documentId: string) {
  return documentOut.parse(await call(`/v1/documents/${encodeURIComponent(documentId)}/complete`, { method: 'POST' }));
}

/** Status read; not on main yet. Shape is DocumentOut plus an optional retake_reason. */
export async function getDocument(documentId: string) {
  return documentOut.parse(await call(`/v1/documents/${encodeURIComponent(documentId)}`, { method: 'GET' }));
}
