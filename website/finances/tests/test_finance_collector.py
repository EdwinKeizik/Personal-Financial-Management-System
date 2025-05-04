import unittest
from unittest.mock import patch, Mock

from website.finances.finance_collector import Savings, Transfer, Withdraw

PATCH_TARGET_FLASH = 'website.finances.finance_collector.flash'


class TestSavings(unittest.TestCase):

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_valid_string_number(self, mock_flash):
        saving = Savings(amount="100.50", user_id=1)
        result = saving.check_input()
        self.assertTrue(result)
        self.assertEqual(saving.amount, 100.50)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_valid_float_number(self, mock_flash):
        saving = Savings(amount=50.0, user_id=1)
        result = saving.check_input()
        self.assertTrue(result)
        self.assertEqual(saving.amount, 50.0)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_valid_integer_number(self, mock_flash):
        saving = Savings(amount=75, user_id=1)
        result = saving.check_input()
        self.assertTrue(result)
        self.assertEqual(saving.amount, 75.0)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_empty_string(self, mock_flash):
        saving = Savings(amount="", user_id=1)
        result = saving.check_input()
        self.assertFalse(result)
        mock_flash.assert_called_once_with('Amount cannot be empty', 'error')

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_whitespace_string(self, mock_flash):
        saving = Savings(amount="   ", user_id=1)
        result = saving.check_input()
        self.assertFalse(result)
        mock_flash.assert_called_once_with('Amount cannot be empty', 'error')

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_none(self, mock_flash):
        saving = Savings(amount=None, user_id=1)
        result = saving.check_input()
        self.assertFalse(result)
        mock_flash.assert_called_once_with('Amount cannot be empty', 'error')

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_invalid_string(self, mock_flash):
        saving = Savings(amount="abc", user_id=1)
        result = saving.check_input()
        self.assertFalse(result)
        mock_flash.assert_called_once_with(
            'Amount must be a valid number', 'error'
        )

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_string_with_comma(self, mock_flash):
        saving = Savings(amount="100,50", user_id=1)
        result = saving.check_input()
        self.assertFalse(result)
        mock_flash.assert_called_once_with(
            'Amount must be a valid number', 'error'
        )


class TestTransfer(unittest.TestCase):

    @patch(PATCH_TARGET_FLASH)
    def test_check_balance_sufficient(self, mock_flash):
        transfer = Transfer(amount=50.0, user_id=1, balance=100.0)
        result = transfer.check_balance()
        self.assertTrue(result)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_balance_equal(self, mock_flash):
        transfer = Transfer(amount=100.0, user_id=1, balance=100.0)
        result = transfer.check_balance()
        self.assertTrue(result)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_balance_insufficient(self, mock_flash):
        transfer = Transfer(amount=150.0, user_id=1, balance=100.0)
        result = transfer.check_balance()
        self.assertFalse(result)
        mock_flash.assert_called_once_with(
            'You do not have enough money on your balance', 'error'
        )

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_valid_sufficient_balance(self, mock_flash):
        transfer = Transfer(amount="50", user_id=1, balance=100.0)
        result = transfer.check_input()
        self.assertTrue(result)
        self.assertEqual(transfer.amount, 50.0)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_invalid_amount(self, mock_flash):
        transfer = Transfer(amount="abc", user_id=1, balance=100.0)
        result = transfer.check_input()
        self.assertFalse(result)
        mock_flash.assert_called_once_with(
            'Amount must be a valid number', 'error'
        )

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_insufficient_balance(self, mock_flash):
        transfer = Transfer(amount="150", user_id=1, balance=100.0)
        result = transfer.check_input()
        self.assertFalse(result)
        self.assertEqual(transfer.amount, 150.0)
        mock_flash.assert_called_once_with(
            'You do not have enough money on your balance', 'error'
        )


class TestWithdraw(unittest.TestCase):

    @patch(PATCH_TARGET_FLASH)
    def test_check_balance_sufficient(self, mock_flash):
        withdraw = Withdraw(amount=50.0, user_id=1, saving_balance=100.0)
        result = withdraw.check_balance()
        self.assertTrue(result)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_balance_equal(self, mock_flash):
        withdraw = Withdraw(amount=100.0, user_id=1, saving_balance=100.0)
        result = withdraw.check_balance()
        self.assertTrue(result)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_balance_insufficient(self, mock_flash):
        withdraw = Withdraw(amount=150.0, user_id=1, saving_balance=100.0)
        result = withdraw.check_balance()
        self.assertFalse(result)
        mock_flash.assert_called_once_with(
            'You do not have enough money on your saving balance', 'error'
        )

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_valid_sufficient_balance(self, mock_flash):
        withdraw = Withdraw(amount="50", user_id=1, saving_balance=100.0)
        result = withdraw.check_input()
        self.assertTrue(result)
        self.assertEqual(withdraw.amount, 50.0)
        mock_flash.assert_not_called()

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_invalid_amount(self, mock_flash):
        withdraw = Withdraw(amount="", user_id=1, saving_balance=100.0)
        result = withdraw.check_input()
        self.assertFalse(result)
        mock_flash.assert_called_once_with('Amount cannot be empty', 'error')

    @patch(PATCH_TARGET_FLASH)
    def test_check_input_insufficient_balance(self, mock_flash):
        withdraw = Withdraw(amount="150", user_id=1, saving_balance=100.0)
        result = withdraw.check_input()
        self.assertFalse(result)
        self.assertEqual(withdraw.amount, 150.0)
        mock_flash.assert_called_once_with(
            'You do not have enough money on your saving balance', 'error'
        )


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)