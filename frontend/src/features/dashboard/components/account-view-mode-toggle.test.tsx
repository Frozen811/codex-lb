import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import i18n from "@/i18n";
import { AccountViewModeToggle } from "./account-view-mode-toggle";

describe("AccountViewModeToggle", () => {
  it("announces the available fullscreen action in both states", async () => {
    const user = userEvent.setup();
    const onFullscreenChange = vi.fn();
    const props = { value: "compact" as const, onChange: vi.fn(), onFullscreenChange };
    const { rerender } = render(<AccountViewModeToggle {...props} fullscreen={false} />);
    const enter = screen.getByRole("button", { name: "Full screen" });
    expect(enter).toHaveAttribute("aria-pressed", "false");
    await user.click(enter);
    expect(onFullscreenChange).toHaveBeenLastCalledWith(true);

    rerender(<AccountViewModeToggle {...props} fullscreen />);
    const exit = screen.getByRole("button", { name: "Exit full screen" });
    expect(exit).toHaveAttribute("aria-pressed", "true");
    await user.click(exit);
    expect(onFullscreenChange).toHaveBeenLastCalledWith(false);
    expect(props.onChange).not.toHaveBeenCalled();
  });

  it.each([
    ["en", "View accounts in compact tables", "Exit full screen"],
    ["ko", "Account를 간결한 표로 보기", "전체 화면 종료"],
    ["zh-CN", "以紧凑表格查看账户", "退出全屏"],
  ])("localizes compact and exit actions in %s", async (locale, compact, exit) => {
    await i18n.changeLanguage(locale);
    try {
      render(<AccountViewModeToggle value="compact" onChange={vi.fn()} fullscreen onFullscreenChange={vi.fn()} />);
      expect(screen.getByRole("radio", { name: compact })).toHaveAttribute("aria-checked", "true");
      expect(screen.getByRole("button", { name: exit })).toHaveAttribute("aria-pressed", "true");
    } finally {
      await i18n.changeLanguage("en");
    }
  });
});
