from datetime import timezone, datetime
import datetime
from datetime import timedelta
from pytz import timezone
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.constant import sleep
from e2e_selenium_tests.BaseClasses.helper import value_selector_for_searchable_drop_downs, get_date, \
    value_selector_for_drop_downs, get_availability_date


class RoomCountReportMainPage(BasePage):
    SEARCH_BUTTON = 'form[name="formSearch"] #btnSearch[type="submit"]'
    SEARCH_BUTTON_XPATH = '//form[@name="formSearch"]//button[@id="btnSearch"]'
    SEARCH_BUTTON_DISABLE = 'form[name="formSearch"] button[id="btnSearch"][disabled="disabled"]'
    SEARCH_BUTTON_SPINNER = 'button[type="submit"][disabled="disabled"] i:Not(.ng-hide):first-of-type'
    RESET_BUTTON = 'button[ng-click="resetForm();"]'
    PORT_MODAL = 'filter.pid'
    PORT_PLACEHOLDER = 'Type port name or prefix'
    ALERT_MESSAGE = '[class="alert alert-danger"]'
    COMM_ADJUST_RATE_BUTTON = '//div[@class="row grid-div-data ng-scope"][div[2][contains(text(), ' \
                              '\"{}\")] and div[5][contains(text(), \"{}\")] and div[4][contains(text(), ' \
                              '\"{}\")]] //div/button[@title="Adjust counts"]'
    NON_COMM_ADJUST_RATE_BUTTON = '//div[@class="row grid-div-data ng-scope bg-danger"][div[2][contains(text(), ' \
                                  '\"{}\")] and div[5][contains(text(), \"{}\")] and div[4][contains(text(), ' \
                                  '\"{}\")]] //div/button[@title="Adjust counts"]'
    RATE_CODE = 'form[name="formRoomCountSplit"] table:first-of-type tr[style="color: blue"] td:nth-of-type(3)'
    COMM_HISTORY_BUTTON = '//div[@class="row grid-div-data ng-scope"][div[2][contains(text(), ' \
                          '\"{}\")] and div[5][contains(text(), \"{}\")] and div[4][contains(text(), ' \
                          '\"{}\")]] //div[last()]//button'
    NON_COMM_HISTORY_BUTTON = '//div[@class="row grid-div-data ng-scope bg-danger"][div[2][contains(text(), ' \
                              '\"{}\")] and div[5][contains(text(), \"{}\")] and div[4][contains(text(), ' \
                              '\"{}\")]] //div[last()]//button'
    HISTORY_MODAL = '[class="modal-content"]'
    DOWNLOAD_REPORT_EXCEL = 'button[title="Download Report"]'
    PAY_TYPE_DROPDOWN = 'select[ng-model="d.voucher_disruption_reason_type_"]'
    ACTUAL_RATE = 'input[ng-model="d.voucher_room_rate_"]'
    CSA = 'input[ng-model="data.selected.voucher_room_csa"]'
    ADJUST_RATE_MODAL = '.modal-content'
    ACTUAL_COUNT = 'input[ng-model="data.selected.actual_total"]'
    NOTES = 'input[ng-model="data.selected.note"]'
    ADD_VOUCHER_SAVE_BUTTON = 'form[name="addVoucherRoomCount"] button[type="submit"]'
    ADJUST_RATE_SAVE_BUTTON = 'form[name="formRoomCountSplit"] button[type="submit"]'
    CLOSE_BUTTON = '.modal-content button.btn-warning'
    CLOSE_SPLIT_ROOM_DIALOG = 'a[title="Close"] span'
    ADJUST_ROOM_MODAL = '.modal-content'
    ROOM_COUNT_VOUCHER_BUTTON = 'a[title="+Voucher"]'
    ROOM_COUNT_VOUCHER_MODAL = 'div[role="dialog"] form[name="addVoucherRoomCount"]'
    DATE_MODAL = 'input[name="block_date"]'
    DATE_MODAL_CLICK = '$(\'div [name="addVoucherRoomCount"] input[name="block_date"]\').trigger("click").focus()'
    DATE_PICKER_MODAL = 'ul.dropdown-menu:nth-of-type(3) div[ng-switch="datepickerMode"]'
    CURRENT_DATE = '//ul[not(contains(@style, "display: none"))]//button[contains(@class,"btn btn-default btn-sm")]' \
                   '[span[text()=%s][not(contains(@class, "muted"))]]'
    CURRENT_DATE_ = '//ul[not(contains(@style, "display: none"))]//button[contains(@class,"btn btn-default btn-sm")]' \
                    '[span[text()=%s][(contains(@class, "text-info"))]]'
    DATE = 'input[name="block_date"]'
    AIRLINE_MODAL = '[name="addVoucherRoomCount"] div[ng-model="filter.aid"]'
    AIRLINE_MODAL_CLICK = '$(\'[name="addVoucherRoomCount"] div[ng-model="filter.aid"] button:last-of-type\').click()'
    RATE_TYPE_MODAL_CLICK = '$(\'[name="addVoucherRoomCount"] div[ng-model="filter.pay_type"] button:last-of-type\')' \
                            '.click()'
    VOUCHER_PORT_MODAL = 'filter.pid'
    HOTEL_MODAL = '[name="addVoucherRoomCount"] div[ng-model="filter.hid"]'
    HOTEL_MODAL_CLICK = '$(\'[name="addVoucherRoomCount"] div[ng-model="filter.hid"] button:last-of-type\').click()'
    VOUCHER_TYPE_MODAL = 'div[ng-model="filter.voucher_type"]'
    VOUCHER_TYPE_MODAL_CLICK = '$(\'div[ng-model="filter.voucher_type"] button:last-of-type\').click()'
    SELECTED_VOUCHER_TYPE = '[ng-model="filter.voucher_type"] span.ng-scope'
    VOUCHER_RATE = 'input[name="rate"]'
    VOUCHER_RATE_DISABLE = 'input[name="rate"][disabled="disabled"]'
    RATE_TYPE_MODAL = 'div[ng-model="filter.pay_type"]'
    RATE_TYPE_MODAL_ = 'div[ng-model="filter.pay_type"] button:last-of-type'
    RATE_TYPE_MODAL_DISABLE = 'div[ng-model="filter.pay_type"] button:last-of-type[disabled="disabled"]'
    RATE_TYPE_LIST = 'div[ng-model="filter.pay_type"] .ui-select-choices-group a .ng-scope'
    SELECTED_RATE_TYPE = '[ng-model="filter.pay_type"] span.ng-scope'
    PAY_BY_MODAL = 'form[name="addVoucherRoomCount"] div[ng-model="filter.pay_by"]'
    PAY_BY_MODAL_CLICK = '$(\'[name="addVoucherRoomCount"] div[ng-model="filter.pay_by"] button:last-of-type\').click()'
    SELECTED_PAY_BY = '//div[@class="form-group"]//span[contains(text(), \"%s\")]'
    VOUCHER_COUNT = 'input[name="count"]'
    VOUCHER_SUCCESS_ALERT = '.alert-success'
    SPLIT_ROOM_COUNT_SUCCESS_ALERT = '.alert-warning'
    ADJUST_ROOM_COUNT_MODAL_FIELDS_VALUES = 'form[name="formRoomCountSplit"] tr td'
    ADJUST_ROOM_COUNT_MODAL_FIELDS_NAME = 'form[name="formRoomCountSplit"] tr th'
    ROOM_COUNT_HISTORY_MODAL_FIELDS_VALUES = 'table tr[ng-repeat="d in data.history"]:nth-of-type(1) td'
    ROOM_COUNT_HISTORY_MODAL_FIELDS_NAME = '.modal-body table tr th'
    HISTORY_DATA = 'table tr[ng-repeat="d in data.history"]:nth-of-type(1)'
    ROOM_COUNT_LISTING_FIELDS_NAME = '.page-listing-results div.grid-div-header div'
    ROOM_COUNT_LISTING_FIELDS_VALUE = '.page-listing-results div.grid-div-data div'
    COMM_LISTING_RECORDS = '//div[@class="row grid-div-data ng-scope"][div[2][contains(text(), \"{}\")] ' \
                           'and div[5][contains(text(), \"{}\")] and div[4][contains(text(), \"{}\")]]'
    NON_COMM_LISTING_RECORDS = '//div[@class="row grid-div-data ng-scope bg-danger"][div[2][contains(text(), \"{}\")]' \
                               ' and div[5][contains(text(), \"{}\")] and div[4][contains(text(), \"{}\")]]'
    DOWNLOAD_FILE = 'button[title="Download Report"]'
    COMMISSION_ABLE = '[model="filter.commissionable"] span[title="Yes"]'
    ADJUST_COMMISSION_ABLE = 'div[model="data.selected.commissionable_row"] span[title=\"%s\"]'
    ISSUED_TOTAL = '//div[contains(@class,"bg-danger") or (@class="row grid-div-data ng-scope")] //div[7]'
    GROUP_BY_ISSUED = '//div[@class="row grid-div-data ng-scope"][div[6][contains(text(),\"${}\")] and div[2]' \
                      '[contains(text(), \"{}\")] and div[5][contains(text(), \"{}\")] and div[4]' \
                      '[contains(text(), \"{}\")]] // div[7]'
    CSA_TOTAL = '//div[contains(@class,"bg-danger") or (@class="row grid-div-data ng-scope")] //div[11]'
    ACTUAL_COUNT_TOTAL = '//div[contains(@class,"bg-danger") or (@class="row grid-div-data ng-scope")] //div[12]'
    ISSUED_ON_LISTING = '.page-listing-results span:nth-of-type(5) span#issued_counts'
    CSA_COUNT_ON_LISTING = '.page-listing-results span:nth-of-type(5) span#csa_count'
    ACTUAL_COUNT_ON_LISTING = '.page-listing-results span span#actual_count'
    RATE_CAPS_WARNING = '[name="addVoucherRoomCount"] .alert-warning'

    def verify_browser_on_the_page(self):
        """Check for the presence of "Search" button """
        assert self.is_visible(self.SEARCH_BUTTON)

    def click_on_search_button(self):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_SPINNER)))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.SEARCH_BUTTON_XPATH)))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, self.SEARCH_BUTTON_XPATH)))
        self.driver.implicitly_wait(2)
        search_button = self.driver.find_element_by_xpath(self.SEARCH_BUTTON_XPATH)
        self.driver.execute_script("arguments[0].click();", search_button)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_SPINNER)),
                        "Page is still searching for results")

    def click_on_adjust_rate_button(self, port, rate_type, hotel, non_comm=False):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_VOUCHER_MODAL)))
        if non_comm:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, self.NON_COMM_ADJUST_RATE_BUTTON
                                                              .format(port, rate_type, hotel))))
            self.driver.find_element_by_xpath(self.NON_COMM_ADJUST_RATE_BUTTON.format(port, rate_type, hotel)).click()
        else:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, self.COMM_ADJUST_RATE_BUTTON
                                                              .format(port, rate_type, hotel))))
            self.driver.find_element_by_xpath(self.COMM_ADJUST_RATE_BUTTON.format(port, rate_type, hotel)).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.CSA)))

    def group_by_records_functionality(self, rate, port, type, hotel):
        issued_count = self.driver.find_element_by_xpath(self.GROUP_BY_ISSUED.format(rate, port, type, hotel)).text
        return int(issued_count)

    def commission_able_working(self, non_comm=False, comm_able=False):
        if non_comm:
            non_comm_able_button = self.driver.find_element_by_css_selector(self.ADJUST_COMMISSION_ABLE % "No")
            self.driver.execute_script("arguments[0].click();", non_comm_able_button)
        if comm_able:
            comm_able_button = self.driver.find_element_by_css_selector(self.ADJUST_COMMISSION_ABLE % "Yes")
            self.driver.execute_script("arguments[0].click();", comm_able_button)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADJUST_RATE_SAVE_BUTTON)))
        self.driver.find_element_by_css_selector(self.ADJUST_RATE_SAVE_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ADJUST_ROOM_MODAL)))
        if non_comm:
            try:
                self.driver.find_element_by_css_selector('.bg-danger')
                return True
            except NoSuchElementException:
                return False
        if comm_able:
            try:
                self.driver.find_element_by_css_selector('[class="row grid-div-data ng-scope"]')
                return True
            except NoSuchElementException:
                return False

    def calculate_count(self, total_issued, non_comm_count, listing_issued=False):
        comm_able_count = int(total_issued) - int(non_comm_count)
        result = comm_able_count
        if listing_issued:
            equation = '{}-{}={}'.format(total_issued, non_comm_count, result)
        else:
            equation = '{} - {} = {}'.format(total_issued, non_comm_count, result)
        return equation, result

    def rate_code_on_adjust_room_count(self):
        rate_code = self.driver.find_element_by_css_selector(self.RATE_CODE).text
        return rate_code

    def total_issued_count_on_listing(self):
        issued_count = self.driver.find_element_by_css_selector(self.ISSUED_ON_LISTING).text
        return int(issued_count)

    def total_csa_count_on_listing(self):
        csa_count = self.driver.find_element_by_css_selector(self.CSA_COUNT_ON_LISTING).text
        return int(csa_count)

    def total_actual_count_on_listing(self):
        actual_count = self.driver.find_element_by_css_selector(self.ACTUAL_COUNT_ON_LISTING).text
        return int(actual_count)

    def calculate_total_issued_count(self):
        total_issued = self.driver.find_elements_by_xpath(self.ISSUED_TOTAL)
        return sum([int(issued.text) for issued in total_issued])

    def calculate_total_csa_count(self):
        total_csa = self.driver.find_elements_by_xpath(self.CSA_TOTAL)
        return sum([int(csa.text) if csa.text else 0 for csa in total_csa])

    def calculate_total_actual_count(self):
        actual_counts = self.driver.find_elements_by_xpath(self.ACTUAL_COUNT_TOTAL)
        return sum([int(actual_count.text) if actual_count.text else 0 for actual_count in actual_counts])

    def get_adjust_room_count_fields_name(self):
        list_of_fields_name = self.driver.find_elements_by_css_selector(self.ADJUST_ROOM_COUNT_MODAL_FIELDS_NAME)
        return [field_name.text for field_name in list_of_fields_name]

    def get_adjust_room_count_fields_values(self):
        list_of_fields_value = self.driver.find_elements_by_css_selector(self.ADJUST_ROOM_COUNT_MODAL_FIELDS_VALUES)
        return [field_value.text for field_value in list_of_fields_value]

    def get_dictionary_of_input_values(self):
        input_keys = [
            "Actual Rate",
            "CSA",
            "Actual Count",
            "Note"
        ]
        input_dictionary = {}
        input_elements = self.driver.find_elements_by_css_selector('form[name="formRoomCountSplit"] tr td input')
        for i, element in enumerate(input_elements):
            value = element.get_attribute("value")
            input_dictionary[input_keys[i]] = value
        return input_dictionary

    def generate_dictionary_of_room_count_fields(self):
        room_count_fields = dict(zip(self.get_adjust_room_count_fields_name(), self.get_adjust_room_count_fields_values()))
        room_count_fields.update(self.get_dictionary_of_input_values())
        # print(room_count_fields)
        return room_count_fields

    def get_split_room_count_history_fields_name(self):
        list_of_fields_name = self.driver.find_elements_by_css_selector(self.ROOM_COUNT_HISTORY_MODAL_FIELDS_NAME)
        return [field_name.text for field_name in list_of_fields_name]

    def get_split_room_count_history_fields_values(self):
        list_of_fields_value = self.driver.find_elements_by_css_selector(self.ROOM_COUNT_HISTORY_MODAL_FIELDS_VALUES)
        return [field_value.text for field_value in list_of_fields_value]

    def generate_dictionary_of_history_fields(self):
        history_fields = dict(zip(self.get_split_room_count_history_fields_name(),
                                  self.get_split_room_count_history_fields_values()))
        return history_fields

    def compare_room_count_and_history_data(self, split_room_count, history):
        same_keys = list(set(split_room_count) & set(history))
        for key in same_keys:
            if split_room_count[key] == history[key]:
                print("Matched result")
            else:
                print("Unmatched data.")

    def get_room_count_listing_fields_name(self):
        list_of_fields_name = self.driver.find_elements_by_css_selector(self.ROOM_COUNT_LISTING_FIELDS_NAME)
        return [field_value.text for field_value in list_of_fields_name]

    def get_room_count_listing_fields_value(self):
        list_of_fields_value = self.driver.find_elements_by_css_selector(self.ROOM_COUNT_LISTING_FIELDS_VALUE)
        return [field_value.text for field_value in list_of_fields_value]

    def generate_dictionary_of_room_count_listing_fields(self):
        room_count_listing_fields = dict(zip(self.get_room_count_listing_fields_name(),
                                         self.get_room_count_listing_fields_value()))
        return room_count_listing_fields

    def verify_newly_added_room_count_on_room_count_listing(self, date, port, airline, hotel, rate, issued, cb_count="0"
                                                            , hb_count="0", actual_rate="", csa="", actual_count="",
                                                            rate_type="", non_comm=False, adjust_room_count=False,
                                                            pp_pay_type=False):
        record_found = False

        self.driver.implicitly_wait(2)
        split_room_count_string = "$" + actual_rate + "\n" + csa + "\n" + actual_count + "\n"
        if non_comm:
            self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                              self.NON_COMM_LISTING_RECORDS.format(port, rate_type,
                                                                                                   hotel))))
            listing_records = self.driver.find_elements_by_xpath(self.NON_COMM_LISTING_RECORDS
                                                                 .format(port, rate_type, hotel))
        else:
            self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                              self.COMM_LISTING_RECORDS.format(port, rate_type,
                                                                                               hotel))))
            listing_records = self.driver.find_elements_by_xpath(self.COMM_LISTING_RECORDS
                                                                 .format(port, rate_type, hotel))
        compare_string = date + "\n" + port + "\n" + airline + "\n" + hotel + "\n" + ("PP" if pp_pay_type else rate_type) \
                              + "\n" + "$" + rate + "\n" + issued + "\n" + cb_count + "\n" + hb_count + "\n" \
                              + (split_room_count_string if adjust_room_count else "") + "Adjust"
        for room_count in listing_records:
            self.driver.implicitly_wait(2)
            if compare_string == room_count.text:
                record_found = True
                break
        return record_found

    def verify_newly_added_room_count_on_history(self, date, user, rate, count, actual_rate, csa, actual_count, notes,
                                                 pp_pay_type=False):
        records_found = False
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HISTORY_DATA)))
        compare_string = date[0] + " " + user + " " + ("PP" if pp_pay_type else "AP") + " " + rate + " " + count + " " \
                                 + actual_rate + " " + csa + " " + actual_count + " " + notes
        compare_string1 = date[1] + " " + user + " " + ("PP" if pp_pay_type else "AP") + " " + rate + " " + count + " "\
                                  + actual_rate + " " + csa + " " + actual_count + " " + notes
        history_data_list = self.driver.find_elements_by_css_selector(self.HISTORY_DATA)
        for history_data in history_data_list:
            self.driver.implicitly_wait(2)
            assert compare_string1 == history_data.text or compare_string == history_data.text
            records_found = True
            break
        return records_found

    def click_on_add_voucher_room_count(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_VOUCHER_BUTTON)))
        self.driver.find_element_by_css_selector(self.ROOM_COUNT_VOUCHER_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_VOUCHER_MODAL)))

    def select_date_from_room_count_voucher(self, history_date=False):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DATE_MODAL)))
        self.driver.find_element_by_css_selector(self.VOUCHER_RATE).click()
        self.driver.find_element_by_css_selector(self.DATE_MODAL).click()
        self.driver.execute_script(self.DATE_MODAL_CLICK)
        self.driver.execute_script(self.DATE_MODAL_CLICK)
        # self.driver.implicitly_wait(1)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DATE_PICKER_MODAL)))
        date_day = get_availability_date("America/Chicago")
        self.driver.find_element_by_xpath(self.CURRENT_DATE % date_day.day).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DATE_PICKER_MODAL)))
        return str(date_day.month).zfill(2) + "/" + str(date_day.day).zfill(2) + "/" + str(date_day.year) + \
            (str(date_day.hour) + str(date_day.minute) + str(date_day.timestamp()) if history_date else "")

    def fill_add_voucher_room_count_form(self, airline, port, hotel, pay_by, rates_type, voucher_rate, voucher_count,
                                         non_comm=False):
        self.driver.execute_script(self.AIRLINE_MODAL_CLICK)
        value_selector_for_drop_downs(self, self.AIRLINE_MODAL, airline)
        value_selector_for_searchable_drop_downs(self, port, self.VOUCHER_PORT_MODAL, self.PORT_PLACEHOLDER,
                                                 prefix_only=True, need_item_class=True, item_class_name="form-group")
        self.driver.execute_script(self.HOTEL_MODAL_CLICK)
        value_selector_for_drop_downs(self, self.HOTEL_MODAL, hotel)
        self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.RATE_TYPE_MODAL_DISABLE)))
        self.driver.execute_script(self.RATE_TYPE_MODAL_CLICK)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RATE_TYPE_MODAL_)))
        # self.driver.find_element_by_css_selector(self.RATE_TYPE_MODAL_).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_TYPE_LIST)))
        get_rate_type_list = self.driver.find_elements_by_css_selector(self.RATE_TYPE_LIST)
        rate_types = [pay_type.text for pay_type in get_rate_type_list]
        for rate_type in rate_types:
            value_selector_for_drop_downs(self, self.RATE_TYPE_MODAL, rate_type)
            selected_rate_type = self.driver.find_element_by_css_selector(self.SELECTED_RATE_TYPE).text
            selected_voucher_type = self.driver.find_element_by_css_selector(self.SELECTED_VOUCHER_TYPE).text
            if rate_type == 'AP':
                assert selected_voucher_type == 'Missed Connection'
            if rate_type == 'PP':
                assert selected_voucher_type == 'Passenger Pay'
            if rate_type == 'HB':
                assert selected_voucher_type == 'Hard Block'
            if rate_type == 'CB':
                assert selected_voucher_type == 'Contracted'
        value_selector_for_drop_downs(self, self.RATE_TYPE_MODAL, rates_type)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_RATE_DISABLE)))
        self.wait.until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, self.VOUCHER_RATE), "0"))
        self.driver.find_element_by_css_selector(self.VOUCHER_RATE).click()
        self.driver.execute_script("$('input[name=\"rate\"]').val("")")
        self.driver.execute_script("$('input[name=\"rate\"]').val({})".format(voucher_rate))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_COUNT)))
        self.driver.find_element_by_css_selector(self.VOUCHER_COUNT).send_keys(voucher_count)
        if non_comm:
            value_selector_for_drop_downs(self, self.PAY_BY_MODAL, pay_by)
            selected_pay_by = self.driver.find_element_by_xpath(self.SELECTED_PAY_BY % pay_by).text
            assert selected_pay_by == pay_by, "Selected pay type is wrong"
            # self.wait.until(EC._element_if_visible((By.XPATH, self.SELECTED_PAY_BY % pay_by)))
            # self.driver.find_element_by_css_selector(self.COMMISSION_ABLE).click()

    def rate_cap_warning_on_room_count_add_voucher(self, port, hotel, voucher_rate):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DATE_MODAL)))
        value_selector_for_searchable_drop_downs(self, port, self.VOUCHER_PORT_MODAL, self.PORT_PLACEHOLDER,
                                                 prefix_only=True, need_item_class=True, item_class_name="form-group")
        self.driver.execute_script(self.HOTEL_MODAL_CLICK)
        value_selector_for_drop_downs(self, self.HOTEL_MODAL, hotel)
        self.wait.until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, self.VOUCHER_RATE), "0"))
        self.driver.find_element_by_css_selector(self.VOUCHER_RATE).click()
        self.driver.execute_script("$('input[name=\"rate\"]').val("")")
        self.driver.execute_script("$('input[name=\"rate\"]').val({})".format(voucher_rate))
        self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_WARNING)),
                        "Rate caps warning is not visible on the page.")
        rate_cap_warning = self.driver.find_element_by_css_selector(self.RATE_CAPS_WARNING).text
        return rate_cap_warning

    def close_add_voucher_modal(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CLOSE_BUTTON)))
        self.driver.find_element_by_css_selector(self.CLOSE_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_VOUCHER_MODAL)),
                        "There is an error while closing add voucher modal.")

    def save_and_close_modal(self, voucher_modal=False, adjust_room_count_modal=False, room_count_history=False):
        if voucher_modal:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_VOUCHER_SAVE_BUTTON)))
            self.driver.find_element_by_css_selector(self.ADD_VOUCHER_SAVE_BUTTON).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_VOUCHER_MODAL)),
                            "There is an error while saving voucher.")
        if adjust_room_count_modal:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADJUST_RATE_SAVE_BUTTON)))
            self.driver.find_element_by_css_selector(self.ADJUST_RATE_SAVE_BUTTON).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ADJUST_ROOM_MODAL)),
                            "There is an error while saving adjust rates.")
        if room_count_history:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.CLOSE_BUTTON)))
            self.driver.find_element_by_css_selector(self.CLOSE_BUTTON).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.HISTORY_MODAL)),
                            "There is an error while closing history modal.")

    def fill_adjust_room_count_form(self, csa, actual_count, notes):
        self.driver.find_element_by_css_selector(self.CSA).send_keys("\b")
        self.driver.find_element_by_css_selector(self.CSA).send_keys(csa)
        self.driver.find_element_by_css_selector(self.ACTUAL_COUNT).send_keys("\b")
        self.driver.find_element_by_css_selector(self.ACTUAL_COUNT).send_keys(actual_count)
        self.driver.find_element_by_css_selector(self.NOTES).send_keys(notes)

    def click_on_room_count_history_button(self, port, rate_type, hotel, non_comm=False):
        if non_comm:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, self.NON_COMM_HISTORY_BUTTON
                                                              .format(port, rate_type, hotel))))
            self.driver.find_element_by_xpath(self.NON_COMM_HISTORY_BUTTON.format(port, rate_type, hotel)).click()
        else:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, self.COMM_HISTORY_BUTTON
                                                              .format(port, rate_type, hotel))))
            self.driver.find_element_by_xpath(self.COMM_HISTORY_BUTTON.format(port, rate_type, hotel)).click()
            # self.driver.execute_script("arguments[0].click();", history_button)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HISTORY_MODAL)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.fa-spin')),
                        "Page is still searching for results")

    def download_room_count_report(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DOWNLOAD_FILE)))
        self.driver.find_element_by_css_selector(self.DOWNLOAD_FILE).click()

    def verify_every_download(self):
        """
        It will returns the paths of downloaded files in chrome download folder.
        :return: list
        """
        if not self.driver.current_url.startswith("chrome://downloads"):
            self.driver.get("chrome://downloads/")
        try:
            self.driver.execute_script("""
            items = downloads.Manager.get().items_;
            if (items.every(e => e.state === "COMPLETE"))
                  return items.map(e => e.file_url);
            """)
            return True
        except:
            # print("Downloaded file doesn't exist in download folder.")
            return False
