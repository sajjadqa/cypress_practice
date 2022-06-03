import datetime

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.constant import sleep
from e2e_selenium_tests.BaseClasses.helper import value_selector_for_searchable_drop_downs, get_date, \
    value_selector_for_drop_downs, get_availability_date, get_hotel_block_fields


class QuickVoucherMainPage(BasePage):
    VOUCHER_CREATION_DATE_VALUE = ""
    HOTEL_NAMES_LIST = 'table.table-condensed tr[title="Click to choose hotel"] td:nth-of-type(1) div:first-of-type'
    HOTEL_TAX_LIST = 'table.table-condensed tr[title="Click to choose hotel"] td:nth-of-type(3) medium'
    HOTEL_HARD_BLOCK_RATES_LIST = 'table.table-condensed tr[title="Click to choose hotel"] td:nth-of-type(3) strong'
    HOTEL_SOFT_BLOCK_RATES_LIST = 'table.table-condensed tr[title="Click to choose hotel"] td:nth-of-type(3) span span'
    REQUESTING_PORT_MODAL = 'data.voucher.voucher_requesting_port'
    REQUESTING_PORT_PLACEHOLDER = 'type port name requested by the airline'
    REPRESENTING_AIRLINE = 'div[ng-model="data.voucher.voucher_disruption_airline"]'
    REPRESENTING_AIRLINE_MODAL_CLICK = \
        '$(\'div[ng-model="data.voucher.voucher_disruption_airline"] button:last-of-type\').click()'
    REPRESENTING_AIRLINE_MODAL = 'data.voucher.voucher_disruption_airline'
    REPRESENTING_AIRLINE_PLACEHOLDER = 'type representing airline name'
    INVOICE_AIRLINE_MODAL = ''
    INVOICE_AIRLINE_PLACEHOLDER = ''
    FLIGHT_NUMBER = '[id="vnFlightNumber"]'
    SELECTED_HOTEL_MODAL = ''
    SELECTED_HOTEL_PLACEHOLDER = ''
    DISRUPTION_DATE = '#vnVoucherCheckIn'
    ROOMS = '#vnHotelRooms'
    PASSENGER_NAME = 'input[placeholder="Enter Passenger Name..."]'
    ADD_PAX_BUTTON = 'td button[title="Add Pax"]'
    ROOM_TYPE_MODAL = 'div.col-sm-10 div[ng-model="data.voucher.voucher_room_type"]'
    ROOM_TYPE_MODAL_CLICK = \
        '$(\'div.col-sm-10 div[ng-model="data.voucher.voucher_room_type"] button:last-of-type\').click()'
    SAVE_VOUCHER_BUTTON = '.bottom-prev-next button[ng-click="utils.save();"]'
    CLOSE_VOUCHER_BUTTON = '.bottom-prev-next button[ng-click="closeVoucherDialog()"]'
    CURRENT_DATE = '//ul[not(contains(@style, "display: none"))]//button[contains(@class,"btn btn-default btn-sm")]' \
                   '[span[text()=%s][not(contains(@class, "muted"))]]'
    PREVIOUS_DATE = '//ul[not(contains(@style, "display: none"))]//button[contains(@class,"btn btn-default btn-sm")]' \
                    '[span[text()=%s][contains(@class, "muted")]]'
    CLOSE_DATE_MODAL = '//ul[not(contains(@style, "display: none"))]/li/span/button'
    FIRST_HOTEL = '.table-hotel-trans tr[title="Click to choose hotel"]:nth-of-type(2)'
    CLOSE_SEND_VOUCHER_DIALOG = 'button[ng-click="closeVoucherDialog()"]'
    VOUCHER_MODAL_HEADER = '#vnModalHeader .modal-title'
    CANCEL_SEND_VOUCHER_DIALOG = '[ng-click="$parent.$parent.stepCurrent=4;"]'
    VOUCHER_CHECK_IN_DATE = "td[ng-click=\"moveToStep(1, 'voucher_disruption_date_focus')\"] a"
    VOUCHER_SAVED_MESSAGE = '[class="alert alert-success"]'
    VOUCHER_ERROR_MESSAGE = '[class="alert alert-danger ng-binding"]'
    DATE_MODAL = 'input[name="vnVoucherCheckIn"]'
    INVENTORY_ERROR = '.vnMainLayout-Steps div[class="alert alert-danger ng-binding"]'

    def verify_browser_on_the_page(self):
        """Check for the presence of representing airline drop down on quick voucher page. """
        assert self.is_visible(self.REPRESENTING_AIRLINE)

    def select_date_from_voucher_modal(self, past_days=False):
        self.driver.find_element_by_css_selector(self.DATE_MODAL).click()
        sleep(2)
        if past_days:
            today_m_5_days = (get_availability_date('America/Chicago') - datetime.timedelta(days=5)).day
            current_day = get_availability_date('America/Chicago').day
            if current_day > 5:
                self.driver.find_element_by_xpath(self.CURRENT_DATE % today_m_5_days).click()
            else:
                self.driver.find_element_by_xpath(self.PREVIOUS_DATE % today_m_5_days).click()
        else:
            date_day = get_availability_date("America/Chicago").day
            self.driver.find_element_by_xpath(self.CURRENT_DATE % date_day).click()
        self.driver.find_element_by_xpath(self.CLOSE_DATE_MODAL).click()

    def fill_data_on_quick_voucher(self, port, airline, accessibility_room=False, exceed_inventory=False, room_count=5,
                                   past_date=False):
        value_selector_for_searchable_drop_downs(self, port, self.REQUESTING_PORT_MODAL,
                                                 self.REQUESTING_PORT_PLACEHOLDER, True)
        self.driver.execute_script(self.REPRESENTING_AIRLINE_MODAL_CLICK)
        value_selector_for_drop_downs(self, self.REPRESENTING_AIRLINE, airline)
        self.driver.find_element_by_css_selector(self.FLIGHT_NUMBER).send_keys("PR-1234")
        if past_date:
            self.select_date_from_voucher_modal(past_days=True)
        if accessibility_room:
            self.driver.execute_script(self.ROOM_TYPE_MODAL_CLICK)
            value_selector_for_drop_downs(self, self.ROOM_TYPE_MODAL, "Accessibility Room")
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.HOTEL_NAMES_LIST)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.FIRST_HOTEL)))
        click_on_first_hotel = self.driver.find_element_by_css_selector(self.FIRST_HOTEL)
        self.driver.execute_script("arguments[0].click();", click_on_first_hotel)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOMS)))
        self.driver.find_element_by_css_selector(self.ROOMS).send_keys('\b')
        if exceed_inventory:
            self.driver.find_element_by_css_selector(self.ROOMS).send_keys("9999")
        else:
            self.driver.find_element_by_css_selector(self.ROOMS).send_keys(room_count)
        self.driver.find_element_by_css_selector(self.PASSENGER_NAME).send_keys("Sajjad Akbar")

    def get_tax_list_on_quick_voucher(self):
        tax_list = self.driver.find_elements_by_css_selector(self.HOTEL_TAX_LIST)
        return [tax.text for tax in tax_list]

    def click_on_save_quick_voucher_button(self):
        self.VOUCHER_CREATION_DATE_VALUE = get_availability_date("America/Chicago")
        # self.VOUCHER_CREATION_DATE_VALUE = datetime.strptime(self.VOUCHER_CREATION_DATE_VALUE, '%d/%m/%Y %H:%M')
        self.driver.find_element_by_css_selector(self.SAVE_VOUCHER_BUTTON).click()
        return self.VOUCHER_CREATION_DATE_VALUE

    def voucher_finalization_alert(self):
        self.wait.until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()

    def get_hotel_inventory_exceed_error(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.INVENTORY_ERROR)))
        inventory_error = self.driver.find_element_by_css_selector(self.INVENTORY_ERROR).text
        return inventory_error

    def get_voucher_checkin_date(self):
        try:
            self.driver.find_element_by_css_selector(self.VOUCHER_ERROR_MESSAGE)
            return False
        except:
            voucher_number = self.driver.find_element_by_css_selector(self.VOUCHER_MODAL_HEADER).text
            voucher_number = voucher_number.split()[2]
            # print(voucher_number, "has been created successfully.")
            self.driver.find_element_by_css_selector(self.CANCEL_SEND_VOUCHER_DIALOG).click()
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.VOUCHER_SAVED_MESSAGE)))
            get_checkin_date = self.driver.find_element_by_css_selector(self.VOUCHER_CHECK_IN_DATE).text
            self.driver.find_element_by_css_selector(self.CLOSE_SEND_VOUCHER_DIALOG).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_MODAL_HEADER)))
            checkin_date = datetime.datetime.strptime(get_checkin_date, '%d/%m/%Y %H:%M')
            return checkin_date

    def get_hotel_hard_blocks_avail_info_list_from_quick_voucher_modal(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.HOTEL_HARD_BLOCK_RATES_LIST)))
        hard_blocks_list = self.driver.find_elements_by_css_selector(self.HOTEL_HARD_BLOCK_RATES_LIST)
        return sum([int((hard_block.text).split("@")[0]) for hard_block in hard_blocks_list])

    def get_hotel_soft_blocks_avail_info_list_from_quick_voucher_modal(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.HOTEL_SOFT_BLOCK_RATES_LIST)))
        soft_blocks_list = self.driver.find_elements_by_css_selector(self.HOTEL_SOFT_BLOCK_RATES_LIST)
        return sum([int((soft_block.text).split("@")[0]) for soft_block in soft_blocks_list])
