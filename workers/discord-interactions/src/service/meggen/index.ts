import { arrayBufferToBase64, readPngSize } from "../../util/binary";

type Point = {
  x: number;
  y: number;
};

type Size = {
  width: number;
  height: number;
};

type Stroke = {
  width: number;
  fill: string;
};

export type MeggenImageType =
  | "fever"
  | "damon"
  | "hkc"
  | "universe"
  | "hasunosorashikanainsuyo"
  | "doya";

export type MeggenImageConfig = {
  rows: number;
  label: string;
  assetPath: string;
  textImageSize: Size;
  textColor: string;
  textFontSize: number;
  textStart: Point;
  textRotate: number;
  textPaste: Point;
  sendFilename: string;
  stroke?: Stroke;
};

export type MeggenPngResult = {
  filename: string;
  data: ArrayBuffer;
};

type MeggenImageOption = {
  name: string;
  value: MeggenImageType;
};

const MEGGEN_IMAGE_OPTIONS: MeggenImageOption[] = [
  { name: "フィーバー", value: "fever" },
  { name: "ハロめぐだもん", value: "damon" },
  { name: "ハクチュー", value: "hkc" },
  { name: "宇宙猫", value: "universe" },
  { name: "蓮ノ空しかないんすよ", value: "hasunosorashikanainsuyo" },
  { name: "ドヤめぐ", value: "doya" },
];

const MEGGEN_IMAGE_CONFIGS: Record<MeggenImageType, MeggenImageConfig> = {
  fever: {
    rows: 3,
    label: "（5文字まで）",
    assetPath: "/meggen/fever.png",
    textImageSize: { width: 600, height: 500 },
    textColor: "#764c4d",
    textFontSize: 100,
    textStart: { x: 30, y: 15 },
    textRotate: 16,
    textPaste: { x: 80, y: 300 },
    sendFilename: "fever.png",
  },
  damon: {
    rows: 2,
    label: "（10文字まで）",
    assetPath: "/meggen/damon.png",
    textImageSize: { width: 1050, height: 300 },
    textColor: "#ceaa9e",
    textFontSize: 100,
    textStart: { x: 20, y: 0 },
    textRotate: 0,
    textPaste: { x: 120, y: 280 },
    stroke: { width: 20, fill: "#633539" },
    sendFilename: "damon.png",
  },
  hkc: {
    rows: 1,
    label: "（7文字まで）",
    assetPath: "/meggen/hkc.png",
    textImageSize: { width: 500, height: 300 },
    textColor: "#c1e3da",
    textFontSize: 60,
    textStart: { x: 60, y: 75 },
    textRotate: 20,
    textPaste: { x: 20, y: 80 },
    stroke: { width: 15, fill: "#9fccbf" },
    sendFilename: "hkc.png",
  },
  universe: {
    rows: 2,
    label: "（5文字まで）",
    assetPath: "/meggen/universe.png",
    textImageSize: { width: 350, height: 320 },
    textColor: "#000000",
    textFontSize: 50,
    textStart: { x: 50, y: 15 },
    textRotate: 340,
    textPaste: { x: 720, y: 450 },
    sendFilename: "universe.png",
  },
  hasunosorashikanainsuyo: {
    rows: 3,
    label: "（10文字まで）",
    assetPath: "/meggen/hasunosorashikanainsuyo.png",
    textImageSize: { width: 1050, height: 400 },
    textColor: "#000000",
    textFontSize: 100,
    textStart: { x: 0, y: 0 },
    textRotate: 0,
    textPaste: { x: 150, y: 50 },
    sendFilename: "hasunosorashikanainsuyo.png",
  },
  doya: {
    rows: 5,
    label: "（10文字まで）",
    assetPath: "/meggen/doya.png",
    textImageSize: { width: 700, height: 500 },
    textColor: "#ffffff",
    textFontSize: 70,
    textStart: { x: 0, y: 0 },
    textRotate: 0,
    textPaste: { x: 50, y: 500 },
    sendFilename: "doya.png",
  },
};

function escapeXml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function normalizeLines(textLines: string[], rows: number): string[] {
  return textLines
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .slice(0, rows);
}

function buildTextTspans(lines: string[], x: number, firstY: number, lineHeight: number): string {
  if (lines.length === 0) return "";
  return lines
    .map((line, index) => {
      const y = firstY + index * lineHeight;
      return `<tspan x="${x}" y="${y}">${escapeXml(line)}</tspan>`;
    })
    .join("");
}

export function getMeggenImageOptions(): MeggenImageOption[] {
  return MEGGEN_IMAGE_OPTIONS;
}

export function getMeggenImageConfig(imageType: string): MeggenImageConfig | undefined {
  if (!(imageType in MEGGEN_IMAGE_CONFIGS)) return undefined;
  return MEGGEN_IMAGE_CONFIGS[imageType as MeggenImageType];
}

export function buildMeggenSvg(params: {
  backgroundDataUrl: string;
  backgroundSize: Size;
  config: MeggenImageConfig;
  textLines: string[];
}): string {
  const lines = normalizeLines(params.textLines, params.config.rows);
  const textLineHeight = Math.floor(params.config.textFontSize * 1.2);
  const rotateCx = Math.floor(params.config.textImageSize.width / 2);
  const rotateCy = Math.floor(params.config.textImageSize.height / 2);
  const strokeAttr = params.config.stroke
    ? `stroke="${params.config.stroke.fill}" stroke-width="${params.config.stroke.width}" paint-order="stroke fill"`
    : "";
  const textTspans = buildTextTspans(
    lines,
    params.config.textStart.x,
    params.config.textStart.y + params.config.textFontSize,
    textLineHeight,
  );

  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${params.backgroundSize.width}" height="${params.backgroundSize.height}" viewBox="0 0 ${params.backgroundSize.width} ${params.backgroundSize.height}">`,
    `<image href="${params.backgroundDataUrl}" width="${params.backgroundSize.width}" height="${params.backgroundSize.height}" />`,
    `<g transform="translate(${params.config.textPaste.x} ${params.config.textPaste.y})">`,
    `<svg width="${params.config.textImageSize.width}" height="${params.config.textImageSize.height}" overflow="visible">`,
    `<g transform="rotate(${-params.config.textRotate} ${rotateCx} ${rotateCy})">`,
    `<text fill="${params.config.textColor}" font-size="${params.config.textFontSize}" font-family="keifont, sans-serif" ${strokeAttr}>`,
    textTspans,
    "</text>",
    "</g>",
    "</svg>",
    "</g>",
    "</svg>",
  ].join("");
}

export async function generateMeggenPng(params: {
  imageType: string;
  textLines: string[];
  backgroundPng: ArrayBuffer;
  fontBytes: Uint8Array;
}): Promise<MeggenPngResult | null> {
  const config = getMeggenImageConfig(params.imageType);
  if (!config) return null;

  try {
    const imageSize = readPngSize(params.backgroundPng);
    if (!imageSize) return null;

    const backgroundDataUrl = `data:image/png;base64,${arrayBufferToBase64(params.backgroundPng)}`;
    const svg = buildMeggenSvg({
      backgroundDataUrl,
      backgroundSize: imageSize,
      config,
      textLines: params.textLines,
    });
    const { renderSvgToPngWithFonts } = await import("../../util/svg-to-png");
    const png = await renderSvgToPngWithFonts(svg, [params.fontBytes]);
    return {
      filename: config.sendFilename,
      data: png,
    };
  } catch (error) {
    console.error("generateMeggenPng failed", error);
    return null;
  }
}
