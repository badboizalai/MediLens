// @vitest-environment jsdom
// Markup snapshots (no browser): catch unintended changes to the rendered 2D body map and odontogram.
import { render } from '@testing-library/react';
import { NextIntlClientProvider } from 'next-intl';
import { describe, expect, it } from 'vitest';
import en from '../../../../messages/en.json';
import { BodyMap2D, type Finding } from '../core/BodyMap2D';
import { Odontogram, type OdontogramTooth } from '../units/dental/Odontogram';

const html = (ui: React.ReactElement) =>
  render(
    <NextIntlClientProvider locale="en" messages={en}>
      {ui}
    </NextIntlClientProvider>,
  ).container.innerHTML.replace(/></g, '>\n<');

// Synthetic finding set: one per severity; 'spread' is the metastasis severity.
const perSeverity: Record<'front' | 'back', Finding[]> = {
  front: [
    { region_code: 'heart', severity: 'reference' },
    { region_code: 'liver', severity: 'monitor' },
    { region_code: 'stomach', severity: 'mild' },
    { region_code: 'lung_l', severity: 'moderate' },
    { region_code: 'lung_r', severity: 'severe' },
    { region_code: 'brain', severity: 'spread' },
  ],
  back: [
    { region_code: 'spleen', severity: 'reference' },
    { region_code: 'kidney_l', severity: 'monitor' },
    { region_code: 'kidney_r', severity: 'mild' },
    { region_code: 'lung_l', severity: 'moderate' },
    { region_code: 'adrenal_l', severity: 'severe' },
    { region_code: 'bone_spine', severity: 'spread' },
  ],
};

describe('BodyMap2D snapshots', () => {
  for (const side of ['front', 'back'] as const) {
    it(`${side}: empty`, () => expect(html(<BodyMap2D side={side} findings={[]} />)).toMatchSnapshot());
    it(`${side}: one finding per severity`, () =>
      expect(html(<BodyMap2D side={side} findings={perSeverity[side]} />)).toMatchSnapshot());
  }
  it('unmapped codes are not drawn but listed as not placed (HZ-002)', () =>
    expect(
      html(<BodyMap2D side="front" findings={[{ region_code: 'nope', severity: 'mild' }, ...perSeverity.front.slice(0, 1)]} />),
    ).toMatchSnapshot());
});

const states: OdontogramTooth[] = [
  { fdi: '16', state: 'caries', surfaces: ['O', 'M'] },
  { fdi: '25', state: 'filled', surfaces: ['D'] },
  { fdi: '36', state: 'missing' },
  { fdi: '46', state: 'implant' },
  { fdi: '11', state: 'filled', surfaces: ['I', 'P'] }, // I->O, P->L
];

describe('Odontogram snapshots', () => {
  it('empty', () => expect(html(<Odontogram teeth={[]} />)).toMatchSnapshot());
  it('each state and surface incl. I->O, P->L', () => expect(html(<Odontogram teeth={states} />)).toMatchSnapshot());
});
