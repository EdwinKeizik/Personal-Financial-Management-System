import unittest
from unittest.mock import patch, Mock, MagicMock
from flask import Flask

from website.ai import _save_chat_message, home

PATCH_TARGET_DB = 'website.ai.db'
PATCH_TARGET_CHAT_MODEL = 'website.ai.ChatAI'
PATCH_TARGET_PRINT = 'builtins.print'
PATCH_TARGET_FLASH = 'website.ai.flash'
PATCH_TARGET_RENDER = 'website.ai.render_template'
PATCH_TARGET_REQUEST = 'website.ai.request'
PATCH_TARGET_REDIRECT = 'website.ai.redirect'
PATCH_TARGET_URL_FOR = 'website.ai.url_for'
PATCH_TARGET_CURRENT_USER = 'website.ai.current_user'
PATCH_TARGET_GET_CONTEXT = 'website.ai.get_user_financial_context'
PATCH_TARGET_BUILD_PROMPT = 'website.ai.build_prompt'
PATCH_TARGET_GET_RESPONSE = 'website.ai.get_ai_response'
PATCH_TARGET_GET_CLIENT = 'website.ai.get_huggingface_client'
PATCH_TARGET_SAVE_MSG = 'website.ai._save_chat_message'
PATCH_TARGET_LOGIN_REQ = 'website.ai.login_required'

class TestAISaveMessage(unittest.TestCase):

    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_CHAT_MODEL)
    def test_save_chat_message_success(self, MockChatAI, mock_db, mock_print):
        user_id = 1
        message = "User message"
        response = "AI response"
        mock_chat_instance = Mock()
        MockChatAI.return_value = mock_chat_instance
        saved, error = _save_chat_message(user_id, message, response)
        self.assertTrue(saved)
        self.assertIsNone(error)
        MockChatAI.assert_called_once_with(user_id=user_id, message=message, response=response)
        mock_db.session.add.assert_called_once_with(mock_chat_instance)
        mock_db.session.commit.assert_called_once()
        mock_db.session.rollback.assert_not_called()
        mock_print.assert_not_called()

    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_CHAT_MODEL)
    def test_save_chat_message_db_exception(self, MockChatAI, mock_db, mock_print):
        user_id = 2
        message = "User message 2"
        response = "AI response 2"
        mock_chat_instance = Mock()
        MockChatAI.return_value = mock_chat_instance
        error_msg = "DB connection lost"
        mock_db.session.commit.side_effect = Exception(error_msg)
        saved, error = _save_chat_message(user_id, message, response)
        self.assertFalse(saved)
        self.assertEqual(error, f"Database error saving chat: {error_msg}")
        MockChatAI.assert_called_once_with(user_id=user_id, message=message, response=response)
        mock_db.session.add.assert_called_once_with(mock_chat_instance)
        mock_db.session.commit.assert_called_once()
        mock_db.session.rollback.assert_called_once()
        mock_print.assert_called_once_with(f"ERROR: Failed to save chat message for user {user_id}: {error_msg}")


class TestAIHomeView(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testing'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.req_context = self.app.test_request_context()
        self.req_context.push()
        self.mock_user_instance = Mock(id=101)
        self.patcher_current_user = patch(PATCH_TARGET_CURRENT_USER, self.mock_user_instance)
        self.mock_current_user_proxy = self.patcher_current_user.start()
        self.addCleanup(self.req_context.pop)
        self.addCleanup(self.app_context.pop)
        self.addCleanup(self.patcher_current_user.stop)

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_CHAT_MODEL)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_get(self, mock_request, mock_render, MockChatAI, mock_login_req): # Check this line
        mock_request.method = 'GET'
        mock_chats = [Mock(), Mock()]
        MockChatAI.query.filter_by.return_value.all.return_value = mock_chats
        mock_render.return_value = "Rendered HTML"
        response = home()
        MockChatAI.query.filter_by.assert_called_once_with(user_id=self.mock_user_instance.id)
        MockChatAI.query.filter_by.return_value.all.assert_called_once()
        mock_render.assert_called_once_with('ai.html', chats=mock_chats, user=self.mock_current_user_proxy)
        self.assertEqual(response, "Rendered HTML")

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_CHAT_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_new_chat_success(self, mock_request, MockChatAI, mock_db, mock_flash, mock_redirect, mock_url_for, mock_login_req): # Check this line
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'new_chat'
        mock_url_for.return_value = "/fake/ai/home"
        mock_redirect.return_value = "Redirect Response"
        mock_delete_query = Mock()
        MockChatAI.query.filter_by.return_value = mock_delete_query
        response = home()
        mock_request.form.get.assert_called_once_with('submit')
        MockChatAI.query.filter_by.assert_called_once_with(user_id=self.mock_user_instance.id)
        mock_delete_query.delete.assert_called_once()
        mock_db.session.commit.assert_called_once()
        mock_db.session.rollback.assert_not_called()
        mock_flash.assert_called_once_with('New chat started! Previous messages cleared.', 'success')
        mock_url_for.assert_called_once_with('ai.home')
        mock_redirect.assert_called_once_with('/fake/ai/home')
        self.assertEqual(response, "Redirect Response")

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_CHAT_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_new_chat_exception(self, mock_request, MockChatAI, mock_db, mock_flash, mock_redirect, mock_url_for, mock_print, mock_login_req): # Check this line
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'new_chat'
        mock_url_for.return_value = "/fake/ai/home"
        mock_redirect.return_value = "Redirect Response"
        error_msg = "Delete failed"
        mock_delete_query = Mock()
        mock_delete_query.delete.side_effect = Exception(error_msg)
        MockChatAI.query.filter_by.return_value = mock_delete_query
        response = home()
        mock_request.form.get.assert_called_once_with('submit')
        MockChatAI.query.filter_by.assert_called_once_with(user_id=self.mock_user_instance.id)
        mock_delete_query.delete.assert_called_once()
        mock_db.session.commit.assert_not_called()
        mock_db.session.rollback.assert_called_once()
        mock_print.assert_called_once_with(f"ERROR: Failed deleting chat history for user {self.mock_user_instance.id}: {error_msg}")
        mock_flash.assert_called_once_with('Error clearing chat history.', 'danger')
        mock_url_for.assert_called_once_with('ai.home')
        mock_redirect.assert_called_once_with('/fake/ai/home')
        self.assertEqual(response, "Redirect Response")

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_GET_CONTEXT)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_context_fails(self, mock_request, mock_get_context, mock_redirect, mock_url_for, mock_login_req): # Check this line
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'budget_analysis'
        mock_get_context.return_value = None
        mock_url_for.return_value = "/fake/ai/home"
        mock_redirect.return_value = "Redirect Response"
        response = home()
        mock_request.form.get.assert_called_once_with('submit')
        mock_get_context.assert_called_once_with(self.mock_user_instance.id)
        mock_url_for.assert_called_once_with('ai.home')
        mock_redirect.assert_called_once_with('/fake/ai/home')
        self.assertEqual(response, "Redirect Response")

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_CHAT_MODEL)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_BUILD_PROMPT)
    @patch(PATCH_TARGET_GET_CONTEXT)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_invalid_action(self, mock_request, mock_get_context, mock_build_prompt, mock_flash, MockChatAI, mock_render, mock_login_req): # Check this line
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'invalid_action'
        mock_get_context.return_value = {'some': 'context'}
        mock_chats = [Mock()]
        MockChatAI.query.filter_by.return_value.all.return_value = mock_chats
        mock_render.return_value = "Rendered HTML"
        response = home()
        mock_request.form.get.assert_called_once_with('submit')
        mock_get_context.assert_called_once_with(self.mock_user_instance.id)
        mock_build_prompt.assert_not_called()
        mock_flash.assert_called_once_with('Invalid action selected.', 'danger')
        MockChatAI.query.filter_by.assert_called_once_with(user_id=self.mock_user_instance.id)
        mock_render.assert_called_once_with('ai.html', chats=mock_chats, user=self.mock_current_user_proxy)
        self.assertEqual(response, "Rendered HTML")


    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_CHAT_MODEL)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_BUILD_PROMPT)
    @patch(PATCH_TARGET_GET_CONTEXT)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_custom_empty_text(self, mock_request, mock_get_context, mock_build_prompt, mock_flash, MockChatAI, mock_render, mock_login_req): # Check this line
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.side_effect = lambda key, default='': {'submit': 'custom', 'customRequestText': '  '}.get(key, default)
        mock_get_context.return_value = {'some': 'context'}
        mock_chats = [Mock()]
        MockChatAI.query.filter_by.return_value.all.return_value = mock_chats
        mock_render.return_value = "Rendered HTML"
        response = home()
        self.assertEqual(mock_request.form.get.call_count, 2)
        mock_request.form.get.assert_any_call('submit')
        mock_request.form.get.assert_any_call('customRequestText', '')
        mock_get_context.assert_called_once_with(self.mock_user_instance.id)
        mock_build_prompt.assert_not_called()
        mock_flash.assert_called_once_with('Please enter your custom request message.', 'warning')
        MockChatAI.query.filter_by.assert_called_once_with(user_id=self.mock_user_instance.id)
        mock_render.assert_called_once_with('ai.html', chats=mock_chats, user=self.mock_current_user_proxy)
        self.assertEqual(response, "Rendered HTML")

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_SAVE_MSG)
    @patch(PATCH_TARGET_GET_RESPONSE)
    @patch(PATCH_TARGET_GET_CLIENT)
    @patch(PATCH_TARGET_BUILD_PROMPT)
    @patch(PATCH_TARGET_GET_CONTEXT)
    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_budget_analysis_full_success(
        self, mock_request, mock_flash, mock_redirect, mock_url_for,
        mock_get_context, mock_build_prompt, mock_get_client, mock_get_response, mock_save_msg, mock_login_req): # Check this line

        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'budget_analysis'
        mock_url_for.return_value = "/fake/ai/home"
        mock_redirect.return_value = "Redirect Response"
        mock_context = {'fake': 'context'}
        mock_get_context.return_value = mock_context
        mock_prompt = "Generated budget prompt"
        mock_build_prompt.return_value = mock_prompt
        mock_client_instance = Mock()
        mock_get_client.return_value = mock_client_instance
        mock_ai_response_content = "Budget analysis result"
        mock_get_response.return_value = (mock_ai_response_content, None)
        mock_save_msg.return_value = (True, None)

        response = home()

        mock_request.form.get.assert_called_once_with('submit')
        mock_get_context.assert_called_once_with(self.mock_user_instance.id)
        mock_build_prompt.assert_called_once_with(mock_context, 'budget_analysis')
        mock_get_client.assert_called_once()
        mock_get_response.assert_called_once_with(mock_client_instance, mock_prompt)
        expected_user_msg = "Generate budget analysis"
        mock_save_msg.assert_called_once_with(self.mock_user_instance.id, expected_user_msg, mock_ai_response_content)
        mock_flash.assert_called_once_with("Budget analysis generated!", 'success')
        mock_url_for.assert_called_once_with('ai.home')
        mock_redirect.assert_called_once_with('/fake/ai/home')
        self.assertEqual(response, "Redirect Response")


    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_SAVE_MSG)
    @patch(PATCH_TARGET_GET_RESPONSE)
    @patch(PATCH_TARGET_GET_CLIENT)
    @patch(PATCH_TARGET_BUILD_PROMPT)
    @patch(PATCH_TARGET_GET_CONTEXT)
    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_custom_full_success(
        self, mock_request, mock_flash, mock_redirect, mock_url_for,
        mock_get_context, mock_build_prompt, mock_get_client, mock_get_response, mock_save_msg, mock_login_req): # Check this line

        custom_text = "How to invest?"
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.side_effect = lambda key, default='': {'submit': 'custom', 'customRequestText': custom_text}.get(key, default)
        mock_url_for.return_value = "/fake/ai/home"
        mock_redirect.return_value = "Redirect Response"
        mock_context = {'fake': 'context'}
        mock_get_context.return_value = mock_context
        mock_prompt = "Generated custom prompt"
        mock_build_prompt.return_value = mock_prompt
        mock_client_instance = Mock()
        mock_get_client.return_value = mock_client_instance
        mock_ai_response_content = "Investment advice result"
        mock_get_response.return_value = (mock_ai_response_content, None)
        mock_save_msg.return_value = (True, None)

        response = home()

        mock_get_context.assert_called_once_with(self.mock_user_instance.id)
        mock_build_prompt.assert_called_once_with(mock_context, 'custom', custom_message=custom_text)
        mock_get_client.assert_called_once()
        mock_get_response.assert_called_once_with(mock_client_instance, mock_prompt)
        mock_save_msg.assert_called_once_with(self.mock_user_instance.id, custom_text, mock_ai_response_content)
        mock_flash.assert_called_once_with("Response to your custom request generated!", 'success')
        mock_url_for.assert_called_once_with('ai.home')
        mock_redirect.assert_called_once_with('/fake/ai/home')
        self.assertEqual(response, "Redirect Response")


    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_SAVE_MSG)
    @patch(PATCH_TARGET_GET_RESPONSE)
    @patch(PATCH_TARGET_GET_CLIENT)
    @patch(PATCH_TARGET_BUILD_PROMPT)
    @patch(PATCH_TARGET_GET_CONTEXT)
    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_get_ai_response_fails(
        self, mock_request, mock_flash, mock_redirect, mock_url_for,
        mock_get_context, mock_build_prompt, mock_get_client, mock_get_response, mock_save_msg, mock_login_req): # Check this line

        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'planning_budget'
        mock_url_for.return_value = "/fake/ai/home"
        mock_redirect.return_value = "Redirect Response"
        mock_get_context.return_value = {'fake': 'context'}
        mock_build_prompt.return_value = "Generated planning prompt"
        mock_get_client.return_value = Mock()
        ai_error_msg = "Rate limit exceeded"
        mock_get_response.return_value = (None, ai_error_msg)

        response = home()

        mock_get_response.assert_called_once()
        mock_save_msg.assert_not_called()
        mock_flash.assert_called_once_with(f"AI Error: {ai_error_msg}", "danger")
        mock_url_for.assert_called_once_with('ai.home')
        mock_redirect.assert_called_once_with('/fake/ai/home')
        self.assertEqual(response, "Redirect Response")


    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_SAVE_MSG)
    @patch(PATCH_TARGET_GET_RESPONSE)
    @patch(PATCH_TARGET_GET_CLIENT)
    @patch(PATCH_TARGET_BUILD_PROMPT)
    @patch(PATCH_TARGET_GET_CONTEXT)
    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_save_message_fails(
        self, mock_request, mock_flash, mock_redirect, mock_url_for,
        mock_get_context, mock_build_prompt, mock_get_client, mock_get_response, mock_save_msg, mock_login_req): # Check this line

        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'investment_recommendation'
        mock_url_for.return_value = "/fake/ai/home"
        mock_redirect.return_value = "Redirect Response"
        mock_get_context.return_value = {'fake': 'context'}
        mock_build_prompt.return_value = "Generated investment prompt"
        mock_get_client.return_value = Mock()
        mock_ai_response_content = "Investment result"
        mock_get_response.return_value = (mock_ai_response_content, None)
        db_error_msg = "DB unique constraint failed"
        mock_save_msg.return_value = (False, db_error_msg)

        response = home()

        mock_get_response.assert_called_once()
        mock_save_msg.assert_called_once()
        mock_flash.assert_called_once_with(f"AI response received, but failed to save: {db_error_msg}", 'danger')
        mock_url_for.assert_called_once_with('ai.home')
        mock_redirect.assert_called_once_with('/fake/ai/home')
        self.assertEqual(response, "Redirect Response")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)