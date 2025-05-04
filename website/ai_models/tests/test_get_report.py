import unittest
from unittest.mock import patch, Mock

from website.ai_models.get_report import get_report_data

PATCH_TARGET_IM = 'website.ai_models.get_report.IncomeModel'
PATCH_TARGET_EM = 'website.ai_models.get_report.ExpensesModel'
PATCH_TARGET_PM = 'website.ai_models.get_report.PlanningModel'
PATCH_TARGET_SM = 'website.ai_models.get_report.SavingsModel'


class MockRecord:
    def __init__(self, amount):
        self.amount = amount


class TestGetReportData(unittest.TestCase):

    @patch(PATCH_TARGET_SM)
    @patch(PATCH_TARGET_PM)
    @patch(PATCH_TARGET_EM)
    @patch(PATCH_TARGET_IM)
    def test_get_report_data_with_data(self, mock_im, mock_em, mock_pm, mock_sm):
        mock_im.query.all.return_value = [MockRecord(1000), MockRecord(500.50)]
        mock_em.query.all.return_value = [MockRecord(200), MockRecord(75.25)]
        mock_pm.query.all.return_value = [MockRecord(500), MockRecord(300)]
        mock_sm.query.all.return_value = [MockRecord(100), MockRecord(25)]

        expected_result = {
            'total_income': 1500.50,
            'total_expenses': 275.25,
            'total_planning': 800.00,
            'balance': 1100.25,
            'total_savings': 125.00,
            'amount_to_cover_planning': -300.25
        }

        result = get_report_data()

        mock_im.query.all.assert_called_once()
        mock_em.query.all.assert_called_once()
        mock_pm.query.all.assert_called_once()
        mock_sm.query.all.assert_called_once()

        self.assertAlmostEqual(
            result['total_income'], expected_result['total_income']
        )
        self.assertAlmostEqual(
            result['total_expenses'], expected_result['total_expenses']
        )
        self.assertAlmostEqual(
            result['total_planning'], expected_result['total_planning']
        )
        self.assertAlmostEqual(result['balance'], expected_result['balance'])
        self.assertAlmostEqual(
            result['total_savings'], expected_result['total_savings']
        )
        self.assertAlmostEqual(
            result['amount_to_cover_planning'],
            expected_result['amount_to_cover_planning']
        )
        self.assertDictEqual(result, expected_result)

    @patch(PATCH_TARGET_SM)
    @patch(PATCH_TARGET_PM)
    @patch(PATCH_TARGET_EM)
    @patch(PATCH_TARGET_IM)
    def test_get_report_data_no_data(self, mock_im, mock_em, mock_pm, mock_sm):
        mock_im.query.all.return_value = []
        mock_em.query.all.return_value = []
        mock_pm.query.all.return_value = []
        mock_sm.query.all.return_value = []

        expected_result = {
            'total_income': 0,
            'total_expenses': 0,
            'total_planning': 0,
            'balance': 0,
            'total_savings': 0,
            'amount_to_cover_planning': 0
        }

        result = get_report_data()

        mock_im.query.all.assert_called_once()
        mock_em.query.all.assert_called_once()
        mock_pm.query.all.assert_called_once()
        mock_sm.query.all.assert_called_once()

        self.assertDictEqual(result, expected_result)

    @patch(PATCH_TARGET_SM)
    @patch(PATCH_TARGET_PM)
    @patch(PATCH_TARGET_EM)
    @patch(PATCH_TARGET_IM)
    def test_get_report_data_some_data_missing(
        self, mock_im, mock_em, mock_pm, mock_sm
    ):
        mock_im.query.all.return_value = [MockRecord(2000)]
        mock_em.query.all.return_value = [MockRecord(500)]
        mock_pm.query.all.return_value = []
        mock_sm.query.all.return_value = [MockRecord(300)]

        expected_result = {
            'total_income': 2000,
            'total_expenses': 500,
            'total_planning': 0,
            'balance': 1200,
            'total_savings': 300,
            'amount_to_cover_planning': -1200
        }

        result = get_report_data()

        mock_im.query.all.assert_called_once()
        mock_em.query.all.assert_called_once()
        mock_pm.query.all.assert_called_once()
        mock_sm.query.all.assert_called_once()

        self.assertDictEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)