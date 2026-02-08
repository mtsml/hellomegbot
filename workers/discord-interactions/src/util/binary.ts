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
