from old.tests.helper_tests import HelperTest


class LoginTest(HelperTest):
    """
    ERP login Test
    """

    def setUp(self):
        super(LoginTest, self).setUp()

    def test_landing_page(self):
        """
        Verify if user is on landing page(before login)
        """
        self.landing_page.visit()
        self.landing_page.is_browser_on_page()

    def test_login_scenario(self):
        """
        Verify user can loggedIn successfully
        """
        self.loggedIn_and_verification_of_home_page()
