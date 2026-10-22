/** Client-side limits (BR-010). The server re-checks everything; this is only fast feedback. */
export const MAX_FILE_BYTES = 20 * 1024 * 1024;
export const MAX_PAGES = 30;
export const ACCEPT = 'image/jpeg,image/png,image/heic,image/heif,application/pdf,.jpg,.jpeg,.png,.heic,.heif,.pdf';

const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png', 'image/heic', 'image/heif', 'application/pdf']);
const EXT_TYPE: Record<string, string> = {
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  png: 'image/png',
  heic: 'image/heic',
  heif: 'image/heif',
  pdf: 'application/pdf',
};

export type FileProblem = 'badType' | 'tooLarge' | 'empty';

/** Some browsers leave `type` empty for HEIC, so fall back to the extension. */
export function contentTypeOf(file: Pick<File, 'name' | 'type'>): string {
  if (ALLOWED_TYPES.has(file.type)) return file.type;
  return EXT_TYPE[file.name.split('.').pop()?.toLowerCase() ?? ''] ?? file.type;
}

export function checkFile(file: Pick<File, 'name' | 'type' | 'size'>): FileProblem | null {
  if (!ALLOWED_TYPES.has(contentTypeOf(file))) return 'badType';
  if (file.size === 0) return 'empty';
  if (file.size > MAX_FILE_BYTES) return 'tooLarge';
  return null;
}
