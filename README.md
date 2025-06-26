# hellomegbot
![Python Tests](https://github.com/mtsml/hellomegbot/actions/workflows/python-tests.yml/badge.svg)

## Development

### Setup Development Environment
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo "DISCORD_BOT_TOKEN=discord_bot_token" >> .env
```

### Run Bot
```bash
python -m src.hellomegbot.main
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run tests with coverage report
pytest --cov=src/ tests/

# Run unit tests only
pytest tests/unit/

# Run integration tests only
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
    └── utils/            # Utilities
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

## Test Strategy

### Unit Tests
- **Target**: Business logic without Discord dependencies
- **Characteristics**: Fast execution, isolated, mockable
- **Coverage**: Gacha probability, image selection, message generation

### Integration Tests
- **Target**: Discord integration and command flow
- **Characteristics**: Mocked Discord objects, async testing
- **Coverage**: Command registration, interaction handling, error cases

## GitHub Actions

Automated tests run on:
- Every push
- Pull requests
- Manual trigger via Actions tab