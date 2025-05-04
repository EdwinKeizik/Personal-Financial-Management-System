import unittest
from unittest.mock import patch, Mock, MagicMock

from website.finances.savings_handler import handle_transfer, handle_withdraw

PATCH_TARGET_FLASH = 'website.finances.savings_handler.flash'
PATCH_TARGET_REDIRECT = 'website.finances.savings_handler.redirect'
PATCH_TARGET_URL_FOR = 'website.finances.savings_handler.url_for'
PATCH_TARGET_SAVINGS_MODEL = 'website.finances.savings_handler.SavingsModel'
PATCH_TARGET_DB = 'website.finances.savings_handler.db'
PATCH_TARGET_TRANSFER = 'website.finances.savings_handler.Transfer'
PATCH_TARGET_WITHDRAW = 'website.finances.savings_handler.Withdraw'


class TestSavingsHandler(unittest.TestCase):

    def setUp(self):
        self.mock_request = Mock()
        self.mock_request.form = {}
        self.mock_user = Mock()
        self.mock_user.id = 99

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_SAVINGS_MODEL)
    @patch(PATCH_TARGET_TRANSFER)
    def test_handle_transfer_success(
        self, MockTransferClass, MockSavingsModel, mock_db, mock_flash,
        mock_redirect, mock_url_for
    ):
        transfer_amount = 100.50
        current_balance = 500.0
        self.mock_request.form = {'transfer-amount': str(transfer_amount)}
        mock_url_for.return_value = '/fake/report/home'

        mock_transfer_instance = Mock()
        mock_transfer_instance.check_input.return_value = True
        mock_transfer_instance.amount = transfer_amount
        MockTransferClass.return_value = mock_transfer_instance

        mock_new_save_instance = Mock()
        MockSavingsModel.return_value = mock_new_save_instance

        response = handle_transfer(
            self.mock_request, self.mock_user, current_balance
        )

        MockTransferClass.assert_called_once_with(
            transfer_amount, self.mock_user.id, current_balance
        )
        mock_transfer_instance.check_input.assert_called_once()
        MockSavingsModel.assert_called_once_with(
            amount=transfer_amount, user_id=self.mock_user.id
        )
        mock_db.session.add.assert_called_once_with(mock_new_save_instance)
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Transfer added successfully!', 'success'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_SAVINGS_MODEL)
    @patch(PATCH_TARGET_TRANSFER)
    def test_handle_transfer_check_input_fails(
        self, MockTransferClass, MockSavingsModel, mock_db, mock_flash,
        mock_redirect, mock_url_for
    ):
        transfer_amount = 100.50
        current_balance = 500.0
        self.mock_request.form = {'transfer-amount': str(transfer_amount)}
        mock_url_for.return_value = '/fake/report/home'

        mock_transfer_instance = Mock()
        mock_transfer_instance.check_input.return_value = False
        mock_transfer_instance.amount = transfer_amount
        MockTransferClass.return_value = mock_transfer_instance

        response = handle_transfer(
            self.mock_request, self.mock_user, current_balance
        )

        MockTransferClass.assert_called_once_with(
            transfer_amount, self.mock_user.id, current_balance
        )
        mock_transfer_instance.check_input.assert_called_once()
        MockSavingsModel.assert_not_called()
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_called_with(
            'Failed to add transfer. Please check your input.', 'error'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_TRANSFER)
    def test_handle_transfer_amount_missing(
        self, MockTransferClass, mock_flash, mock_redirect, mock_url_for
    ):
        self.mock_request.form = {}
        mock_url_for.return_value = '/fake/report/home'

        response = handle_transfer(self.mock_request, self.mock_user, 500.0)

        MockTransferClass.assert_not_called()
        mock_flash.assert_called_once_with(
            'Please enter a transfer amount.', 'error'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_TRANSFER)
    def test_handle_transfer_amount_invalid(
        self, MockTransferClass, mock_flash, mock_redirect, mock_url_for
    ):
        self.mock_request.form = {'transfer-amount': 'abc'}
        mock_url_for.return_value = '/fake/report/home'

        response = handle_transfer(self.mock_request, self.mock_user, 500.0)

        MockTransferClass.assert_not_called()
        mock_flash.assert_called_once_with(
            'Invalid transfer amount. Please enter a number.', 'error'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_SAVINGS_MODEL)
    @patch(PATCH_TARGET_WITHDRAW)
    def test_handle_withdraw_success(
        self, MockWithdrawClass, MockSavingsModel, mock_db, mock_flash,
        mock_redirect, mock_url_for
    ):
        withdraw_input_amount = 50.25
        expected_processed_amount = -50.25
        current_total_savings = 200.0
        self.mock_request.form = {'transfer-amount': str(withdraw_input_amount)}
        mock_url_for.return_value = '/fake/report/home'

        mock_withdraw_instance = Mock()
        mock_withdraw_instance.check_input.return_value = True
        mock_withdraw_instance.amount = expected_processed_amount
        MockWithdrawClass.return_value = mock_withdraw_instance

        mock_new_save_instance = Mock()
        MockSavingsModel.return_value = mock_new_save_instance

        response = handle_withdraw(
            self.mock_request, self.mock_user, current_total_savings
        )

        MockWithdrawClass.assert_called_once_with(
            expected_processed_amount, self.mock_user.id,
            current_total_savings
        )
        mock_withdraw_instance.check_input.assert_called_once()
        MockSavingsModel.assert_called_once_with(
            amount=expected_processed_amount, user_id=self.mock_user.id
        )
        mock_db.session.add.assert_called_once_with(mock_new_save_instance)
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Withdrawal added successfully!', 'success'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_SAVINGS_MODEL)
    @patch(PATCH_TARGET_WITHDRAW)
    def test_handle_withdraw_check_input_fails(
        self, MockWithdrawClass, MockSavingsModel, mock_db, mock_flash,
        mock_redirect, mock_url_for
    ):
        withdraw_input_amount = 50.25
        expected_processed_amount = -50.25
        current_total_savings = 200.0
        self.mock_request.form = {'transfer-amount': str(withdraw_input_amount)}
        mock_url_for.return_value = '/fake/report/home'

        mock_withdraw_instance = Mock()
        mock_withdraw_instance.check_input.return_value = False
        mock_withdraw_instance.amount = expected_processed_amount
        MockWithdrawClass.return_value = mock_withdraw_instance

        response = handle_withdraw(
            self.mock_request, self.mock_user, current_total_savings
        )

        MockWithdrawClass.assert_called_once_with(
            expected_processed_amount, self.mock_user.id,
            current_total_savings
        )
        mock_withdraw_instance.check_input.assert_called_once()
        MockSavingsModel.assert_not_called()
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_called_with(
            'Failed to add transfer. Please check your input.', 'error'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_WITHDRAW)
    def test_handle_withdraw_amount_missing(
        self, MockWithdrawClass, mock_flash, mock_redirect, mock_url_for
    ):
        self.mock_request.form = {}
        mock_url_for.return_value = '/fake/report/home'

        response = handle_withdraw(self.mock_request, self.mock_user, 200.0)

        MockWithdrawClass.assert_not_called()
        mock_flash.assert_called_once_with(
            'Please enter a withdrawal amount.', 'error'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_WITHDRAW)
    def test_handle_withdraw_amount_invalid(
        self, MockWithdrawClass, mock_flash, mock_redirect, mock_url_for
    ):
        self.mock_request.form = {'transfer-amount': 'xyz'}
        mock_url_for.return_value = '/fake/report/home'

        response = handle_withdraw(self.mock_request, self.mock_user, 200.0)

        MockWithdrawClass.assert_not_called()
        mock_flash.assert_called_once_with(
            'Invalid withdrawal amount. Please enter a number.', 'error'
        )
        mock_url_for.assert_called_once_with('report.home')
        mock_redirect.assert_called_once_with('/fake/report/home')
        self.assertEqual(response, mock_redirect.return_value)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)