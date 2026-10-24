import type { SeverityKey } from '@medilens/design-system';
import type { ShareDto, SharedFindingDto } from '@/lib/api/shares';

export const EXPIRY_HOURS = [1, 24, 72, 168] as const; // 1 h to 7 d (API max 168)
export type ShareStatus = 'active' | 'expired' | 'revoked';

export const statusOf = (s: Pick<ShareDto, 'expires_at' | 'revoked_at'>, now = Date.now()): ShareStatus =>
  s.revoked_at ? 'revoked' : Date.parse(s.expires_at) <= now ? 'expired' : 'active';

/** Time left rounded up; up to 24 h shown in hours, beyond that in days. */
export function timeLeft(expiresAt: string, now = Date.now()) {
  const hours = Math.max(0, Math.ceil((Date.parse(expiresAt) - now) / 3_600_000));
  return hours > 24 ? { unit: 'days' as const, n: Math.ceil(hours / 24) } : { unit: 'hours' as const, n: hours };
}

export const shortId = (uuid: string) => uuid.slice(0, 8);

const SEVERITIES = new Set<string>(['monitor', 'mild', 'moderate', 'severe', 'spread', 'reference']);
export const toRegions = (fs: SharedFindingDto[]) =>
  fs.map((f) => ({
    region_code: f.region_code,
    severity: (f.severity && SEVERITIES.has(f.severity) ? f.severity : 'reference') as SeverityKey,
    label: f.label ?? f.region_code,
  }));
