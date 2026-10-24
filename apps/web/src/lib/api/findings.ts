import { z } from 'zod';

/** GET /v1/profiles/{profile_id}/findings — keyset-paginated; observations come on the first page only. */
const finding = z.object({
  region_code: z.string(),
  laterality: z.string().nullable(),
  severity: z.string().nullable(),
  unit_code: z.string().nullable(),
  is_metastasis: z.boolean(),
  observed_at: z.string().nullable(),
  document_id: z.string().nullable(),
  label: z.string().nullable(),
  source: z.string().nullish(),
});
const observation = z.object({
  name: z.string(),
  value: z.string().nullable(),
  unit: z.string().nullable(),
  loinc_code: z.string().nullable(),
  ref_low: z.number().nullable(),
  ref_high: z.number().nullable(),
  observed_at: z.string().nullable(),
  document_id: z.string().nullable(),
});
const page = z.object({
  findings: z.array(finding),
  observations: z.array(observation),
  next_cursor: z.string().nullable(),
});
export type FindingDto = z.infer<typeof finding>;
export type ObservationDto = z.infer<typeof observation>;
export type FindingsPage = z.infer<typeof page>;

export async function getFindings(profileId: string, cursor?: string): Promise<FindingsPage> {
  const qs = cursor ? `?cursor=${encodeURIComponent(cursor)}` : '';
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const res = await fetch(`${base}/v1/profiles/${encodeURIComponent(profileId)}/findings${qs}`, { credentials: 'include' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return page.parse(await res.json());
}
