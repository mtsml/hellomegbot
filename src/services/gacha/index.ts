type GachaImage = {
  filepath: string;
  twitter_id: string;
};

export enum Rarity {
  UR = "ur",
  SR = "sr",
  NORMAL = "normal",
}

type GachaSrResult = {
  filepath: string;
  twitterId: string;
};

export function drawRarity(
  urProbability: number,
  srProbability: number,
): Rarity {
  const rand = Math.random();
  if (rand < urProbability) return Rarity.UR;
  if (rand < urProbability + srProbability) return Rarity.SR;
  return Rarity.NORMAL;
}

export async function buildSrResult(
  jsonUrl: string,
): Promise<GachaSrResult | null> {
  try {
    const response = await fetch(jsonUrl);
    const images = (await response.json()) as GachaImage[];
    const picked = images[Math.floor(Math.random() * images.length)];

    return {
      filepath: picked.filepath,
      twitterId: picked.twitter_id,
    };
  } catch (error) {
    console.error("gacha service fallback", {
      phase: "sr_assets",
      error,
    });
    return null;
  }
}
