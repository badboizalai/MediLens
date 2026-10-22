import 'vitest';
import type { AxeMatchers } from 'vitest-axe/matchers';

declare module 'vitest' {
  interface Assertion<T = unknown> extends AxeMatchers {
    __axe?: T;
  }
  interface AsymmetricMatchersContaining extends AxeMatchers {
    __axe?: never;
  }
}
