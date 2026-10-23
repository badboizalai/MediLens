import backRaw from '../../../../../../packages/anatomy-assets/svg/body-back.svg?raw';
import frontRaw from '../../../../../../packages/anatomy-assets/svg/body-front.svg?raw';

export type Side = 'front' | 'back';
export type Shape = { id?: string; tag: 'path' | 'ellipse'; attrs: Record<string, string> };
export type ParsedBody = { viewBox: string; silhouette: Shape[]; regions: Shape[] };

const attrsOf = (s: string) => Object.fromEntries([...s.matchAll(/([\w-]+)="([^"]*)"/g)].map((m) => [m[1]!, m[2]!]));

// The SVGs are our own trusted, fixed-format artwork (S8-T72), so a regex is enough; shapes become
// React elements, nothing is injected as HTML. shortcut: only <path>/<ellipse>, upgrade if the art adds more.
export function parseBodySvg(raw: string): ParsedBody {
  const group = (id: string) => raw.match(new RegExp(`<g id="${id}"[^>]*>([\\s\\S]*?)</g>`))?.[1] ?? '';
  const shapes = (src: string): Shape[] =>
    [...src.matchAll(/<(path|ellipse)\s([^>]*?)\/?>/g)].map((m) => {
      const { id, class: _c, ...attrs } = attrsOf(m[2]!);
      return { id, tag: m[1] as Shape['tag'], attrs };
    });
  return {
    viewBox: raw.match(/viewBox="([^"]+)"/)?.[1] ?? '0 0 200 460',
    silhouette: shapes(group('aux_silhouette')),
    regions: shapes(group('aux_regions')),
  };
}

export const BODY: Record<Side, ParsedBody> = { front: parseBodySvg(frontRaw), back: parseBodySvg(backRaw) };
