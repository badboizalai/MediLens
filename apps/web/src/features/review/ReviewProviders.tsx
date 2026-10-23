'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { ReviewScreen } from './ReviewScreen';

// No app-wide QueryClientProvider exists yet; the review route owns one.
export function ReviewProviders({ documentId }: { documentId: string }) {
  const [client] = useState(() => new QueryClient({ defaultOptions: { queries: { retry: false } } }));
  return (
    <QueryClientProvider client={client}>
      <ReviewScreen documentId={documentId} />
    </QueryClientProvider>
  );
}
