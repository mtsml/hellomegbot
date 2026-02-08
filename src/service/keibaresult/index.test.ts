import { describe, expect, it, vi } from "vitest";

import { KeibaResult, runKeibaResult, validateKeibaAmount } from "./index";

describe("validateKeibaAmount", () => {
  it("rejects win with 0 amount", () => {
    const result = validateKeibaAmount(KeibaResult.WIN, 0);
    expect(result).toEqual({ valid: false, errorMessage: "amount に 0 より大き値を入れろ" });
  });

  it("rejects lose with 0 amount", () => {
    const result = validateKeibaAmount(KeibaResult.LOSE, 0);
    expect(result).toEqual({ valid: false, errorMessage: "amount に 0 より大き値を入れろ" });
  });

  it("rejects draw with non-zero amount", () => {
    const result = validateKeibaAmount(KeibaResult.DRAW, 1);
    expect(result).toEqual({ valid: false, errorMessage: "amount に 0 を入れろ" });
  });

  it("accepts valid values", () => {
    expect(validateKeibaAmount(KeibaResult.WIN, 100)).toEqual({ valid: true });
    expect(validateKeibaAmount(KeibaResult.LOSE, 100)).toEqual({ valid: true });
    expect(validateKeibaAmount(KeibaResult.DRAW, 0)).toEqual({ valid: true });
  });
});

describe("runKeibaResult", () => {
  it("returns win response with imagePath", () => {
    vi.spyOn(Math, "random").mockReturnValue(0);

    const result = runKeibaResult(KeibaResult.WIN, 12000);

    expect(result).toEqual({
      content: "ハロめぐー！ (+12,000)",
      imagePath: "/keibaresult/win/win.png",
    });
  });

  it("returns lose response with one of lose image paths", () => {
    vi.spyOn(Math, "random").mockReturnValue(0.9);

    const result = runKeibaResult(KeibaResult.LOSE, 5000);

    expect(result.content).toBe("バイめぐ〜 (-5,000)");
    if (!("imagePath" in result)) {
      throw new Error("expected imagePath for LOSE");
    }
    expect(result.imagePath).toMatch(/^\/keibaresult\/lose\/lose_00[1-3]\.png$/);
  });

  it("returns draw response without imagePath", () => {
    const result = runKeibaResult(KeibaResult.DRAW, 0);
    expect(result).toEqual({ content: "めぐ (±0)" });
  });
});
