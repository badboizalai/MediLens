import type { Preview } from "@storybook/react";
import { cssVariables } from "../src/tokens/tokens";
import "../src/styles.css";

const preview: Preview = {
  globalTypes: {
    theme: { description: "Theme", toolbar: { icon: "circlehollow", items: ["light", "dark"], dynamicTitle: true } },
  },
  initialGlobals: { theme: "light" },
  decorators: [
    (Story, ctx) => {
      document.documentElement.dataset.theme = ctx.globals.theme;
      return (
        <>
          <style>{cssVariables()}</style>
          <div style={{ background: "var(--ml-color-brand-surface)", padding: 16 }}>
            <Story />
          </div>
        </>
      );
    },
  ],
};
export default preview;
