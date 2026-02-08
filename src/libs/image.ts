import { Resvg, initWasm } from "@resvg/resvg-wasm";

let initialized = false;

async function loadResvgWasm(): Promise<ArrayBuffer> {
  try {
    const wasmModule = await import("@resvg/resvg-wasm/index_bg.wasm");
    return wasmModule.default as ArrayBuffer;
  } catch {
    const { readFile } = await import("node:fs/promises");
    const { fileURLToPath } = await import("node:url");
    const wasmPath = fileURLToPath(
      new URL("../../node_modules/@resvg/resvg-wasm/index_bg.wasm", import.meta.url),
    );
    const buffer = await readFile(wasmPath);
    return buffer.buffer.slice(
      buffer.byteOffset,
      buffer.byteOffset + buffer.byteLength,
    ) as ArrayBuffer;
  }
}

async function ensureInitialized(): Promise<void> {
  if (initialized) return;
  await initWasm(await loadResvgWasm());
  initialized = true;
}

export function arrayBufferToBase64(data: ArrayBuffer): string {
  const bytes = new Uint8Array(data);
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary);
}

export function readPngSize(data: ArrayBuffer): { width: number; height: number } | null {
  const bytes = new Uint8Array(data);
  if (bytes.length < 24) return null;

  const signature = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  for (let i = 0; i < signature.length; i += 1) {
    if (bytes[i] !== signature[i]) return null;
  }

  const view = new DataView(data);
  const width = view.getUint32(16);
  const height = view.getUint32(20);
  return { width, height };
}

export async function renderSvgToPng(svg: string): Promise<ArrayBuffer> {
  await ensureInitialized();
  const renderer = new Resvg(svg, { fitTo: { mode: "original" } });
  const rendered = renderer.render();
  const png = rendered.asPng();
  return png.buffer.slice(
    png.byteOffset,
    png.byteOffset + png.byteLength,
  ) as ArrayBuffer;
}

export async function renderSvgToPngWithFonts(
  svg: string,
  fontBuffers: Uint8Array[],
): Promise<ArrayBuffer> {
  await ensureInitialized();
  const renderer = new Resvg(svg, {
    fitTo: { mode: "original" },
    font: {
      fontBuffers,
      defaultFontFamily: "keifont",
    },
  });
  const rendered = renderer.render();
  const png = rendered.asPng();
  return png.buffer.slice(
    png.byteOffset,
    png.byteOffset + png.byteLength,
  ) as ArrayBuffer;
}
