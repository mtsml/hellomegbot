import unittest
from src.hellomegbot.commands.helloruri import HelloRuri
from src.hellomegbot.commands.helloruri import (
    HELLORURI_COMMAND_NAME,
    HELLORURI_COMMAND_DESC,
    HELLORURI_MESSAGE_MEDIUM,
    HELLORURI_MESSAGE_LARGE,
    HELLORURI_JSON_URL
)

class TestHelloRuri(unittest.TestCase):
    def setUp(self):
        self.ur_probability = 0.01
        self.sr_probability = 0.1
        self.helloruri = HelloRuri(self.ur_probability, self.sr_probability)

    def test_initialization(self):
        self.assertEqual(self.helloruri.command_name, HELLORURI_COMMAND_NAME)
        self.assertEqual(self.helloruri.command_description, HELLORURI_COMMAND_DESC)
        self.assertEqual(self.helloruri.message_medium.strip(), HELLORURI_MESSAGE_MEDIUM.strip())
        self.assertEqual(self.helloruri.message_large.strip(), HELLORURI_MESSAGE_LARGE.strip())
        self.assertEqual(self.helloruri.json_url, HELLORURI_JSON_URL)

    def test_probabilities(self):
        self.assertEqual(self.helloruri.ur_probability, self.ur_probability)
        self.assertEqual(self.helloruri.sr_probability, self.sr_probability)

    def test_initialization_with_none_probabilities(self):
        helloruri = HelloRuri(None, None)
        # Default values from GachaBase are used when None is passed
        self.assertEqual(helloruri.ur_probability, 0.03)
        self.assertEqual(helloruri.sr_probability, 0.18)

if __name__ == "__main__":
    unittest.main()
