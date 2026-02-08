export type Env = {
  ASSETS: {
    fetch(request: Request): Promise<Response>;
  };
  ASSETS_BASE_URL: string;
  DISCORD_PUBLIC_KEY: string;
  DISCORD_SKIP_SIGNATURE_VERIFICATION?: string;
  HELLOMEG_UR_PROBABILITY?: string;
  HELLOMEG_SR_PROBABILITY?: string;
  HELLORURI_UR_PROBABILITY?: string;
  HELLORURI_SR_PROBABILITY?: string;
  MMM_MM_MMMMMMMM_UR_PROBABILITY?: string;
  MMM_MM_MMMMMMMM_SR_PROBABILITY?: string;
};
