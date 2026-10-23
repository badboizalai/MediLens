/**
 * Placeholder until the profile API lands: the active profile is a UUID.
 * Set NEXT_PUBLIC_DEV_PROFILE_ID in dev; replace with a real profile query later.
 */
const NIL_UUID = '00000000-0000-0000-0000-000000000000';

export function useProfileId(): string {
  return process.env.NEXT_PUBLIC_DEV_PROFILE_ID ?? NIL_UUID;
}
