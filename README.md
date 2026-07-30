# hellomegbot

Discord Interactions を Cloudflare Workers で処理する bot です。

## Setup

```bash
npm ci
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

コマンドを登録後、ローカル Worker を Quick Tunnel で公開して動作確認します。

```bash
DISCORD_APPLICATION_ID=<development-application-id> \
DISCORD_BOT_TOKEN=<development-bot-token> \
npm run register:commands
```

続けて、開発用 Application の公開鍵を指定して Worker を起動します。`DISCORD_SKIP_SIGNATURE_VERIFICATION` は指定しません。

```bash
npx wrangler dev \
  --var DISCORD_PUBLIC_KEY:<development-application-public-key> \
  --var ASSETS_BASE_URL:https://hellomeg-assets.pages.dev
```

さらに別のターミナルで Quick Tunnel を起動します。

```bash
cloudflared tunnel --url http://localhost:8787
```

表示された `https://<random>.trycloudflare.com/interactions` を Discord Developer Portal の開発用 Application の **Interactions Endpoint URL** に設定します。その後、テスト用サーバーでコマンドを実行します。Quick Tunnel の URL は起動ごとに変わるため、その都度 Endpoint URL を更新してください。

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
