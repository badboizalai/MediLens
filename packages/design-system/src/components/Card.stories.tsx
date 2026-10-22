import type { Meta, StoryObj } from "@storybook/react";
import { Card } from "./Card";

const meta = { title: "Components/Card", component: Card } satisfies Meta<typeof Card>;
export default meta;

export const Titled: StoryObj<typeof meta> = { args: { title: "Kết quả", children: "Nội dung minh hoạ." } };
export const Untitled: StoryObj<typeof meta> = { args: { children: "Thẻ không tiêu đề." } };
