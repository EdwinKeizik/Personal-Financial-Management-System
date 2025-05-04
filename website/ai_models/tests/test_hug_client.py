import unittest
from unittest.mock import patch, Mock
import os

from website.ai_models.hug_client import get_huggingface_client, LLM_PROVIDER

PATCH_TARGET_INFERENCE_CLIENT = 'website.ai_models.hug_client.InferenceClient'
PATCH_TARGET_FLASH = 'website.ai_models.hug_client.flash'
PATCH_TARGET_PRINT = 'builtins.print'
PATCH_TARGET_OS_GETENV = 'website.ai_models.hug_client.os.getenv'


class TestHugClient(unittest.TestCase):

    @patch(PATCH_TARGET_OS_GETENV)
    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_INFERENCE_CLIENT)
    def test_get_huggingface_client_success(
        self, MockInferenceClient, mock_flash, mock_print, mock_getenv
    ):
        dummy_api_key = "dummy_hf_key_12345"
        mock_getenv.return_value = dummy_api_key
        mock_client_instance = Mock()
        MockInferenceClient.return_value = mock_client_instance

        client = get_huggingface_client()

        mock_getenv.assert_called_once_with("HUGGINGFACE_API_KEY")
        MockInferenceClient.assert_called_once_with(
            provider=LLM_PROVIDER,
            api_key=dummy_api_key
        )
        self.assertEqual(client, mock_client_instance)
        mock_flash.assert_not_called()
        mock_print.assert_not_called()

    @patch(PATCH_TARGET_OS_GETENV)
    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_INFERENCE_CLIENT)
    def test_get_huggingface_client_instantiation_exception(
        self, MockInferenceClient, mock_flash, mock_print, mock_getenv
    ):
        dummy_api_key = "dummy_hf_key_12345"
        mock_getenv.return_value = dummy_api_key
        error_message = "Connection timed out"
        MockInferenceClient.side_effect = Exception(error_message)

        client = get_huggingface_client()

        mock_getenv.assert_called_once_with("HUGGINGFACE_API_KEY")
        MockInferenceClient.assert_called_once_with(
            provider=LLM_PROVIDER,
            api_key=dummy_api_key
        )
        self.assertIsNone(client)
        mock_print.assert_called_once_with(
            f"ERROR: Failed to create InferenceClient: {error_message}"
        )
        mock_flash.assert_called_once_with(
            f"AI service connection error: {error_message}", "danger"
        )

    @patch(PATCH_TARGET_OS_GETENV)
    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_INFERENCE_CLIENT)
    def test_get_huggingface_client_no_api_key(
        self, MockInferenceClient, mock_flash, mock_print, mock_getenv
    ):
        mock_getenv.return_value = None

        client = get_huggingface_client()

        mock_getenv.assert_called_once_with("HUGGINGFACE_API_KEY")
        self.assertIsNone(client)
        mock_print.assert_called_once_with(
            "ERROR: HUGGINGFACE_API_KEY environment variable not set."
        )
        mock_flash.assert_called_once_with(
            "AI service is not configured correctly (Missing API Key).", "danger"
        )
        MockInferenceClient.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)