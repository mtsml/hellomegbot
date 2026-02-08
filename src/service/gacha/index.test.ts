import { afterEach, describe, expect, it, vi } from "vitest";

import { Rarity, buildSrResult, drawRarity } from "./index";

const TEST_JSON_URL = "https://example.com/test-gacha.json";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("drawRarity", () => {
  it("returns UR when random is under urProbability", () => {
    vi.spyOn(Math, "random").mockReturnValue(0.01);
    expect(drawRarity(0.03, 0.18)).toBe(Rarity.UR);
  });

  it("returns SR when random is in sr range", () => {
    vi.spyOn(Math, "random").mockReturnValue(0.1);
    expect(drawRarity(0.03, 0.18)).toBe(Rarity.SR);
  });

  it("returns NORMAL when random is outside ur/sr range", () => {
    vi.spyOn(Math, "random").mockReturnValue(0.99);
    expect(drawRarity(0.03, 0.18)).toBe(Rarity.NORMAL);
  });
});

describe("buildSrResult", () => {
  it("returns SR payload when image fetch succeeds", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0.0);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify([{ filepath: "public/sr.png", twitter_id: "abc" }])),
      ),
    );

    const result = await buildSrResult(TEST_JSON_URL);
    expect(result).toEqual({
      filepath: "public/sr.png",
      twitterId: "abc",
    });
  });

  it("returns null when image fetch fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("boom")));

    const result = await buildSrResult(TEST_JSON_URL);
    expect(result).toBeNull();
  });
});
