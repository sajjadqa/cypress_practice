import faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from e2e_selenium_tests.BaseClasses.helper import generate_random_data_for_sso_enabled_user_ids_pattern
from e2e_selenium_tests.BaseClasses.base import BasePage


def generate_random_data_for_tvl_users():
    fake = faker.Faker()
    person_name = fake.name()
    user_email = fake.email()
    user_id = fake.profile(fields=['username'])['username']
    random_number_for_user_id = fake.random_number(3)
    user_name = user_id + str(random_number_for_user_id)
    user_name = user_name if len(user_name) < 15 else user_name[:14]
    user_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    return person_name, user_email, user_name, user_password


def set_values_to_add_new_tvl_user(person_name="", user_email="", user_id="", user_password="",
                                   user_role="", sso_user_format=False):
    """
    Assigning random generated values to new tvl user fields.
    :param : * string
    :return: dictionary
    """
    get_person_name, get_user_email,  get_user_name, get_user_password = generate_random_data_for_tvl_users()
    get_sso_user_format_ids = generate_random_data_for_sso_enabled_user_ids_pattern()
    add_new_tvl_user_fields = {
        'person_name': person_name or get_person_name,
        'user_email': user_email or get_user_email,
        'user_id': (get_sso_user_format_ids if sso_user_format else get_user_name),
        'user_password': user_password or get_user_password,
        'user_role': user_role
    }
    return add_new_tvl_user_fields


class TvaUsersMainPage(BasePage):
    ADD_NEW_USER_BUTTON = '#breadcrumb li [title="Add New User"]'
    PERSON_NAME = 'input[name="inName"]'
    PERSON_EMAIL = 'input[name="inEmail"]'
    USER_NAME = 'input[name="inUser"]'
    USER_PASSWORD = 'input[name="newUserP"]'
    CONFIRM_PASSWORD = 'input[name="newUserPCnf"]'
    SAVE_BUTTON = 'button[type="submit"]'
    USER_ID = '[name="formDetail"] tr:nth-of-type(2) td:nth-of-type(2)'
    ADD_PORT_BUTTON = '[title="Add Port"]'
    USER_ROLES = 'input[type="radio"]'
    USER_CREATION_ERROR = '[name="formDetail"] span[ng-bind-html="data.err.errMsg"]'

    def verify_browser_on_the_page(self):
        """Check for the presence of "Add new user" button """
        assert self.is_visible(self.ADD_NEW_USER_BUTTON)

    def click_on_add_new_user_button(self):
        """
        It will click on add new user button from add new user page.
        :return:
        """
        self.driver.find_element_by_css_selector(self.ADD_NEW_USER_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PERSON_NAME)),
                        "Add new user page is not loaded yet.")

    def fill_data_in_new_tvl_user_form(self, new_user_fields, role):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SAVE_BUTTON)))
        self.driver.find_element_by_css_selector(self.PERSON_NAME).send_keys(new_user_fields['person_name'])
        self.driver.find_element_by_css_selector(role).click()
        self.driver.find_element_by_css_selector(self.PERSON_EMAIL).send_keys(new_user_fields['user_email'])
        self.driver.find_element_by_css_selector(self.USER_NAME).send_keys(new_user_fields['user_id'])
        self.driver.find_element_by_css_selector(self.USER_PASSWORD).send_keys(new_user_fields['user_password'])
        self.driver.find_element_by_css_selector(self.CONFIRM_PASSWORD).send_keys(new_user_fields['user_password'])
        return new_user_fields['user_id'], new_user_fields['user_password']

    def click_on_save_user_button(self, sso_user_format=False):
        self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
        if sso_user_format:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_CREATION_ERROR)),
                            "This user name should not allowed for non sso airline")
            error_message = self.driver.find_element_by_css_selector(self.USER_CREATION_ERROR).text
            return error_message
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_CREATION_ERROR)))
            error = self.driver.find_element_by_css_selector(self.USER_CREATION_ERROR).text
            if error != "Username already in use. Please try different username.":
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_ID)))
                user_id = self.driver.find_element_by_css_selector(self.USER_ID).text
                return user_id
            return error

    def get_tvl_users_roles(self):
        user_roles_list = [
            ["finance", 'input[value="Finance"]'],
            ["operator", 'input[value="Operator"]'],
            ["supervisor", 'input[value="Supervisor"]'],
            ["read_only_user", 'input[value="Read Only User"]'],
            ["senior_management", 'input[value="Senior Management"]']
        ]
        return user_roles_list

    def get_current_url_of_tvl_user_page(self):
        """
        Gets the URL of the current page.
        :return: string
        """
        current_url = self.driver.current_url
        return current_url
