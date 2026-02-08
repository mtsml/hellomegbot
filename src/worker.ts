import { keibaresultController } from "./controllers/keibaresult";
import { hellomegController } from "./controllers/hellomeg";
import { helloruriController } from "./controllers/helloruri";
import { mmmMmMmmmmmmmController } from "./controllers/mmm-mm-mmmmmmmm";
import { meggenCommandController, meggenModalController } from "./controllers/meggen";
import type { Env } from "./utils/env";
import {
  InteractionResponseType,
  InteractionType,
} from "./libs/discord";
import type { DiscordInteraction } from "./libs/discord";
import { jsonResponse } from "./utils";
import { verifyDiscordSignature } from "./libs/discord";
import { shouldVerifySignature } from "./utils";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { pathname } = new URL(request.url);

    if (pathname === "/interactions" && request.method === "POST") {
      const signature = request.headers.get("X-Signature-Ed25519");
      const timestamp = request.headers.get("X-Signature-Timestamp");
      const rawBody = await request.text();

      if (shouldVerifySignature(env)) {
        const isValid = await verifyDiscordSignature(
          env.DISCORD_PUBLIC_KEY,
          timestamp,
          rawBody,
          signature,
        );
        if (!isValid) return new Response("invalid request signature", { status: 401 });
      }

      let interaction: DiscordInteraction;
      try {
        interaction = JSON.parse(rawBody) as DiscordInteraction;
      } catch {
        return jsonResponse({ error: "invalid JSON" }, 400);
      }

      // エンドポイント登録時などに送られてくる PING に応答する
      if (interaction.type === InteractionType.PING) {
        return jsonResponse({ type: InteractionResponseType.PONG });
      }

      // 各種コマンド処理を contoller に振り分ける
      if (interaction.type === InteractionType.APPLICATION_COMMAND) {
        const commandName = interaction.data?.name;
        switch (commandName) {
          case "hellomeg":
            return hellomegController(env);
          case "helloruri":
            return helloruriController(env);
          case "mmm-mm-mmmmmmmm":
            return mmmMmMmmmmmmmController(env);
          case "keibaresult":
            return keibaresultController(env, interaction.data?.options);
          case "meggen":
            return meggenCommandController(interaction.data?.options);
          default:
            return new Response("Not Found", { status: 404 });
        }
      }

      // モーダル送信時の処理
      if (interaction.type === InteractionType.MODAL_SUBMIT) {
        const customId = interaction.data?.custom_id;
        if (customId?.startsWith("meggen:")) {
          return meggenModalController({
            env,
            customId,
            components: interaction.data?.components,
          });
        }
      }

      return new Response("Not Found", { status: 404 });
    }

    return new Response("Not Found", { status: 404 });
  },
};
