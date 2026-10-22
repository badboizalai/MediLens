import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { Alert, Button, Card, Dropzone, SeverityBadge, severityKeys, cssVariables } from "../index";
import preset from "../tokens/tailwind-preset";

describe("Button", () => {
  it("defaults to type=button and fires onClick", async () => {
    const onClick = vi.fn();
    const { container } = render(<Button onClick={onClick}>Save</Button>);
    const btn = screen.getByRole("button", { name: "Save" });
    expect(btn).toHaveAttribute("type", "button");
    await userEvent.click(btn);
    expect(onClick).toHaveBeenCalledOnce();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("asChild renders the child element", () => {
    render(<Button asChild><a href="/x">Go</a></Button>);
    expect(screen.getByRole("link", { name: "Go" })).toHaveClass("ml-btn");
  });
});

describe("Card", () => {
  it("renders a titled section and passes axe", async () => {
    const { container } = render(<Card title="Summary">Body</Card>);
    expect(screen.getByRole("heading", { name: "Summary" })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});

describe("SeverityBadge (BR-020)", () => {
  it.each(severityKeys)("%s shows a text label and a hidden glyph", async (key) => {
    const { container } = render(<SeverityBadge severity={key} locale="en" />);
    expect(container.querySelector(".ml-badge__glyph")).toHaveAttribute("aria-hidden", "true");
    expect(container.textContent?.replace(/\s/g, "").length).toBeGreaterThan(1);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("localises the label", () => {
    render(<SeverityBadge severity="spread" />);
    expect(screen.getByText("Di căn / lan rộng")).toBeInTheDocument();
  });
});

describe("Alert", () => {
  it("uses role=alert for danger and role=status for info", async () => {
    const { container } = render(<><Alert tone="danger" title="Oops">x</Alert><Alert>fyi</Alert></>);
    expect(screen.getByRole("alert")).toHaveTextContent("Oops");
    expect(screen.getByRole("status")).toHaveTextContent("fyi");
    expect(await axe(container)).toHaveNoViolations();
  });
});

describe("Dropzone", () => {
  const big = new File([new Uint8Array(20)], "big.pdf", { type: "application/pdf" });
  const small = new File([new Uint8Array(5)], "small.pdf", { type: "application/pdf" });

  it("is labelled, passes axe", async () => {
    const { container } = render(<Dropzone label="Upload record" maxSizeBytes={10} onFiles={() => {}} />);
    expect(screen.getByLabelText(/Upload record/)).toHaveAttribute("type", "file");
    expect(await axe(container)).toHaveNoViolations();
  });

  it("accepts files within the limit and reports oversize ones", async () => {
    const onFiles = vi.fn();
    render(<Dropzone label="Upload" multiple maxSizeBytes={10} onFiles={onFiles} />);
    await userEvent.upload(screen.getByLabelText(/Upload/), [small, big]);
    expect(onFiles).toHaveBeenCalledWith([small]);
    expect(screen.getByRole("alert")).toHaveTextContent("big.pdf");
  });

  it("does not call onFiles when everything is too large", async () => {
    const onFiles = vi.fn();
    render(<Dropzone label="Upload" maxSizeBytes={10} onFiles={onFiles} />);
    await userEvent.upload(screen.getByLabelText(/Upload/), big);
    expect(onFiles).not.toHaveBeenCalled();
  });
});

describe("tokens", () => {
  it("emits light + dark severity variables", () => {
    const css = cssVariables();
    expect(css).toContain("--ml-color-severity-spread: #7D3C98;");
    expect(css).toContain('[data-theme="dark"]');
    expect(css).toContain("--ml-color-severity-spread: #BB8FCE;");
  });

  it("tailwind preset maps colours to variables", () => {
    const colors = preset.theme?.extend?.colors as Record<string, Record<string, string>>;
    expect(colors.severity.severe).toBe("var(--ml-color-severity-severe)");
    expect(colors.brand.surfaceMuted).toBe("var(--ml-color-brand-surface-muted)");
  });
});
