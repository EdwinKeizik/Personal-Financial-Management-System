import unittest
from unittest.mock import patch, Mock, MagicMock

from website.ai_models.ai_functionality import build_prompt, get_ai_response
from website.ai_models.ai_functionality import LLM_MODEL_NAME, MAX_TOKENS


class TestAIFunctionality(unittest.TestCase):

    def setUp(self):
        self.sample_context = {
            'income_str': 'Salary: €3000',
            'expense_str': 'Rent: €1000, Food: €500',
            'planning_str': 'Vacation: €1000',
            'total_income': '3000.00',
            'total_expenses': '1500.00',
            'total_planning': '1000.00',
            'balance': '1500.00',
            'total_savings': '5000.00',
            'amount_to_cover_planning': (
                '0.00 You can cover all your planning expenses.'
            )
        }
        self.expected_financial_context_part = (
            "\n--- INCOME ---\n"
            "Salary: €3000\n\n"
            "--- EXPENSES ---\n"
            "Rent: €1000, Food: €500\n\n"
            "--- PLANNED EXPENSES ---\n"
            "Vacation: €1000\n\n"
            "--- SUMMARY ---\n"
            "Total Income: €3000.00\n"
            "Total Expenses: €1500.00\n"
            "Total Planned Expenses: €1000.00\n"
            "Balance (Income - Expenses): €1500.00\n"
            "Savings: €5000.00\n"
            "Extra amount needed to cover planned expenses: "
            "€0.00 You can cover all your planning expenses.\n"
        )

    def test_build_prompt_budget_analysis(self):
        prompt = build_prompt(self.sample_context, 'budget_analysis')
        self.assertIsInstance(prompt, str)
        self.assertIn("You are a financial advisor.", prompt)
        self.assertIn("Give a clear budget analysis", prompt)
        self.assertIn(self.expected_financial_context_part, prompt)
        self.assertIn(
            "Ask at the end if user want your help with budget planning",
            prompt
        )

    def test_build_prompt_planning_budget(self):
        prompt = build_prompt(self.sample_context, 'planning_budget')
        self.assertIsInstance(prompt, str)
        self.assertIn("You are a financial planner.", prompt)
        self.assertIn(
            "Allocate the user’s income into appropriate categories", prompt
        )
        self.assertIn(self.expected_financial_context_part, prompt)
        self.assertIn(
            "End by asking if they want to receive investment recommendations",
            prompt
        )

    def test_build_prompt_investment_recommendation(self):
        prompt = build_prompt(self.sample_context, 'investment_recommendation')
        self.assertIsInstance(prompt, str)
        self.assertIn("suggest smart and safe investment strategies.", prompt)
        self.assertIn(self.expected_financial_context_part, prompt)
        self.assertIn(
            "Recommend suitable low- and medium-risk investment options",
            prompt
        )
        self.assertIn(
            "End with a reminder that this is not professional financial advice",
            prompt
        )

    def test_build_prompt_custom_with_message(self):
        custom_msg = "How can I save more money?"
        prompt = build_prompt(self.sample_context, 'custom', custom_msg)
        self.assertIsInstance(prompt, str)
        self.assertIn("You are a financial assistant chatbot", prompt)
        self.assertIn(
            "ONLY respond to messages that are directly related to personal finance",
            prompt
        )
        self.assertIn(f"--- USER MESSAGE ---\n{custom_msg}", prompt)
        self.assertIn(self.expected_financial_context_part, prompt)

    def test_build_prompt_custom_no_message(self):
        prompt = build_prompt(self.sample_context, 'custom', None)
        self.assertIsNone(prompt)

    def test_build_prompt_invalid_type(self):
        prompt = build_prompt(self.sample_context, 'invalid_type')
        self.assertIsNone(prompt)

    def test_get_ai_response_success(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "AI success response."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        prompt_text = "Test prompt"
        response_content, error = get_ai_response(mock_client, prompt_text)

        self.assertEqual(response_content, "AI success response.")
        self.assertIsNone(error)
        mock_client.chat.completions.create.assert_called_once_with(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=MAX_TOKENS,
        )

    def test_get_ai_response_no_client(self):
        response_content, error = get_ai_response(None, "Test prompt")
        self.assertIsNone(response_content)
        self.assertEqual(error, "Missing AI client or prompt.")

    def test_get_ai_response_no_prompt(self):
        mock_client = Mock()
        response_content, error = get_ai_response(mock_client, None)
        self.assertIsNone(response_content)
        self.assertEqual(error, "Missing AI client or prompt.")

        response_content, error = get_ai_response(mock_client, "")
        self.assertIsNone(response_content)
        self.assertEqual(error, "Missing AI client or prompt.")

    def test_get_ai_response_no_choices(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        prompt_text = "Test prompt"
        response_content, error = get_ai_response(mock_client, prompt_text)

        self.assertIsNone(response_content)
        self.assertEqual(error, "AI returned no response.")
        mock_client.chat.completions.create.assert_called_once()

    @patch('builtins.print')
    def test_get_ai_response_exception(self, mock_print):
        mock_client = Mock()
        error_message = "API connection error"
        mock_client.chat.completions.create.side_effect = Exception(
            error_message
        )

        prompt_text = "Test prompt"
        response_content, error = get_ai_response(mock_client, prompt_text)

        self.assertIsNone(response_content)
        self.assertEqual(
            error, f"Failed to get response from AI: {error_message}"
        )
        mock_client.chat.completions.create.assert_called_once()
        mock_print.assert_called_once_with(
            f"ERROR: Exception during AI completion request: {error_message}"
        )


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)