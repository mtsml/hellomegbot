import unittest
from src.hellomegbot.commands.mmm_mm_mmmmmmmm import (
    MMM_MM_MMMMMMMM_COMMAND_NAME,
    MMM_MM_MMMMMMMM_COMMAND_DESC,
    MMM_MM_MMMMMMMM_MESSAGE_MEDIUM,
    MMM_MM_MMMMMMMM_MESSAGE_LARGE,
    MMM_MM_MMMMMMMM_JSON_URL,
    MmmMmMmmmmmmm
)

class TestMmmMmMmmmmmmmm(unittest.TestCase):
    def setUp(self):
        self.ur_probability = 0.02
        self.sr_probability = 0.15
        self.mmm = MmmMmMmmmmmmm(self.ur_probability, self.sr_probability)

    def test_initialization(self):
        self.assertEqual(self.mmm.command_name, MMM_MM_MMMMMMMM_COMMAND_NAME)
        self.assertEqual(self.mmm.command_description, MMM_MM_MMMMMMMM_COMMAND_DESC)
        self.assertEqual(self.mmm.message_medium.strip(), MMM_MM_MMMMMMMM_MESSAGE_MEDIUM.strip())
        self.assertEqual(self.mmm.message_large.strip(), MMM_MM_MMMMMMMM_MESSAGE_LARGE.strip())
        self.assertEqual(self.mmm.json_url, MMM_MM_MMMMMMMM_JSON_URL)

    def test_probabilities(self):
        self.assertEqual(self.mmm.ur_probability, self.ur_probability)
        self.assertEqual(self.mmm.sr_probability, self.sr_probability)

    def test_initialization_with_none_probabilities(self):
        mmm = MmmMmMmmmmmmm(None, None)
        # Default values from GachaBase are used when None is passed
        self.assertEqual(mmm.ur_probability, 0.03)
        self.assertEqual(mmm.sr_probability, 0.18)

if __name__ == "__main__":
    unittest.main()
