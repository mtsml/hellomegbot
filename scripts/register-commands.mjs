import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

function parseArgs(argv) {
  const args = { file: "scripts/commands.json" };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--file") {
      args.file = argv[i + 1] ?? "scripts/commands.json";
      i += 1;
    }
  }

  return args;
}

async function main() {
  const { file } = parseArgs(process.argv.slice(2));

  const appId = process.env.DISCORD_APPLICATION_ID;
  const botToken = process.env.DISCORD_BOT_TOKEN;

  if (!appId || !botToken) {
    console.error("DISCORD_APPLICATION_ID and DISCORD_BOT_TOKEN are required");
    process.exit(1);
  }

  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const baseDir = path.resolve(scriptDir, "..");
  const filePath = path.resolve(baseDir, file);

  const raw = await readFile(filePath, "utf8");
  const payload = JSON.parse(raw);

  const endpoint = `https://discord.com/api/v10/applications/${appId}/commands`;

  const response = await fetch(endpoint, {
    method: "PUT",
    headers: {
      authorization: `Bot ${botToken}`,
      "content-type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const body = await response.text();
  if (!response.ok) {
    console.error(`Failed: ${response.status}`);
    console.error(body);
    process.exit(1);
  }

  console.log("Registered commands: global");
  console.log(body);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
