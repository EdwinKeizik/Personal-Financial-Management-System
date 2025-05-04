import unittest
import datetime
from unittest.mock import patch, Mock, MagicMock

from website.finances.submit_finances import process_form_submission

PATCH_TARGET_FLASH = 'website.finances.submit_finances.flash'
PATCH_TARGET_IM = 'website.finances.submit_finances.IncomeModel'
PATCH_TARGET_EM = 'website.finances.submit_finances.ExpensesModel'
PATCH_TARGET_PM = 'website.finances.submit_finances.PlanningModel'
PATCH_TARGET_IC = 'website.finances.submit_finances.IncomeClass'
PATCH_TARGET_EC = 'website.finances.submit_finances.ExpensesClass'
PATCH_TARGET_PC = 'website.finances.submit_finances.PlanningClass'
PATCH_TARGET_DB = 'website.finances.submit_finances.db'


class TestSubmitFinances(unittest.TestCase):

    def setUp(self):
        self.mock_request = Mock()
        self.mock_request.form = MagicMock()
        self.mock_user = Mock()
        self.mock_user.id = 123

    def test_process_form_invalid_submit_value(self):
        self.mock_request.form.get.return_value = 'unknown'
        result = process_form_submission(self.mock_request, self.mock_user)
        self.mock_request.form.get.assert_called_once_with('submit')
        self.assertFalse(result)

    def test_process_form_no_submit_value(self):
        self.mock_request.form.get.return_value = None
        result = process_form_submission(self.mock_request, self.mock_user)
        self.mock_request.form.get.assert_called_once_with('submit')
        self.assertFalse(result)

    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_IM)
    @patch(PATCH_TARGET_IC)
    @patch(PATCH_TARGET_FLASH)
    def test_process_income_success(
        self, mock_flash, MockIncomeClass, MockIncomeModel, mock_db
    ):
        form_data = {
            'submit': 'income',
            'amountI': '100.50',
            'nameI': 'Salary',
            'dateI': '2025-05-01'
        }
        self.mock_request.form.get.side_effect = lambda key: form_data.get(key)

        mock_item_instance = Mock()
        mock_item_instance.check_input.return_value = True
        mock_item_instance.amount = 100.50
        mock_item_instance.name = 'Salary'
        mock_item_instance.date = datetime.date(2025, 5, 1)
        mock_item_instance.type = 'Income'
        MockIncomeClass.return_value = mock_item_instance

        mock_model_instance = Mock()
        MockIncomeModel.return_value = mock_model_instance

        result = process_form_submission(self.mock_request, self.mock_user)

        self.assertTrue(result)
        MockIncomeClass.assert_called_once_with(
            '100.50', 'Salary', '2025-05-01', 'Income', self.mock_user.id
        )
        mock_item_instance.check_input.assert_called_once()
        MockIncomeModel.assert_called_once_with(
            amount=100.50,
            name='Salary',
            date=datetime.date(2025, 5, 1),
            type='Income',
            user_id=self.mock_user.id
        )
        mock_db.session.add.assert_called_once_with(mock_model_instance)
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Income added successfully!', 'success'
        )

    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_IM)
    @patch(PATCH_TARGET_IC)
    @patch(PATCH_TARGET_FLASH)
    def test_process_income_check_input_fails(
        self, mock_flash, MockIncomeClass, MockIncomeModel, mock_db
    ):
        form_data = {
            'submit': 'income',
            'amountI': '-10',
            'nameI': 'Salary',
            'dateI': '2025-05-01'
        }
        self.mock_request.form.get.side_effect = lambda key: form_data.get(key)

        mock_item_instance = Mock()
        mock_item_instance.check_input.return_value = False
        MockIncomeClass.return_value = mock_item_instance

        result = process_form_submission(self.mock_request, self.mock_user)

        self.assertTrue(result)
        MockIncomeClass.assert_called_once_with(
            '-10', 'Salary', '2025-05-01', 'Income', self.mock_user.id
        )
        mock_item_instance.check_input.assert_called_once()
        MockIncomeModel.assert_not_called()
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_called_once_with(
            'Failed to add Income. Please check your input.', 'error'
        )

    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_EM)
    @patch(PATCH_TARGET_EC)
    @patch(PATCH_TARGET_FLASH)
    def test_process_expenses_success(
        self, mock_flash, MockExpensesClass, MockExpensesModel, mock_db
    ):
        form_data = {
            'submit': 'expenses',
            'amountE': '50.25',
            'nameE': 'Groceries',
            'dateE': '2025-05-02'
        }
        self.mock_request.form.get.side_effect = lambda key: form_data.get(key)

        mock_item_instance = Mock()
        mock_item_instance.check_input.return_value = True
        mock_item_instance.amount = 50.25
        mock_item_instance.name = 'Groceries'
        mock_item_instance.date = datetime.date(2025, 5, 2)
        mock_item_instance.type = 'Expenses'
        MockExpensesClass.return_value = mock_item_instance

        mock_model_instance = Mock()
        MockExpensesModel.return_value = mock_model_instance

        result = process_form_submission(self.mock_request, self.mock_user)

        self.assertTrue(result)
        MockExpensesClass.assert_called_once_with(
            '50.25', 'Groceries', '2025-05-02', 'Expenses', self.mock_user.id
        )
        mock_item_instance.check_input.assert_called_once()
        MockExpensesModel.assert_called_once_with(
            amount=50.25,
            name='Groceries',
            date=datetime.date(2025, 5, 2),
            type='Expenses',
            user_id=self.mock_user.id
        )
        mock_db.session.add.assert_called_once_with(mock_model_instance)
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Expenses added successfully!', 'success'
        )

    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_EM)
    @patch(PATCH_TARGET_EC)
    @patch(PATCH_TARGET_FLASH)
    def test_process_expenses_check_input_fails(
        self, mock_flash, MockExpensesClass, MockExpensesModel, mock_db
    ):
        form_data = {
            'submit': 'expenses',
            'amountE': '50',
            'nameE': 'Gr',
            'dateE': '2025-05-02'
        }
        self.mock_request.form.get.side_effect = lambda key: form_data.get(key)

        mock_item_instance = Mock()
        mock_item_instance.check_input.return_value = False
        MockExpensesClass.return_value = mock_item_instance

        result = process_form_submission(self.mock_request, self.mock_user)

        self.assertTrue(result)
        MockExpensesClass.assert_called_once_with(
            '50', 'Gr', '2025-05-02', 'Expenses', self.mock_user.id
        )
        mock_item_instance.check_input.assert_called_once()
        MockExpensesModel.assert_not_called()
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_called_once_with(
            'Failed to add Expenses. Please check your input.', 'error'
        )

    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_PM)
    @patch(PATCH_TARGET_PC)
    @patch(PATCH_TARGET_FLASH)
    def test_process_planning_success(
        self, mock_flash, MockPlanningClass, MockPlanningModel, mock_db
    ):
        form_data = {
            'submit': 'planning',
            'amountP': '2000',
            'nameP': 'Vacation',
            'dateP': '2025-08-15'
        }
        self.mock_request.form.get.side_effect = lambda key: form_data.get(key)

        mock_item_instance = Mock()
        mock_item_instance.check_input.return_value = True
        mock_item_instance.amount = 2000.00
        mock_item_instance.name = 'Vacation'
        mock_item_instance.date = datetime.date(2025, 8, 15)
        mock_item_instance.type = 'Planning'
        MockPlanningClass.return_value = mock_item_instance

        mock_model_instance = Mock()
        MockPlanningModel.return_value = mock_model_instance

        result = process_form_submission(self.mock_request, self.mock_user)

        self.assertTrue(result)
        MockPlanningClass.assert_called_once_with(
            '2000', 'Vacation', '2025-08-15', 'Planning', self.mock_user.id
        )
        mock_item_instance.check_input.assert_called_once()
        MockPlanningModel.assert_called_once_with(
            amount=2000.00,
            name='Vacation',
            date=datetime.date(2025, 8, 15),
            type='Planning',
            user_id=self.mock_user.id
        )
        mock_db.session.add.assert_called_once_with(mock_model_instance)
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Planning added successfully!', 'success'
        )

    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_PM)
    @patch(PATCH_TARGET_PC)
    @patch(PATCH_TARGET_FLASH)
    def test_process_planning_check_input_fails(
        self, mock_flash, MockPlanningClass, MockPlanningModel, mock_db
    ):
        form_data = {
            'submit': 'planning',
            'amountP': '2000',
            'nameP': 'Vacation',
            'dateP': '2025-04-01'
        }
        self.mock_request.form.get.side_effect = lambda key: form_data.get(key)

        mock_item_instance = Mock()
        mock_item_instance.check_input.return_value = False
        MockPlanningClass.return_value = mock_item_instance

        result = process_form_submission(self.mock_request, self.mock_user)

        self.assertTrue(result)
        MockPlanningClass.assert_called_once_with(
            '2000', 'Vacation', '2025-04-01', 'Planning', self.mock_user.id
        )
        mock_item_instance.check_input.assert_called_once()
        MockPlanningModel.assert_not_called()
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_called_once_with(
            'Failed to add Planning. Please check your input.', 'error'
        )


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)