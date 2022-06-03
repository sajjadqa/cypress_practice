from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL, INVALID_URL_PARAMS

TVL_USER_NAME = "support"
TVL_USER_PASSWORD = "test"
INVALID_PASSWORD = "invalid@password"
AIRLINE_USER_NAME = "sajjad.jq"
AIRLINE_USER_PASSWORD = "Tvlinc123!@"
NEW_PASSWORD = "Tvlinc123!@#@"


class TestLoginPage(TestBaseClass):
    def setUp(self):
        super(TestLoginPage, self).setUp()

    @ignore_warnings
    def test_login_success(self):
        """
        Verify that user is successfully logged in with valid credentials and Dashboard is fully loaded.
        """
        self.login_user(TVL_USER_NAME, TVL_USER_PASSWORD)
        self.assertIn("Ops Dashboard", self.login_page.get_page_html_source(), "Dashboard page is not fully loaded!")
        self.dashboard_page.verify_browser_on_the_page()

    @ignore_warnings
    def test_login_with_invalid_credentials(self):
        """
        Verify that user is not logged in with invalid credentials and error message is being displayed.
        """
        # errors = ['Incorrect Username or Password!', 'Oops! Seems there are some errors.']
        self.login_page.verify_browser_on_the_page()
        self.login_page.provide_credentials(TVL_USER_NAME, INVALID_PASSWORD)
        self.assertFalse(self.login_page.click_on_login_button(new_password=NEW_PASSWORD))
        self.assertIn('Incorrect Username or Password!', self.login_page.perform_error_validation(),
                      "Failed invalid credentials test")

    @ignore_warnings
    def test_invalid_url_redirection_without_login(self):
        """
        Verify that user should redirect to 404 page when invalid params are passed in url and user is not logged in.
        :return:
        """
        self.browser.get(STORMX_URL + INVALID_URL_PARAMS)
        self.assertEqual(self.login_page.invalid_url_redirection(), "Error 404")

    @ignore_warnings
    def test_invalid_url_redirection_with_login(self):
        """
        Verify that user should redirect to 404 page when invalid params are passed in url and user is logged in to app.
        :return:
        """
        self.login_user(TVL_USER_NAME, TVL_USER_PASSWORD)
        self.browser.get(STORMX_URL + INVALID_URL_PARAMS)
        self.assertEqual(self.login_page.invalid_url_redirection(), "Error 404")

    def tearDown(self):
        self.browser.close()
