import type { Env } from "./env";

export function jsonResponse(body: object, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=UTF-8" },
  });
}

export function parseEnvNumber(value: string | undefined, fallback: number): number {
  if (!value) return fallback;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

/**
 * Discord 署名検証を行うかどうかを判定する
 * 
 * Discord bot なしで起動できるように署名検証をスキップする env を提供している
 */
export function shouldVerifySignature(env: Env): boolean {
  return env.DISCORD_SKIP_SIGNATURE_VERIFICATION !== "true";
}
