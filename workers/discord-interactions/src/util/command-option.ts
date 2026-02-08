import type { DiscordCommandOption } from "../types";

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
