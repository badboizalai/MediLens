// WebMCP: expose MediLens page tools to in-browser AI agents via navigator.modelContext
// (W3C Web Machine Learning CG proposal). Feature-detected: a no-op in browsers without it.
// Tools must never return PHI unless the user is signed in and the tool is scoped to their profile.

export type WebMcpTool = {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  execute: (input: Record<string, unknown>) => Promise<unknown> | unknown;
};

type ModelContext = {
  registerTool: (tool: WebMcpTool) => { unregister?: () => void } | void;
};

export function registerWebMcpTools(tools: WebMcpTool[]): () => void {
  const ctx = (globalThis.navigator as Navigator & { modelContext?: ModelContext })?.modelContext;
  if (!ctx?.registerTool) return () => {};
  const handles = tools.map((t) => ctx.registerTool(t));
  return () => handles.forEach((h) => h && h.unregister?.());
}
