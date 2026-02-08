import { KeibaResult, runKeibaResult, validateKeibaAmount } from "../../services/keibaresult";
import {
  InteractionResponseType,
  type DiscordCommandOption,
} from "../../libs/discord";
import type { Env } from "../../utils/env";
import {
  createJsonInteractionResponse,
  createMultipartInteractionResponse,
} from "../../libs/discord";
import {
  getNumberCommandOption,
  getStringCommandOption,
} from "../../libs/discord";

const EPHEMERAL_FLAG = 1 << 6;

function parseKeibaOptions(options: DiscordCommandOption[] | undefined): {
  result?: string;
  amount?: number;
} {
  return {
    result: getStringCommandOption(options, "result"),
    amount: getNumberCommandOption(options, "amount"),
  };
}

export async function keibaresultController(
  env: Env,
  options: DiscordCommandOption[] | undefined,
): Promise<Response> {
  const parsed = parseKeibaOptions(options);
  if (parsed.result === undefined || parsed.amount === undefined) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: {
        content: "result と amount の指定が必要です",
        flags: EPHEMERAL_FLAG,
      },
    });
  }

  if (
    parsed.result !== KeibaResult.WIN &&
    parsed.result !== KeibaResult.LOSE &&
    parsed.result !== KeibaResult.DRAW
  ) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: {
        content: "result の値が不正です",
        flags: EPHEMERAL_FLAG,
      },
    });
  }

  const validation = validateKeibaAmount(parsed.result, parsed.amount);
  if (!validation.valid) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: {
        content: validation.errorMessage,
        flags: EPHEMERAL_FLAG,
      },
    });
  }

  const result = runKeibaResult(parsed.result, parsed.amount);
  if (!("imagePath" in result)) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: result.content },
    });
  }

  const filename = result.imagePath.split("/").pop() ?? "keibaresult.png";
  try {
    const assetUrl = new URL(`https://assets.local${result.imagePath}`);
    const imageResponse = await env.ASSETS.fetch(new Request(assetUrl.toString()));
    if (!imageResponse.ok) throw new Error("failed to fetch attachment image");
    const imageData = await imageResponse.arrayBuffer();
    return createMultipartInteractionResponse({
      content: result.content,
      attachment: {
        filename,
        contentType: imageResponse.headers.get("content-type") ?? "image/png",
        data: imageData,
      },
    });
  } catch (error) {
    console.error("keibaresult controller fallback", { phase: "attachment", error });
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: result.content },
    });
  }
}
