import unittest
from unittest.mock import patch, Mock, MagicMock
from flask import Flask
import datetime

from website.views import home

PATCH_TARGET_RENDER = 'website.views.render_template'
PATCH_TARGET_REQUEST = 'website.views.request'
PATCH_TARGET_LOGIN_REQ = 'website.views.login_required'
PATCH_TARGET_CURRENT_USER = 'website.views.current_user'
PATCH_TARGET_DATETIME = 'website.views.datetime'

PATCH_TARGET_FILTER_REPORTS = 'website.views.filter_reports'
PATCH_TARGET_PROCESS_SUBMIT = 'website.views.process_form_submission'
PATCH_TARGET_PROCESS_DELETE = 'website.views.process_delete_request'

class TestViewsHome(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testing_views'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.req_context = self.app.test_request_context()
        self.req_context.push()

        self.mock_user_instance = Mock(id=303)
        self.patcher_current_user = patch(PATCH_TARGET_CURRENT_USER, self.mock_user_instance)
        self.patcher_current_user.start()

        self.patcher_login_req = patch(PATCH_TARGET_LOGIN_REQ, lambda func: func)
        self.patcher_login_req.start()

        self.addCleanup(self.req_context.pop)
        self.addCleanup(self.app_context.pop)
        self.addCleanup(self.patcher_current_user.stop)
        self.addCleanup(self.patcher_login_req.stop)

        self.mock_filtered_results = {
            'income': [Mock(name='Income1')],
            'expenses': [Mock(name='Expense1')],
            'planning': [Mock(name='Plan1')]
        }

    @patch(PATCH_TARGET_PROCESS_DELETE)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_FILTER_REPORTS)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_get_no_filters(self, mock_request, mock_render, mock_dt, mock_filter_reports, mock_proc_submit, mock_proc_delete):
        mock_request.method = 'GET'
        mock_request.args = MagicMock()
        mock_request.args.get.side_effect = lambda key: None # No filter args
        mock_filter_reports.return_value = self.mock_filtered_results
        mock_render.return_value = "Rendered Index"

        response = home()

        mock_proc_submit.assert_not_called()
        mock_proc_delete.assert_not_called()
        mock_request.args.get.assert_any_call("Fprice")
        mock_request.args.get.assert_any_call("Fname")
        mock_request.args.get.assert_any_call("Fdate")
        mock_request.args.get.assert_any_call("Ftype")
        mock_filter_reports.assert_called_once_with(
            user_id=self.mock_user_instance.id,
            amount_query=None,
            name_query=None,
            date=None,
            report_type=None
        )
        mock_render.assert_called_once_with(
            "index.html",
            user=self.mock_user_instance,
            income=self.mock_filtered_results['income'],
            expenses=self.mock_filtered_results['expenses'],
            planning=self.mock_filtered_results['planning']
        )
        self.assertEqual(response, "Rendered Index")


    @patch(PATCH_TARGET_PROCESS_DELETE)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_FILTER_REPORTS)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_get_with_filters(self, mock_request, mock_render, mock_dt, mock_filter_reports, mock_proc_submit, mock_proc_delete):
        name_q = "TestName"
        date_q_str = "2025-04-10"
        date_q_obj = datetime.date(2025, 4, 10)
        type_q = "Income"
        amount_q = "100.00"

        mock_request.method = 'GET'
        mock_request.args = MagicMock()
        mock_request.args.get.side_effect = lambda key: {
            "Fprice": amount_q, "Fname": name_q, "Fdate": date_q_str, "Ftype": type_q
        }.get(key)

        mock_dt.strptime.return_value.date.return_value = date_q_obj # Mock date parsing

        mock_filter_reports.return_value = self.mock_filtered_results
        mock_render.return_value = "Rendered Index With Filters"

        response = home()

        mock_proc_submit.assert_not_called()
        mock_proc_delete.assert_not_called()

        mock_dt.strptime.assert_called_once_with(date_q_str, "%Y-%m-%d")
        mock_filter_reports.assert_called_once_with(
            user_id=self.mock_user_instance.id,
            amount_query=amount_q,
            name_query=name_q,
            date=date_q_obj,
            report_type=type_q
        )
        mock_render.assert_called_once_with(
            "index.html",
            user=self.mock_user_instance,
            income=self.mock_filtered_results['income'],
            expenses=self.mock_filtered_results['expenses'],
            planning=self.mock_filtered_results['planning']
        )
        self.assertEqual(response, "Rendered Index With Filters")


    @patch(PATCH_TARGET_PROCESS_DELETE)
    @patch(PATCH_TARGET_PROCESS_SUBMIT)
    @patch(PATCH_TARGET_FILTER_REPORTS)
    @patch(PATCH_TARGET_DATETIME)
    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_home_post(self, mock_request, mock_render, mock_dt, mock_filter_reports, mock_proc_submit, mock_proc_delete):
        mock_request.method = 'POST'
        mock_request.args = {} # Assume no args on POST for simplicity

        mock_filter_reports.return_value = self.mock_filtered_results
        mock_render.return_value = "Rendered Index After POST"

        response = home()

        mock_proc_submit.assert_called_once_with(mock_request, self.mock_user_instance)
        mock_proc_delete.assert_called_once_with(mock_request, self.mock_user_instance)

        # Verify it still falls through to filter and render
        mock_filter_reports.assert_called_once_with(
            user_id=self.mock_user_instance.id,
            amount_query=None,
            name_query=None,
            date=None,
            report_type=None
        )
        mock_render.assert_called_once_with(
            "index.html",
            user=self.mock_user_instance,
            income=self.mock_filtered_results['income'],
            expenses=self.mock_filtered_results['expenses'],
            planning=self.mock_filtered_results['planning']
        )
        self.assertEqual(response, "Rendered Index After POST")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)