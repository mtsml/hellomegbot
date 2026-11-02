import { describe, expect, it } from "vitest";

import { buildLowTemperatureSvg } from "./index";

describe("buildLowTemperatureSvg", () => {
  it("draws the temperature in the lower-left blank area", () => {
    const svg = buildLowTemperatureSvg({
      backgroundDataUrl: "data:image/png;base64,background",
      backgroundSize: { width: 1280, height: 1280 },
      temperature: 5,
    });

    expect(svg).toContain('x="60" y="990"');
    expect(svg).toContain('font-size="160">5℃');
    expect(svg).toContain("data:image/png;base64,background");
  });
});
