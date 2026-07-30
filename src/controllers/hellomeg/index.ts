import { Rarity, buildSrResult, drawRarity } from "../../services/gacha";
import { getKanazawaCurrentTemperature } from "../../services/weather";
import { InteractionResponseType } from "../../libs/discord";
import type { Env } from "../../utils/env";
import {
  createJsonInteractionResponse,
  createMultipartInteractionResponse,
} from "../../libs/discord";
import { parseEnvNumber } from "../../utils";
import {
  HELLOMEG_JSON_PATH,
  HELLOMEG_HIGH_TEMPERATURE_SR_RESULT,
  HELLOMEG_HIGH_TEMPERATURE_THRESHOLD_CELSIUS_DEFAULT,
  HELLOMEG_MESSAGE_NORMAL,
  HELLOMEG_MESSAGE_UR,
  HELLOMEG_SR_PROBABILITY_DEFAULT,
  HELLOMEG_UR_PROBABILITY_DEFAULT,
  SR_MESSAGE_PREFIX,
} from "./constants";

export async function hellomegController(env: Env): Promise<Response> {
  const assetsBaseUrl = env.ASSETS_BASE_URL.replace(/\/+$/, "");

  if (env.HELLOMEG_HIGH_TEMPERATURE_ENABLED === "true") {
    const currentTemperature = await getKanazawaCurrentTemperature();
    const highTemperatureThreshold = parseEnvNumber(
      env.HELLOMEG_HIGH_TEMPERATURE_THRESHOLD_CELSIUS,
      HELLOMEG_HIGH_TEMPERATURE_THRESHOLD_CELSIUS_DEFAULT,
    );
    if (
      currentTemperature !== null
      && currentTemperature >= highTemperatureThreshold
    ) {
      return createSrImageResponse(
        assetsBaseUrl,
        HELLOMEG_HIGH_TEMPERATURE_SR_RESULT,
      );
    }
  }

  const urProbability = parseEnvNumber(
    env.HELLOMEG_UR_PROBABILITY,
    HELLOMEG_UR_PROBABILITY_DEFAULT,
  );
  const srProbability = parseEnvNumber(
    env.HELLOMEG_SR_PROBABILITY,
    HELLOMEG_SR_PROBABILITY_DEFAULT,
  );
  const rarity = drawRarity(urProbability, srProbability);

  if (rarity === Rarity.UR || rarity === Rarity.NORMAL) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: rarity === Rarity.UR ? HELLOMEG_MESSAGE_UR : HELLOMEG_MESSAGE_NORMAL },
    });
  }

  const result = await buildSrResult(
    `${assetsBaseUrl}/${HELLOMEG_JSON_PATH.replace(/^\/+/, "")}`,
  );
  if (!result) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: HELLOMEG_MESSAGE_NORMAL },
    });
  }
  return createSrImageResponse(assetsBaseUrl, result);
}

async function createSrImageResponse(
  assetsBaseUrl: string,
  result: { filepath: string; twitterId: string },
): Promise<Response> {
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
    console.error("hellomeg controller fallback", { phase: "attachment", error });
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content },
    });
  }
}
