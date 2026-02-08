import { registerGlobalCommand } from "../../util/discord-api";
import { jsonResponse } from "../../util/http";
import type { Env } from "../../types";

export async function handleAdminRegisterController(env: Env): Promise<Response> {
  const commands = [
    { name: "hellomeg", description: "ハロめぐー！", type: 1 as const },
    { name: "helloruri", description: "ハロるりー！", type: 1 as const },
    {
      name: "mmm-mm-mmmmmmmm",
      description: "萌萌萌・萌萌・萌萌萌萌萌萌萌萌",
      type: 1 as const,
    },
    {
      name: "keibaresult",
      description: "競馬の結果を報告する",
      type: 1 as const,
      options: [
        {
          type: 3,
          name: "result",
          description: "今日の競馬の結果は？",
          required: true,
          choices: [
            { name: "ハロめぐー！", value: "ハロめぐー！" },
            { name: "バイめぐ〜", value: "バイめぐ〜" },
            { name: "めぐ", value: "めぐ" },
          ],
        },
        {
          type: 4,
          name: "amount",
          description: "いくら？",
          required: true,
          min_value: 0,
        },
      ],
    },
  ];

  const results = await Promise.all(
    commands.map(async (command) => {
      const response = await registerGlobalCommand(env, command);
      return {
        command: command.name,
        status: response.status,
        body: await response.text(),
      };
    }),
  );

  const hasError = results.some((result) => result.status >= 400);
  return jsonResponse({ results }, hasError ? 500 : 200);
}
