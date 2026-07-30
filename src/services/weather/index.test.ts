import { afterEach, describe, expect, it, vi } from "vitest";

import { getKanazawaCurrentTemperature } from "./index";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("getKanazawaCurrentTemperature", () => {
  it("fetches the current temperature", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ current: { temperature_2m: 34.9 } })),
    );
    vi.stubGlobal("fetch", fetchSpy);

    await expect(getKanazawaCurrentTemperature()).resolves.toBe(34.9);
    expect(String(fetchSpy.mock.calls[0][0])).toBe(
      "https://api.open-meteo.com/v1/forecast?latitude=36.56&longitude=136.66&current=temperature_2m&timezone=Asia%2FTokyo",
    );
  });

  it("returns null when the weather API does not return a temperature", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({}))));
    vi.spyOn(console, "error").mockImplementation(() => {});

    await expect(getKanazawaCurrentTemperature()).resolves.toBeNull();
  });
});
