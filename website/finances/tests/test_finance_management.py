import unittest
from unittest.mock import patch, Mock
import datetime

from website.finances.finance_management import Income, Expenses, Planning

PATCH_TARGET_FLASH = 'website.finances.finance_management.flash'
PATCH_TARGET_DATETIME = 'website.finances.finance_management.datetime'

MOCKED_CURRENT_DATE = datetime.date(2025, 5, 4)


class TestIncome(unittest.TestCase):

    def setUp(self):
        self.patcher_dt = patch(PATCH_TARGET_DATETIME)
        self.mock_dt = self.patcher_dt.start()
        self.mock_dt.now.return_value.date.return_value = MOCKED_CURRENT_DATE
        self.mock_dt.strptime = datetime.datetime.strptime
        self.patcher_flash = patch(PATCH_TARGET_FLASH)
        self.mock_flash = self.patcher_flash.start()
        self.addCleanup(self.patcher_dt.stop)
        self.addCleanup(self.patcher_flash.stop)

    def test_income_init(self):
        date_obj = MOCKED_CURRENT_DATE
        income = Income(
            amount=100, name="Salary", date=date_obj, type="Monthly",
            user_id=1
        )
        self.assertEqual(income.amount, 100)
        self.assertEqual(income.name, "Salary")
        self.assertEqual(income.date, date_obj)
        self.assertEqual(income.type, "Monthly")
        self.assertEqual(income.user_id, 1)

    def test_check_input_valid(self):
        income = Income(
            amount="150.75", name="Bonus", date="2025-05-01", type="One-time",
            user_id=1
        )
        self.assertTrue(income.check_input())
        self.assertEqual(income.amount, 150.75)
        self.assertEqual(income.date, datetime.date(2025, 5, 1))
        self.mock_flash.assert_not_called()

    def test_check_input_amount_empty(self):
        income = Income(
            amount="", name="Bonus", date="2025-05-01", type="One-time",
            user_id=1
        )
        self.assertFalse(income.check_input())
        self.mock_flash.assert_called_once_with(
            'Amount cannot be empty', 'error'
        )

    def test_check_input_amount_invalid_str(self):
        income = Income(
            amount="abc", name="Bonus", date="2025-05-01", type="One-time",
            user_id=1
        )
        self.assertFalse(income.check_input())
        self.mock_flash.assert_called_once_with(
            'Amount must be a valid number', 'error'
        )

    def test_check_input_amount_zero(self):
        income = Income(
            amount="0", name="Bonus", date="2025-05-01", type="One-time",
            user_id=1
        )
        self.assertFalse(income.check_input())
        self.mock_flash.assert_called_once_with(
            'Amount must be greater than 0', 'error'
        )

    def test_check_input_amount_negative(self):
        income = Income(
            amount="-50", name="Bonus", date="2025-05-01", type="One-time",
            user_id=1
        )
        self.assertFalse(income.check_input())
        self.mock_flash.assert_called_once_with(
            'Amount must be greater than 0', 'error'
        )

    def test_check_input_name_empty(self):
        income = Income(
            amount="100", name="", date="2025-05-01", type="One-time",
            user_id=1
        )
        self.assertFalse(income.check_input())
        self.mock_flash.assert_called_once_with('Name cannot be empty', 'error')

    def test_check_input_name_too_short(self):
        income = Income(
            amount="100", name="Bo", date="2025-05-01", type="One-time",
            user_id=1
        )
        self.assertFalse(income.check_input())
        self.mock_flash.assert_called_once_with(
            'Name must be at least 3 characters long', 'error'
        )

    def test_check_date_valid_past(self):
        income = Income(
            amount="100", name="Salary", date="2025-04-30", type="Monthly",
            user_id=1
        )
        self.assertTrue(income.check_date())
        self.assertEqual(income.date, datetime.date(2025, 4, 30))
        self.mock_flash.assert_not_called()

    def test_check_date_valid_today(self):
        income = Income(
            amount="100", name="Salary", date="2025-05-04", type="Monthly",
            user_id=1
        )
        self.assertTrue(income.check_date())
        self.assertEqual(income.date, datetime.date(2025, 5, 4))
        self.mock_flash.assert_not_called()

    def test_check_date_valid_date_object(self):
        date_obj = datetime.date(2025, 5, 1)
        income = Income(
            amount="100", name="Salary", date=date_obj, type="Monthly",
            user_id=1
        )
        self.assertTrue(income.check_date())
        self.assertEqual(income.date, date_obj)
        self.mock_flash.assert_not_called()

    def test_check_date_empty(self):
        income = Income(
            amount="100", name="Salary", date="", type="Monthly", user_id=1
        )
        self.assertFalse(income.check_date())
        self.mock_flash.assert_called_once_with(
            'Date cannot be empty', 'error'
        )

    def test_check_date_invalid_format(self):
        income = Income(
            amount="100", name="Salary", date="04-05-2025", type="Monthly",
            user_id=1
        )
        self.assertFalse(income.check_date())
        self.mock_flash.assert_called_once_with(
            'Invalid date format. Please use YYYY-MM-DD.', 'error'
        )

    def test_check_date_future(self):
        income = Income(
            amount="100", name="Salary", date="2025-05-05", type="Monthly",
            user_id=1
        )
        self.assertFalse(income.check_date())
        self.mock_flash.assert_called_once_with(
            'Date cannot be in the future', 'error'
        )

    def test_check_input_calls_check_date_fail(self):
        income = Income(
            amount="100", name="Salary", date="2025-05-05", type="Monthly",
            user_id=1
        )
        self.assertFalse(income.check_input())
        self.mock_flash.assert_called_once_with(
            'Date cannot be in the future', 'error'
        )


class TestExpenses(unittest.TestCase):

    def setUp(self):
        self.patcher_dt = patch(PATCH_TARGET_DATETIME)
        self.mock_dt = self.patcher_dt.start()
        self.mock_dt.now.return_value.date.return_value = MOCKED_CURRENT_DATE
        self.mock_dt.strptime = datetime.datetime.strptime
        self.patcher_flash = patch(PATCH_TARGET_FLASH)
        self.mock_flash = self.patcher_flash.start()
        self.addCleanup(self.patcher_dt.stop)
        self.addCleanup(self.patcher_flash.stop)

    def test_expense_check_input_valid(self):
        expense = Expenses(
            amount="50.25", name="Groceries", date="2025-05-03", type="Food",
            user_id=1
        )
        self.assertTrue(expense.check_input())
        self.assertEqual(expense.amount, 50.25)
        self.assertEqual(expense.date, datetime.date(2025, 5, 3))
        self.mock_flash.assert_not_called()

    def test_expense_check_input_future_date(self):
        expense = Expenses(
            amount="50", name="Groceries", date="2025-05-05", type="Food",
            user_id=1
        )
        self.assertFalse(expense.check_input())
        self.mock_flash.assert_called_once_with(
            'Date cannot be in the future', 'error'
        )

    def test_expense_check_input_invalid_amount(self):
        expense = Expenses(
            amount="-10", name="Groceries", date="2025-05-03", type="Food",
            user_id=1
        )
        self.assertFalse(expense.check_input())
        self.mock_flash.assert_called_once_with(
            'Amount must be greater than 0', 'error'
        )

    def test_expense_check_input_invalid_name(self):
        expense = Expenses(
            amount="50", name="Gr", date="2025-05-03", type="Food", user_id=1
        )
        self.assertFalse(expense.check_input())
        self.mock_flash.assert_called_once_with(
            'Name must be at least 3 characters long', 'error'
        )


class TestPlanning(unittest.TestCase):

    def setUp(self):
        self.patcher_dt = patch(PATCH_TARGET_DATETIME)
        self.mock_dt = self.patcher_dt.start()
        self.mock_dt.now.return_value.date.return_value = MOCKED_CURRENT_DATE
        self.mock_dt.strptime = datetime.datetime.strptime
        self.patcher_flash = patch(PATCH_TARGET_FLASH)
        self.mock_flash = self.patcher_flash.start()
        self.addCleanup(self.patcher_dt.stop)
        self.addCleanup(self.patcher_flash.stop)

    def test_check_date_valid_future(self):
        planning = Planning(
            amount="200", name="Vacation", date="2025-06-01", type="Travel",
            user_id=1
        )
        self.assertTrue(planning.check_date())
        self.assertEqual(planning.date, datetime.date(2025, 6, 1))
        self.mock_flash.assert_not_called()

    def test_check_date_valid_today(self):
        planning = Planning(
            amount="200", name="Concert", date="2025-05-04",
            type="Entertainment", user_id=1
        )
        self.assertTrue(planning.check_date())
        self.assertEqual(planning.date, datetime.date(2025, 5, 4))
        self.mock_flash.assert_not_called()

    def test_check_date_valid_date_object(self):
        date_obj = datetime.date(2025, 5, 10)
        planning = Planning(
            amount="200", name="Gift", date=date_obj, type="Misc", user_id=1
        )
        self.assertTrue(planning.check_date())
        self.assertEqual(planning.date, date_obj)
        self.mock_flash.assert_not_called()

    def test_check_date_empty(self):
        planning = Planning(
            amount="200", name="Vacation", date="", type="Travel", user_id=1
        )
        self.assertFalse(planning.check_date())
        self.mock_flash.assert_called_once_with(
            'Date cannot be empty', 'error'
        )

    def test_check_date_invalid_format(self):
        planning = Planning(
            amount="200", name="Vacation", date="01/06/2025", type="Travel",
            user_id=1
        )
        self.assertFalse(planning.check_date())
        self.mock_flash.assert_called_once_with(
            'Invalid date format. Please use YYYY-MM-DD.', 'error'
        )

    def test_check_date_past(self):
        planning = Planning(
            amount="200", name="Vacation", date="2025-05-03", type="Travel",
            user_id=1
        )
        self.assertFalse(planning.check_date())
        self.mock_flash.assert_called_once_with(
            'Date cannot be in the past', 'error'
        )

    def test_check_input_valid(self):
        planning = Planning(
            amount="500", name="New Laptop", date="2025-07-15",
            type="Electronics", user_id=1
        )
        self.assertTrue(planning.check_input())
        self.assertEqual(planning.amount, 500.0)
        self.assertEqual(planning.date, datetime.date(2025, 7, 15))
        self.mock_flash.assert_not_called()

    def test_check_input_past_date(self):
        planning = Planning(
            amount="500", name="New Laptop", date="2025-04-15",
            type="Electronics", user_id=1
        )
        self.assertFalse(planning.check_input())
        self.mock_flash.assert_called_once_with(
            'Date cannot be in the past', 'error'
        )

    def test_check_input_invalid_amount(self):
        planning = Planning(
            amount="-50", name="New Laptop", date="2025-07-15",
            type="Electronics", user_id=1
        )
        self.assertFalse(planning.check_input())
        self.mock_flash.assert_called_once_with(
            'Amount must be greater than 0', 'error'
        )

    def test_check_input_invalid_name(self):
        planning = Planning(
            amount="500", name="La", date="2025-07-15", type="Electronics",
            user_id=1
        )
        self.assertFalse(planning.check_input())
        self.mock_flash.assert_called_once_with(
            'Name must be at least 3 characters long', 'error'
        )


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)