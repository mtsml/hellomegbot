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
