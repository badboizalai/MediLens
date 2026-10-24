'use client';

import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import { Alert, Button, Card, Dropzone } from '@/components/ui';
import {
  completeDocument,
  createDocument,
  putToPresignedUrl,
  type UploadTarget,
} from '@/lib/api/client';
import { useProfileId } from '@/lib/profile/useProfileId';
import { ACCEPT, checkFile, contentTypeOf, MAX_FILE_BYTES, MAX_PAGES } from './validation';

interface Page {
  id: number;
  file: File;
}
type Phase = 'select' | 'uploading';

const mb = (bytes: number) => (bytes / 1_048_576).toFixed(1);

export function UploadScreen({ profileId: override }: { profileId?: string }) {
  const fromHook = useProfileId();
  const profileId = override ?? fromHook;
  const t = useTranslations('upload');
  const router = useRouter();
  const locale = useLocale();
  const [pages, setPages] = useState<Page[]>([]);
  const [problems, setProblems] = useState<string[]>([]);
  const [phase, setPhase] = useState<Phase>('select');
  const [done, setDone] = useState(0);
  const [networkError, setNetworkError] = useState(false);
  const nextId = useRef(0);
  const created = useRef<UploadTarget[]>([]);
  const captureRef = useRef<HTMLInputElement>(null);

  const addFiles = (files: File[]) => {
    const msgs: string[] = [];
    const ok: Page[] = [];
    for (const file of files) {
      const problem = checkFile(file);
      if (problem) msgs.push(t(problem, { name: file.name }));
      else ok.push({ id: nextId.current++, file });
    }
    if (pages.length + ok.length > MAX_PAGES) {
      msgs.push(t('tooManyPages'));
    } else if (ok.length) {
      setPages([...pages, ...ok]);
    }
    setProblems(msgs);
  };

  const move = (i: number, by: -1 | 1) => {
    const next = [...pages];
    [next[i], next[i + by]] = [next[i + by]!, next[i]!];
    setPages(next);
  };

  const start = async () => {
    setNetworkError(false);
    setProblems([]);
    setPhase('uploading');
    try {
      // One document per page. Targets are kept so a retry after a dropped connection re-uses them.
      for (let i = done; i < pages.length; i++) {
        const file = pages[i]!.file;
        created.current[i] ??= await createDocument(profileId, {
          content_type: contentTypeOf(file),
          size_bytes: file.size,
        });
        await putToPresignedUrl(created.current[i]!, file);
        await completeDocument(created.current[i]!.document_id);
        setDone(i + 1);
      }
      // Progress is its own route; with several pages it follows the first document.
      router.push(`/${locale}/documents/${created.current[0]!.document_id}/progress`);
    } catch (e) {
      // fetch rejects with TypeError on network failure; keep the selection so Retry continues.
      if (e instanceof TypeError) setNetworkError(true);
      else setProblems([t('genericError')]);
      setPhase('select');
    }
  };

  const uploading = phase === 'uploading';
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <section className="grid content-start gap-4" aria-labelledby="upload-select">
        <h2 id="upload-select" className="sr-only">
          {t('title')}
        </h2>
        <Dropzone
          label={<span className="font-semibold">{t('chooseFile')}</span>}
          hint={`${t('dropHere')} · ${t('hint')}`}
          maxSizeBytes={MAX_FILE_BYTES}
          accept={ACCEPT}
          multiple
          disabled={uploading}
          onFiles={addFiles}
          tooLargeMessage={(f) => t('tooLarge', { name: f.name })}
        />
        <Button variant="secondary" disabled={uploading} onClick={() => captureRef.current?.click()}>
          {t('takePhoto')}
        </Button>
        <input
          ref={captureRef}
          type="file"
          accept="image/*"
          capture="environment"
          hidden
          data-testid="capture-input"
          onChange={(e) => {
            addFiles(Array.from(e.target.files ?? []));
            e.target.value = '';
          }}
        />

        {problems.length > 0 && (
          <Alert tone="danger">
            <ul>
              {problems.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          </Alert>
        )}
        {networkError && (
          <Alert tone="warning">
            <p>{t('retry')}</p>
            <Button variant="secondary" onClick={start}>
              {t('retryButton')}
            </Button>
          </Alert>
        )}

        {pages.length > 0 && (
          <Card>
            <h3 className="ml-card__title">{t('selected')}</h3>
            <ol className="grid gap-2">
              {pages.map((p, i) => (
                <li key={p.id} className="flex flex-wrap items-center gap-2">
                  <span className="grow break-all">
                    {t('pageLabel', { n: i + 1 })} · {p.file.name} · {t('size', { mb: mb(p.file.size) })}
                  </span>
                  <Button variant="secondary" disabled={uploading || i === 0} onClick={() => move(i, -1)} aria-label={t('moveUp', { name: p.file.name })}>
                    ↑
                  </Button>
                  <Button variant="secondary" disabled={uploading || i === pages.length - 1} onClick={() => move(i, 1)} aria-label={t('moveDown', { name: p.file.name })}>
                    ↓
                  </Button>
                  <Button variant="secondary" disabled={uploading} onClick={() => setPages(pages.filter((x) => x.id !== p.id))} aria-label={t('remove', { name: p.file.name })}>
                    ✕
                  </Button>
                </li>
              ))}
            </ol>
          </Card>
        )}

        {uploading && (
          <div>
            <progress className="w-full" max={pages.length} value={done} aria-label={t('progress.label')} />
            <p role="status">{t('progress.uploading', { done, total: pages.length })}</p>
          </div>
        )}
        <Button disabled={uploading || pages.length === 0} onClick={start}>
          {t('submit')}
        </Button>
      </section>

      <CaptureTips />
    </div>
  );
}

function CaptureTips() {
  const t = useTranslations('upload.tips');
  return (
    <details open id="capture-tips" className="ml-card self-start">
      <summary className="ml-card__title cursor-pointer">{t('title')}</summary>
      <ul className="grid list-disc gap-1 pl-5">
        {(['light', 'flat', 'frame', 'glare', 'privacy'] as const).map((k) => (
          <li key={k}>{t(k)}</li>
        ))}
      </ul>
    </details>
  );
}
