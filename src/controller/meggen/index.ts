import {
  InteractionResponseType,
  type DiscordCommandOption,
  type DiscordModalSubmitComponent,
} from "../../libs/discord";
import type { Env } from "../../util/env";
import {
  generateMeggenPng,
  getMeggenImageConfig,
} from "../../service/meggen";
import {
  createJsonInteractionResponse,
  createMultipartInteractionResponse,
} from "../../libs/discord";
import { getStringCommandOption } from "../../libs/discord";
import {
  MEGGEN_MODAL_CUSTOM_ID_PREFIX,
  MEGGEN_MODAL_TEXT_CUSTOM_ID_PREFIX,
  MEGGEN_MODAL_TITLE,
} from "./constants";

const MEGGEN_ASSET_FONT_PATH = "/fonts/keifont.ttf";

function parseMeggenImageType(options: DiscordCommandOption[] | undefined): string | null {
  return getStringCommandOption(options, "img") ?? null;
}

function createMeggenModalResponse(imageType: string, rows: number, label: string): Response {
  return createJsonInteractionResponse({
    type: InteractionResponseType.MODAL,
    data: {
      title: MEGGEN_MODAL_TITLE,
      custom_id: `${MEGGEN_MODAL_CUSTOM_ID_PREFIX}${imageType}`,
      components: Array.from({ length: rows }).map((_, index) => ({
        type: 1,
        components: [
          {
            type: 4,
            custom_id: `${MEGGEN_MODAL_TEXT_CUSTOM_ID_PREFIX}${index + 1}`,
            label: `${index + 1}行目${label}`,
            style: 1,
            required: false,
          },
        ],
      })),
    },
  });
}

function extractTextLines(components: DiscordModalSubmitComponent[] | undefined): string[] {
  if (!components) return [];
  const lines: string[] = [];
  for (const row of components) {
    for (const component of row.components ?? []) {
      if (typeof component.value !== "string") continue;
      if (!component.custom_id?.startsWith(MEGGEN_MODAL_TEXT_CUSTOM_ID_PREFIX)) continue;
      lines.push(component.value);
    }
  }
  return lines;
}

export function meggenCommandController(options: DiscordCommandOption[] | undefined): Response {
  const imageType = parseMeggenImageType(options);
  if (!imageType) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: "img の指定が必要です" },
    });
  }

  const config = getMeggenImageConfig(imageType);
  if (!config) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: "img の値が不正です" },
    });
  }

  return createMeggenModalResponse(imageType, config.rows, config.label);
}

export async function meggenModalController(params: {
  env: Env;
  customId: string | undefined;
  components: DiscordModalSubmitComponent[] | undefined;
}): Promise<Response> {
  if (!params.customId?.startsWith(MEGGEN_MODAL_CUSTOM_ID_PREFIX)) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: "invalid modal custom_id" },
    });
  }

  const imageType = params.customId.slice(MEGGEN_MODAL_CUSTOM_ID_PREFIX.length);
  const config = getMeggenImageConfig(imageType);
  if (!config) {
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: "img の値が不正です" },
    });
  }

  try {
    const assetUrl = new URL(`https://assets.local${config.assetPath}`);
    const imageResponse = await params.env.ASSETS.fetch(new Request(assetUrl.toString()));
    if (!imageResponse.ok) throw new Error("failed to fetch meggen background image");
    const imageData = await imageResponse.arrayBuffer();

    const textLines = extractTextLines(params.components);
    const fontUrl = new URL(`https://assets.local${MEGGEN_ASSET_FONT_PATH}`);
    const fontResponse = await params.env.ASSETS.fetch(new Request(fontUrl.toString()));
    if (!fontResponse.ok) throw new Error("meggen font not found in assets");
    const fontBytes = new Uint8Array(await fontResponse.arrayBuffer());
    const result = await generateMeggenPng({
      imageType,
      textLines,
      backgroundPng: imageData,
      fontBytes,
    });
    if (!result) throw new Error("failed to generate meggen png");

    return createMultipartInteractionResponse({
      content: "",
      attachment: {
        filename: result.filename,
        contentType: "image/png",
        data: result.data,
      },
    });
  } catch (error) {
    console.error("meggen controller fallback", { phase: "render", error });
    return createJsonInteractionResponse({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: "画像生成に失敗しました" },
    });
  }
}
