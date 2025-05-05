# hellomegbot
![Python Tests](https://github.com/username/hellomegbot/actions/workflows/python-tests.yml/badge.svg)
### Usage
1. 環境変数 `DISCORD_BOT_TOKEN` を設定
    ```bash
    echo "DISCORD_BOT_TOKEN=discord_bot_token" >> .env
    ```
2. ライブラリをインストール
    ```bash
    pip install -r requirements.txt
    ```
3. 起動
    ```bash
    python main.py
    ```

### Development

#### Setup Development Environment
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Running Tests
```bash
# Run all tests
pytest tests/

# Run tests with coverage report
pytest --cov=src/ tests/

# Run specific test file
pytest tests/unit/commands/test_hellomeg.py
```

#### GitHub Actions

このプロジェクトはGitHub Actionsを使用して自動テストを実行します。

- プッシュやプルリクエスト時に自動的にテストが実行されます
- GitHub UIから手動でテストを実行することも可能です:
  1. リポジトリの "Actions" タブに移動
  2. 左側のサイドバーから "Python Tests" ワークフローを選択
  3. "Run workflow" ボタンをクリック
  4. 以下のオプションを設定可能:
     - `Python version`: テストするPythonバージョン（カンマ区切りで複数指定可能、例: `3.8,3.9`）
     - `Skip coverage`: カバレッジレポート生成をスキップするかどうか
  5. "Run workflow" をクリック
