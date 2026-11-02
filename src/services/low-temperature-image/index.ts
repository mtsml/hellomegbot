import {
  arrayBufferToBase64,
  readPngSize,
  renderSvgToPngWithFonts,
} from "../../libs/image";

const TEMPERATURE_TEXT_X = 60;
const TEMPERATURE_TEXT_Y = 990;
const TEMPERATURE_TEXT_LINE_HEIGHT = 190;
const TEMPERATURE_TEXT_COLOR = "#1261b8";
const TEMPERATURE_TEXT_FONT_SIZE = 110;
const TEMPERATURE_VALUE_FONT_SIZE = 160;
const TEMPERATURE_TEXT_STROKE_COLOR = "#ffffff";
const TEMPERATURE_TEXT_STROKE_WIDTH = 10;

type Size = {
  width: number;
  height: number;
};

export type LowTemperaturePngResult = {
  filename: string;
  data: ArrayBuffer;
};

export function buildLowTemperatureSvg(params: {
  backgroundDataUrl: string;
  backgroundSize: Size;
  temperature: number;
}): string {
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${params.backgroundSize.width}" height="${params.backgroundSize.height}" viewBox="0 0 ${params.backgroundSize.width} ${params.backgroundSize.height}">`,
    `<image href="${params.backgroundDataUrl}" width="${params.backgroundSize.width}" height="${params.backgroundSize.height}" />`,
    `<text x="${TEMPERATURE_TEXT_X}" y="${TEMPERATURE_TEXT_Y}" fill="${TEMPERATURE_TEXT_COLOR}" font-size="${TEMPERATURE_TEXT_FONT_SIZE}" font-family="keifont, sans-serif" stroke="${TEMPERATURE_TEXT_STROKE_COLOR}" stroke-width="${TEMPERATURE_TEXT_STROKE_WIDTH}" paint-order="stroke fill"><tspan>金沢は</tspan><tspan x="${TEMPERATURE_TEXT_X}" dy="${TEMPERATURE_TEXT_LINE_HEIGHT}" font-size="${TEMPERATURE_VALUE_FONT_SIZE}">${params.temperature}℃</tspan></text>`,
    "</svg>",
  ].join("");
}

export async function generateLowTemperaturePng(params: {
  backgroundPng: ArrayBuffer;
  fontBytes: Uint8Array;
  temperature: number;
  filename: string;
}): Promise<LowTemperaturePngResult | null> {
  try {
    const backgroundSize = readPngSize(params.backgroundPng);
    if (!backgroundSize) return null;

    const svg = buildLowTemperatureSvg({
      backgroundDataUrl: `data:image/png;base64,${arrayBufferToBase64(params.backgroundPng)}`,
      backgroundSize,
      temperature: params.temperature,
    });
    const data = await renderSvgToPngWithFonts(svg, [params.fontBytes]);
    return { filename: params.filename, data };
  } catch (error) {
    console.error("generateLowTemperaturePng failed", error);
    return null;
  }
}
