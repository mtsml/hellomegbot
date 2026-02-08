import { Rarity, buildSrResult, drawRarity } from "../../services/gacha";
import { InteractionResponseType } from "../../libs/discord";
import type { Env } from "../../utils/env";
import {
  createJsonInteractionResponse,
  createMultipartInteractionResponse,
} from "../../libs/discord";
import { parseEnvNumber } from "../../utils";
import { joinUrl } from "../../utils";
import {
  MMM_MM_MMMMMMMM_JSON_PATH,
  MMM_MM_MMMMMMMM_MESSAGE_NORMAL,
  MMM_MM_MMMMMMMM_MESSAGE_UR,
  MMM_MM_MMMMMMMM_SR_PROBABILITY_DEFAULT,
  MMM_MM_MMMMMMMM_UR_PROBABILITY_DEFAULT,
  SR_MESSAGE_PREFIX,
} from "./constants";

export async function mmmMmMmmmmmmmController(env: Env): Promise<Response> {
  const urProbability = parseEnvNumber(
    env.MMM_MM_MMMMMMMM_UR_PROBABILITY,
    MMM_MM_MMMMMMMM_UR_PROBABILITY_DEFAULT,
  );
  const srProbability = parseEnvNumber(
    env.MMM_MM_MMMMMMMM_SR_PROBABILITY,
    MMM_MM_MMMMMMMM_SR_PROBABILITY_DEFAULT,
  );
  const rarity = drawRarity(urProbability, srProbability);

  if (rarity === Rarity.UR || rarity === Rarity.NORMAL) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: {
        content:
          rarity === Rarity.UR
            ? MMM_MM_MMMMMMMM_MESSAGE_UR
            : MMM_MM_MMMMMMMM_MESSAGE_NORMAL,
      },
    });
  }
  const result = await buildSrResult(
    joinUrl(env.ASSETS_BASE_URL, MMM_MM_MMMMMMMM_JSON_PATH),
  );
  if (!result) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: MMM_MM_MMMMMMMM_MESSAGE_NORMAL },
    });
  }

  const content = `${SR_MESSAGE_PREFIX}[@${result.twitterId}](<https://twitter.com/${result.twitterId}>)`;
  const imageUrl = joinUrl(env.ASSETS_BASE_URL, result.filepath);
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
    console.error("mmm-mm-mmmmmmmm controller fallback", {
      phase: "attachment",
      error,
    });
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content },
    });
  }
}
