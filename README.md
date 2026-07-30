# hellomegbot

Discord Interactions を Cloudflare Workers で処理する bot です。

## Setup

```bash
npm i
```

## Local

実際の Discord bot と連携せずにローカルで動作確認を行う手順です。\
署名検証をスキップすることで、curl で直接リクエストを送信できます。

```bash
npx wrangler dev \
  --var DISCORD_SKIP_SIGNATURE_VERIFICATION:true \
  --var ASSETS_BASE_URL:http://127.0.0.1:8787 \
  --var DISCORD_PUBLIC_KEY:dummy
```

```bash
URL=http://127.0.0.1:8787/interactions
```

```bash
# hellomeg
curl -sS "$URL" -H 'content-type: application/json' -d '{"type":2,"data":{"name":"hellomeg"}}'

# helloruri
curl -sS "$URL" -H 'content-type: application/json' -d '{"type":2,"data":{"name":"helloruri"}}'

# mmm-mm-mmmmmmmm
curl -sS "$URL" -H 'content-type: application/json' -d '{"type":2,"data":{"name":"mmm-mm-mmmmmmmm"}}'

# keibaresult
curl -sS "$URL" -H 'content-type: application/json' -d '{"type":2,"data":{"name":"keibaresult","options":[{"name":"result","type":3,"value":"ハロめぐー！"},{"name":"amount","type":4,"value":1000}]}}'

# meggen (modal を返す)
curl -sS "$URL" -H 'content-type: application/json' -d '{"type":2,"data":{"name":"meggen","options":[{"name":"img","type":3,"value":"fever"}]}}'

# meggen modal submit (画像を返す)
curl -sS "$URL" -H 'content-type: application/json' -d '{"type":5,"data":{"custom_id":"meggen:fever","components":[{"type":1,"components":[{"type":4,"custom_id":"line_1","value":"ハロ"}]},{"type":1,"components":[{"type":4,"custom_id":"line_2","value":"めぐ"}]},{"type":1,"components":[{"type":4,"custom_id":"line_3","value":"です"}]}]}}'
```

## Dev

TODO: 実際の Discord bot と連携して動作確認を行う手順を記載する。

## Test

```bash
npm test
```

## Deploy

```bash
npx wrangler deploy
```

## Weather data attribution

The `/hellomeg` high-temperature response uses weather data from [Open-Meteo.com](https://open-meteo.com/) under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Register Commands

必要な環境変数:
- `DISCORD_APPLICATION_ID`
- `DISCORD_BOT_TOKEN`

```bash
npm run register:commands
```
