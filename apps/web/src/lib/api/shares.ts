import { z } from 'zod';
import { ApiError } from './client';

/** Typed client for apps/api sharing router (S11-T103). Scope is fixed server-side to findings:read. */
const share = z.object({
  id: z.string().uuid(),
  profile_id: z.string().uuid(),
  grantee_user_id: z.string().uuid(),
  scope: z.string(),
  expires_at: z.string(),
  revoked_at: z.string().nullable(),
});
const sharedFinding = z.object({
  region_code: z.string(),
  laterality: z.string().nullable(),
  severity: z.string().nullable(),
  unit_code: z.string().nullable(),
  is_metastasis: z.boolean(),
  observed_at: z.string().nullable(),
  label: z.string().nullable(),
});
const findingsPage = z.object({ findings: z.array(sharedFinding), next_cursor: z.string().nullable() });
const sharedShare = z.object({ share_id: z.string().uuid(), scope: z.string(), expires_at: z.string(), status: z.string() });
const me = z.object({ sub: z.string() });
export type ShareDto = z.infer<typeof share>;
export type SharedFindingDto = z.infer<typeof sharedFinding>;

async function call(path: string, init: RequestInit = {}): Promise<unknown> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? ''}/v1${path}`, {
    ...init,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init.headers },
  });
  if (!res.ok) {
    const problem = (await res.json().catch(() => ({}))) as { title?: string }; // title only, never detail
    throw new ApiError(res.status, problem.title);
  }
  return res.status === 204 ? null : res.json();
}

const id = encodeURIComponent;

export const createShare = async (profileId: string, granteeUserId: string, expiresInHours: number) =>
  share.parse(
    await call(`/profiles/${id(profileId)}/shares`, {
      method: 'POST',
      body: JSON.stringify({ grantee_user_id: granteeUserId, expires_in_hours: expiresInHours }),
    }),
  );
export const listShares = async (profileId: string) =>
  z.array(share).parse(await call(`/profiles/${id(profileId)}/shares`));
export const revokeShare = async (shareId: string) => void (await call(`/shares/${id(shareId)}`, { method: 'DELETE' }));
export const getSharedFindings = async (shareId: string, cursor?: string) =>
  findingsPage.parse(await call(`/shared/${id(shareId)}/findings${cursor ? `?cursor=${id(cursor)}` : ''}`));
export const getMe = async () => me.parse(await call('/me'));
export const getSharedShare = async (shareId: string) => sharedShare.parse(await call(`/shared/${id(shareId)}`));
