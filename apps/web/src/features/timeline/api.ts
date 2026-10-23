import { QueryClient, useQuery } from '@tanstack/react-query';
import { getFindings, type FindingsPage } from '@/lib/api/findings';
import { groupVisits } from './logic';

const MAX_PAGES = 20; // safety stop; a profile with more pages shows what was loaded

async function loadAll(profileId: string) {
  const out: FindingsPage = { findings: [], observations: [], next_cursor: null };
  let cursor: string | undefined;
  for (let i = 0; i < MAX_PAGES; i++) {
    const p = await getFindings(profileId, cursor);
    out.findings.push(...p.findings);
    out.observations.push(...p.observations); // API sends these on the first page only
    if (!p.next_cursor) break;
    cursor = p.next_cursor;
  }
  return groupVisits(out.findings, out.observations);
}

export const useVisits = (profileId: string) =>
  useQuery({ queryKey: ['profile-visits', profileId], queryFn: () => loadAll(profileId) });

export const newClient = () => new QueryClient({ defaultOptions: { queries: { retry: false } } });
