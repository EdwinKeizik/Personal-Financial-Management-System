import unittest
from unittest.mock import patch, Mock

from website.finances.delete_finances import process_delete_request


class MockModelInstance:
    def __init__(self, id):
        self.id = id


class TestDeleteFinances(unittest.TestCase):

    def setUp(self):
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_request = Mock()
        self.mock_request.form = {}

    @patch('website.finances.delete_finances.flash')
    @patch('website.finances.delete_finances.db')
    @patch('website.finances.delete_finances.PlanningModel')
    @patch('website.finances.delete_finances.ExpensesModel')
    @patch('website.finances.delete_finances.IncomeModel')
    def test_delete_income_success(
        self, MockIncomeModel, MockExpensesModel, MockPlanningModel, mock_db,
        mock_flash
    ):
        self.mock_request.form = {'delete': 'delI_10'}
        delete_id = 10
        mock_income_instance = MockModelInstance(id=delete_id)
        MockIncomeModel.query.filter_by.return_value.first.return_value = (
            mock_income_instance
        )

        process_delete_request(self.mock_request, self.mock_user)

        MockIncomeModel.query.filter_by.assert_called_once_with(
            id=str(delete_id), user_id=self.mock_user.id
        )
        MockExpensesModel.query.filter_by.assert_not_called()
        MockPlanningModel.query.filter_by.assert_not_called()
        mock_db.session.delete.assert_called_once_with(mock_income_instance)
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Deleted successfully!', 'success'
        )

    @patch('website.finances.delete_finances.flash')
    @patch('website.finances.delete_finances.db')
    @patch('website.finances.delete_finances.PlanningModel')
    @patch('website.finances.delete_finances.ExpensesModel')
    @patch('website.finances.delete_finances.IncomeModel')
    def test_delete_expense_success(
        self, MockIncomeModel, MockExpensesModel, MockPlanningModel, mock_db,
        mock_flash
    ):
        self.mock_request.form = {'delete': 'delE_25'}
        delete_id = 25
        mock_expense_instance = MockModelInstance(id=delete_id)
        MockExpensesModel.query.filter_by.return_value.first.return_value = (
            mock_expense_instance
        )

        process_delete_request(self.mock_request, self.mock_user)

        MockExpensesModel.query.filter_by.assert_called_once_with(
            id=str(delete_id), user_id=self.mock_user.id
        )
        MockIncomeModel.query.filter_by.assert_not_called()
        MockPlanningModel.query.filter_by.assert_not_called()
        mock_db.session.delete.assert_called_once_with(mock_expense_instance)
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Deleted successfully!', 'success'
        )

    @patch('website.finances.delete_finances.flash')
    @patch('website.finances.delete_finances.db')
    @patch('website.finances.delete_finances.PlanningModel')
    @patch('website.finances.delete_finances.ExpensesModel')
    @patch('website.finances.delete_finances.IncomeModel')
    def test_delete_planning_success(
        self, MockIncomeModel, MockExpensesModel, MockPlanningModel, mock_db,
        mock_flash
    ):
        self.mock_request.form = {'delete': 'delP_5'}
        delete_id = 5
        mock_planning_instance = MockModelInstance(id=delete_id)
        MockPlanningModel.query.filter_by.return_value.first.return_value = (
            mock_planning_instance
        )

        process_delete_request(self.mock_request, self.mock_user)

        MockPlanningModel.query.filter_by.assert_called_once_with(
            id=str(delete_id), user_id=self.mock_user.id
        )
        MockIncomeModel.query.filter_by.assert_not_called()
        MockExpensesModel.query.filter_by.assert_not_called()
        mock_db.session.delete.assert_called_once_with(
            mock_planning_instance
        )
        mock_db.session.commit.assert_called_once()
        mock_flash.assert_called_once_with(
            'Deleted successfully!', 'success'
        )

    @patch('website.finances.delete_finances.flash')
    @patch('website.finances.delete_finances.db')
    @patch('website.finances.delete_finances.PlanningModel')
    @patch('website.finances.delete_finances.ExpensesModel')
    @patch('website.finances.delete_finances.IncomeModel')
    def test_delete_record_not_found(
        self, MockIncomeModel, MockExpensesModel, MockPlanningModel, mock_db,
        mock_flash
    ):
        self.mock_request.form = {'delete': 'delI_99'}
        delete_id = 99
        MockIncomeModel.query.filter_by.return_value.first.return_value = None

        process_delete_request(self.mock_request, self.mock_user)

        MockIncomeModel.query.filter_by.assert_called_once_with(
            id=str(delete_id), user_id=self.mock_user.id
        )
        mock_db.session.delete.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_called_once_with('Failed to delete.', 'error')

    @patch('website.finances.delete_finances.flash')
    @patch('website.finances.delete_finances.db')
    @patch('website.finances.delete_finances.PlanningModel')
    @patch('website.finances.delete_finances.ExpensesModel')
    @patch('website.finances.delete_finances.IncomeModel')
    def test_delete_invalid_type(
        self, MockIncomeModel, MockExpensesModel, MockPlanningModel, mock_db,
        mock_flash
    ):
        self.mock_request.form = {'delete': 'delX_1'}

        process_delete_request(self.mock_request, self.mock_user)

        MockIncomeModel.query.filter_by.assert_not_called()
        MockExpensesModel.query.filter_by.assert_not_called()
        MockPlanningModel.query.filter_by.assert_not_called()
        mock_db.session.delete.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_called_once_with('Failed to delete.', 'error')

    @patch('website.finances.delete_finances.flash')
    @patch('website.finances.delete_finances.db')
    @patch('website.finances.delete_finances.PlanningModel')
    @patch('website.finances.delete_finances.ExpensesModel')
    @patch('website.finances.delete_finances.IncomeModel')
    def test_no_delete_key_in_form(
        self, MockIncomeModel, MockExpensesModel, MockPlanningModel, mock_db,
        mock_flash
    ):
        self.mock_request.form = {'other_key': 'some_value'}

        process_delete_request(self.mock_request, self.mock_user)

        MockIncomeModel.query.filter_by.assert_not_called()
        MockExpensesModel.query.filter_by.assert_not_called()
        MockPlanningModel.query.filter_by.assert_not_called()
        mock_db.session.delete.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_flash.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)