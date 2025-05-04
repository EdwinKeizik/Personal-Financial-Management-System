import unittest
from unittest.mock import patch, Mock, MagicMock
import datetime

from website.ai_models.user_finances import get_user_financial_context

PATCH_TARGET_INCOME = 'website.ai_models.user_finances.Income'
PATCH_TARGET_EXPENSES = 'website.ai_models.user_finances.Expenses'
PATCH_TARGET_PLANNING = 'website.ai_models.user_finances.Planning'
PATCH_TARGET_GET_REPORT = 'website.ai_models.user_finances.get_report_data'
PATCH_TARGET_FLASH = 'website.ai_models.user_finances.flash'
PATCH_TARGET_PRINT = 'builtins.print'


class MockRecord:
    def __init__(self, name, amount, date_str, type_str):
        self.name = name
        self.amount = amount
        self.date = (
            datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if date_str else None
        )
        self.type = type_str


class TestUserFinances(unittest.TestCase):

    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_GET_REPORT)
    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_get_user_financial_context_success(
        self, mock_income, mock_expenses, mock_planning,
        mock_get_report, mock_flash, mock_print
    ):
        user_id_to_test = 42

        mock_incomes_list = [
            MockRecord("Salary", 3000, "2025-05-01", "Monthly"),
            MockRecord("Bonus", 500, "2025-04-15", "One-time")
        ]
        mock_expenses_list = [
            MockRecord("Rent", 1200, "2025-05-01", "Housing"),
            MockRecord("Food", 450, "2025-05-03", "Groceries")
        ]
        mock_planning_list = [
            MockRecord("Vacation", 1500, "2025-08-01", None),
            MockRecord("New Phone", 800, "2025-06-10", None)
        ]
        mock_report_dict = {
            'total_income': 3500.00,
            'total_expenses': 1650.00,
            'total_planning': 2300.00,
            'balance': 1500.00,
            'total_savings': 5000.00,
            'amount_to_cover_planning': 800.00
        }

        mock_income.query.filter_by.return_value.all.return_value = (
            mock_incomes_list
        )
        mock_expenses.query.filter_by.return_value.all.return_value = (
            mock_expenses_list
        )
        mock_planning.query.filter_by.return_value.all.return_value = (
            mock_planning_list
        )
        mock_get_report.return_value = mock_report_dict

        expected_income_str = (
            "- Salary: €3000 on 2025-05-01 (Monthly)\n"
            "- Bonus: €500 on 2025-04-15 (One-time)"
        )
        expected_expense_str = (
            "- Rent: €1200 on 2025-05-01 (Housing)\n"
            "- Food: €450 on 2025-05-03 (Groceries)"
        )
        expected_planning_str = (
            "- Vacation: €1500 planned on 2025-08-01\n"
            "- New Phone: €800 planned on 2025-06-10"
        )

        expected_result = {
            "income_str": expected_income_str,
            "expense_str": expected_expense_str,
            "planning_str": expected_planning_str,
            "total_income": 3500.00,
            "total_expenses": 1650.00,
            "total_planning": 2300.00,
            "balance": 1500.00,
            "total_savings": 5000.00,
            "amount_to_cover_planning": 800.00
        }

        result = get_user_financial_context(user_id_to_test)

        mock_income.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_expenses.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_planning.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_income.query.filter_by.return_value.all.assert_called_once()
        mock_expenses.query.filter_by.return_value.all.assert_called_once()
        mock_planning.query.filter_by.return_value.all.assert_called_once()
        mock_get_report.assert_called_once()

        self.assertDictEqual(result, expected_result)
        mock_flash.assert_not_called()
        mock_print.assert_not_called()

    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_GET_REPORT)
    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_get_user_financial_context_db_exception(
        self, mock_income, mock_expenses, mock_planning,
        mock_get_report, mock_flash, mock_print
    ):
        user_id_to_test = 43
        error_message = "Database connection failed"
        mock_income.query.filter_by.side_effect = Exception(error_message)

        result = get_user_financial_context(user_id_to_test)

        self.assertIsNone(result)
        mock_income.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_expenses.query.filter_by.assert_not_called()
        mock_planning.query.filter_by.assert_not_called()
        mock_get_report.assert_not_called()

        mock_print.assert_called_once_with(
            f"ERROR: Failed to get financial context for user "
            f"{user_id_to_test}: {error_message}"
        )
        mock_flash.assert_called_once_with(
            "Could not retrieve your financial data.", "danger"
        )

    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_GET_REPORT)
    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_get_user_financial_context_report_exception(
        self, mock_income, mock_expenses, mock_planning,
        mock_get_report, mock_flash, mock_print
    ):
        user_id_to_test = 44
        error_message = "Calculation error in report"

        mock_income.query.filter_by.return_value.all.return_value = []
        mock_expenses.query.filter_by.return_value.all.return_value = []
        mock_planning.query.filter_by.return_value.all.return_value = []
        mock_get_report.side_effect = Exception(error_message)

        result = get_user_financial_context(user_id_to_test)

        self.assertIsNone(result)
        mock_income.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_expenses.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_planning.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_get_report.assert_called_once()

        mock_print.assert_called_once_with(
            f"ERROR: Failed to get financial context for user "
            f"{user_id_to_test}: {error_message}"
        )
        mock_flash.assert_called_once_with(
            "Could not retrieve your financial data.", "danger"
        )

    @patch(PATCH_TARGET_PRINT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_GET_REPORT)
    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_get_user_financial_context_no_data(
        self, mock_income, mock_expenses, mock_planning,
        mock_get_report, mock_flash, mock_print
    ):
        user_id_to_test = 45

        mock_income.query.filter_by.return_value.all.return_value = []
        mock_expenses.query.filter_by.return_value.all.return_value = []
        mock_planning.query.filter_by.return_value.all.return_value = []
        mock_report_dict = {
            'total_income': 0,
            'total_expenses': 0,
            'total_planning': 0,
            'balance': 0,
            'total_savings': 0,
            'amount_to_cover_planning': 0
        }
        mock_get_report.return_value = mock_report_dict

        expected_result = {
            "income_str": "",
            "expense_str": "",
            "planning_str": "",
            "total_income": 0,
            "total_expenses": 0,
            "total_planning": 0,
            "balance": 0,
            "total_savings": 0,
            "amount_to_cover_planning": 0
        }

        result = get_user_financial_context(user_id_to_test)

        self.assertDictEqual(result, expected_result)
        mock_flash.assert_not_called()
        mock_print.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)