import type { Config } from 'tailwindcss';
import designSystemPreset from '@medilens/design-system/tailwind-preset';

const config: Config = {
  presets: [designSystemPreset as Config],
  content: ['./src/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
};

export default config;
