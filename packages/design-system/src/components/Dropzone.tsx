import { useId, useState, type ChangeEvent, type DragEvent, type ReactNode } from "react";

export interface DropzoneProps {
  label: ReactNode;
  /** Shown under the label, e.g. accepted formats. */
  hint?: ReactNode;
  /** Per-file size limit in bytes. */
  maxSizeBytes: number;
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
  /** Receives only files within the size limit. */
  onFiles: (files: File[]) => void;
  /** Builds the message for a rejected file (lets callers localise). */
  tooLargeMessage?: (file: File, maxSizeBytes: number) => string;
}

const defaultTooLarge = (f: File, max: number) => `${f.name}: file exceeds ${(max / 1_048_576).toFixed(0)} MB`;

/** A native file input wrapped in a label: keyboard- and screen-reader-accessible, drag-and-drop is an enhancement. */
export function Dropzone({
  label, hint, maxSizeBytes, accept, multiple = false, disabled, onFiles, tooLargeMessage = defaultTooLarge,
}: DropzoneProps) {
  const id = useId();
  const [over, setOver] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const handle = (list: FileList | null) => {
    const files = Array.from(list ?? []);
    const ok = files.filter((f) => f.size <= maxSizeBytes);
    setErrors(files.filter((f) => f.size > maxSizeBytes).map((f) => tooLargeMessage(f, maxSizeBytes)));
    if (ok.length) onFiles(ok);
  };
  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setOver(false);
    if (!disabled) handle(e.dataTransfer.files);
  };

  return (
    <div>
      <label
        htmlFor={id}
        className={`ml-dropzone${over ? " ml-dropzone--over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={onDrop}
      >
        {label}
        {hint ? <span className="ml-dropzone__hint">{hint}</span> : null}
        <input
          id={id}
          type="file"
          className="ml-dropzone__input"
          accept={accept}
          multiple={multiple}
          disabled={disabled}
          aria-describedby={errors.length ? `${id}-err` : undefined}
          onChange={(e: ChangeEvent<HTMLInputElement>) => { handle(e.target.files); e.target.value = ""; }}
        />
      </label>
      {errors.length ? (
        <div id={`${id}-err`} role="alert" className="ml-dropzone__error">
          {errors.map((m) => <div key={m}>{m}</div>)}
        </div>
      ) : null}
    </div>
  );
}
