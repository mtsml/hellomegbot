import pytest
from hellomegbot.commands.mmm_mm_mmmmmmmm import (
    MMM_MM_MMMMMMMM_COMMAND_NAME,
    MMM_MM_MMMMMMMM_COMMAND_DESC,
    MMM_MM_MMMMMMMM_MESSAGE_MEDIUM,
    MMM_MM_MMMMMMMM_MESSAGE_LARGE,
    MMM_MM_MMMMMMMM_JSON_URL,
    MmmMmMmmmmmmm
)

class TestMmmMmMmmmmmmmm:
    @pytest.fixture
    def ur_probability(self):
        return 0.02
        
    @pytest.fixture
    def sr_probability(self):
        return 0.15
        
    @pytest.fixture
    def mmm(self, ur_probability, sr_probability):
        return MmmMmMmmmmmmm(ur_probability, sr_probability)

    def test_initialization(self, mmm):
        assert mmm.command_name == MMM_MM_MMMMMMMM_COMMAND_NAME
        assert mmm.command_description == MMM_MM_MMMMMMMM_COMMAND_DESC
        assert mmm.message_medium.strip() == MMM_MM_MMMMMMMM_MESSAGE_MEDIUM.strip()
        assert mmm.message_large.strip() == MMM_MM_MMMMMMMM_MESSAGE_LARGE.strip()
        assert mmm.json_url == MMM_MM_MMMMMMMM_JSON_URL

    def test_probabilities(self, mmm, ur_probability, sr_probability):
        assert mmm.ur_probability == ur_probability
        assert mmm.sr_probability == sr_probability

    def test_initialization_with_none_probabilities(self):
        mmm = MmmMmMmmmmmmm(None, None)
        # Default values from GachaBase are used when None is passed
        assert mmm.ur_probability == 0.03
        assert mmm.sr_probability == 0.18
