import { beforeEach, describe, expect, it, vi } from "vitest";

import type { DiscordCommandOption, Env } from "../../types";
import { KeibaResult } from "../../service/keibaresult";
import { handleKeibaresultController } from "./index";
import * as keibaService from "../../service/keibaresult";

vi.mock("../../service/keibaresult", async () => {
  const actual = await vi.importActual<typeof import("../../service/keibaresult")>(
    "../../service/keibaresult",
  );
  return {
    ...actual,
    validateKeibaAmount: vi.fn(),
    runKeibaResult: vi.fn(),
  };
});

function createEnv(overrides?: Partial<Env>): Env {
  return {
    ASSETS: {
      fetch: vi.fn(),
    },
    GACHA_ASSETS_BASE_URL: "https://cdn.example.com",
    DISCORD_PUBLIC_KEY: "pub",
    ...overrides,
  };
}

function option(name: string, type: number, value: string | number | boolean): DiscordCommandOption {
  return { name, type, value };
}

beforeEach(() => {
  vi.resetAllMocks();
  vi.spyOn(console, "error").mockImplementation(() => {});
});

describe("handleKeibaresultController", () => {
  it("returns ephemeral error when required options are missing", async () => {
    const response = await handleKeibaresultController(createEnv(), undefined);
    const payload = await response.json();

    expect(payload.data.content).toBe("result と amount の指定が必要です");
    expect(payload.data.flags).toBe(64);
  });

  it("returns ephemeral error when result is invalid", async () => {
    const response = await handleKeibaresultController(createEnv(), [
      option("result", 3, "invalid"),
      option("amount", 4, 100),
    ]);
    const payload = await response.json();

    expect(payload.data.content).toBe("result の値が不正です");
    expect(payload.data.flags).toBe(64);
  });

  it("returns validation error from service", async () => {
    vi.mocked(keibaService.validateKeibaAmount).mockReturnValue({
      valid: false,
      errorMessage: "amount is invalid",
    });

    const response = await handleKeibaresultController(createEnv(), [
      option("result", 3, KeibaResult.WIN),
      option("amount", 4, 100),
    ]);
    const payload = await response.json();

    expect(payload.data.content).toBe("amount is invalid");
    expect(payload.data.flags).toBe(64);
  });

  it("returns JSON when service returns text-only result", async () => {
    vi.mocked(keibaService.validateKeibaAmount).mockReturnValue({ valid: true });
    vi.mocked(keibaService.runKeibaResult).mockReturnValue({
      content: "ハロめぐー！",
    });

    const response = await handleKeibaresultController(createEnv(), [
      option("result", 3, KeibaResult.WIN),
      option("amount", 4, 100),
    ]);
    const payload = await response.json();

    expect(payload.data.content).toBe("ハロめぐー！");
    expect(response.headers.get("content-type")).toContain("application/json");
  });

  it("returns multipart when service returns image and asset fetch succeeds", async () => {
    vi.mocked(keibaService.validateKeibaAmount).mockReturnValue({ valid: true });
    vi.mocked(keibaService.runKeibaResult).mockReturnValue({
      content: "バイめぐ〜",
      imagePath: "/keibaresult/lose/lose_001.png",
    });

    const assetsFetch = vi.fn().mockResolvedValue(
      new Response(new Uint8Array([1, 2, 3]), {
        headers: { "content-type": "image/png" },
      }),
    );

    const response = await handleKeibaresultController(
      createEnv({ ASSETS: { fetch: assetsFetch } }),
      [option("result", 3, KeibaResult.LOSE), option("amount", 4, 100)],
    );

    const bodyText = new TextDecoder().decode(await response.arrayBuffer());

    expect(response.headers.get("content-type")).toContain("multipart/form-data");
    expect(assetsFetch).toHaveBeenCalledTimes(1);
    const request = vi.mocked(assetsFetch).mock.calls[0][0] as Request;
    expect(request.url).toBe("https://assets.local/keibaresult/lose/lose_001.png");
    expect(bodyText).toContain("バイめぐ〜");
    expect(bodyText).toContain('filename="lose_001.png"');
  });

  it("falls back to JSON when asset fetch fails", async () => {
    vi.mocked(keibaService.validateKeibaAmount).mockReturnValue({ valid: true });
    vi.mocked(keibaService.runKeibaResult).mockReturnValue({
      content: "バイめぐ〜",
      imagePath: "/keibaresult/lose/lose_001.png",
    });

    const assetsFetch = vi.fn().mockRejectedValue(new Error("boom"));

    const response = await handleKeibaresultController(
      createEnv({ ASSETS: { fetch: assetsFetch } }),
      [option("result", 3, KeibaResult.LOSE), option("amount", 4, 100)],
    );

    const payload = await response.json();

    expect(payload.data.content).toBe("バイめぐ〜");
    expect(response.headers.get("content-type")).toContain("application/json");
  });
});
