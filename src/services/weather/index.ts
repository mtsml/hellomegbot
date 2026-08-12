const KANAZAWA_LATITUDE = 36.56;
const KANAZAWA_LONGITUDE = 136.66;

type OpenMeteoResponse = {
  current?: {
    temperature_2m?: unknown;
  };
};

function parseTemperature(payload: OpenMeteoResponse): number | null {
  const temperature = payload.current?.temperature_2m;
  return typeof temperature === "number" && Number.isFinite(temperature)
    ? temperature
    : null;
}

/**
 * 金沢の現在気温を摂氏で返す。天気 API の利用に失敗した場合は null を返す。
 */
export async function getKanazawaCurrentTemperature(): Promise<number | null> {
  try {
    console.info({
      event: "weather_service_request",
      phase: "current_temperature",
      location: "Kanazawa",
    });

    const apiUrl = new URL("https://api.open-meteo.com/v1/forecast");
    apiUrl.searchParams.set("latitude", String(KANAZAWA_LATITUDE));
    apiUrl.searchParams.set("longitude", String(KANAZAWA_LONGITUDE));
    apiUrl.searchParams.set("current", "temperature_2m");
    apiUrl.searchParams.set("timezone", "Asia/Tokyo");

    const response = await fetch(apiUrl);
    const body = await response.text();
    console.info({
      event: "weather_service_http_response",
      phase: "current_temperature",
      location: "Kanazawa",
      status: response.status,
      url: response.url,
      body,
    });
    if (!response.ok) throw new Error("failed to fetch current temperature");

    const payload = JSON.parse(body) as OpenMeteoResponse;
    const temperature = parseTemperature(payload);
    if (temperature === null) throw new Error("invalid current temperature response");

    console.info({
      event: "weather_service_response",
      phase: "current_temperature",
      location: "Kanazawa",
      temperature,
    });

    return temperature;
  } catch (error) {
    console.error({
      event: "weather_service_fallback",
      phase: "current_temperature",
      errorMessage: error instanceof Error ? error.message : String(error),
    });
    return null;
  }
}
