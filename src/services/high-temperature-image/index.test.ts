import { describe, expect, it } from "vitest";

import { buildHighTemperatureSvg } from "./index";

describe("buildHighTemperatureSvg", () => {
  it("draws the temperature over the background image", () => {
    const svg = buildHighTemperatureSvg({
      backgroundDataUrl: "data:image/png;base64,xxx",
      backgroundSize: { width: 1280, height: 1280 },
      temperature: 35.4,
    });

    expect(svg).toContain('href="data:image/png;base64,xxx"');
    expect(svg).toContain("<tspan>金沢は</tspan>");
    expect(svg).toContain(
      '<tspan x="60" dy="190" font-size="160">35.4℃</tspan>',
    );
    expect(svg).toContain('x="60" y="990"');
  });
});
