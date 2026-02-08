import { describe, expect, it } from "vitest";

import {
  buildMeggenSvg,
  getMeggenImageConfig,
  getMeggenImageOptions,
} from "./index";

describe("getMeggenImageOptions", () => {
  it("returns available choices including fever", () => {
    const options = getMeggenImageOptions();
    expect(options.map((option) => option.value)).toEqual([
      "fever",
      "damon",
      "hkc",
      "universe",
      "hasunosorashikanainsuyo",
      "doya",
    ]);
  });
});

describe("getMeggenImageConfig", () => {
  it("returns config for valid image type", () => {
    const config = getMeggenImageConfig("damon");
    expect(config?.rows).toBe(2);
    expect(config?.assetPath).toBe("/meggen/damon.png");
  });

  it("returns undefined for unknown image type", () => {
    expect(getMeggenImageConfig("unknown")).toBeUndefined();
  });
});

describe("buildMeggenSvg", () => {
  it("builds svg with escaped text and stroke settings", () => {
    const config = getMeggenImageConfig("damon");
    if (!config) throw new Error("missing config");

    const svg = buildMeggenSvg({
      backgroundDataUrl: "data:image/png;base64,xxx",
      backgroundSize: { width: 1280, height: 720 },
      config,
      textLines: ["<hello>", "world"],
    });

    expect(svg).toContain('width="1280"');
    expect(svg).toContain("data:image/png;base64,xxx");
    expect(svg).toContain("stroke-width=\"20\"");
    expect(svg).toContain("&lt;hello&gt;");
  });
});
