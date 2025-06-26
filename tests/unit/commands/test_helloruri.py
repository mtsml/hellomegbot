import pytest
from hellomegbot.commands.helloruri import HelloRuri
from hellomegbot.commands.helloruri import (
    HELLORURI_COMMAND_NAME,
    HELLORURI_COMMAND_DESC,
    HELLORURI_MESSAGE_MEDIUM,
    HELLORURI_MESSAGE_LARGE,
    HELLORURI_JSON_URL
)

class TestHelloRuri:
    @pytest.fixture
    def ur_probability(self):
        return 0.01
        
    @pytest.fixture
    def sr_probability(self):
        return 0.1
        
    @pytest.fixture
    def helloruri(self, ur_probability, sr_probability):
        return HelloRuri(ur_probability, sr_probability)

    def test_initialization(self, helloruri):
        assert helloruri.command_name == HELLORURI_COMMAND_NAME
        assert helloruri.command_description == HELLORURI_COMMAND_DESC
        assert helloruri.message_medium.strip() == HELLORURI_MESSAGE_MEDIUM.strip()
        assert helloruri.message_large.strip() == HELLORURI_MESSAGE_LARGE.strip()
        assert helloruri.json_url == HELLORURI_JSON_URL

    def test_probabilities(self, helloruri, ur_probability, sr_probability):
        assert helloruri.ur_probability == ur_probability
        assert helloruri.sr_probability == sr_probability

    def test_initialization_with_none_probabilities(self):
        helloruri = HelloRuri(None, None)
        # Default values from GachaBase are used when None is passed
        assert helloruri.ur_probability == 0.03
        assert helloruri.sr_probability == 0.18
