import type { Field } from './api';

/** BR-012: a low-confidence field blocks confirm until it has confirmed_at. */
export const pending = (fields: Field[]) => fields.filter((f) => f.needs_confirmation && !f.confirmed_at);
export const canConfirm = (fields: Field[]) => fields.length > 0 && pending(fields).length === 0;
export const shown = (f: Field) => f.user_value ?? f.value ?? '';
