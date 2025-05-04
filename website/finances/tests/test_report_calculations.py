import unittest
from unittest.mock import patch, Mock, MagicMock
import datetime

from website.finances.report_calculations import (
    get_financial_data,
    calculate_totals,
    calculate_balance_and_coverage,
    get_period_data,
    calculate_period_totals,
)

PATCH_TARGET_INCOME = 'website.finances.report_calculations.IncomeModel'
PATCH_TARGET_EXPENSES = 'website.finances.report_calculations.ExpensesModel'
PATCH_TARGET_PLANNING = 'website.finances.report_calculations.PlanningModel'
PATCH_TARGET_SAVINGS = 'website.finances.report_calculations.SavingsModel'


class MockFinancialRecord:
    def __init__(self, amount, date_str=None):
        self.amount = amount
        self.date = (
            datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if date_str else None
        )


class TestReportCalculation(unittest.TestCase):

    @patch(PATCH_TARGET_SAVINGS)
    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_get_financial_data(
        self, mock_income_model, mock_expenses_model,
        mock_planning_model, mock_savings_model
    ):
        user_id_to_test = 5
        mock_income_list = [MockFinancialRecord(100)]
        mock_expenses_list = [MockFinancialRecord(50)]
        mock_planning_list = [MockFinancialRecord(200)]
        mock_savings_list = [MockFinancialRecord(30)]

        mock_income_model.query.filter_by.return_value.all.return_value = (
            mock_income_list
        )
        mock_expenses_model.query.filter_by.return_value.all.return_value = (
            mock_expenses_list
        )
        mock_planning_model.query.filter_by.return_value.all.return_value = (
            mock_planning_list
        )
        mock_savings_model.query.filter_by.return_value.all.return_value = (
            mock_savings_list
        )

        income, expenses, planning, savings = get_financial_data(
            user_id_to_test
        )

        mock_income_model.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_expenses_model.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_planning_model.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )
        mock_savings_model.query.filter_by.assert_called_once_with(
            user_id=user_id_to_test
        )

        mock_income_model.query.filter_by.return_value.all.assert_called_once()
        mock_expenses_model.query.filter_by.return_value.all.assert_called_once()
        mock_planning_model.query.filter_by.return_value.all.assert_called_once()
        mock_savings_model.query.filter_by.return_value.all.assert_called_once()

        self.assertEqual(income, mock_income_list)
        self.assertEqual(expenses, mock_expenses_list)
        self.assertEqual(planning, mock_planning_list)
        self.assertEqual(savings, mock_savings_list)

    def test_calculate_totals_non_empty(self):
        income = [MockFinancialRecord(1000), MockFinancialRecord(500.50)]
        expenses = [
            MockFinancialRecord(200), MockFinancialRecord(75.25),
            MockFinancialRecord(100)
        ]
        planning = [MockFinancialRecord(1000)]
        savings = [MockFinancialRecord(50)]

        total_i, total_e, total_p, total_s = calculate_totals(
            income, expenses, planning, savings
        )

        self.assertAlmostEqual(total_i, 1500.50)
        self.assertAlmostEqual(total_e, 375.25)
        self.assertAlmostEqual(total_p, 1000)
        self.assertAlmostEqual(total_s, 50)

    def test_calculate_totals_empty(self):
        total_i, total_e, total_p, total_s = calculate_totals([], [], [], [])
        self.assertEqual(total_i, 0)
        self.assertEqual(total_e, 0)
        self.assertEqual(total_p, 0)
        self.assertEqual(total_s, 0)

    def test_calculate_balance_and_coverage_positive_cover(self):
        balance, cover = calculate_balance_and_coverage(
            total_income=1000, total_expenses=500, total_savings=100,
            total_planning=500
        )
        self.assertAlmostEqual(balance, 400)
        self.assertAlmostEqual(cover, 100)

    def test_calculate_balance_and_coverage_zero_cover(self):
        balance, cover = calculate_balance_and_coverage(
            total_income=1000, total_expenses=500, total_savings=100,
            total_planning=400
        )
        self.assertAlmostEqual(balance, 400)
        self.assertEqual(
            cover, "0.00 You can cover all your planning expenses."
        )

    def test_calculate_balance_and_coverage_negative_cover(self):
        balance, cover = calculate_balance_and_coverage(
            total_income=1000, total_expenses=500, total_savings=100,
            total_planning=300
        )
        self.assertAlmostEqual(balance, 400)
        self.assertEqual(
            cover, "0.00 You can cover all your planning expenses."
        )

    def test_calculate_balance_and_coverage_zero_totals(self):
        balance, cover = calculate_balance_and_coverage(
            total_income=0, total_expenses=0, total_savings=0, total_planning=0
        )
        self.assertAlmostEqual(balance, 0)
        self.assertEqual(
            cover, "0.00 You can cover all your planning expenses."
        )

    def test_get_period_data_filters_correctly(self):
        income = [
            MockFinancialRecord(100, "2025-04-15"),
            MockFinancialRecord(200, "2025-04-30"),
            MockFinancialRecord(300, "2025-05-01"),
            MockFinancialRecord(400, "2025-05-15"),
            MockFinancialRecord(500, "2025-05-20"),
        ]
        expenses = [
            MockFinancialRecord(10, "2025-04-20"),
            MockFinancialRecord(20, "2025-05-01"),
            MockFinancialRecord(30, "2025-05-10"),
            MockFinancialRecord(40, "2025-05-18"),
        ]
        planning = [
            MockFinancialRecord(1000, "2025-05-02"),
            MockFinancialRecord(2000, "2025-06-01"),
        ]

        start_date = datetime.date(2025, 4, 30)
        end_date = datetime.date(2025, 5, 15)

        p_income, p_expenses, p_planning = get_period_data(
            income, expenses, planning, start_date, end_date,
            start_date, end_date, start_date, end_date
        )

        self.assertEqual(len(p_income), 3)
        self.assertEqual([i.amount for i in p_income], [200, 300, 400])
        self.assertEqual(len(p_expenses), 2)
        self.assertEqual([e.amount for e in p_expenses], [20, 30])
        self.assertEqual(len(p_planning), 1)
        self.assertEqual([p.amount for p in p_planning], [1000])

    def test_get_period_data_no_match(self):
        income = [MockFinancialRecord(100, "2025-04-15")]
        expenses = [MockFinancialRecord(10, "2025-04-20")]
        planning = [MockFinancialRecord(1000, "2025-06-01")]

        start_date = datetime.date(2025, 5, 1)
        end_date = datetime.date(2025, 5, 31)

        p_income, p_expenses, p_planning = get_period_data(
            income, expenses, planning, start_date, end_date,
            start_date, end_date, start_date, end_date
        )

        self.assertEqual(len(p_income), 0)
        self.assertEqual(len(p_expenses), 0)
        self.assertEqual(len(p_planning), 0)

    def test_get_period_data_missing_dates(self):
        income = [MockFinancialRecord(100, "2025-04-15")]
        expenses = [MockFinancialRecord(10, "2025-04-20")]
        planning = [MockFinancialRecord(1000, "2025-06-01")]

        start_date = datetime.date(2025, 4, 1)
        end_date = datetime.date(2025, 4, 30)

        p_income, p_expenses, p_planning = get_period_data(
            income, expenses, planning, start_date, end_date,
            None, None, None, None
        )

        self.assertEqual(len(p_income), 1)
        self.assertEqual(len(p_expenses), 0)
        self.assertEqual(len(p_planning), 0)

    def test_get_period_data_empty_input_lists(self):
        start_date = datetime.date(2025, 5, 1)
        end_date = datetime.date(2025, 5, 31)

        p_income, p_expenses, p_planning = get_period_data(
            [], [], [], start_date, end_date, start_date, end_date,
            start_date, end_date
        )

        self.assertEqual(len(p_income), 0)
        self.assertEqual(len(p_expenses), 0)
        self.assertEqual(len(p_planning), 0)

    def test_calculate_period_totals_non_empty(self):
        p_income = [MockFinancialRecord(100), MockFinancialRecord(200.50)]
        p_expenses = [MockFinancialRecord(50), MockFinancialRecord(25.75)]
        p_planning = [MockFinancialRecord(500)]

        total_pi, total_pe, total_pp = calculate_period_totals(
            p_income, p_expenses, p_planning
        )

        self.assertAlmostEqual(total_pi, 300.50)
        self.assertAlmostEqual(total_pe, 75.75)
        self.assertAlmostEqual(total_pp, 500)

    def test_calculate_period_totals_empty(self):
        total_pi, total_pe, total_pp = calculate_period_totals([], [], [])
        self.assertEqual(total_pi, 0)
        self.assertEqual(total_pe, 0)
        self.assertEqual(total_pp, 0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)