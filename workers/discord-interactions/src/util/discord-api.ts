import type { Env } from "../types";

const DISCORD_API_BASE = "https://discord.com/api/v10";

type RegisterCommandPayload = {
  name: string;
  description: string;
  type: 1;
  options?: Array<{
    type: number;
    name: string;
    description: string;
    required?: boolean;
    min_value?: number;
    choices?: Array<{ name: string; value: string | number }>;
  }>;
};

export async function registerGlobalCommand(
  env: Env,
  payload: RegisterCommandPayload,
): Promise<Response> {
  if (!env.DISCORD_APPLICATION_ID || !env.DISCORD_BOT_TOKEN) {
    return new Response(
      JSON.stringify({
        error: "DISCORD_APPLICATION_ID and DISCORD_BOT_TOKEN are required",
      }),
      {
        status: 400,
        headers: { "content-type": "application/json; charset=UTF-8" },
      },
    );
  }

  const url = `${DISCORD_API_BASE}/applications/${env.DISCORD_APPLICATION_ID}/commands`;

  const res = await fetch(url, {
    method: "POST",
    headers: {
      authorization: `Bot ${env.DISCORD_BOT_TOKEN}`,
      "content-type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return new Response(await res.text(), {
    status: res.status,
    headers: { "content-type": "application/json; charset=UTF-8" },
  });
}
