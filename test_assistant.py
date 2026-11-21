import unittest
from unittest.mock import Mock, patch

import assistant
import web_app


class RequestAnswerTests(unittest.TestCase):
    @patch("assistant.requests.post")
    def test_sends_conversation_and_returns_text(self, post):
        response = Mock()
        response.json.return_value = {
            "content": [
                {"type": "text", "text": "Bonjour."},
                {"type": "text", "text": "Comment aider ?"},
            ]
        }
        post.return_value = response
        messages = [{"role": "user", "content": "Bonjour"}]

        answer = assistant.request_answer(
            messages, "test-key", "test-model", "system prompt"
        )

        self.assertEqual(answer, "Bonjour.\nComment aider ?")
        post.assert_called_once()
        self.assertEqual(post.call_args.kwargs["json"]["messages"], messages)
        self.assertEqual(post.call_args.kwargs["headers"]["x-api-key"], "test-key")

    @patch("assistant.requests.post")
    def test_rejects_response_without_text(self, post):
        response = Mock()
        response.json.return_value = {"content": [{"type": "tool_use"}]}
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "aucun texte"):
            assistant.request_answer([], "test-key", "test-model", "system prompt")


class WebAppTests(unittest.TestCase):
    def test_accepts_valid_multilingual_conversation_history(self):
        messages = [
            {"role": "user", "content": "Bonjour"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "¿Cómo funciona el presupuesto?"},
        ]

        self.assertTrue(web_app.valid_messages(messages))

    def test_rejects_conversation_that_does_not_end_with_user(self):
        messages = [
            {"role": "user", "content": "Bonjour"},
            {"role": "assistant", "content": "Bonjour !"},
        ]

        self.assertFalse(web_app.valid_messages(messages))

    def test_prompt_requests_replies_in_the_users_language(self):
        prompt = assistant.load_system_prompt()

        self.assertIn("dans la langue utilisée", prompt)
        self.assertIn("stock", prompt.lower())


if __name__ == "__main__":
    unittest.main()
