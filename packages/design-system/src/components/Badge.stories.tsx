import type { Meta, StoryObj } from "@storybook/react";
import { severityKeys } from "../tokens/tokens";
import { SeverityBadge } from "./Badge";

const meta = { title: "Components/SeverityBadge", component: SeverityBadge, args: { severity: "monitor" } } satisfies Meta<typeof SeverityBadge>;
export default meta;

export const Single: StoryObj<typeof meta> = {};
export const AllLevels: StoryObj<typeof meta> = {
  render: (args) => (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {severityKeys.map((k) => <SeverityBadge key={k} {...args} severity={k} />)}
    </div>
  ),
};
export const English: StoryObj<typeof meta> = { args: { severity: "spread", locale: "en" } };
