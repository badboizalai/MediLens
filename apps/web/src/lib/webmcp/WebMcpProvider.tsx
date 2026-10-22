'use client';

import { useEffect } from 'react';
import { registerWebMcpTools } from './register';

export function WebMcpProvider() {
  useEffect(
    () =>
      registerWebMcpTools([
        {
          name: 'medilens_about',
          description: 'What MediLens does and its safety boundary (no diagnosis, dosing or prognosis).',
          inputSchema: { type: 'object', properties: {} },
          execute: () => ({
            product: 'MediLens',
            purpose: 'Helps patients understand their own medical records on a 2D/3D body model.',
            boundary: 'Illustration and explanation only; not a diagnosis or treatment advice.',
          }),
        },
      ]),
    [],
  );
  return null;
}
