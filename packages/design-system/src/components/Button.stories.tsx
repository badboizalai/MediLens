import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = { title: "Components/Button", component: Button, args: { children: "Tải lên" } } satisfies Meta<typeof Button>;
export default meta;
type S = StoryObj<typeof meta>;

export const Primary: S = {};
export const Secondary: S = { args: { variant: "secondary" } };
export const Danger: S = { args: { variant: "danger", children: "Xoá" } };
export const Disabled: S = { args: { disabled: true } };
