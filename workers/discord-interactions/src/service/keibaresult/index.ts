const KEIBA_RESULT_WIN = "ハロめぐー！";
const KEIBA_RESULT_LOSE = "バイめぐ〜";
const KEIBA_RESULT_DRAW = "めぐ";
const KEIBA_WIN_IMAGES = ["/keibaresult/win/win.png"];
const KEIBA_LOSE_IMAGES = [
  "/keibaresult/lose/lose_001.png",
  "/keibaresult/lose/lose_002.png",
  "/keibaresult/lose/lose_003.png",
];

export enum KeibaResult {
  WIN = "ハロめぐー！",
  LOSE = "バイめぐ〜",
  DRAW = "めぐ",
}

type KeibaValidationError = {
  valid: false;
  errorMessage: string;
};

type KeibaValidationSuccess = {
  valid: true;
};

export type KeibaValidation = KeibaValidationError | KeibaValidationSuccess;

type KeibaResponseWithImage = {
  content: string;
  imagePath: string;
};

type KeibaResponseWithoutImage = {
  content: string;
};

export type KeibaServiceResponse = KeibaResponseWithImage | KeibaResponseWithoutImage;

function formatAmount(amount: number): string {
  return amount.toLocaleString("en-US");
}

function pickRandom(items: string[]): string {
  return items[Math.floor(Math.random() * items.length)];
}

export function validateKeibaAmount(result: string, amount: number): KeibaValidation {
  if (result === KeibaResult.WIN && amount === 0) {
    return { valid: false, errorMessage: "amount に 0 より大き値を入れろ" };
  }
  if (result === KeibaResult.LOSE && amount === 0) {
    return { valid: false, errorMessage: "amount に 0 より大き値を入れろ" };
  }
  if (result === KeibaResult.DRAW && amount !== 0) {
    return { valid: false, errorMessage: "amount に 0 を入れろ" };
  }
  return { valid: true };
}

export function runKeibaResult(result: string, amount: number): KeibaServiceResponse {
  const formatted = formatAmount(amount);

  if (result === KEIBA_RESULT_WIN) {
    return {
      content: `${KEIBA_RESULT_WIN} (+${formatted})`,
      imagePath: pickRandom(KEIBA_WIN_IMAGES),
    };
  }
  if (result === KEIBA_RESULT_LOSE) {
    return {
      content: `${KEIBA_RESULT_LOSE} (-${formatted})`,
      imagePath: pickRandom(KEIBA_LOSE_IMAGES),
    };
  }
  return { content: `${KEIBA_RESULT_DRAW} (±0)` };
}
