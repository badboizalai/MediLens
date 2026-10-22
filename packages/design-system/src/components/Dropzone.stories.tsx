import type { Meta, StoryObj } from "@storybook/react";
import { Dropzone } from "./Dropzone";

const meta = {
  title: "Components/Dropzone",
  component: Dropzone,
  args: {
    label: "Chọn hoặc kéo thả tệp",
    hint: "PDF, JPG, PNG, tối đa 10 MB",
    maxSizeBytes: 10 * 1_048_576,
    accept: ".pdf,image/*",
    onFiles: () => {},
  },
} satisfies Meta<typeof Dropzone>;
export default meta;

export const Default: StoryObj<typeof meta> = {};
export const Multiple: StoryObj<typeof meta> = { args: { multiple: true } };
export const Disabled: StoryObj<typeof meta> = { args: { disabled: true } };
