import unittest
from unittest.mock import patch, Mock, MagicMock
from flask import Flask

from website.auth import login, register

PATCH_TARGET_RENDER = 'website.auth.render_template'
PATCH_TARGET_REQUEST = 'website.auth.request'
PATCH_TARGET_FLASH = 'website.auth.flash'
PATCH_TARGET_REDIRECT = 'website.auth.redirect'
PATCH_TARGET_URL_FOR = 'website.auth.url_for'
PATCH_TARGET_USER_MODEL = 'website.auth.User'
PATCH_TARGET_GEN_HASH = 'website.auth.generate_password_hash'
PATCH_TARGET_CHECK_HASH = 'website.auth.check_password_hash'
PATCH_TARGET_DB = 'website.auth.db'
PATCH_TARGET_LOGIN_USER = 'website.auth.login_user'
PATCH_TARGET_CURRENT_USER = 'website.auth.current_user'


class TestAuthViews(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'testing_auth'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.req_context = self.app.test_request_context()
        self.req_context.push()

        self.mock_user_proxy_instance = Mock(is_authenticated=False)  # Default mock for current_user
        self.patcher_current_user = patch(PATCH_TARGET_CURRENT_USER, self.mock_user_proxy_instance)
        self.patcher_current_user.start()

        self.addCleanup(self.req_context.pop)
        self.addCleanup(self.app_context.pop)
        self.addCleanup(self.patcher_current_user.stop)

    # --- Login Tests ---

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_login_get(self, mock_request, mock_render):
        mock_request.method = 'GET'
        mock_render.return_value = "Login Page"

        response = login()

        mock_render.assert_called_once_with("login.html", user=self.mock_user_proxy_instance)
        self.assertEqual(response, "Login Page")

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_CHECK_HASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_login_post_user_not_found(self, mock_request, MockUser, mock_check_hash, mock_flash, mock_render):
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.side_effect = lambda key: {'username': 'testuser', 'password': 'password123'}.get(key)
        MockUser.query.filter_by.return_value.first.return_value = None  # User not found
        mock_render.return_value = "Login Page Rendered Again"

        response = login()

        MockUser.query.filter_by.assert_called_once_with(username='testuser')
        mock_check_hash.assert_not_called()
        mock_flash.assert_called_once_with("Username does not exist, please try again.", "error")
        mock_render.assert_called_once_with("login.html", user=self.mock_user_proxy_instance)
        self.assertEqual(response, "Login Page Rendered Again")

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_CHECK_HASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_login_post_incorrect_password(self, mock_request, MockUser, mock_check_hash, mock_flash, mock_render):
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.side_effect = lambda key: {'username': 'testuser', 'password': 'wrongpassword'}.get(key)

        mock_found_user = Mock()
        mock_found_user.password = "hashed_password"
        MockUser.query.filter_by.return_value.first.return_value = mock_found_user

        mock_check_hash.return_value = False  # Password check fails
        mock_render.return_value = "Login Page Rendered Again"

        response = login()

        MockUser.query.filter_by.assert_called_once_with(username='testuser')
        mock_check_hash.assert_called_once_with("hashed_password", "wrongpassword")
        mock_flash.assert_called_once_with("Incorrect password, please try again.", "error")
        mock_render.assert_called_once_with("login.html", user=self.mock_user_proxy_instance)
        self.assertEqual(response, "Login Page Rendered Again")

    @patch(PATCH_TARGET_URL_FOR)
    @patch(PATCH_TARGET_REDIRECT)
    @patch(PATCH_TARGET_LOGIN_USER)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_CHECK_HASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_login_post_success(self, mock_request, MockUser, mock_check_hash, mock_flash, mock_login_user, mock_redirect, mock_url_for):
        mock_request.method = 'POST'
        mock_request.form = MagicMock()
        mock_request.form.get.side_effect = lambda key: {'username': 'testuser', 'password': 'correctpassword'}.get(key)

        mock_found_user = Mock()
        mock_found_user.password = "hashed_password"
        MockUser.query.filter_by.return_value.first.return_value = mock_found_user

        mock_check_hash.return_value = True  # Password check succeeds
        mock_url_for.return_value = "/fake/home"
        mock_redirect.return_value = "Redirected Home"

        response = login()

        MockUser.query.filter_by.assert_called_once_with(username='testuser')
        mock_check_hash.assert_called_once_with("hashed_password", "correctpassword")
        mock_flash.assert_called_once_with("Login successful!", "success")
        mock_login_user.assert_called_once_with(mock_found_user, remember=True)
        mock_url_for.assert_called_once_with("views.home")
        mock_redirect.assert_called_once_with("/fake/home")
        self.assertEqual(response, "Redirected Home")

    # --- Register Tests ---

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_REQUEST)
    def test_register_get(self, mock_request, mock_render):
        mock_request.method = 'GET'
        mock_render.return_value = "Register Page"

        response = register()

        mock_render.assert_called_once_with("register.html", user=self.mock_user_proxy_instance)
        self.assertEqual(response, "Register Page")

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_register_post_username_exists(self, mock_request, MockUser, mock_flash, mock_render):
        mock_request.method = 'POST'
        mock_request.form = {'username': 'existinguser', 'password': 'password123'}
        mock_render.return_value = "Register Page Rendered Again"
        MockUser.query.filter_by.return_value.first.return_value = Mock()  # User exists

        response = register()

        MockUser.query.filter_by.assert_called_once_with(username='existinguser')
        mock_flash.assert_called_once_with("Username already exists", "error")
        mock_render.assert_called_once_with("register.html")
        self.assertEqual(response, "Register Page Rendered Again")

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_register_post_username_too_short(self, mock_request, MockUser, mock_flash, mock_render):
        mock_request.method = 'POST'
        mock_request.form = {'username': 'usr', 'password': 'password123'}
        mock_render.return_value = "Register Page Rendered Again"
        MockUser.query.filter_by.return_value.first.return_value = None  # User does not exist

        response = register()

        MockUser.query.filter_by.assert_called_once_with(username='usr')
        mock_flash.assert_called_once_with("Username must be at least 4 characters long", "error")
        mock_render.assert_called_once_with("register.html")
        self.assertEqual(response, "Register Page Rendered Again")

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_register_post_password_too_short(self, mock_request, MockUser, mock_flash, mock_render):
        mock_request.method = 'POST'
        mock_request.form = {'username': 'gooduser', 'password': 'pass'}
        mock_render.return_value = "Register Page Rendered Again"
        MockUser.query.filter_by.return_value.first.return_value = None  # User does not exist

        response = register()

        MockUser.query.filter_by.assert_called_once_with(username='gooduser')
        mock_flash.assert_called_once_with("Password must be at least 8 characters long", "error")
        mock_render.assert_called_once_with("register.html")
        self.assertEqual(response, "Register Page Rendered Again")

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_register_post_username_equals_password(self, mock_request, MockUser, mock_flash, mock_render):
        mock_request.method = 'POST'
        mock_request.form = {'username': 'password123', 'password': 'password123'}
        mock_render.return_value = "Register Page Rendered Again"
        MockUser.query.filter_by.return_value.first.return_value = None  # User does not exist

        response = register()

        MockUser.query.filter_by.assert_called_once_with(username='password123')
        mock_flash.assert_called_once_with("Username and password cannot be the same", "error")
        mock_render.assert_called_once_with("register.html")
        self.assertEqual(response, "Register Page Rendered Again")

    @patch(PATCH_TARGET_RENDER)
    @patch(PATCH_TARGET_DB)
    @patch(PATCH_TARGET_GEN_HASH)
    @patch(PATCH_TARGET_FLASH)
    @patch(PATCH_TARGET_USER_MODEL)
    @patch(PATCH_TARGET_REQUEST)
    def test_register_post_success(self, mock_request, MockUser, mock_flash, mock_gen_hash, mock_db, mock_render):
        username = 'newuser'
        password = 'newpassword123'
        hashed_pw = 'hashed_newpassword123'

        mock_request.method = 'POST'
        mock_request.form = {'username': username, 'password': password}
        mock_render.return_value = "Login Page Rendered"
        MockUser.query.filter_by.return_value.first.return_value = None  # User does not exist
        mock_gen_hash.return_value = hashed_pw

        mock_new_user_instance = Mock()
        MockUser.return_value = mock_new_user_instance

        response = register()

        MockUser.query.filter_by.assert_called_once_with(username=username)
        mock_flash.assert_called_once_with("Registration successful! Now you can login.", "success")
        mock_gen_hash.assert_called_once_with(password, method="pbkdf2:sha256")
        MockUser.assert_called_once_with(username=username, password=hashed_pw)
        mock_db.session.add.assert_called_once_with(mock_new_user_instance)
        mock_db.session.commit.assert_called_once()
        mock_render.assert_called_once_with("login.html")
        self.assertEqual(response, "Login Page Rendered")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)