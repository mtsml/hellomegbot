function hexToUint8Array(hex: string): Uint8Array {
  if (hex.length % 2 !== 0) throw new Error("invalid hex");
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i += 1) {
    out[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return out;
}

export async function verifyDiscordSignature(
  publicKey: string,
  timestamp: string | null,
  rawBody: string,
  signature: string | null,
): Promise<boolean> {
  if (!publicKey || !timestamp || !rawBody || !signature) return false;

  try {
    const keyData = hexToUint8Array(publicKey);
    const signatureData = hexToUint8Array(signature);
    const encoder = new TextEncoder();
    const message = encoder.encode(timestamp + rawBody);
    const key = await crypto.subtle.importKey(
      "raw",
      keyData,
      { name: "Ed25519" },
      false,
      ["verify"],
    );
    return crypto.subtle.verify("Ed25519", key, signatureData, message);
  } catch {
    return false;
  }
}
