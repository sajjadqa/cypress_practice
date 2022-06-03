from pytz import timezone
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from e2e_selenium_tests.BaseClasses.helper import value_selector_for_drop_downs, \
    value_selector_for_searchable_drop_downs
from e2e_selenium_tests.BaseClasses.base import BasePage


class PortAllowances(BasePage):
    TABLE_HEADING_ROW = 'table tr th'
    SEARCH_BUTTON_DISABLE = 'button#btnSearch[disabled="disabled"]'
    ADD_NEW_ALLOWANCE = 'a[title="Add New Allowance"] .fa-plus'
    ADD_NEW_ALLOWANCE_CLICK = "$('a[title=\"Add New Allowance\"] .fa-plus').click()"
    ADD_NEW_ALLOWANCE_FORM = 'form[name="formAllowance"]'
    PORT_MODAL = 'div[ng-model="data.selected_port"] button:first-of-type'
    PORT_MODAL_ = 'div[ng-model="data.selected_port"]'
    PORT_INPUT = 'input[placeholder="%s"]'
    PORT_DROPDOWN_PLACEHOLDER = 'Type port name or prefix'
    SELECTED_PORT = '[ng-model="data.selected_port"] span.ng-scope'
    SELECTED_AIRLINE = '[ng-model="data.selected_airline"] span.ng-scope'
    AIRLINE_MODAL = 'div[ng-model="data.selected_airline"]'
    AIRLINE_MODAL_CLICK = '$(\'div[ng-model="data.selected_airline"] button:last-of-type\').click()'
    AIRLINE_PLACEHOLDER = 'Choose Airline'
    ALLOWANCES = 'input[name="allowance"]'
    SAVE_BUTTON = 'form[name="formAllowance"] button[type="submit"]'
    CLOSE_BUTTON = 'form[name="formAllowance"] button[ng-click="cancel()"]'
    TEMPORARY_ALLOWANCE_ADD_BUTTON = '[ng-click="temporary_allowance.save(d)"]'
    TEMPORARY_ALLOWANCE_TEXT_FIELD = 'input[ng-model="d.new_temporary_allowance"]'
    ALLOWANCES_SUCCESS_ALERT = '.alert-success'
    ALLOWANCES_LISTING_ERROR = '.alert-danger'
    ALLOWANCES_ERROR_ALERT = '[name="formAllowance"] .alert-danger'
    ALLOWANCES_REQUIRED_ALERT = '[ng-model="data.allowance"]+span:not(.ng-hide)'
    ALLOWANCES_ERROR = 'input[name="allowance"]+span'
    EDIT_ALLOWANCE = 'button[title="Edit Allowance"] .fa-pencil-square-o'
    DELETE_ALLOWANCE = 'button[title="Delete Allowance"] .fa-remove'
    ALLOWANCES_LISTING_RECORDS = '.page-listing-results div tr.bg-active'
    TOTAL_ALLOWANCE_VALUE = '.page-listing-results div tr.bg-active td:nth-of-type(5) strong'

    def verify_browser_on_the_page(self):
        """Check for the presence of hotel allowance table rows text on the page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_ALLOWANCE)),
                        "Add new Allowance page is not loaded yet..")
        assert self.is_visible(self.TABLE_HEADING_ROW)

    def click_on_add_new_allowance_button(self):
        """
        It will click on add new allowance button from port allowances listing page.
        :return:
        """
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)),
                        "Add new Allowance button is not enabled on page.")
        # self.driver.find_element_by_css_selector(self.ADD_NEW_ALLOWANCE).click()
        self.driver.execute_script(self.ADD_NEW_ALLOWANCE_CLICK)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALLOWANCES)),
                        "Add new port allowances form is not fully loaded.")
        self.actions.send_keys(Keys.TAB).perform()

    def select_port(self, query_text, dropdown_modal, dropdown_placeholder):
        """
        It will select a port from port dropdown on QRT page
        :param query_text:
        :param dropdown_modal:
        :param dropdown_placeholder:
        :return:
        """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORT_MODAL_)),
                        "Add new allowance form is not fully loaded")
        value_selector_for_searchable_drop_downs(self, query_text, dropdown_modal, dropdown_placeholder,
                                                 prefix_only=True, need_item_class=True, item_class_name="form-group")
        selected_port = self.driver.find_element_by_css_selector(self.SELECTED_PORT).text
        assert query_text in selected_port

    def fill_data_on_port_allowance_form(self, airline_name, allowance):
        self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_MODAL)))
        value_selector_for_drop_downs(self, self.AIRLINE_MODAL, airline_name)
        selected_airline = self.driver.find_element_by_css_selector(self.SELECTED_AIRLINE).text
        assert selected_airline == airline_name
        self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALLOWANCES)))
        self.driver.find_element_by_css_selector(self.ALLOWANCES).send_keys(allowance)

    def click_on_save_allowance_button(self, check_duplicate=False):
        self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
        if check_duplicate:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALLOWANCES_ERROR_ALERT)))
            return self.driver.find_element_by_css_selector(self.ALLOWANCES_ERROR_ALERT).text
        else:
            try:
                error = self.driver.find_element_by_css_selector(self.ALLOWANCES_REQUIRED_ALERT).text
                return error
            except NoSuchElementException:
                try:
                    error = self.driver.find_element_by_css_selector(self.ALLOWANCES_ERROR_ALERT).text
                    return error
                except NoSuchElementException:
                    self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_ALLOWANCE_FORM)))
                    return self.driver.find_element_by_css_selector(self.ALLOWANCES_SUCCESS_ALERT).text.\
                        replace('×\n', '')

    def click_on_close_button(self):
        self.driver.find_element_by_css_selector(self.CLOSE_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_ALLOWANCE_FORM)))

    def verify_newly_added_allowances_on_allowances_listing(self, port, airline, allowance, total_allowance, date):
        record_found = False
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALLOWANCES_LISTING_RECORDS)))
        allowance_listing_records = self.driver.find_elements_by_css_selector(self.ALLOWANCES_LISTING_RECORDS)
        compare_string = port + " " + airline + " " + allowance + " " + '+add' + " " + total_allowance + " " + date[0]
        compare_string1 = port + " " + airline + " " + allowance + " " + '+add' + " " + total_allowance + " " + date[1]
        for allowance in allowance_listing_records:
            self.driver.implicitly_wait(2)
            if compare_string == allowance.text or compare_string1 == allowance.text:
                record_found = True
                break
        # if not record_found:
        #     print([allowance_records.text for allowance_records in allowance_listing_records],
        #           [1, compare_string], [2, compare_string1])
        return record_found

    def edit_allowance(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EDIT_ALLOWANCE)))
        self.driver.find_element_by_css_selector(self.EDIT_ALLOWANCE).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_ALLOWANCE_FORM)),
                        "Edit port allowances form is not fully loaded.")

    def delete_allowance(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DELETE_ALLOWANCE)))
        delete_allowance_button = self.driver.find_element_by_css_selector(self.DELETE_ALLOWANCE)
        self.driver.execute_script("arguments[0].click();", delete_allowance_button)
        self.driver.switch_to.alert.accept()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALLOWANCES_LISTING_RECORDS)))
        return self.driver.find_element_by_css_selector(self.ALLOWANCES_SUCCESS_ALERT).text.replace('×\n', '')

    def add_temporary_allowances(self, temp_allowance, boundary_value=False):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TEMPORARY_ALLOWANCE_TEXT_FIELD)))
        self.driver.find_element_by_css_selector(self.TEMPORARY_ALLOWANCE_TEXT_FIELD).send_keys(temp_allowance)
        self.driver.find_element_by_css_selector(self.TEMPORARY_ALLOWANCE_ADD_BUTTON).click()
        if boundary_value:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALLOWANCES_LISTING_ERROR)))
            return self.driver.find_element_by_css_selector(self.ALLOWANCES_LISTING_ERROR).text.replace('×\n', '')
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALLOWANCES_SUCCESS_ALERT)))
            allowances_success_message = self.driver.find_element_by_css_selector(self.ALLOWANCES_SUCCESS_ALERT)\
                .text.replace('×\n', '')
            self.driver.refresh()
            return allowances_success_message

    def total_allowance_calculation(self):
        return self.driver.find_element_by_css_selector(self.TOTAL_ALLOWANCE_VALUE).text
