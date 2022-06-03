import faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.constant import sleep
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL, IDP_URL
from selenium.common.exceptions import NoSuchElementException, InvalidElementStateException
from selenium.webdriver.common.keys import Keys


class SsoLoginMainPage(BasePage):
    USER_NAME = 'input[name="username"]'
    PASSWORD = 'input[name="password"]'
    LOGIN_BUTTON = 'button[id="submit_button"]'
    ERROR_MESSAGE_ON_LOGIN_FORM = 'div p strong'
    CREDENTIAL_REGEX = '^[a-z]\d{6}'
    ADD_NEW_USER_FORM = 'form[name="formUser"] > div'
    DISABLED_PERSON_NAME = 'input[name="name"][disabled="disabled"]'
    DISABLED_USER_EMAIL = 'input[name="email"][disabled="disabled"]'
    DISABLED_USER_ID = 'input[name="login"][disabled="disabled"]'
    DISABLED_USER_PASSWORD = 'input[name="password"][disabled="disabled"]'
    DISABLED_USER_ROLE = 'select[name="role"][disabled="disabled"]'
    DISABLED_PORT_TO_SERVICE = 'select[data-ng-model="data.userNew.port_id"][disabled="disabled"]'
    ENABLED_PERSON_NAME = 'input[name="name"]:not([disabled])'
    ENABLED_USER_EMAIL = 'input[name="email"]:not([disabled])'
    ENABLED_USER_ID = 'input[name="login"]:not([disabled])'
    ENABLED_USER_PASSWORD = 'input[name="password"]:not([disabled])'
    ENABLED_USER_ROLE = 'select[name="role"]:not([disabled])'
    ENABLED_PORT_TO_SERVICE = 'select[data-ng-model="data.userNew.port_id"]:not([disabled])'
    LOGOUT_BUTTON = '.navbar-right>li:nth-of-type(3) >a >i'
    LOGOUT = 'li[class="dropdown open"] ul[role="menu"] li:nth-of-type(3) a'
    EDIT_FIRST_USER_BUTTON = 'tr:nth-of-type(1) a[ng-click="users.edit($index);"]'
    DELETE_USER_BUTTON = 'tr:nth-of-type(1) td a[ng-click="users.remove($index);"]'
    DELETE_SSO_USER_BUTTON = '//td[contains(text(),"%s")]/following-sibling::td[1]//a[2]'
    DELETE_USERS = 'tr td a[ng-click="users.remove($index);"]'
    AIRLINE_DROPDOWN = '[ng-model="data.selected_airline"]'
    ADD_NEW_HOTEL_BUTTON = 'a[title="Add New Hotel"] i[class="fa fa-plus"]'

    def verify_browser_on_the_page(self):
        """check for the presence of "user_name" text field on sso login page."""
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_NAME)), "IDP page is not loaded.")
        assert self.is_visible(self.USER_NAME)

    def provide_credentials(self, username, password):
        self.driver.find_element_by_css_selector(self.USER_NAME).clear()
        self.driver.find_element_by_css_selector(self.USER_NAME).send_keys(username)
        self.driver.find_element_by_css_selector(self.PASSWORD).clear()
        self.driver.find_element_by_css_selector(self.PASSWORD).send_keys(password)

    def perform_error_validation(self):
        error_message = self.driver.find_element_by_css_selector(self.ERROR_MESSAGE_ON_LOGIN_FORM)
        return error_message.text

    def click_on_login_button(self):
        """ Click on the Login button"""
        self.driver.find_element_by_css_selector(self.LOGIN_BUTTON).click()
        sleep(2)
        try:
            self.driver.find_element_by_css_selector('[ng-model="data.selected_port"]')
        except:
            self.driver.find_element_by_css_selector('[id="dashboard-header"]')
        finally:
            return NoSuchElementException

    def open_new_tab(self):
        """Open IDP page in new tab of current browser"""
        # self.actions.send_keys(Keys.COMMAND + 't').perform()
        # self.actions.key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
        self.driver.execute_script("window.open('" + IDP_URL + "');")
        window_handle = self.driver.window_handles
        self.driver.switch_to.window(window_handle[1])

    def verify_employe_at_port_dashboard(self):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_DROPDOWN)))

    def disable_add_new_user_for_sso_airlines(self, super_user=False):
        """
        Add new user functionality should be disabled for united airline.
        :return:
        """
        try:
            if super_user:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_USER_FORM)))
                self.driver.find_element_by_css_selector(self.DISABLED_PERSON_NAME)
                self.driver.find_element_by_css_selector(self.DISABLED_USER_EMAIL)
                self.driver.find_element_by_css_selector(self.DISABLED_USER_ID)
                self.driver.find_element_by_css_selector(self.DISABLED_USER_PASSWORD)
                self.driver.find_element_by_css_selector(self.DISABLED_USER_ROLE)
                # self.driver.find_element_by_css_selector(self.DISABLED_PORT_TO_SERVICE)
            else:
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_USER_FORM)))
                # self.driver.find_element_by_css_selector(self.ADD_NEW_USER_FORM)
            return True
        except NoSuchElementException as e:
            element = self.driver.find_element_by_css_selector(self.ADD_NEW_USER_FORM)
            print("All add new users fields are not disabled for sso airline. ",
                  super_user, str(e), element.get_attribute('innerHTML'), self.driver.current_url)
            return False

    def enable_add_new_user_for_other_airlines(self):
        """
        Add new user functionality should be enabled for other than united airline.
        :return:
        """
        try:
            self.driver.find_element_by_css_selector(self.ENABLED_PERSON_NAME)
            self.driver.find_element_by_css_selector(self.ENABLED_USER_EMAIL)
            self.driver.find_element_by_css_selector(self.ENABLED_USER_ID)
            self.driver.find_element_by_css_selector(self.ENABLED_USER_PASSWORD)
            self.driver.find_element_by_css_selector(self.ENABLED_USER_ROLE)
            self.driver.find_element_by_css_selector(self.ENABLED_PORT_TO_SERVICE)
            return True
        except NoSuchElementException:
            return False

    def click_edit_user_button_for_it_support_user(self):
        try:
            self.driver.find_element_by_css_selector(self.EDIT_FIRST_USER_BUTTON).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ENABLED_USER_ROLE)))
        except NoSuchElementException:
            print("There are no airline users added yet.")

    def click_delete_user_button_for_it_support_user(self, user_id):
        try:
            delete_button = self.driver.find_element_by_xpath(self.DELETE_SSO_USER_BUTTON % user_id)
            self.driver.execute_script("arguments[0].click();", delete_button)
            self.driver.switch_to.alert.accept()
            return True
        except NoSuchElementException:
            print("There are no such airline user added yet.")
            return False

    def disable_user_edit_button_for_sso_airline(self):
        try:
            self.driver.find_element_by_css_selector(self.EDIT_FIRST_USER_BUTTON)
            return False
        except:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.EDIT_FIRST_USER_BUTTON)))
            return True

    def disable_user_delete_button_for_sso_airline(self):
        try:
            self.driver.find_element_by_css_selector(self.DELETE_USER_BUTTON)
            return False
        except:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DELETE_USER_BUTTON)))
            return True

    def verify_sso_user_non_editable_for_tvl_users(self, it_user=False):
        try:
            self.driver.find_element_by_css_selector(self.DISABLED_PERSON_NAME)
            self.driver.find_element_by_css_selector(self.DISABLED_USER_EMAIL)
            self.driver.find_element_by_css_selector(self.DISABLED_USER_ID)
            if it_user:
                self.driver.find_element_by_css_selector(self.ENABLED_USER_ROLE)
            else:
                self.driver.find_element_by_css_selector(self.DISABLED_USER_ROLE)
            self.driver.find_element_by_css_selector(self.DISABLED_PORT_TO_SERVICE)
            return True
        except NoSuchElementException:
            return False

    def logout_user(self, sso_logout=False):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.LOGOUT_BUTTON)))
        self.driver.find_element_by_css_selector(self.LOGOUT_BUTTON).click()
        if sso_logout:
            pass
        else:
            self.driver.find_element_by_css_selector(self.LOGOUT_BUTTON).click()
        self.driver.find_element_by_css_selector(self.LOGOUT).click()
        # assert "logout" in self.driver.current_url
        # self.wait.until(EC.url_to_be(TARGET_URL +
        #                              "/admin/index.php?logout=true&continue=admin%2Fquick-room-transfer.php"))
