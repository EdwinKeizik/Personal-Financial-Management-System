import unittest
from unittest.mock import patch, Mock, MagicMock
import datetime

from website.filters import filter_reports

PATCH_TARGET_INCOME = 'website.filters.Income'
PATCH_TARGET_EXPENSES = 'website.filters.Expenses'
PATCH_TARGET_PLANNING = 'website.filters.Planning'


class TestFilterReports(unittest.TestCase):

    def setUp(self):
        self.user_id = 1
        self.mock_income_record = Mock(id=1, name='Salary', amount=3000.0, date=datetime.date(2025, 5, 1),
                                        type='Monthly')
        self.mock_expense_record = Mock(id=2, name='Rent', amount=1200.0, date=datetime.date(2025, 5, 1),
                                         type='Housing')
        self.mock_planning_record = Mock(id=3, name='Vacation', amount=1500.0, date=datetime.date(2025, 8, 1),
                                          type='Travel')  # type might differ

    def _setup_mock_queries(self, mock_income, mock_expenses, mock_planning):
        mock_income_query = MagicMock(name='IncomeQuery')
        mock_expenses_query = MagicMock(name='ExpensesQuery')
        mock_planning_query = MagicMock(name='PlanningQuery')

        mock_income.query.filter_by.return_value = mock_income_query
        mock_expenses.query.filter_by.return_value = mock_expenses_query
        mock_planning.query.filter_by.return_value = mock_planning_query

        mock_income_query.filter.return_value = mock_income_query
        mock_expenses_query.filter.return_value = mock_expenses_query
        mock_planning_query.filter.return_value = mock_planning_query

        # Mock column comparators used in filters
        for model_mock in [mock_income, mock_expenses, mock_planning]:
            model_mock.id = MagicMock(name=f'{model_mock._extract_mock_name()}.id')
            model_mock.id.__eq__ = Mock(
                return_value=f"{model_mock._extract_mock_name()}.id == None")  # Return value is just for identification in asserts
            model_mock.name = MagicMock(name=f'{model_mock._extract_mock_name()}.name')
            model_mock.name.like = Mock(return_value=f"{model_mock._extract_mock_name()}.name LIKE %query%")
            model_mock.date = MagicMock(name=f'{model_mock._extract_mock_name()}.date')
            model_mock.date.__eq__ = Mock(return_value=f"{model_mock._extract_mock_name()}.date == date")
            model_mock.amount = MagicMock(name=f'{model_mock._extract_mock_name()}.amount')
            model_mock.amount.__eq__ = Mock(return_value=f"{model_mock._extract_mock_name()}.amount == amount")

        return mock_income_query, mock_expenses_query, mock_planning_query

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_no_filters(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        mock_income_query.all.return_value = [self.mock_income_record]
        mock_expenses_query.all.return_value = [self.mock_expense_record]
        mock_planning_query.all.return_value = [self.mock_planning_record]

        result = filter_reports(self.user_id)

        mock_income.query.filter_by.assert_called_once_with(user_id=self.user_id)
        mock_expenses.query.filter_by.assert_called_once_with(user_id=self.user_id)
        mock_planning.query.filter_by.assert_called_once_with(user_id=self.user_id)

        mock_income_query.filter.assert_not_called()
        mock_expenses_query.filter.assert_not_called()
        mock_planning_query.filter.assert_not_called()

        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()

        self.assertEqual(result['income'], [self.mock_income_record])
        self.assertEqual(result['expenses'], [self.mock_expense_record])
        self.assertEqual(result['planning'], [self.mock_planning_record])

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_report_type_income(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        result = filter_reports(self.user_id, report_type="Income")

        mock_income_query.filter.assert_not_called()
        mock_expenses_query.filter.assert_called_once_with(mock_expenses.id.__eq__(None))
        mock_planning_query.filter.assert_called_once_with(mock_planning.id.__eq__(None))
        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_report_type_expenses(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        result = filter_reports(self.user_id, report_type="Expenses")

        mock_income_query.filter.assert_called_once_with(mock_income.id.__eq__(None))
        mock_expenses_query.filter.assert_not_called()
        mock_planning_query.filter.assert_called_once_with(mock_planning.id.__eq__(None))
        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_report_type_planning(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        result = filter_reports(self.user_id, report_type="Planning Expenses")

        mock_income_query.filter.assert_called_once_with(mock_income.id.__eq__(None))
        mock_expenses_query.filter.assert_called_once_with(mock_expenses.id.__eq__(None))
        mock_planning_query.filter.assert_not_called()
        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_name_query(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        name_q = "Sal"
        result = filter_reports(self.user_id, name_query=name_q)

        mock_income.name.like.assert_called_once_with(f"%{name_q}%")
        mock_expenses.name.like.assert_called_once_with(f"%{name_q}%")
        mock_planning.name.like.assert_called_once_with(f"%{name_q}%")

        mock_income_query.filter.assert_called_once_with(mock_income.name.like.return_value)
        mock_expenses_query.filter.assert_called_once_with(mock_expenses.name.like.return_value)
        mock_planning_query.filter.assert_called_once_with(mock_planning.name.like.return_value)
        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_date_query(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        date_q = datetime.date(2025, 5, 10)
        result = filter_reports(self.user_id, date=date_q)

        mock_income.date.__eq__.assert_called_once_with(date_q)
        mock_expenses.date.__eq__.assert_called_once_with(date_q)
        mock_planning.date.__eq__.assert_called_once_with(date_q)

        mock_income_query.filter.assert_called_once_with(mock_income.date.__eq__.return_value)
        mock_expenses_query.filter.assert_called_once_with(mock_expenses.date.__eq__.return_value)
        mock_planning_query.filter.assert_called_once_with(mock_planning.date.__eq__.return_value)
        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_amount_query(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        amount_q_str = "123.45"
        amount_q_float = 123.45
        result = filter_reports(self.user_id, amount_query=amount_q_str)

        mock_income.amount.__eq__.assert_called_once_with(amount_q_float)
        mock_expenses.amount.__eq__.assert_called_once_with(amount_q_float)
        mock_planning.amount.__eq__.assert_called_once_with(amount_q_float)

        mock_income_query.filter.assert_called_once_with(mock_income.amount.__eq__.return_value)
        mock_expenses_query.filter.assert_called_once_with(mock_expenses.amount.__eq__.return_value)
        mock_planning_query.filter.assert_called_once_with(mock_planning.amount.__eq__.return_value)
        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()

    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_multiple_filters_and_type(self, mock_income, mock_expenses, mock_planning):
        mock_income_query, mock_expenses_query, mock_planning_query = self._setup_mock_queries(
            mock_income, mock_expenses, mock_planning
        )
        name_q = "Rent"
        date_q = datetime.date(2025, 5, 1)

        result = filter_reports(
            self.user_id,
            name_query=name_q,
            date=date_q,
            report_type="Expenses"
        )

        # Assertions for Income query
        self.assertEqual(mock_income_query.filter.call_count, 3)
        mock_income.id.__eq__.assert_called_once_with(None)
        mock_income.name.like.assert_called_once_with(f"%{name_q}%")
        mock_income.date.__eq__.assert_called_once_with(date_q)
        mock_income_query.filter.assert_any_call(mock_income.id.__eq__.return_value)
        mock_income_query.filter.assert_any_call(mock_income.name.like.return_value)
        mock_income_query.filter.assert_any_call(mock_income.date.__eq__.return_value)

        # Assertions for Planning query
        self.assertEqual(mock_planning_query.filter.call_count, 3)
        mock_planning.id.__eq__.assert_called_once_with(None)
        mock_planning.name.like.assert_called_once_with(f"%{name_q}%")
        mock_planning.date.__eq__.assert_called_once_with(date_q)
        mock_planning_query.filter.assert_any_call(mock_planning.id.__eq__.return_value)
        mock_planning_query.filter.assert_any_call(mock_planning.name.like.return_value)
        mock_planning_query.filter.assert_any_call(mock_planning.date.__eq__.return_value)

        # Assertions for Expenses query
        self.assertEqual(mock_expenses_query.filter.call_count, 2)
        mock_expenses.name.like.assert_called_once_with(f"%{name_q}%")
        mock_expenses.date.__eq__.assert_called_once_with(date_q)
        mock_expenses_query.filter.assert_any_call(mock_expenses.name.like.return_value)
        mock_expenses_query.filter.assert_any_call(mock_expenses.date.__eq__.return_value)
        mock_expenses.id.__eq__.assert_not_called()  # Important: ID filter NOT applied

        mock_income_query.all.assert_called_once()
        mock_expenses_query.all.assert_called_once()
        mock_planning_query.all.assert_called_once()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)