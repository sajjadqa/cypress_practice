from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.constant import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


USERNAME = 'input#uID'
PASSWORD = 'input#uPwd'
NEW_PASSOWRD = '.newpassword'
LOGIN_BUTTON = 'button[name="mbrIN"]'
FORGOT_PASSWORD = 'a[id="goForForgot"]'
PLEASE_SIGNIN_TEXT_ON_LOGIN = '#divLogin LEGEND'
ERROR_MESSAGE_ON_LOGIN_FORM = 'div#divLogin>span>div'
ERROR_404_PAGE = '.hero-unit h1'
ERROR_CODE = '.hero-unit h1 small'
REFRESH_BUTTON = 'button#dashboard-refresh-button'
LOGIN_ERROR = '#divLogin #errorMsg'


class LoginMainPage(BasePage):

    def verify_browser_on_the_page(self):
        """check for the presence of "Forgot Password" Text on login page."""
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, FORGOT_PASSWORD)),
                        "StormX Login page is not loaded.")
        assert self.is_visible(FORGOT_PASSWORD)

    def provide_credentials(self, username, password):
        self.driver.find_element_by_css_selector(USERNAME).clear()
        self.driver.find_element_by_css_selector(USERNAME).send_keys(username)
        self.driver.find_element_by_css_selector(PASSWORD).clear()
        self.driver.find_element_by_css_selector(PASSWORD).send_keys(password)

    def perform_error_validation(self):
        error_message = self.driver.find_element_by_css_selector(ERROR_MESSAGE_ON_LOGIN_FORM)
        return error_message.text.strip("×\n")

    def invalid_url_redirection(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ERROR_404_PAGE)),
                        'User is not redirected to 404 page.')
        error_code = self.driver.find_element_by_css_selector(ERROR_CODE).text
        return error_code

    def click_on_login_button(self, new_password):
        """ Click on the Login button, go to home page """
        self.driver.find_element_by_css_selector(LOGIN_BUTTON).click()
        sleep(2)
        try:
            self.driver.find_element_by_css_selector(NEW_PASSOWRD).send_keys(new_password)
            self.driver.find_element_by_css_selector(LOGIN_BUTTON).click()
            sleep(1)
            return True
        except:
            try:
                login_error = self.driver.find_element_by_css_selector(LOGIN_ERROR)
                # print(login_error.text)
                return False
            except NoSuchElementException:
                return True
