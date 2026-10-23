import { z } from 'zod';

/** Typed calls for the extraction review API (S7-T63): fields, edit+confirm one field, confirm document. */
const field = z.object({
  id: z.string(),
  field_path: z.string(),
  value: z.string().nullable(),
  user_value: z.string().nullable(),
  confidence: z.number().nullable(),
  source_page: z.number().nullable(),
  source_box: z.unknown().optional(),
  needs_confirmation: z.boolean(),
  confirmed_at: z.string().nullable(),
});
export type Field = z.infer<typeof field>;

/** 422 from confirm: ids of low-confidence fields still unconfirmed. */
export class UnconfirmedError extends Error {
  constructor(readonly fieldIds: string[]) {
    super('unconfirmed-fields');
  }
}

const base = () => process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

async function call(path: string, init: RequestInit = {}) {
  const res = await fetch(`${base()}/v1/documents/${path}`, {
    ...init,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
  });
  if (res.status === 422) {
    const p = (await res.json().catch(() => ({}))) as { field_ids?: string[] };
    throw new UnconfirmedError(p.field_ids ?? []);
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res;
}

export async function listFields(documentId: string) {
  const res = await call(`${encodeURIComponent(documentId)}/fields`);
  return z.array(field).parse(await res.json());
}

export async function editField(documentId: string, fieldId: string, userValue: string) {
  const res = await call(`${encodeURIComponent(documentId)}/fields/${encodeURIComponent(fieldId)}`, {
    method: 'PATCH',
    body: JSON.stringify({ user_value: userValue }),
  });
  return field.parse(await res.json());
}

export async function confirmDocument(documentId: string) {
  await call(`${encodeURIComponent(documentId)}/confirm`, { method: 'POST' });
}

/** Normalised x0,y0,x1,y1 (0..1, origin top-left), or null when absent/malformed. */
export function parseBox(raw: unknown): [number, number, number, number] | null {
  const n = z.number().min(0).max(1);
  const r = z.tuple([n, n, n, n]).safeParse(raw);
  return r.success && r.data[2] > r.data[0] && r.data[3] > r.data[1] ? r.data : null;
}

/** Short-lived presigned URL of one processed page image. */
export async function pageImageUrl(documentId: string, page: number) {
  const res = await call(`${encodeURIComponent(documentId)}/pages/${page}/image`);
  return z.object({ url: z.string().url() }).parse(await res.json()).url;
}
