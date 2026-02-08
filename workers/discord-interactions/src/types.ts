export type Env = {
  ASSETS: {
    fetch(request: Request): Promise<Response>;
  };
  GACHA_ASSETS_BASE_URL: string;
  DISCORD_PUBLIC_KEY: string;
  DISCORD_APPLICATION_ID?: string;
  DISCORD_BOT_TOKEN?: string;
  DISCORD_SKIP_SIGNATURE_VERIFICATION?: string;
  HELLOMEG_UR_PROBABILITY?: string;
  HELLOMEG_SR_PROBABILITY?: string;
  HELLORURI_UR_PROBABILITY?: string;
  HELLORURI_SR_PROBABILITY?: string;
  MMM_MM_MMMMMMMM_UR_PROBABILITY?: string;
  MMM_MM_MMMMMMMM_SR_PROBABILITY?: string;
};

export enum InteractionType {
  PING = 1,
  APPLICATION_COMMAND = 2,
}

export type DiscordInteraction = {
  type: InteractionType;
  data?: {
    name?: string;
    options?: DiscordCommandOption[];
  };
};

export type DiscordCommandOption = {
  name: string;
  type: number;
  value: string | number | boolean;
};

export enum InteractionResponseType {
  PONG = 1,
  CHANNEL_MESSAGE_WITH_SOURCE = 4,
}

export type DiscordInteractionResponse = {
  type: InteractionResponseType;
  data?: {
    content?: string;
    embeds?: Array<{ image: { url: string } }>;
    attachments?: Array<{ id: number; filename: string }>;
    flags?: number;
  };
};
