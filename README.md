# hellomegbot
![Python Tests](https://github.com/mtsml/hellomegbot/actions/workflows/python-tests.yml/badge.svg)

### Development

#### Setup Development Environment
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo "DISCORD_BOT_TOKEN=discord_bot_token" >> .env
```

#### Serve Local
```bash
python main.py
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
