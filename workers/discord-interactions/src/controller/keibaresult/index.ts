import { KeibaResult, runKeibaResult, validateKeibaAmount } from "../../service/keibaresult";
import {
  InteractionResponseType,
  type DiscordCommandOption,
} from "../../types";
import type { Env } from "../../types";
import {
  createJsonInteractionResponse,
  createMultipartInteractionResponse,
} from "../../util/interaction-response";

const EPHEMERAL_FLAG = 1 << 6;

function findOption(
  options: DiscordCommandOption[] | undefined,
  name: string,
): DiscordCommandOption | undefined {
  return options?.find((option) => option.name === name);
}

function parseKeibaOptions(options: DiscordCommandOption[] | undefined): {
  result?: string;
  amount?: number;
} {
  const resultOption = findOption(options, "result");
  const amountOption = findOption(options, "amount");
  return {
    result: typeof resultOption?.value === "string" ? resultOption.value : undefined,
    amount: typeof amountOption?.value === "number" ? amountOption.value : undefined,
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
