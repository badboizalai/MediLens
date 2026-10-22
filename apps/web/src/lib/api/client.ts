import { z } from 'zod';

/**
 * Typed client for the upload flow (BR-010):
 *   POST /v1/profiles/{id}/documents   -> presigned PUT targets (one per page, in order)
 *   PUT  <presigned url>               -> bytes go straight to storage
 *   POST /v1/documents/{id}/complete   -> starts processing
 *   GET  /v1/documents/{id}            -> processing status / retake reason
 */

export const RETAKE_REASONS = ['blurry', 'too_dark', 'not_a_document'] as const;
export type RetakeReason = (typeof RETAKE_REASONS)[number];

const createResponse = z.object({
  document_id: z.string().min(1),
  uploads: z.array(z.object({ url: z.string().url(), headers: z.record(z.string()).optional() })).min(1),
});
const statusResponse = z.object({
  status: z.enum(['queued', 'reading', 'extracting', 'ready', 'needs_retake', 'failed']),
  retake_reason: z.enum(RETAKE_REASONS).nullish(),
});
export type DocumentStatus = z.infer<typeof statusResponse>;

export interface PageFile {
  filename: string;
  content_type: string;
  size_bytes: number;
}

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
  return res.status === 204 ? null : res.json();
}

export async function createDocument(profileId: string, pages: PageFile[]) {
  const body = await call(`/v1/profiles/${encodeURIComponent(profileId)}/documents`, {
    method: 'POST',
    body: JSON.stringify({ pages }),
  });
  return createResponse.parse(body);
}

export async function putToPresignedUrl(
  target: { url: string; headers?: Record<string, string> },
  file: Blob,
  signal?: AbortSignal,
) {
  const res = await fetch(target.url, { method: 'PUT', body: file, headers: target.headers, signal });
  if (!res.ok) throw new ApiError(res.status);
}

export async function completeDocument(documentId: string) {
  await call(`/v1/documents/${encodeURIComponent(documentId)}/complete`, { method: 'POST' });
}

export async function getDocumentStatus(documentId: string) {
  return statusResponse.parse(await call(`/v1/documents/${encodeURIComponent(documentId)}`, { method: 'GET' }));
}
