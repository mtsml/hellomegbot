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
import { shouldVerifySignature, unsupported } from "./utils";

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
