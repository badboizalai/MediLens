'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useForm, type Resolver } from 'react-hook-form';
import { z } from 'zod';
import { Alert, Button, Card } from '@/components/ui';
import { confirmDocument, editField, listFields, pageImageUrl, parseBox, UnconfirmedError, type Field } from './api';
import { canConfirm, pending, shown } from './logic';

const MAX_LEN = 2000; // matches the API's EditRequest
const schema = z.object({ value: z.string().trim().min(1, 'required').max(MAX_LEN, 'tooLong') });
type Form = z.infer<typeof schema>;

const resolver: Resolver<Form> = async (values) => {
  const r = schema.safeParse(values);
  if (r.success) return { values: r.data, errors: {} };
  const issue = r.error.issues[0]!;
  return { values: {}, errors: { value: { type: issue.code, message: issue.message } } };
};

export function ReviewScreen({ documentId }: { documentId: string }) {
  const t = useTranslations('review');
  const qc = useQueryClient();
  const key = ['review-fields', documentId];
  const fields = useQuery({ queryKey: key, queryFn: () => listFields(documentId) });
  const confirm = useMutation({ mutationFn: () => confirmDocument(documentId) });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const left = fields.data ? pending(fields.data) : [];

  if (fields.isPending) return <p role="status">{t('loading')}</p>;
  if (fields.isError) return <Alert tone="danger">{t('loadError')}</Alert>;
  const data = fields.data;
  const blocked = confirm.error instanceof UnconfirmedError ? confirm.error : null;

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <SourcePanel documentId={documentId} field={data.find((f) => f.id === selectedId) ?? null} />
      <section aria-labelledby="review-fields" className="grid content-start gap-4">
        <h2 id="review-fields" className="text-lg font-semibold">
          {t('fields')}
        </h2>
        <p>{t('aiNote')}</p>
        {data.length === 0 && <Alert tone="info">{t('empty')}</Alert>}
        <ul className="grid gap-3">
          {data.map((f) => (
            <FieldRow
              key={f.id}
              field={f}
              documentId={documentId}
              selected={f.id === selectedId}
              onSelect={() => setSelectedId(f.id)}
              onSaved={(saved) =>
                qc.setQueryData<Field[]>(key, (old) => old?.map((x) => (x.id === saved.id ? saved : x)))
              }
            />
          ))}
        </ul>

        {blocked && (
          <Alert tone="danger" title={t('blocked')}>
            <ul>
              {blocked.fieldIds.map((id) => (
                <li key={id}>{data.find((f) => f.id === id)?.field_path ?? id}</li>
              ))}
            </ul>
          </Alert>
        )}
        {confirm.isError && !blocked && <Alert tone="danger">{t('saveError')}</Alert>}
        {confirm.isSuccess && <Alert tone="success">{t('done')}</Alert>}

        <div className="sticky bottom-0 flex flex-wrap items-center gap-3 bg-[var(--ml-color-surface,#fff)] py-3">
          <p aria-live="polite" className="grow">
            {t('remaining', { n: left.length })}
          </p>
          <Button disabled={!canConfirm(data) || confirm.isPending || confirm.isSuccess} onClick={() => confirm.mutate()}>
            {t('confirmAll')}
          </Button>
        </div>
      </section>
    </div>
  );
}

function FieldRow({
  field,
  documentId,
  selected,
  onSelect,
  onSaved,
}: {
  field: Field;
  documentId: string;
  selected: boolean;
  onSelect: () => void;
  onSaved: (f: Field) => void;
}) {
  const t = useTranslations('review');
  const form = useForm<Form>({ resolver, defaultValues: { value: shown(field) } });
  const save = useMutation({
    mutationFn: (v: Form) => editField(documentId, field.id, v.value),
    onSuccess: onSaved,
  });
  const low = field.needs_confirmation && !field.confirmed_at;
  const inputId = `field-${field.id}`;
  const errId = `${inputId}-err`;
  const error = form.formState.errors.value;

  return (
    <li>
      <Card className={low ? 'border-2 border-dashed border-amber-600' : undefined}>
        <form onSubmit={form.handleSubmit((v) => save.mutate(v))} noValidate className="grid gap-2">
          <label htmlFor={inputId} className="font-semibold">
            {field.field_path}
          </label>
          <p className="text-sm">
            {field.user_value != null ? t('edited') : t('aiExtracted')}
            {field.source_page != null && ` · ${t('page', { n: field.source_page })}`}
            {field.confirmed_at && ` · ✓ ${t('confirmed')}`}
          </p>
          {low && (
            <p className="font-semibold">
              <span aria-hidden="true">▲ </span>
              {t('needsCheck')} {t('lowConfidence')}
            </p>
          )}
          <input
            id={inputId}
            className="rounded border border-neutral-500 p-2"
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? errId : undefined}
            {...form.register('value')}
          />
          {error && (
            <p id={errId} role="alert">
              {t(error.message === 'tooLong' ? 'tooLong' : 'required', { max: MAX_LEN })}
            </p>
          )}
          {save.isError && <p role="alert">{t('saveError')}</p>}
          <div className="flex flex-wrap gap-2">
            {field.source_page != null && (
              <Button type="button" variant="secondary" aria-pressed={selected} onClick={onSelect}>
                {t('showOnPage')}
              </Button>
            )}
            <Button type="submit" variant={low ? 'primary' : 'secondary'} disabled={save.isPending}>
              {low ? t('confirmField') : t('save')}
            </Button>
          </div>
        </form>
      </Card>
    </li>
  );
}

function SourcePanel({ documentId, field }: { documentId: string; field: Field | null }) {
  const t = useTranslations('review');
  const page = field?.source_page ?? null;
  const box = field ? parseBox(field.source_box) : null;
  const [broken, setBroken] = useState<string | null>(null);
  const img = useQuery({
    queryKey: ['review-page-image', documentId, page],
    queryFn: () => pageImageUrl(documentId, page!),
    enabled: page != null,
    staleTime: 240_000, // presigned URL lives 300 s
    retry: false,
  });
  const url = img.data;
  const failed = page != null && (img.isError || (url != null && broken === url));
  return (
    <section aria-labelledby="review-source" className="self-start">
      <Card>
        <h2 id="review-source" className="ml-card__title">
          {t('source')}
        </h2>
        {page == null && <p>{t('sourceSelect')}</p>}
        {page != null && img.isPending && <p role="status">{t('sourceLoading')}</p>}
        {failed && <Alert tone="info">{t('imageMissing')}</Alert>}
        {page != null && url != null && !failed && (
          <>
            <div className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element -- presigned URL, not optimisable */}
              <img src={url} alt={t('sourceAlt', { n: page })} className="block w-full" onError={() => setBroken(url)} />
              {box && (
                <div
                  data-testid="bbox"
                  aria-hidden="true"
                  className="pointer-events-none absolute border-2 border-amber-600 bg-amber-300/30"
                  style={{
                    left: `${box[0] * 100}%`,
                    top: `${box[1] * 100}%`,
                    width: `${(box[2] - box[0]) * 100}%`,
                    height: `${(box[3] - box[1]) * 100}%`,
                  }}
                />
              )}
            </div>
            <p className="text-sm">{box ? t('boxNote') : t('noBox')}</p>
          </>
        )}
      </Card>
    </section>
  );
}
