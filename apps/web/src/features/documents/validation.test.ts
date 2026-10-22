import { describe, expect, it } from 'vitest';
import { checkFile, contentTypeOf, MAX_FILE_BYTES } from './validation';

const f = (name: string, type: string, size = 1000) => ({ name, type, size });

describe('checkFile (BR-010)', () => {
  it('accepts JPG, PNG, HEIC and PDF', () => {
    expect(checkFile(f('a.jpg', 'image/jpeg'))).toBeNull();
    expect(checkFile(f('a.png', 'image/png'))).toBeNull();
    expect(checkFile(f('a.heic', 'image/heic'))).toBeNull();
    expect(checkFile(f('a.pdf', 'application/pdf'))).toBeNull();
  });
  it('falls back to the extension when the browser gives no type (HEIC)', () => {
    expect(contentTypeOf(f('IMG_1.HEIC', ''))).toBe('image/heic');
    expect(checkFile(f('IMG_1.HEIC', ''))).toBeNull();
  });
  it('rejects other formats', () => {
    expect(checkFile(f('a.exe', 'application/x-msdownload'))).toBe('badType');
    expect(checkFile(f('a.svg', 'image/svg+xml'))).toBe('badType');
  });
  it('enforces the 20 MB limit at the boundary', () => {
    expect(checkFile(f('a.pdf', 'application/pdf', MAX_FILE_BYTES))).toBeNull();
    expect(checkFile(f('a.pdf', 'application/pdf', MAX_FILE_BYTES + 1))).toBe('tooLarge');
  });
  it('rejects empty files', () => {
    expect(checkFile(f('a.png', 'image/png', 0))).toBe('empty');
  });
});
