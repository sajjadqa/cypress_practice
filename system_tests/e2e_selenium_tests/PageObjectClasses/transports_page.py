import faker
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from e2e_selenium_tests.BaseClasses.helper import value_selector_for_searchable_drop_downs, \
    generate_random_data_for_sso_enabled_user_ids_pattern
from selenium.webdriver.common.by import By
from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL


def generate_random_data_for_transport_users():
    fake = faker.Faker()
    person_name = fake.name()
    user_email = fake.email()
    user_id = fake.profile(fields=['username'])['username']
    random_number_for_user_id = fake.random_number(3)
    user_name = user_id + str(random_number_for_user_id)
    user_name = user_name if len(user_name) < 15 else user_name[:14]
    user_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    return person_name, user_email, user_name, user_password


def set_values_to_add_new_transport_user(person_name="", user_email="", user_id="", user_password="",
                                         sso_user_format=False):
    """
    Assigning random generated values to new transport user fields.
    :param : * string
    :return: dictionary
    """
    get_person_name, get_user_email,  get_user_name, get_user_password = generate_random_data_for_transport_users()
    get_sso_user_format_ids = generate_random_data_for_sso_enabled_user_ids_pattern()
    add_new_transport_user_fields = {
        'person_name': person_name or get_person_name,
        'user_email': user_email or get_user_email,
        'user_id': (get_sso_user_format_ids if sso_user_format else get_user_name),
        'user_password': user_password or get_user_password,
    }
    return add_new_transport_user_fields


class TransportMainPage(BasePage):
    ADD_NEW_TRANSPORT_BUTTON = 'a[title="Add New Transport"] i[class="fa fa-plus"]'
    TRANSPORT_ID = 'tr:first-of-type td strong'
    TRANSPORT_NAME = 'input[name="transport_name"]'
    TRANSPORT_INFORMATION = '#page_links'
    TRANSPORT_SEARCH_FILTER = 'input[ng-model="filter.tid"][placeholder="type transport name/ids here e.g 116, 140"]'
    USERS_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'2\'"]'
    PORTS_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'1\'"]'
    PERSON_NAME = 'input[name="name"]'
    USER_EMAIL = 'input[name="email"]'
    USER_ID = 'input[name="login"]'
    USER_PASSWORD = 'input[name="password"]'
    USER_ROLE = 'select[name="role"]'
    PORT_TO_SERVICE = 'select[data-ng-model="data.userNew.port_id"]'
    SAVE_NEW_USER_BUTTON = '[name="formUser"] .table-no-borders .btn-primary'
    RESET_NEW_USER_BUTTON = '[name="formUser"] .table-no-borders .btn-danger'
    EDIT_USER_BUTTON = 'td a .fa-edit'
    SEARCH_BUTTON = 'button#btnSearch'
    REFRESH_SPINNER = '[class="dropdown ng-hide"] strong'
    TRANSPORT_BUTTONS = '.page-listing-results .table-no-borders .btn-group'
    TRANSPORT_DETAILS_BUTTON = 'button[title="Detail"]'

    def verify_browser_on_the_page(self):
        """Check for the presence of transport name/ids search filter on transport listing page."""
        assert self.is_visible(self.TRANSPORT_SEARCH_FILTER)

    def click_on_users_tab_from_transport_details(self):
        self.driver.find_element_by_css_selector(self.USERS_TAB).click()

    def fill_data_in_new_transport_user(self, new_user_fields):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SAVE_NEW_USER_BUTTON)))
        self.driver.find_element_by_css_selector(self.PERSON_NAME).send_keys(new_user_fields['person_name'])
        self.driver.find_element_by_css_selector(self.USER_EMAIL).send_keys(new_user_fields['user_email'])
        self.driver.find_element_by_css_selector(self.USER_ID).send_keys(new_user_fields['user_id'])
        self.driver.find_element_by_css_selector(self.USER_PASSWORD).send_keys(new_user_fields['user_password'])
        return new_user_fields['user_id'], new_user_fields['user_password']

    def click_on_save_user_button(self, sso_user_format=False):
        self.driver.find_element_by_css_selector(self.SAVE_NEW_USER_BUTTON).click()
        if sso_user_format:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger ul li")),
                            "This user name should not allowed for non sso airline")
            error_message = self.driver.find_element_by_css_selector(".alert-danger ul li").text
            self.driver.find_element_by_css_selector(self.RESET_NEW_USER_BUTTON).click()
            return error_message
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EDIT_USER_BUTTON)),
                            "Something is missing while creating new airline user.")

    def open_transport_detail_page_via_api(self, transport):
        self.driver.get(STORMX_URL + '/admin/transport_detail.php?rid=' + str(transport))

    def transport_search_filter(self, transport):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TRANSPORT_SEARCH_FILTER)))
        self.driver.find_element_by_css_selector(self.TRANSPORT_SEARCH_FILTER).send_keys(transport)
        self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))

    def open_transport_details_page(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TRANSPORT_BUTTONS)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.TRANSPORT_DETAILS_BUTTON)))
        self.driver.find_element_by_css_selector(self.TRANSPORT_DETAILS_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TRANSPORT_NAME)))
