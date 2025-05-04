import unittest
from unittest.mock import patch, Mock, MagicMock
from flask import Flask
import datetime


from website.report import home

print("--- EXECUTING test_report.py ---") 

PATCH_TARGET_RENDER = 'website.report.render_template'
PATCH_TARGET_REQUEST = 'website.report.request'
PATCH_TARGET_FLASH = 'website.report.flash'
PATCH_TARGET_REDIRECT = 'website.report.redirect'
PATCH_TARGET_URL_FOR = 'website.report.url_for'
PATCH_TARGET_LOGIN_REQ = 'website.report.login_required'
PATCH_TARGET_CURRENT_USER = 'website.report.current_user'
PATCH_TARGET_DATETIME = 'website.report.datetime'

PATCH_TARGET_GET_FIN_DATA = 'website.report.get_financial_data'
PATCH_TARGET_CALC_TOTALS = 'website.report.calculate_totals'
PATCH_TARGET_CALC_BALANCE = 'website.report.calculate_balance_and_coverage'
PATCH_TARGET_PROCESS_SUBMIT = 'website.report.process_form_submission'
PATCH_TARGET_HANDLE_TRANSFER = 'website.report.handle_transfer'
PATCH_TARGET_HANDLE_WITHDRAW = 'website.report.handle_withdraw'
PATCH_TARGET_GET_PERIOD = 'website.report.get_period_data'
PATCH_TARGET_CALC_PERIOD = 'website.report.calculate_period_totals'

print("--- EXECUTING test_report.py ---")

class TestReportView(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testing_report'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.req_context = self.app.test_request_context()
        self.req_context.push()

        self.mock_user_instance = Mock(id=202)
        self.patcher_current_user = patch(PATCH_TARGET_CURRENT_USER, self.mock_user_instance)
        self.patcher_current_user.start()

        # No need to start/stop login_required patch here, do it per method

        self.addCleanup(self.req_context.pop)
        self.addCleanup(self.app_context.pop)
        self.addCleanup(self.patcher_current_user.stop)

        self.mock_income_data = [Mock(amount=100)]
        self.mock_expenses_data = [Mock(amount=50)]
        self.mock_planning_data = [Mock(amount=200)]
        self.mock_savings_data = [Mock(amount=1000)]
        self.mock_period_income = [Mock(amount=10)]
        self.mock_period_expenses = [Mock(amount=5)]
        self.mock_period_planning = [Mock(amount=20)]

    # Add login_required patch and argument to all tests calling home()
    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_CALC_PERIOD)
    @patch(PATCH_TARGET_GET_PERIOD)
    @patch(PATCH_TARGET_HANDLE_WITHDRAW)
    @patch(PATCH_TARGET_HANDLE_TRANSFER)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_CALC_BALANCE)
    @patch(PATCH_TARGET_CALC_TOTALS)
    @patch(PATCH_TARGET_GET_FIN_DATA)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_get_no_dates(self, mock_request, mock_render, mock_dt, mock_get_fin, mock_calc_totals, mock_calc_bal, mock_proc_sub, mock_h_trans, mock_h_with, mock_get_period, mock_calc_period, mock_login_req):
        print("--- RUNNING test_home_get_no_dates ---")
        mock_request.method = 'GET'
        mock_request.args = {}

        mock_get_fin.return_value = (self.mock_income_data, self.mock_expenses_data, self.mock_planning_data, self.mock_savings_data)
        mock_calc_totals.return_value = (100, 50, 200, 1000)
        mock_calc_bal.return_value = (-950, 1150)
        mock_get_period.return_value = ([], [], [])
        mock_calc_period.return_value = (0, 0, 0)
        mock_render.return_value = "Report Rendered"

        response = home()

        mock_get_fin.assert_called_once_with(self.mock_user_instance.id)
        mock_calc_totals.assert_called_once_with(self.mock_income_data, self.mock_expenses_data, self.mock_planning_data, self.mock_savings_data)
        mock_calc_bal.assert_called_once_with(100, 50, 1000, 200)
        mock_get_period.assert_called_once_with(self.mock_income_data, self.mock_expenses_data, self.mock_planning_data, None, None, None, None, None, None)
        mock_calc_period.assert_called_once_with([], [], [])
        mock_proc_sub.assert_not_called()
        mock_h_trans.assert_not_called()
        mock_h_with.assert_not_called()
        mock_render.assert_called_once()
        args, kwargs = mock_render.call_args
        self.assertEqual(args[0], "report.html")
        self.assertEqual(kwargs['total_income'], 100)
        self.assertEqual(kwargs['balance'], -950)
        self.assertEqual(response, "Report Rendered")

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_CALC_PERIOD)
    @patch(PATCH_TARGET_GET_PERIOD)
    @patch(PATCH_TARGET_HANDLE_WITHDRAW)
    @patch(PATCH_TARGET_HANDLE_TRANSFER)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_CALC_BALANCE)
    @patch(PATCH_TARGET_CALC_TOTALS)
    @patch(PATCH_TARGET_GET_FIN_DATA)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_get_with_dates(self, mock_request, mock_render, mock_dt, mock_get_fin, mock_calc_totals, mock_calc_bal, mock_proc_sub, mock_h_trans, mock_h_with, mock_get_period, mock_calc_period, mock_login_req):
        mock_request.method = 'GET'
        date_str_i_start = "2025-04-01"
        date_str_p_end = "2025-04-30"
        mock_request.args = {'Istart_date': date_str_i_start, 'Pend_date': date_str_p_end}
        mock_dt.strptime = datetime.datetime.strptime

        mock_get_fin.return_value = (self.mock_income_data, self.mock_expenses_data, self.mock_planning_data, self.mock_savings_data)
        mock_calc_totals.return_value = (100, 50, 200, 1000)
        mock_calc_bal.return_value = (-950, 1150)
        mock_get_period.return_value = (self.mock_period_income, [], self.mock_period_planning)
        mock_calc_period.return_value = (10, 0, 20)
        mock_render.return_value = "Report Rendered With Dates"

        response = home()

        date_i_start = datetime.date(2025, 4, 1)
        date_p_end = datetime.date(2025, 4, 30)
        mock_get_period.assert_called_once_with(self.mock_income_data, self.mock_expenses_data, self.mock_planning_data, date_i_start, None, None, None, None, date_p_end)
        mock_calc_period.assert_called_once_with(self.mock_period_income, [], self.mock_period_planning)
        mock_render.assert_called_once()
        args, kwargs = mock_render.call_args
        self.assertEqual(kwargs['total_period_income'], 10)
        self.assertEqual(kwargs['Istart_date'], date_str_i_start)
        self.assertEqual(response, "Report Rendered With Dates")

    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_CALC_PERIOD)
    @patch(PATCH_TARGET_GET_PERIOD)
    @patch(PATCH_TARGET_HANDLE_WITHDRAW)
    @patch(PATCH_TARGET_HANDLE_TRANSFER)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_CALC_BALANCE)
    @patch(PATCH_TARGET_CALC_TOTALS)
    @patch(PATCH_TARGET_GET_FIN_DATA)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_form_submission_fallthrough(self, mock_request, mock_render, mock_dt, mock_get_fin, mock_calc_totals, mock_calc_bal, mock_proc_sub, mock_h_trans, mock_h_with, mock_get_period, mock_calc_period, mock_login_req):
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'income'
        mock_request.args = {}

        mock_get_fin.return_value = ([], [], [], [])
        mock_calc_totals.return_value = (0, 0, 0, 0)
        mock_calc_bal.return_value = (0, 0)
        mock_get_period.return_value = ([], [], [])
        mock_calc_period.return_value = (0, 0, 0)
        mock_render.return_value = "Report Rendered After POST"

        response = home()

        mock_proc_sub.assert_called_once_with(mock_request, self.mock_user_instance)
        mock_h_trans.assert_not_called()
        mock_h_with.assert_not_called()
        mock_get_fin.assert_called_once()
        mock_render.assert_called_once()
        self.assertEqual(response, "Report Rendered After POST")


    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_CALC_PERIOD)
    @patch(PATCH_TARGET_GET_PERIOD)
    @patch(PATCH_TARGET_HANDLE_WITHDRAW)
    @patch(PATCH_TARGET_HANDLE_TRANSFER)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_CALC_BALANCE)
    @patch(PATCH_TARGET_CALC_TOTALS)
    @patch(PATCH_TARGET_GET_FIN_DATA)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_transfer(self, mock_request, mock_render, mock_dt, mock_get_fin, mock_calc_totals, mock_calc_bal, mock_proc_sub, mock_h_trans, mock_h_with, mock_get_period, mock_calc_period, mock_login_req):
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'transfer'
        mock_request.args = {}

        mock_get_fin.return_value = ([], [], [], [])
        mock_calc_totals.return_value = (100, 50, 0, 1000)
        mock_calc_bal.return_value = (-950, 950)
        mock_h_trans.return_value = "Transfer Redirect Response"

        response = home()

        mock_proc_sub.assert_called_once_with(mock_request, self.mock_user_instance)
        mock_h_trans.assert_called_once_with(mock_request, self.mock_user_instance, -950)
        mock_h_with.assert_not_called()
        mock_get_period.assert_not_called()
        mock_calc_period.assert_not_called()
        mock_render.assert_not_called()
        self.assertEqual(response, "Transfer Redirect Response")


    @patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
    @patch(PATCH_TARGET_CALC_PERIOD)
    @patch(PATCH_TARGET_GET_PERIOD)
    @patch(PATCH_TARGET_HANDLE_WITHDRAW)
    @patch(PATCH_TARGET_HANDLE_TRANSFER)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_CALC_BALANCE)
    @patch(PATCH_TARGET_CALC_TOTALS)
    @patch(PATCH_TARGET_GET_FIN_DATA)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post_withdraw(self, mock_request, mock_render, mock_dt, mock_get_fin, mock_calc_totals, mock_calc_bal, mock_proc_sub, mock_h_trans, mock_h_with, mock_get_period, mock_calc_period, mock_login_req):
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.return_value = 'withdraw'
        mock_request.args = {}

        mock_get_fin.return_value = ([], [], [], [])
        mock_calc_totals.return_value = (100, 50, 0, 1000)
        mock_calc_bal.return_value = (-950, 950)
        mock_h_with.return_value = "Withdraw Redirect Response"

        response = home()

        mock_proc_sub.assert_called_once_with(mock_request, self.mock_user_instance)
        mock_h_trans.assert_not_called()
        mock_h_with.assert_called_once_with(mock_request, self.mock_user_instance, 1000)
        mock_get_period.assert_not_called()
        mock_calc_period.assert_not_called()
        mock_render.assert_not_called()
        self.assertEqual(response, "Withdraw Redirect Response")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)