from old.pages.common_helper_func import HelperFunctions
from selenium.webdriver.common.keys import Keys
from old.constants import EMAIL_FIELD_CSS, PWD_FIELD_CSS, USER_EMAIL, USER_PWD
import time


class LoginPage(HelperFunctions):
    """
    Google Login Page
    """

    def enter_verified_email(self, useremail):
        """
        Enter verified email
        :param useremail: verified user account
        """
        self.wait_for_visibility_of_element(EMAIL_FIELD_CSS)
        user_email_field = self.wait_for_an_element_to_be_present(EMAIL_FIELD_CSS)
        user_email_field.send_keys(useremail)
        user_email_field.send_keys(Keys.RETURN)

    def enter_verified_pwd(self, userpassword):
        """
        Enter correct password
        :param userpassword: verified account password
        """
        self.wait_for_visibility_of_element(PWD_FIELD_CSS)
        self.wait_for_ajax()
        time.sleep(2)
        user_pwd_field = self.wait_for_an_element_to_be_present(PWD_FIELD_CSS)
        user_pwd_field.send_keys(userpassword)
        user_pwd_field.send_keys(Keys.RETURN)

    def login(self):
        """
        Enter user email
        Enter user password
        Switch driver to default content
        """
        window = self.driver.window_handles[-1]
        self.driver.switch_to.window(window)
        self.enter_verified_email(USER_EMAIL)
        self.enter_verified_pwd(USER_PWD)

        # switch to default window
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.wait_for_ajax()
        time.sleep(3)
