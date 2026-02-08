import { keibaresultController } from "./controller/keibaresult";
import { hellomegController } from "./controller/hellomeg";
import { helloruriController } from "./controller/helloruri";
import { mmmMmMmmmmmmmController } from "./controller/mmm-mm-mmmmmmmm";
import { meggenCommandController, meggenModalController } from "./controller/meggen";
import type { Env } from "./util/env";
import {
  InteractionResponseType,
  InteractionType,
} from "./libs/discord";
import type { DiscordInteraction } from "./libs/discord";
import { jsonResponse } from "./util";
import { verifyDiscordSignature } from "./libs/discord";
import { shouldVerifySignature, unsupported } from "./util";

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

      if (interaction.type === InteractionType.PING) {
        return jsonResponse({ type: InteractionResponseType.PONG });
      }

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
            return unsupported(`Unknown command: ${commandName ?? "undefined"}`);
        }
      }

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

      return unsupported("Unsupported interaction type.");
    }

    return new Response("Not Found", { status: 404 });
  },
};
