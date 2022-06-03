import faker
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import Select
from e2e_selenium_tests.BaseClasses.helper import value_selector_for_searchable_drop_downs, \
    generate_random_data_for_sso_enabled_user_ids_pattern, value_selector_for_drop_downs
from selenium.webdriver.common.by import By
from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.constant import sleep, STORMX_URL


def generate_random_data_for_new_airline():
    fake = faker.Faker()
    airline_name = fake.first_name()
    airline_prefix = fake.first_name()
    flight_prefix = fake.first_name()
    state = fake.state()
    post_code = fake.random_number(4)
    street_address = fake.first_name()
    notes = fake.name()
    corporate_person = fake.name()
    corporate_email = fake.email()
    corporate_phone = fake.random_number(6)
    corporate_url = fake.url()
    finance_person = fake.name()
    finance_phone = fake.random_number(7)
    finance_email = fake.email()
    sales_phone = fake.random_number(7)
    sales_url = fake.url()
    return airline_name, airline_prefix, flight_prefix, state, post_code, street_address, notes, corporate_person, \
        corporate_email, corporate_phone, corporate_url, finance_person, finance_phone, finance_email, sales_phone, \
        sales_url


def generate_random_data_for_airline_users():
    fake = faker.Faker()
    person_name = fake.name()
    user_email = fake.email()
    user_id = fake.profile(fields=['username'])['username']
    random_number_for_user_id = fake.random_number(3)
    user_name = user_id + str(random_number_for_user_id)
    user_name = user_name if len(user_name) < 15 else user_name[:14]
    user_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    return person_name, user_email, user_name, user_password


def set_values_to_new_airline_fields(airline_name="", airline_prefix="", flight_prefix="", airline_brand="CanJet",
                                     country="PAK", state="",
                                     suburb="Abc Testing", post_code="", street_address1="", street_address2="",
                                     notes="",
                                     corporate_person="", corporate_phone="", corporate_email="", corporate_fax="",
                                     corporate_url="", finance_person="", finance_email="", finance_phone="",
                                     sales_phone="", sales_url=""):
    """
    Assigning random generated values to new airline fields.
    :param  * strings
    :return: dictionary
    """
    get_airline_name, get_airline_prefix, get_flight_prefix, get_state, get_post_code, get_street_address, get_notes, \
        get_corporate_person, get_corporate_email, get_corporate_phone, get_corporate_url, get_finance_person, \
        get_finance_phone, get_finance_email, get_sales_phone, get_sales_url = generate_random_data_for_new_airline()
    add_new_airline_fields = {
        'airline_name': airline_name or "Air " + get_airline_name,
        'airline_prefix': airline_prefix or get_airline_prefix,
        'flight_prefix': flight_prefix or get_flight_prefix,
        'airline_brand': airline_brand,
        'country': country,
        'state': state or get_state,
        'suburb': suburb,
        'post_code': post_code or get_post_code,
        'street_address1': street_address1 or get_street_address,
        'street_address2': street_address2,
        'notes': notes or get_notes,
        'corporate_person': corporate_person or get_corporate_person,
        'corporate_phone': corporate_phone or get_corporate_phone,
        'corporate_email': corporate_email or get_corporate_email,
        'corporate_fax': corporate_fax,
        'corporate_url': corporate_url or get_corporate_url,
        'finance_person': finance_person or get_finance_person,
        'finance_email': finance_email or get_finance_email,
        'finance_phone': finance_phone or get_finance_phone,
        'sales_phone': sales_phone or get_sales_phone,
        'sales_url': sales_url or get_sales_url
    }
    return add_new_airline_fields


def set_values_to_add_new_airline_user(person_name="", user_email="", user_id="", user_password="",
                                       user_role="", port_to_service="", sso_user_format=False):
    """
    Assigning random generated values to new airline user fields.
    :param : * string
    :return: dictionary
    """
    get_person_name, get_user_email,  get_user_name, get_user_password = generate_random_data_for_airline_users()
    get_sso_user_format_ids = generate_random_data_for_sso_enabled_user_ids_pattern()
    add_new_airline_user_fields = {
        'person_name': person_name or get_person_name,
        'user_email': user_email or get_user_email,
        'user_id': (get_sso_user_format_ids if sso_user_format else get_user_name),
        'user_password': user_password or get_user_password,
        'user_role': user_role,
        'port_to_service': port_to_service
    }
    return add_new_airline_user_fields


class AirlineMainPage(BasePage):
    ADD_NEW_AIRLINE_BUTTON = 'a[title="Add New Airline"] i[class="fa fa-plus"]'
    AIRLINE_ID_LISTING = 'tr:nth-of-type(1) input.copy-text-input'
    AIRLINE_ID_VALUE = 'input[value="%s"]'
    AIRLINE_ID = 'tr:first-of-type td strong'
    AIRLINE_INFORMATION = '#page_links'
    AIRLINE_NAME = '//form[@name="formDetail"]//td//input[@name="airline_name"]'
    AIRLINE_PREFIX = 'input[name="airline_prefix"]'
    FLIGHT_PREFIX = 'input[name="airline_flight_prefix"]'
    AIRLINE_BRAND = 'select[id="airline_brand_id"]'
    COUNTRY = 'select[id="airline_country"]'
    STATE = 'input[name="airline_state"]'
    SUBURB = 'input[name="airline_suburb"]'
    POST_CODE = 'input[name="airline_postcode"]'
    STREET_ADDRESS1 = 'input[name="airline_address1"]'
    STREET_ADDRESS2 = 'input[name="airline_address2"]'
    NOTES = 'textarea[name="airline_notes"]'
    CORPORATE_CONTACT_PERSON = 'input[name="airline_contact_person"]'
    CORPORATE_CONTACT_PHONE = 'input[name="airline_contact_phone"]'
    CORPORATE_CONTACT_EMAIL = 'input[name="airline_contact_email"]'
    CORPORATE_CONTACT_FAX = 'input[name="airline_contact_fax"]'
    CORPORATE_CONTACT_URL = 'input[name="airline_url"]'
    FINANCE_CONTACT_PERSON = 'input[name="airline_finance_contact"]'
    FINANCE_CONTACT_PHONE = 'input[name="airline_finance_phone"]'
    FINANCE_CONTACT_EMAIL = 'input[name="airline_finance_email"]'
    SALES_CONTACT_PHONE = 'input[name="airline_booking_phone"]'
    SALES_CONTACT_URL = 'input[name="airline_booking_url"]'
    SAVE_BUTTON = '.page-header>.pull-right>.btn-primary'
    AIRLINE_SEARCH_FILTER = 'input[ng-model="filter.aid"][placeholder="type airline name/ids here e.g 116, 140"]'
    USERS_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'1\'"]'
    PORTS_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'2\'"]'
    PORTS_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'2\'"]'
    PERSON_NAME = 'input[name="name"]'
    USER_EMAIL = 'input[name="email"]'
    USER_ID = 'input[name="login"]'
    USER_PASSWORD = 'input[name="password"]'
    USER_ROLE = 'select[name="role"]'
    PORT_TO_SERVICE = 'select[data-ng-model="data.userNew.port_id"]'
    _PORTS_LIST = 'select[data-ng-model="data.userNew.port_id"] option'
    PORT_SELECTED = 'select[data-ng-model="data.userNew.port_id"]+span'
    SAVE_NEW_USER_BUTTON = '[name="formUser"] .table-no-borders .btn-primary'
    RESET_NEW_USER_BUTTON = '[name="formUser"] .table-no-borders .btn-danger'
    EDIT_USER_BUTTON = 'td a .fa-edit'
    USER_CREATION_ERRORS = '[name="formUser"] .ng-dirty+div'
    PORT_FILTER = 'div[ng-model="%s"] button:first-of-type'
    PORT_INPUT = 'input[class="form-control ui-select-search ng-pristine ng-valid"]'
    PORTS_LIST = 'ul li div.ui-select-choices-row'
    REFRESH_SPINNER = '[class="dropdown ng-hide"] strong'
    PAGINATION = 'li a[ng-click="selectPage(1)"]'
    ADD_PORT_BUTTON = 'button[ng-click="ports.add()"] i'
    ADD_PORT_BUTTON_DISABLE = 'button[ng-click="ports.add()"][disabled="disabled"] i'
    PORTS_CONTACT = '.active div:nth-of-type(2) h4 span'
    SERVICED_PORT = 'tr:nth-of-type(3).info td:first-of-type[ng-click="ports.onSelect($index)"]'
    USER_INFO_DROPDOWN = '.navbar-right>li:nth-of-type(5) >a >i'
    LOGOUT_BUTTON_OTHER_USERS = '.navbar-right>li:nth-of-type(2) >a >i'
    LOGOUT = 'li[class="dropdown open"] ul[role="menu"] li:nth-of-type(5) a'
    LOGOUT_OTHER_USERS = 'li[class="dropdown open"] ul[role="menu"] li:nth-of-type(3) a'
    ADDITIONAL_CONTACTS_BUTTON = 'button[title="Additional Contacts"]'
    REFRESH_ADDITIONAL_CONTACTS_BUTTON = 'button[title="Refresh Additonal Contacts"]'
    CONTACT_TYPE = 'tr:nth-of-type(2) div[ng-model="d.contactType"]'
    CONTACT_NAME = 'tr:nth-of-type(2) input[ng-model="d.name"]'
    CONTACT_PHONE = 'tr:nth-of-type(2) input[id="phone"]'
    CONTACT_EMAIL = 'tr:nth-of-type(2) input[id="email"]'
    CONTACT_ADDRESS = 'tr:nth-of-type(2) textarea[id="address"]'
    CONTACT_ADD_BUTTON = 'tr:nth-of-type(2) [type="button"] i'
    LAST_UPDATED_BY = 'tr:nth-of-type(3) [id="lastUpdated"]'
    CONTACT_DELETE = 'tr:nth-of-type(1) td a[ng-click="contacts.remove(d);"]'
    MAIN_WINDOW_HANDLER = ""
    NO_CONTACT_MESSAGE = 'tr[ng-if="filteredContacts.length==0"] td'
    SERVICED_PORTS_LIST = 'tr.anim-data td[ng-click="ports.onSelect($index)"]'
    BLOG_MESSAGES_BUTTON = 'tr:nth-of-type(1) button[title="Messages"]'
    NEW_MESSAGE_TEXTAREA = 'textarea[name="blogMessage"]'
    SAVE_MESSAGE_BUTTON = '[name="formBlog"] button[type="submit"]'
    SAVE_MESSAGE_BUTTON_CLICK = "$('[name=\"formBlog\"] button[type=\"submit\"]').click()"
    RESET_MESSAGE_BUTTON = '[name="formBlog"] button[ng-click="data.newMessage={}"]'
    CLOSE_MESSAGE_MODAL = '[name="formBlog"] button[ng-click="cancel()"]'
    CLOSE_MESSAGE_MODAL_BUTTON = '$(\'[name="formBlog"] button[ng-click="cancel()"]\').click()'
    MESSAGE_AT_BLOG_FORM = 'ul:first-of-type .chat-body p'
    MESSAGE_REQUIRED_ERROR = '[name="blogMessage"]+div'
    BLOG_MESSAGES_SPINNER = '[class="modal-title ng-binding"] i'
    MESSAGE_MARK_AS_UNREAD = 'ul:first-of-type [title="Mark as UnRead"] i[ng-click="markRead(d)"]'
    MESSAGE_MARK_AS_READ = 'ul:first-of-type [title="Mark as Read"] i.fa-envelope'
    MESSAGE_UNREAD_ON_LISTING = '[title="Messages"] span'
    CONTACT_TYPE_MODAL = 'd.contactType'
    CONTACT_TYPE_PLACEHOLDER = 'Type'
    CONTACT_TYPE_VALUE = 'IT Personnel'
    SERVICED_PORT_MODAL = 'data.portServiceNew'
    SERVICED_PORT_PLACEHOLDER = 'Type port name or prefix'
    CONTACT_PORT_MODAL = 'd.contactPort'
    CONTACT_PORT_PLACEHOLDER = 'Port'
    SEARCH_BUTTON = 'button#btnSearch'
    SEARCH_BUTTON_DISABLE = 'button#btnSearch[disabled="disabled"]'
    BLOG_MESSAGES_MODAL = 'form[name="formBlog"]'
    INACTIVE_AIRLINE = '.form-inline i[title="In-Active"]'
    AIRLINE_DETAILS_BUTTON = 'button[title="Detail"]'
    AIRLINE_BUTTONS = '.page-listing-results .table-no-borders .btn-group'
    NO_PORTS_TEXT = '[ng-if="data.portsServiced.length==0"] [class="text-danger"]'
    USER_DELETE = 'tr:first-of-type  a[ng-click="users.remove($index);"]'
    USER_UPDATE = 'tr:first-of-type .fa-edit'
    MANDATORY_FIELDS_ERRORS = '//form[@name="formDetail"]//tr//td[2]//input[@ng-required="true"]' \
                              '//following-sibling::div[1][not(contains(@class, "ng-hide"))]'

    def verify_browser_on_the_page(self):
        """Check for the presence of airline name/ids search filter on airline listing page."""
        assert self.is_visible(self.AIRLINE_SEARCH_FILTER)

    def verify_default_selected_status_filter_airlines_on_page(self):
        """
        Verify that on page loading only active status airlines should be visible on page.
        :return:
        """
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        inactive_airlines = self.driver.find_elements_by_css_selector(self.INACTIVE_AIRLINE)
        if inactive_airlines:
            return False
        else:
            return True

    def click_on_add_new_airline_button(self):
        """
        It will click on add new airline button from airline listing page.
        :return:
        """
        self.driver.find_element_by_css_selector(self.ADD_NEW_AIRLINE_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SAVE_BUTTON)),
                        "Add new airline page is not fully loaded.")

    def click_on_blog_messages_button(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_BUTTON)))
        self.wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_SPINNER)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.BLOG_MESSAGES_BUTTON)))
        self.driver.find_element_by_css_selector(self.BLOG_MESSAGES_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_SPINNER)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SAVE_MESSAGE_BUTTON)))

    def fill_data_in_new_airline_form(self, airline_fields):
        # self.driver.find_element_by_xpath(self.AIRLINE_NAME).send_keys(airline_fields["airline_name"])
        # self.driver.find_element_by_css_selector(self.AIRLINE_PREFIX).send_keys(airline_fields["airline_prefix"])
        # self.driver.find_element_by_css_selector(self.FLIGHT_PREFIX).send_keys(airline_fields["flight_prefix"])
        self.driver.find_element_by_css_selector(self.AIRLINE_BRAND).send_keys(airline_fields["airline_brand"])
        self.actions.send_keys(Keys.TAB).perform()
        self.driver.find_element_by_css_selector(self.COUNTRY).send_keys(airline_fields["country"])
        self.actions.send_keys(Keys.TAB).perform()
        self.driver.find_element_by_css_selector(self.STATE).send_keys(airline_fields["state"])
        self.driver.find_element_by_css_selector(self.SUBURB).send_keys(airline_fields["suburb"])
        self.driver.find_element_by_css_selector(self.POST_CODE).send_keys(airline_fields["post_code"])
        self.driver.find_element_by_css_selector(self.STREET_ADDRESS1).send_keys(airline_fields["street_address1"])
        self.driver.find_element_by_css_selector(self.STREET_ADDRESS2).send_keys(airline_fields["street_address1"])
        self.driver.find_element_by_css_selector(self.NOTES).send_keys(airline_fields["notes"])
        self.driver.find_element_by_xpath(self.AIRLINE_NAME).send_keys(airline_fields["airline_name"])
        self.driver.find_element_by_css_selector(self.AIRLINE_PREFIX).send_keys(airline_fields["airline_prefix"])
        self.driver.find_element_by_css_selector(self.FLIGHT_PREFIX).send_keys(airline_fields["flight_prefix"])
        self.driver.find_element_by_css_selector(self.CORPORATE_CONTACT_PERSON).send_keys(
            airline_fields["corporate_person"])
        self.driver.find_element_by_css_selector(self.CORPORATE_CONTACT_PHONE).send_keys(
            airline_fields["corporate_phone"])
        self.driver.find_element_by_css_selector(self.CORPORATE_CONTACT_EMAIL).send_keys(
            airline_fields["corporate_email"])
        self.driver.find_element_by_css_selector(self.CORPORATE_CONTACT_URL).send_keys(airline_fields["corporate_url"])
        self.driver.find_element_by_css_selector(self.FINANCE_CONTACT_PERSON).send_keys(
            airline_fields["finance_person"])
        self.driver.find_element_by_css_selector(self.FINANCE_CONTACT_EMAIL).send_keys(airline_fields["finance_email"])
        self.driver.find_element_by_css_selector(self.FINANCE_CONTACT_PHONE).send_keys(airline_fields["finance_phone"])
        self.driver.find_element_by_css_selector(self.SALES_CONTACT_PHONE).send_keys(airline_fields["sales_phone"])
        self.driver.find_element_by_css_selector(self.SALES_CONTACT_URL).send_keys(airline_fields["sales_url"])

    def click_on_airline_save_button(self):
        self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
        error = self.driver.find_elements_by_xpath(self.MANDATORY_FIELDS_ERRORS)
        if error:
            print([error.text for error in error], "check is not working on page.")
            return False, ""
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USERS_TAB)),
                            "Airline is not added successfully.")
            airline_id = self.driver.find_element_by_css_selector(self.AIRLINE_ID).text
            return True, airline_id

    def get_current_url_of_airline_page(self):
        """
        Gets the URL of the current page.
        :return: string
        """
        current_url = self.driver.current_url
        return current_url

    def get_airline_user_roles(self):
        roles_list = self.driver.find_elements_by_css_selector('[data-ng-model="data.userNew.role"] option')
        return [user_role.text for user_role in roles_list]

    def click_on_users_tab_from_airline_details(self):
        self.driver.find_element_by_css_selector(self.USERS_TAB).click()

    def click_on_ports_tab_from_airline_details(self):
        self.driver.find_element_by_css_selector(self.PORTS_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORTS_ACTIVE_TAB)),
                        "Ports Tab is not selected")

    def fill_data_in_contacts_form(self, new_contact_fields):
        value_selector_for_searchable_drop_downs(self, self.CONTACT_TYPE_VALUE, self.CONTACT_TYPE_MODAL,
                                                 self.CONTACT_TYPE_PLACEHOLDER)
        self.driver.find_element_by_css_selector(self.CONTACT_NAME).send_keys(new_contact_fields['corporate_person'])
        self.driver.find_element_by_css_selector(self.CONTACT_PHONE).send_keys(new_contact_fields['corporate_phone'])
        self.driver.find_element_by_css_selector(self.CONTACT_EMAIL).send_keys(new_contact_fields['corporate_email'])
        self.driver.find_element_by_css_selector(self.CONTACT_ADDRESS).send_keys(new_contact_fields['street_address1'])
        self.driver.find_element_by_css_selector(self.CONTACT_ADD_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.LAST_UPDATED_BY)),
                        "Contact is not added successfully.")
        last_updated_by = self.driver.find_element_by_css_selector(self.LAST_UPDATED_BY).text
        return last_updated_by

    def fill_data_in_new_airline_user(self, new_user_fields, port_id):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SAVE_NEW_USER_BUTTON)))
        self.driver.find_element_by_css_selector(self.PERSON_NAME).send_keys(new_user_fields['person_name'])
        self.driver.find_element_by_css_selector(self.USER_EMAIL).send_keys(new_user_fields['user_email'])
        self.driver.find_element_by_css_selector(self.USER_ID).send_keys(new_user_fields['user_id'])
        self.driver.find_element_by_css_selector(self.USER_PASSWORD).send_keys(new_user_fields['user_password'])
        self.driver.find_element_by_css_selector(self.USER_ROLE).send_keys(new_user_fields['user_role'])
        if new_user_fields['user_role'] == "Employee at Port" or new_user_fields['user_role'] == "Port Manager":
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORT_TO_SERVICE)))
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, self._PORTS_LIST)))
            list_of_ports = self.driver.find_elements_by_css_selector(self._PORTS_LIST)
            if len(list_of_ports) > 1:
                select = Select(self.driver.find_element_by_css_selector(self.PORT_TO_SERVICE))
                select.select_by_value(port_id)
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORT_SELECTED)),
                                "Serviced Port is not added for this user.")
        return new_user_fields['user_id'], new_user_fields['user_password'], new_user_fields['user_role']

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

    def select_serviced_port(self, port_prefix):
        value_selector_for_searchable_drop_downs(self, port_prefix, self.SERVICED_PORT_MODAL,
                                                 self.SERVICED_PORT_PLACEHOLDER, prefix_only=True)

    def select_contact_port(self, port_prefix):
        value_selector_for_searchable_drop_downs(self, port_prefix, self.CONTACT_PORT_MODAL,
                                                 self.CONTACT_PORT_PLACEHOLDER, prefix_only=True)

    def click_on_add_port_button(self):
        self.driver.find_element_by_css_selector(self.ADD_PORT_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ADD_PORT_BUTTON_DISABLE)),
                        "Button is still in disabled state and ports list can't be fetched if button is disabled.")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.NO_PORTS_TEXT)),
                        "Port is not added successfully.")

    def refresh_page(self):
        self.driver.refresh()

    def click_on_additional_contacts_button(self):
        self.MAIN_WINDOW_HANDLER = self.driver.current_window_handle
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADDITIONAL_CONTACTS_BUTTON)))
        self.driver.find_element_by_css_selector(self.ADDITIONAL_CONTACTS_BUTTON).click()
        sleep(1)
        additional_contacts_windows = self.driver.window_handles[1]
        self.driver.switch_to.window(additional_contacts_windows)

    def verify_additional_contact_under_port_contacts_section(self):
        self.driver.close()
        self.driver.switch_to.window(self.MAIN_WINDOW_HANDLER)
        self.driver.find_element_by_css_selector(self.REFRESH_ADDITIONAL_CONTACTS_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.NO_CONTACT_MESSAGE)),
                        "Contact is not added successfully.")

    def delete_additional_contact_from_ports_contact_section(self):
        self.driver.find_element_by_css_selector(self.CONTACT_DELETE).click()
        self.driver.switch_to.alert.accept()
        self.driver.find_element_by_css_selector(self.REFRESH_ADDITIONAL_CONTACTS_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.NO_CONTACT_MESSAGE)),
                        "Contact is not added successfully.")
        no_contact_message = self.driver.find_element_by_css_selector(self.NO_CONTACT_MESSAGE).text
        return no_contact_message

    def get_port_name_from_service_ports_section(self):
        serviced_port = self.driver.find_element_by_css_selector(self.SERVICED_PORT).text
        return serviced_port

    def get_port_name_from_ports_contact_section(self):
        contacts_port = self.driver.find_element_by_css_selector(self.PORTS_CONTACT)
        return contacts_port

    def get_serviced_port_list(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.SERVICED_PORTS_LIST)),
                        "Ports list is not loaded yet.")
        serviced_ports_list = self.driver.find_elements_by_css_selector(self.SERVICED_PORTS_LIST)
        return [serviced_port.text for serviced_port in serviced_ports_list]

    def adding_new_blog_message(self):
        self.driver.find_element_by_css_selector(self.NEW_MESSAGE_TEXTAREA).send_keys("Testing Blog Messages!")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SAVE_MESSAGE_BUTTON)))
        self.driver.execute_script(self.SAVE_MESSAGE_BUTTON_CLICK)
        # self.driver.find_element_by_css_selector(self.SAVE_MESSAGE_BUTTON).click()
        # sleep(1)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_SPINNER)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.MESSAGE_AT_BLOG_FORM)),
                        "Message is not added successfully.")
        blog_message = self.driver.find_elements_by_css_selector(self.MESSAGE_AT_BLOG_FORM)
        if len(blog_message) > 0:
            blog_message = self.driver.find_element_by_css_selector(self.MESSAGE_AT_BLOG_FORM).text
            return blog_message
        else:
            return ""

    def empty_blog_message_save(self):
        self.wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_SPINNER)))
        self.driver.find_element_by_css_selector(self.NEW_MESSAGE_TEXTAREA).click()
        # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.MESSAGE_AT_BLOG_FORM)))
        self.driver.find_element_by_css_selector(self.RESET_MESSAGE_BUTTON).click()
        self.wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_SPINNER)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SAVE_MESSAGE_BUTTON)))
        self.driver.execute_script(self.SAVE_MESSAGE_BUTTON_CLICK)
        # self.driver.find_element_by_css_selector(self.SAVE_MESSAGE_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.MESSAGE_REQUIRED_ERROR)),
                        "Required error message is not visible on page.")
        required_message_error = self.driver.find_element_by_css_selector(self.MESSAGE_REQUIRED_ERROR).text
        return required_message_error

    def blog_messages_unread(self):
        # sleep(2)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_MODAL)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.MESSAGE_AT_BLOG_FORM)))
        self.driver.find_element_by_css_selector(self.MESSAGE_MARK_AS_UNREAD).click()
        # sleep(2)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.MESSAGE_MARK_AS_READ)))
        self.driver.find_element_by_css_selector(self.CLOSE_MESSAGE_MODAL).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_MODAL)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SEARCH_BUTTON)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PAGINATION)))
        try:
            self.driver.find_element_by_css_selector(self.MESSAGE_UNREAD_ON_LISTING)
            return True
        except NoSuchElementException:
            return False

    def blog_messages_read(self):
        self.click_on_blog_messages_button()
        # sleep(2)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_MODAL)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.MESSAGE_AT_BLOG_FORM)))
        # self.driver.find_element_by_css_selector(self.MESSAGE_MARK_AS_READ).click()
        self.driver.execute_script('$(\'ul:first-of-type [title="Mark as Read"] i.fa-envelope\').click()')
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CLOSE_MESSAGE_MODAL)))
        self.driver.find_element_by_css_selector(self.CLOSE_MESSAGE_MODAL).click()
        self.driver.execute_script(self.CLOSE_MESSAGE_MODAL_BUTTON)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.BLOG_MESSAGES_MODAL)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SEARCH_BUTTON)))
        self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PAGINATION)))
        # sleep(2)
        try:
            self.driver.find_element_by_css_selector(self.MESSAGE_UNREAD_ON_LISTING)
            return True
        except NoSuchElementException:
            return False

    def logout_user(self, read_only_user=False, supervisor_or_operator_user=False):
        if read_only_user:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.LOGOUT_BUTTON_OTHER_USERS)))
            self.driver.find_element_by_css_selector(self.LOGOUT_BUTTON_OTHER_USERS).click()
            self.driver.find_element_by_css_selector(self.LOGOUT_BUTTON_OTHER_USERS).click()
            self.driver.find_element_by_css_selector(self.LOGOUT_OTHER_USERS).click()
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_INFO_DROPDOWN)))
            self.driver.find_element_by_css_selector(self.USER_INFO_DROPDOWN).click()
            self.driver.find_element_by_css_selector(self.USER_INFO_DROPDOWN).click()
            if supervisor_or_operator_user:
                self.driver.find_element_by_css_selector(self.LOGOUT_OTHER_USERS).click()
            else:
                self.driver.find_element_by_css_selector(self.LOGOUT).click()

    def get_user_creation_error_messages(self):
        """
        It will get all error messages on page.
        :return: list
        """
        errors_list = self.driver.find_elements_by_css_selector(self.USER_CREATION_ERRORS)
        return errors_list

    def search_and_open_detail_page(self, airline_name):
        try:
            self.airline_search_filter(airline_name=airline_name)
            self.open_airline_details_page()
            self.wait.until(EC.visibility_of_element_located((By.XPATH, self.AIRLINE_NAME)))
        except StaleElementReferenceException:
            # Element becomes stale due to auto-refresh on listing page
            self.airline_search_filter(airline_name=airline_name)
            self.open_airline_details_page()

    def open_airline_details_page_via_api(self, airline_id):
        # directly accessing detail page for now
        self.driver.get(STORMX_URL + '/admin/airline_detail.php?rid=' + str(airline_id))

    def airline_search_filter(self, airline_name):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.driver.find_element_by_css_selector(self.AIRLINE_SEARCH_FILTER).clear()
        self.driver.find_element_by_css_selector(self.AIRLINE_SEARCH_FILTER).send_keys(airline_name)
        self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_ID_LISTING)))
        assert airline_name == self.driver.find_element_by_css_selector(self.AIRLINE_ID_LISTING).get_attribute('value')\
            , "Sorry! we did not find any airlines against this search."

    def open_airline_details_page(self):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_BUTTONS)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_DETAILS_BUTTON)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.AIRLINE_DETAILS_BUTTON)))
        self.driver.find_element_by_css_selector(self.AIRLINE_DETAILS_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.AIRLINE_NAME)))

    def delete_airline_user(self):
        self.driver.find_element_by_css_selector(self.USER_DELETE)

    def update_airline_user(self):
        self.driver.find_element_by_css_selector(self.USER_UPDATE)

    def search_airline_on_listing(self, airline_id):
        self.driver.get(STORMX_URL + '/admin/airlines.php?page=&pid=&hid=' + str(airline_id))
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_ID_VALUE % airline_id)),
                            "{}, Desired airline is not found on listing after click on search button.".
                            format(airline_id))
        except TimeoutException:
            pass
