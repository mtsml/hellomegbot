import { describe, expect, it, vi, beforeEach } from "vitest";

import type { Env } from "../../utils/env";
import { Rarity } from "../../services/gacha";
import { hellomegController } from "./index";
import * as gachaService from "../../services/gacha";
import * as weatherService from "../../services/weather";
import * as highTemperatureImageService from "../../services/high-temperature-image";
import { HELLOMEG_MESSAGE_NORMAL, HELLOMEG_MESSAGE_UR } from "./constants";

vi.mock("../../services/gacha", async () => {
  const actual = await vi.importActual<typeof import("../../services/gacha")>(
    "../../services/gacha",
  );
  return {
    ...actual,
    drawRarity: vi.fn(),
    buildSrResult: vi.fn(),
  };
});

vi.mock("../../services/weather", () => ({
  getKanazawaCurrentTemperature: vi.fn(),
}));

vi.mock("../../services/high-temperature-image", () => ({
  generateHighTemperaturePng: vi.fn(),
}));

function createEnv(overrides?: Partial<Env>): Env {
  return {
    ASSETS: { fetch: vi.fn() },
    ASSETS_BASE_URL: "https://cdn.example.com",
    DISCORD_PUBLIC_KEY: "pub",
    HELLOMEG_UR_PROBABILITY: "0.11",
    HELLOMEG_SR_PROBABILITY: "0.22",
    ...overrides,
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(weatherService.getKanazawaCurrentTemperature).mockResolvedValue(null);
  vi.spyOn(console, "error").mockImplementation(() => {});
});

describe("hellomegController", () => {
  it("returns the fixed SR image without a rarity draw at 30 degrees or above", async () => {
    vi.mocked(weatherService.getKanazawaCurrentTemperature).mockResolvedValue(35);
    vi.mocked(highTemperatureImageService.generateHighTemperaturePng).mockResolvedValue({
      filename: "tokemeg.png",
      data: new Uint8Array([4, 5, 6]).buffer,
    });
    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(new Uint8Array([1, 2, 3]), {
        headers: { "content-type": "image/png" },
      }),
    );
    vi.stubGlobal("fetch", fetchSpy);

    const response = await hellomegController(createEnv({
      ASSETS: {
        fetch: vi.fn().mockResolvedValue(new Response(new Uint8Array([7, 8, 9]))),
      },
      HELLOMEG_HIGH_TEMPERATURE_ENABLED: "true",
    }));
    const bodyText = new TextDecoder().decode(await response.arrayBuffer());

    expect(response.headers.get("content-type")).toContain("multipart/form-data");
    expect(fetchSpy).toHaveBeenCalledWith(
      "https://cdn.example.com/images/pine_nm/tokemeg.png",
    );
    expect(bodyText).toContain("イラスト：[@pine_nm](<https://twitter.com/pine_nm>)");
    expect(bodyText).toContain('filename="tokemeg.png"');
    expect(highTemperatureImageService.generateHighTemperaturePng).toHaveBeenCalledWith(
      expect.objectContaining({ temperature: 35, filename: "tokemeg.png" }),
    );
    expect(gachaService.drawRarity).not.toHaveBeenCalled();
    expect(gachaService.buildSrResult).not.toHaveBeenCalled();
  });

  it("falls back to the normal gacha when the temperature is unavailable", async () => {
    vi.mocked(weatherService.getKanazawaCurrentTemperature).mockResolvedValue(null);
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.NORMAL);

    const response = await hellomegController(createEnv({
      HELLOMEG_HIGH_TEMPERATURE_ENABLED: "true",
    }));
    const payload = await response.json();

    expect(payload.data.content).toBe(HELLOMEG_MESSAGE_NORMAL);
    expect(gachaService.drawRarity).toHaveBeenCalledWith(0.11, 0.22);
    expect(gachaService.buildSrResult).not.toHaveBeenCalled();
  });

  it("returns JSON with UR large message", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.UR);

    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);

    const response = await hellomegController(createEnv());
    const payload = await response.json();

    expect(payload.data.content).toBe(HELLOMEG_MESSAGE_UR);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(gachaService.drawRarity).toHaveBeenCalledWith(0.11, 0.22);
    expect(gachaService.buildSrResult).not.toHaveBeenCalled();
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("falls back to normal message when SR metadata is unavailable", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.SR);
    vi.mocked(gachaService.buildSrResult).mockResolvedValue(null);

    const response = await hellomegController(createEnv());
    const payload = await response.json();

    expect(payload.data.content).toBe(HELLOMEG_MESSAGE_NORMAL);
    expect(response.headers.get("content-type")).toContain("application/json");
  });

  it("returns multipart response when SR image fetch succeeds", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.SR);
    vi.mocked(gachaService.buildSrResult).mockResolvedValue({
      filepath: "public/hellomegbot/sr/sample.png",
      twitterId: "artist_id",
    });

    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(new Uint8Array([1, 2, 3]), {
        headers: { "content-type": "image/png" },
      }),
    );
    vi.stubGlobal("fetch", fetchSpy);

    const response = await hellomegController(createEnv());
    const bodyText = new TextDecoder().decode(await response.arrayBuffer());

    expect(response.headers.get("content-type")).toContain("multipart/form-data");
    expect(fetchSpy).toHaveBeenCalledWith(
      "https://cdn.example.com/public/hellomegbot/sr/sample.png",
    );
    expect(bodyText).toContain('name="payload_json"');
    expect(bodyText).toContain("イラスト：[@artist_id](<https://twitter.com/artist_id>)");
    expect(bodyText).toContain('filename="sample.png"');
  });

  it("falls back to JSON when SR image fetch fails", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.SR);
    vi.mocked(gachaService.buildSrResult).mockResolvedValue({
      filepath: "public/hellomegbot/sr/sample.png",
      twitterId: "artist_id",
    });

    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("boom")));

    const response = await hellomegController(createEnv());
    const payload = await response.json();

    expect(payload.data.content).toBe(
      "イラスト：[@artist_id](<https://twitter.com/artist_id>)",
    );
    expect(response.headers.get("content-type")).toContain("application/json");
  });
});
