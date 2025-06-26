# hellomegbot
![Python Tests](https://github.com/mtsml/hellomegbot/actions/workflows/python-tests.yml/badge.svg)

## Development

### Setup
```bash
# 依存関係のインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 環境変数の設定
echo "DISCORD_BOT_TOKEN=your_discord_bot_token" >> .env
```

### Run Bot
```bash
python -m src.hellomegbot.main
```

### Running Tests
```bash
# 全テストを実行
pytest tests/

# カバレッジレポート付きでテストを実行
pytest --cov=src/ tests/

# ユニットテストのみ実行
pytest tests/unit/

# 統合テストのみ実行
pytest tests/integration/
```

## Project Structure

### Source Code
```
src/
└── hellomegbot/
    ├── main.py            # Bot entry point
    ├── commands/          # Discord command handlers
    ├── services/          # Business logic & data management
    └── utils/             # Utilities
```

### Tests
```
tests/
├── unit/                  # Unit tests
│   ├── commands/          # Command logic tests
│   └── services/          # Service logic tests
└── integration/           # Integration tests
    └── test_bot.py        # End-to-end bot tests
```

## アーキテクチャ

### クリーンアーキテクチャの採用

このプロジェクトでは、ビジネスロジックと Discord インターフェースを分離したクリーンアーキテクチャを採用しています。

#### サービス層（Services）
- **責務**: ビジネスロジックの実装
- **特徴**: Discord 依存なし、テスト容易、再利用可能
- **例**: ガチャ確率計算、画像生成、バリデーション

#### コマンド層（Commands）
- **責務**: Discord インターフェースの処理
- **特徴**: Discord.py 依存、ユーザー入力処理、レスポンス送信
- **例**: スラッシュコマンド登録、インタラクション処理

### 依存性注入パターン

```python
# サービスの注入例
service = HellomegService(
    fever_minute=0,
    ur_probability=0.03,
    sr_probability=0.18
)
command = Hellomeg(service=service)
```

## Test Strategy

### Unit Tests
- **対象**: Discord依存のないビジネスロジック
- **特徴**: 高速実行、独立性、モック可能
- **カバレッジ**: ガチャ確率、画像選択、メッセージ生成

### Integration Tests
- **対象**: Discord統合とコマンドフロー
- **特徴**: Discordオブジェクトのモック、非同期テスト
- **カバレッジ**: コマンド登録、インタラクション処理、エラーケース

## GitHub Actions

以下のタイミングで自動テストが実行されます：
- プッシュ時
- プルリクエスト作成時
- Actionsタブからの手動実行

## 開発ガイドライン

### 新しいコマンドの追加

1. **サービスクラスの作成** (`services/`ディレクトリ)
   - ビジネスロジックの実装
   - Discord依存を含めない

2. **コマンドクラスの作成** (`commands/`ディレクトリ)
   - Discordインターフェースの実装
   - サービスクラスを使用

3. **テストの作成**
   - サービスのユニットテスト
   - コマンドのユニットテスト

4. **main.pyへの登録**
   - サービスのインスタンス化
   - コマンドの登録

### コーディング規約

- サービスとコマンドの責務を明確に分離
- 型ヒントの使用を推奨
- テストカバレッジ80%以上を目標
- ドキュメント文字列の記載