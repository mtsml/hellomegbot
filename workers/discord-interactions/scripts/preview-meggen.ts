import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  generateMeggenPng,
  getMeggenImageConfig,
  type MeggenImageType,
} from "../src/service/meggen/index";

function parseArgs(argv: string[]): {
  imageType: MeggenImageType;
  lines: string[];
  outputPath?: string;
} {
  let imageType: MeggenImageType = "damon";
  const lines: string[] = [];
  let outputPath: string | undefined;

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--img") {
      imageType = (argv[i + 1] as MeggenImageType) ?? "damon";
      i += 1;
      continue;
    }
    if (token === "--line") {
      lines.push(argv[i + 1] ?? "");
      i += 1;
      continue;
    }
    if (token === "--out") {
      outputPath = argv[i + 1];
      i += 1;
    }
  }

  return { imageType, lines, outputPath };
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  const config = getMeggenImageConfig(args.imageType);
  if (!config) {
    throw new Error(`Unknown image type: ${args.imageType}`);
  }

  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const repoRoot = path.resolve(scriptDir, "..", "..", "..");

  const backgroundPath = path.join(repoRoot, "assets", config.assetPath.replace(/^\//, ""));
  const fontPath = path.join(repoRoot, "assets", "fonts", "keifont.ttf");

  const [backgroundPng, fontBytes] = await Promise.all([
    readFile(backgroundPath),
    readFile(fontPath),
  ]);

  const result = await generateMeggenPng({
    imageType: args.imageType,
    textLines: args.lines,
    backgroundPng: backgroundPng.buffer.slice(
      backgroundPng.byteOffset,
      backgroundPng.byteOffset + backgroundPng.byteLength,
    ) as ArrayBuffer,
    fontBytes,
  });

  if (!result) {
    throw new Error("Failed to generate image");
  }

  const outDir = path.join(repoRoot, "tmp");
  await mkdir(outDir, { recursive: true });
  const outPath = args.outputPath
    ? path.resolve(repoRoot, args.outputPath)
    : path.join(outDir, `meggen-preview-${args.imageType}.png`);

  await writeFile(outPath, Buffer.from(result.data));
  console.log(`generated: ${outPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
