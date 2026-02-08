import { InteractionResponseType } from "../types";
import type { DiscordInteractionResponse } from "../types";

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
