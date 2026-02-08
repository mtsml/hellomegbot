import { describe, expect, it, vi, beforeEach } from "vitest";

import type { Env } from "../../util/env";
import { Rarity } from "../../service/gacha";
import { helloruriController } from "./index";
import * as gachaService from "../../service/gacha";
import { HELLORURI_MESSAGE_UR } from "./constants";

vi.mock("../../service/gacha", async () => {
  const actual = await vi.importActual<typeof import("../../service/gacha")>(
    "../../service/gacha",
  );
  return {
    ...actual,
    drawRarity: vi.fn(),
    buildSrResult: vi.fn(),
  };
});

function createEnv(overrides?: Partial<Env>): Env {
  return {
    ASSETS: { fetch: vi.fn() },
    ASSETS_BASE_URL: "https://cdn.example.com",
    DISCORD_PUBLIC_KEY: "pub",
    HELLORURI_UR_PROBABILITY: "0.11",
    HELLORURI_SR_PROBABILITY: "0.22",
    ...overrides,
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  vi.spyOn(console, "error").mockImplementation(() => {});
});

describe("helloruriController", () => {
  it("returns JSON with UR message", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.UR);

    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);

    const response = await helloruriController(createEnv());
    const payload = await response.json();

    expect(payload.data.content).toBe(HELLORURI_MESSAGE_UR);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(gachaService.drawRarity).toHaveBeenCalledWith(0.11, 0.22);
    expect(gachaService.buildSrResult).not.toHaveBeenCalled();
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("falls back to normal message when SR metadata is unavailable", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.SR);
    vi.mocked(gachaService.buildSrResult).mockResolvedValue(null);

    const response = await helloruriController(createEnv());
    const payload = await response.json();

    expect(payload.data.content).toBe("ハロるりー！");
    expect(response.headers.get("content-type")).toContain("application/json");
  });

  it("returns multipart response when SR image fetch succeeds", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.SR);
    vi.mocked(gachaService.buildSrResult).mockResolvedValue({
      filepath: "public/helloruri/sr/sample.png",
      twitterId: "artist_id",
    });

    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(new Uint8Array([1, 2, 3]), {
        headers: { "content-type": "image/png" },
      }),
    );
    vi.stubGlobal("fetch", fetchSpy);

    const response = await helloruriController(createEnv());
    const bodyText = new TextDecoder().decode(await response.arrayBuffer());

    expect(response.headers.get("content-type")).toContain("multipart/form-data");
    expect(fetchSpy).toHaveBeenCalledWith(
      "https://cdn.example.com/public/helloruri/sr/sample.png",
    );
    expect(bodyText).toContain('name="payload_json"');
    expect(bodyText).toContain("イラスト：[@artist_id](<https://twitter.com/artist_id>)");
    expect(bodyText).toContain('filename="sample.png"');
  });

  it("falls back to JSON when SR image fetch fails", async () => {
    vi.mocked(gachaService.drawRarity).mockReturnValue(Rarity.SR);
    vi.mocked(gachaService.buildSrResult).mockResolvedValue({
      filepath: "public/helloruri/sr/sample.png",
      twitterId: "artist_id",
    });

    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("boom")));

    const response = await helloruriController(createEnv());
    const payload = await response.json();

    expect(payload.data.content).toBe(
      "イラスト：[@artist_id](<https://twitter.com/artist_id>)",
    );
    expect(response.headers.get("content-type")).toContain("application/json");
  });
});
