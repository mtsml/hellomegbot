import {
  InteractionResponseType,
  type DiscordInteractionResponse,
} from "../types";
import type { Env } from "../types";
import { jsonResponse } from "./http";

export function unsupported(content: string): Response {
  const body: DiscordInteractionResponse = {
    type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
    data: { content },
  };
  return jsonResponse(body);
}

export function shouldVerifySignature(env: Env): boolean {
  return env.DISCORD_SKIP_SIGNATURE_VERIFICATION !== "true";
}
