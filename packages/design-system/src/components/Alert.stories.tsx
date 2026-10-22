import type { Meta, StoryObj } from "@storybook/react";
import { Alert } from "./Alert";

const meta = { title: "Components/Alert", component: Alert, args: { children: "Vui lòng kiểm tra lại." } } satisfies Meta<typeof Alert>;
export default meta;
type S = StoryObj<typeof meta>;

export const Info: S = { args: { tone: "info", title: "Lưu ý" } };
export const Success: S = { args: { tone: "success", title: "Đã lưu" } };
export const Warning: S = { args: { tone: "warning", title: "Độ tin cậy thấp" } };
export const Danger: S = { args: { tone: "danger", title: "Tải lên thất bại" } };
