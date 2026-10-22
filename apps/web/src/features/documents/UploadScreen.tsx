'use client';

import { useEffect, useRef, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Alert, Button, Card, Dropzone } from '@/components/ui';
import {
  completeDocument,
  createDocument,
  getDocumentStatus,
  putToPresignedUrl,
  type DocumentStatus,
} from '@/lib/api/client';
import { ACCEPT, checkFile, contentTypeOf, MAX_FILE_BYTES, MAX_PAGES } from './validation';

interface Page {
  id: number;
  file: File;
}
type Phase = 'select' | 'uploading' | 'processing';
type Created = Awaited<ReturnType<typeof createDocument>>;

const POLL_MS = 2000;
const STEPS = ['queued', 'reading', 'extracting'] as const;
const mb = (bytes: number) => (bytes / 1_048_576).toFixed(1);

export function UploadScreen({ profileId, pollMs = POLL_MS }: { profileId: string; pollMs?: number }) {
  const t = useTranslations('upload');
  const [pages, setPages] = useState<Page[]>([]);
  const [problems, setProblems] = useState<string[]>([]);
  const [phase, setPhase] = useState<Phase>('select');
  const [done, setDone] = useState(0);
  const [networkError, setNetworkError] = useState(false);
  const [status, setStatus] = useState<DocumentStatus | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const nextId = useRef(0);
  const created = useRef<Created | null>(null);
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
    setStatus(null);
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
      // Re-use an already created document when retrying after a dropped connection.
      created.current ??= await createDocument(
        profileId,
        pages.map(({ file }) => ({ filename: file.name, content_type: contentTypeOf(file), size_bytes: file.size })),
      );
      const { document_id, uploads } = created.current;
      for (let i = done; i < pages.length; i++) {
        await putToPresignedUrl(uploads[i]!, pages[i]!.file);
        setDone(i + 1);
      }
      await completeDocument(document_id);
      setDocumentId(document_id);
      setPhase('processing');
    } catch (e) {
      // fetch rejects with TypeError on network failure; keep the selection so Retry continues.
      if (e instanceof TypeError) setNetworkError(true);
      else setProblems([t('genericError')]);
      setPhase('select');
    }
  };

  const reset = () => {
    created.current = null;
    setPages([]);
    setDone(0);
    setStatus(null);
    setDocumentId(null);
    setPhase('select');
  };

  useEffect(() => {
    if (phase !== 'processing' || !documentId) return;
    let stop = false;
    let timer: ReturnType<typeof setTimeout>;
    const tick = async () => {
      try {
        const s = await getDocumentStatus(documentId);
        if (stop) return;
        setStatus(s);
        if (s.status === 'ready' || s.status === 'needs_retake' || s.status === 'failed') return;
      } catch {
        // transient: keep polling
      }
      if (!stop) timer = setTimeout(tick, pollMs);
    };
    void tick();
    return () => {
      stop = true;
      clearTimeout(timer);
    };
  }, [phase, documentId, pollMs]);

  if (phase === 'processing') return <Progress status={status} onRetake={reset} />;

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
    <details open className="ml-card self-start">
      <summary className="ml-card__title cursor-pointer">{t('title')}</summary>
      <ul className="grid list-disc gap-1 pl-5">
        {(['light', 'flat', 'frame', 'glare', 'privacy'] as const).map((k) => (
          <li key={k}>{t(k)}</li>
        ))}
      </ul>
    </details>
  );
}

function Progress({ status, onRetake }: { status: DocumentStatus | null; onRetake: () => void }) {
  const t = useTranslations('upload');
  const s = status?.status ?? 'queued';

  if (s === 'needs_retake') {
    const reason = status?.retake_reason;
    return (
      <Alert tone="warning" title={t('retake.title')}>
        <p>{reason ? t(`retake.${reason}`) : t('failed')}</p>
        <p>{t('retake.note')}</p>
        <Button onClick={onRetake}>{t('retake.button')}</Button>
      </Alert>
    );
  }
  if (s === 'failed') {
    return (
      <Alert tone="danger">
        <p>{t('failed')}</p>
        <Button onClick={onRetake}>{t('retryButton')}</Button>
      </Alert>
    );
  }
  if (s === 'ready') return <Alert tone="success">{t('ready')}</Alert>;

  const current = STEPS.indexOf(s);
  return (
    <Card>
      <p role="status">{t('processing')}</p>
      <ol aria-label={t('steps.label')} className="mt-3 grid gap-1">
        {STEPS.map((step, i) => (
          <li key={step} aria-current={i === current ? 'step' : undefined}>
            <span aria-hidden="true">{i < current ? '✓' : i === current ? '●' : '○'} </span>
            {t(`steps.${step}`)}
          </li>
        ))}
      </ol>
      <p className="mt-3">{t('leave')}</p>
    </Card>
  );
}
