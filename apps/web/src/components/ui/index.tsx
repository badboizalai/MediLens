'use client';

// The design-system barrel mixes server-safe and hook-using components, so server code must go
// through this client boundary instead of importing '@medilens/design-system' directly.
import { cssVariables } from '@medilens/design-system';

export { Alert, Button, Card, Dropzone } from '@medilens/design-system';

/** Injects the --ml-* design tokens (light default, dark via [data-theme="dark"]). */
export function ThemeStyle() {
  return <style dangerouslySetInnerHTML={{ __html: cssVariables() }} />;
}
