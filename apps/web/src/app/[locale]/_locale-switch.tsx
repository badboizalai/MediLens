'use client';

import { usePathname } from 'next/navigation';

const LOCALES = [
  { code: 'vi', label: 'VI' },
  { code: 'en', label: 'EN' },
];

export function LocaleSwitch({ label }: { label: string }) {
  const pathname = usePathname();
  const [, current, ...rest] = pathname.split('/');
  const tail = rest.length ? `/${rest.join('/')}` : '';
  return (
    <ul aria-label={label} className="flex gap-1 text-sm">
      {LOCALES.map(({ code, label: text }) => (
        <li key={code}>
          <a
            href={`/${code}${tail}`}
            hrefLang={code}
            lang={code}
            aria-current={code === current ? 'true' : undefined}
            className={`rounded px-2 py-1 ${code === current ? 'font-semibold underline' : 'hover:bg-neutral-100'}`}
          >
            {text}
          </a>
        </li>
      ))}
    </ul>
  );
}
