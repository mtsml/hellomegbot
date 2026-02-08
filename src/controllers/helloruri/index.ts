import { Rarity, buildSrResult, drawRarity } from "../../services/gacha";
import { InteractionResponseType } from "../../libs/discord";
import type { Env } from "../../utils/env";
import {
  createJsonInteractionResponse,
  createMultipartInteractionResponse,
} from "../../libs/discord";
import { parseEnvNumber } from "../../utils";
import {
  HELLORURI_JSON_PATH,
  HELLORURI_MESSAGE_NORMAL,
  HELLORURI_MESSAGE_UR,
  HELLORURI_SR_PROBABILITY_DEFAULT,
  HELLORURI_UR_PROBABILITY_DEFAULT,
  SR_MESSAGE_PREFIX,
} from "./constants";

export async function helloruriController(
  env: Env,
): Promise<Response> {
  const assetsBaseUrl = env.ASSETS_BASE_URL.replace(/\/+$/, "");
  const urProbability = parseEnvNumber(
    env.HELLORURI_UR_PROBABILITY,
    HELLORURI_UR_PROBABILITY_DEFAULT,
  );
  const srProbability = parseEnvNumber(
    env.HELLORURI_SR_PROBABILITY,
    HELLORURI_SR_PROBABILITY_DEFAULT,
  );
  const rarity = drawRarity(urProbability, srProbability);

  if (rarity === Rarity.UR || rarity === Rarity.NORMAL) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: rarity === Rarity.UR ? HELLORURI_MESSAGE_UR : HELLORURI_MESSAGE_NORMAL },
    });
  }

  const result = await buildSrResult(
    `${assetsBaseUrl}/${HELLORURI_JSON_PATH.replace(/^\/+/, "")}`,
  );
  if (!result) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: HELLORURI_MESSAGE_NORMAL },
    });
  }

  const content = `${SR_MESSAGE_PREFIX}[@${result.twitterId}](<https://twitter.com/${result.twitterId}>)`;
  const imageUrl = `${assetsBaseUrl}/${result.filepath.replace(/^\/+/, "")}`;
  const filename = result.filepath.split("/").pop() ?? "image.png";

  try {
    const imageResponse = await fetch(imageUrl);
    if (!imageResponse.ok) throw new Error("failed to fetch attachment image");
    const imageData = await imageResponse.arrayBuffer();
    return createMultipartInteractionResponse({
      content,
      attachment: {
        filename,
        contentType: imageResponse.headers.get("content-type") ?? "image/png",
        data: imageData,
      },
    });
  } catch (error) {
    console.error("helloruri controller fallback", { phase: "attachment", error });
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content },
    });
  }
}
