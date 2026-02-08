export enum InteractionType {
  PING = 1,
  APPLICATION_COMMAND = 2,
  MODAL_SUBMIT = 5,
}

export type DiscordTextInputComponent = {
  type: number;
  custom_id?: string;
  value?: string;
};

export type DiscordModalSubmitComponent = {
  type: number;
  components?: DiscordTextInputComponent[];
};

export type DiscordCommandOption = {
  name: string;
  type: number;
  value: string | number | boolean;
};

export type DiscordInteraction = {
  type: InteractionType;
  data?: {
    name?: string;
    options?: DiscordCommandOption[];
    custom_id?: string;
    components?: DiscordModalSubmitComponent[];
  };
};

export enum InteractionResponseType {
  PONG = 1,
  CHANNEL_MESSAGE_WITH_SOURCE = 4,
  MODAL = 9,
}

export type DiscordInteractionResponse = {
  type: InteractionResponseType;
  data?: {
    content?: string;
    embeds?: Array<{ image: { url: string } }>;
    attachments?: Array<{ id: number; filename: string }>;
    flags?: number;
    title?: string;
    custom_id?: string;
    components?: Array<{
      type: number;
      components: Array<{
        type: number;
        custom_id: string;
        label: string;
        style: number;
        required?: boolean;
      }>;
    }>;
  };
};

type AttachmentInput = {
  filename: string;
  contentType: string;
  data: ArrayBuffer;
};

function concatUint8Arrays(chunks: Uint8Array[]): Uint8Array {
  const total = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const merged = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }
  return merged;
}

function hexToUint8Array(hex: string): Uint8Array {
  if (hex.length % 2 !== 0) throw new Error("invalid hex");
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i += 1) {
    out[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return out;
}

export function findCommandOption(
  options: DiscordCommandOption[] | undefined,
  name: string,
): DiscordCommandOption | undefined {
  return options?.find((option) => option.name === name);
}

export function getStringCommandOption(
  options: DiscordCommandOption[] | undefined,
  name: string,
): string | undefined {
  const option = findCommandOption(options, name);
  return typeof option?.value === "string" ? option.value : undefined;
}

export function getNumberCommandOption(
  options: DiscordCommandOption[] | undefined,
  name: string,
): number | undefined {
  const option = findCommandOption(options, name);
  return typeof option?.value === "number" ? option.value : undefined;
}

export function createJsonInteractionResponse(
  body: DiscordInteractionResponse,
): Response {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json; charset=UTF-8" },
  });
}

export function createMultipartInteractionResponse(params: {
  content: string;
  attachment: AttachmentInput;
}): Response {
  const boundary = `----hellomeg-${crypto.randomUUID()}`;
  const encoder = new TextEncoder();
  const payload: DiscordInteractionResponse = {
    type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
    data: {
      content: params.content,
      attachments: [{ id: 0, filename: params.attachment.filename }],
    },
  };

  const head = encoder.encode(
    `--${boundary}\r\n` +
      'Content-Disposition: form-data; name="payload_json"\r\n' +
      "Content-Type: application/json\r\n\r\n" +
      `${JSON.stringify(payload)}\r\n` +
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="files[0]"; filename="${params.attachment.filename}"\r\n` +
      `Content-Type: ${params.attachment.contentType}\r\n\r\n`,
  );
  const fileBytes = new Uint8Array(params.attachment.data);
  const tail = encoder.encode(`\r\n--${boundary}--\r\n`);
  const body = concatUint8Arrays([head, fileBytes, tail]);

  return new Response(body, {
    headers: {
      "content-type": `multipart/form-data; boundary=${boundary}`,
    },
  });
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
