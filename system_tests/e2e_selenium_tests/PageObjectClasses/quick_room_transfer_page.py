import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.helper import value_selector_for_drop_downs, fill_quick_room_transfer_form, value_selector_for_searchable_drop_downs
from e2e_selenium_tests.BaseClasses.constant import sleep
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuickRoomMainPage(BasePage):
    PORT_DROP_DOWN = 'div[ng-model="data.selected_port"] button:first-of-type'
    AIRLINE_DROP_DOWN = 'div[ng-model="data.selected_airline"]'
    REFRESH_BUTTON = 'form[name="QuickVoucherForm"] a'
    PHONE_NUMBER = '[ng-model="data.contact_phone"]'
    PHONE_NUMBER_ERROR = 'span[ng-show="isDirty(QuickVoucherForm.contact_phone)"]'
    PHONE_EXTENSION = '[ng-model="data.extension"]'
    COMMENTS = 'textarea[ng-model="data.comments"]'
    FLIGHT_NUMBER = 'input[name="flight_number"]'
    SAVE_BUTTON = 'button[type="submit"]'
    ROOM_AVAIL_COUNT_AT_QRT_FORM = '[class="available"] span[class="number ng-binding"]'
    ROOM_USED_COUNT_AT_QRT_FORM = '[class="used"] span[class="number ng-binding"]'
    MAX_ALLOWED = '[class="rooms"] [class="available"]:last-of-type span:first-of-type'
    # BOOKING_ERROR = '[name="QuickVoucherForm"] div[class="save_response alert alert-danger"] span'
    FIRST_HOTEL = 'tbody tr[class="hotels-list ng-scope"]:nth-of-type(2) td a'
    SECTION_TITLE = '[class="container-fluid section-title-container"] [class="section-title"]>span'
    ROOM_NEED = 'tr:nth-of-type(2) tbody tr:nth-of-type(1) td input[ng-model="block.need"]'
    PORT_INPUT = 'input[placeholder="Type port name or prefix"]'
    PORTS_LIST = 'ul li div[class*="ui-select-choices-row"]'
    VOUCHER_AT_HISTORY = '[class="usage"] tr:nth-of-type(2) .item1 a[ng-click="openVoucherDetail(item)"]'
    VOUCHER_MODAL = '[class="modal-content"]'
    CLOSE_MODAL_BUTTON = '.modal-header a[ng-click="cancel()"]'
    NO_HOTEL_RECORD_FOUND = '.hotels .table-responsive tbody tr[ng-if="!data.inventory||data.inventory.length==0"] td'
    SUCCESS_RESPONSE = 'div[class="save_response alert alert-success"]'
    TOP_CREATED_VOUCHER_NUMBER = 'tr:nth-of-type(2) a[ng-click="openVoucherDetail(item)"]'
    ALL_VOUCHER_NUMBERS = 'tr a[ng-click="openVoucherDetail(item)"]'
    RETURN_BUTTON = '[ng-repeat="item in data.bookingHistory track by $index"]:nth-of-type(2) td button'
    ROOMS_ADJUSTED = '[name="rooms"]'
    UPDATE_BUTTON = 'div[class="modal-footer"] [type="submit"]'
    ADJUSTED_ROOM_COUNT = '[ng-show="data.usage.voucher_room_total - data.rooms > 0"]'
    INVENTORY_ERROR_MESSAGE = '[name="QuickVoucherForm"] div[class="save_response alert alert-danger"] span'
    ROOM_USED_COUNT_ON_HOTEL_USAGE = 'tbody tr[ng-repeat="item in data.bookingHistory track by $index"] td:nth-of-type(3)'
    ROOMS_USED_FIRST_VOUCHER_ON_USAGE = '.usage tr:nth-of-type(2) td:nth-of-type(3)'
    HOTEL_INFO = '[class="hotel-info ng-scope"] div[class="hotel-name ng-binding"]'
    REFRESH_SPINNER = '[class="header"] [class="fa fa-circle-o-notch fa-spin"]'
    NO_HOTEL_USAGE_RECORD_FOUND = \
        '.usage .table-responsive tbody tr[ng-if="!data.bookingHistory||data.bookingHistory.length==0"] td'
    BUTTON_VIEW_HOTEL_MAP = 'button[title="View hotel on map"]'
    HOTEL_MAP = 'div[class="map ng-scope"]'
    MAP_IFRAME = '[class="angular-google-map"] iframe'
    BUTTON_HIDE_MAP = 'button[title="Hide map"]'
    # ROOMS_USED_AT_PREVIEW = "tr[ng-repeat='pax in d.voucherInfoPax'] td:nth-of-type(3)"
    ROOMS_USED_AT_PREVIEW = '[ng-if="!d.isTransportOnly&&d.hotel_name!=\'\'"] div:nth-of-type(7)'

    def verify_browser_on_the_page(self):
        """ check for the presence of "Travelliance: (800) 642-7310" Text """
        assert self.is_visible(self.SECTION_TITLE)

    def find_and_select_port_from_dropdown(self, query_text, dropdown_modal, dropdown_placeholder):
        """
        It will select a port from port dropdown on QRT page
        :param query_text:
        :param dropdown_modal:
        :param dropdown_placeholder:
        :return:
        """
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
        value_selector_for_searchable_drop_downs(self, query_text, dropdown_modal, dropdown_placeholder,
                                                 prefix_only=True)

    def find_and_select_airline_from_dropdown(self, query_text, dropdown_modal, dropdown_placeholder):
        """
        It will select desired airline for TVL users on QRT page.
        :param query_text:
        :param dropdown_modal:
        :param dropdown_placeholder:
        :return:
        """
        value_selector_for_searchable_drop_downs(self, query_text, dropdown_modal, dropdown_placeholder,
                                                 prefix_only=True)
        # select_value_from_drop_downs(self, 'div[ng-model="data.selected_airline"]', airline_name)
        # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
        #                 "Page is not fully loaded.")

    def fill_quick_room_transfer_fields(self, quick_room_transfer_fields):
        """ This function will fill all the quick room transfer page fields data"""
        if self.no_hotel_record_found_from_qrt_form():
            pass
        else:
            self.driver.find_element_by_css_selector(self.ROOM_NEED).send_keys(quick_room_transfer_fields["room_need"])
        if self.no_hotel_record_found_from_qrt_form():
            pass
        else:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.PHONE_NUMBER)))
            self.driver.find_element_by_css_selector(self.PHONE_NUMBER).clear()
            self.driver.find_element_by_css_selector(self.PHONE_NUMBER). \
                send_keys(quick_room_transfer_fields["direct_phone_number"])
        if self.no_hotel_record_found_from_qrt_form():
            pass
        else:
            self.driver.find_element_by_css_selector(self.PHONE_EXTENSION). \
                send_keys(quick_room_transfer_fields["phone_extension"])
        if self.no_hotel_record_found_from_qrt_form():
            pass
        else:
            self.driver.find_element_by_css_selector(self.COMMENTS).send_keys(
                quick_room_transfer_fields["comments"])
        if self.no_hotel_record_found_from_qrt_form():
            pass
        else:
            self.driver.find_element_by_css_selector(self.FLIGHT_NUMBER). \
                send_keys(quick_room_transfer_fields["flight_number"])

    def get_total_rooms_avails_from_stats_bar(self):
        """ It will get the room avails count on QRT form"""
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)),
                        "Page is not fully loaded.")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_AVAIL_COUNT_AT_QRT_FORM)))
        quick_room_transfer_room_avails = self.driver.find_element_by_css_selector(self.ROOM_AVAIL_COUNT_AT_QRT_FORM).text
        room_count = int(quick_room_transfer_room_avails)
        # logger.debug("Total rooms avail shown on Quick Room Transfer form: %s", room_count)
        # print("Total rooms avail shown on Quick Room Transfer form:", room_count)
        return room_count

    def get_total_rooms_used_from_stats_bar(self):
        """ It will get the room used count on QRT form"""
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)),
                        "Page is not fully loaded.")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_USED_COUNT_AT_QRT_FORM)))
        quick_room_transfer_room_used = self.driver.find_element_by_css_selector(self.ROOM_USED_COUNT_AT_QRT_FORM).text
        # logger.debug("Total rooms used shown on Quick Room Transfer form: %s", quick_room_transfer_room_used)
        # print("Total rooms used shown on Quick Room Transfer form:", quick_room_transfer_room_used)
        return quick_room_transfer_room_used

    def get_room_used_count_from_usage_history(self):
        """ It will get the room used count on hotel usage section"""
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)),
                        "Hotel usage history is not fully loaded.")
        if self.no_hotel_record_found_from_usage_history():
            # logger.debug("Total room used shown on Hotel usage : 0")
            return str(0)
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_AT_HISTORY)),
                            "Hotel usage history is not fully loaded.")
            room_used = self.driver.find_elements_by_css_selector(self.ROOM_USED_COUNT_ON_HOTEL_USAGE)
            # logger.debug("Total room used shown on Hotel usage :", str(sum([int(room.text) for room in room_used])))
            return str(sum([int(room.text) for room in room_used]))

    def click_on_save_button(self):
        """ It will click on Save button and waits for form submission. if there occurs no inventory error, it will
        create a voucher and after that performs return rooms to inventory functionality. """
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
            sleep(5)
            if not(self.inventory_error()):
                self.voucher_creation_success_response()
                # self.rooms_return_to_inventory_on_base_of_paytype(port_id, airline_id)

    def inventory_error(self):
        """ It will return the rooms inventory errors"""
        try:
            inventory_error_msg = self.driver.find_element_by_css_selector(self.INVENTORY_ERROR_MESSAGE).text
            # print(inventory_error_msg)
            return True, inventory_error_msg
        except NoSuchElementException:
            return False

    def voucher_creation_success_response(self):
        """ It will return voucher creation success response."""
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SUCCESS_RESPONSE)),
                            "Voucher is not created!")
            success_response = self.driver.find_element_by_css_selector(self.SUCCESS_RESPONSE).text
            # created_voucher = self.driver.find_element_by_css_selector(TOP_CREATED_VOUCHER_NUMBER).text
            # print("Voucher #", created_voucher, "has been created successfully!")
            return success_response.strip("×\n")

    def return_rooms_from_usage_history(self):
        """ It will click on return button in hotel usage section. It will display the pop up of number of rooms
        returned, enter the same number of rooms that are used in voucher and click on the Update button."""
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.driver.find_element_by_css_selector(self.RETURN_BUTTON).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOMS_ADJUSTED)))
            adjusted_room_count = self.driver.find_element_by_css_selector(self.ADJUSTED_ROOM_COUNT).text
            room = adjusted_room_count.strip("Adjusted Room Count:")
            self.driver.find_element_by_css_selector(self.ROOMS_ADJUSTED).send_keys(room)
            self.driver.find_element_by_css_selector(self.UPDATE_BUTTON).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
            # logger.debug("%s rooms has been returned and Voucher is being canceled", room)
            sleep(3)

    def click_on_refresh_button(self):
        """ It will refresh the count of number of room avails and used"""
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.REFRESH_BUTTON)))
        self.driver.execute_script("$('form[name=\"QuickVoucherForm\"] a').click()")
        # self.driver.find_element_by_css_selector(self.REFRESH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))

    def voucher_numbers_list_from_usage_history(self):
        """ It will return the vouchers list from hotel usage section."""
        if not(self.no_hotel_record_found_from_usage_history()):
            voucher_numbers_list = self.driver.find_elements_by_css_selector(self.ALL_VOUCHER_NUMBERS)
            return voucher_numbers_list
        return []

    def rooms_return_to_inventory_on_base_of_paytype(self, port_id, airline_id):
        """ Firstly, it will get the response of quick room transfer page then verify the pay type of selected hotel. In
        case if pay type is 'Travelliance Wex' then it will not allow the user to return the number of rooms. """
        if not (self.no_hotel_record_found_from_usage_history()):
            response = self.get_hotel_inventory(port_id, airline_id)
            json_data = response.json()
            is_room_return_allowed = json_data[0]['is_rooms_return_allowed']
            """
            If is_room_return flag is true, rooms cannot be returned to inventory.
            """
            if not (int(is_room_return_allowed) == int(False)):
                self.return_rooms_from_usage_history()
            # else:
            #     logger.info("Rooms cannot return for Hotels with TVA WEX pay type and hard blocks")

    def get_top_created_voucher_number(self):
        """ It will return the top created voucher number on hotel usage section."""
        if not (self.no_hotel_record_found_from_usage_history()):
            top_created_voucher = self.driver.find_element_by_css_selector(self.TOP_CREATED_VOUCHER_NUMBER).text
            return top_created_voucher

    def no_hotel_record_found_from_qrt_form(self):
        """ In case, if selected port and airline doesn't have any inventory
        Find_element_by_css returns True if it finds an element, exception if not.
        :return: Bool
        """
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)))
            self.driver.find_element_by_css_selector(self.NO_HOTEL_RECORD_FOUND)
            # print("No Record Found!")
            return True
        except NoSuchElementException:
            return False

    def no_hotel_record_found_from_usage_history(self):
        """
        Find_element_by_css returns True if it finds an element, exception if not.
        :return: Bool
        """
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)))
            self.driver.find_element_by_css_selector(self.NO_HOTEL_USAGE_RECORD_FOUND)
            return True
        except NoSuchElementException:
            return False

    def verify_max_allowed_visible_for_airline_user(self):
        """ It will check either 'MAX ALLOWED' count is visible or not on QRT page for airline users"""
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
                            "Page is not fully loaded.")
            assert self.is_visible(self.MAX_ALLOWED)

    def check_inventory_allowance_exceeded(self):
        """ It will check Inventory exceeded error is visible, in case, if value of needed room is greater than the
        count of max allowed limit."""
        if self.no_hotel_record_found_from_qrt_form():
            return "No Record Found!"
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
                            "Page is not fully loaded.")
            max_allowed_limit = self.driver.find_element_by_css_selector(self.MAX_ALLOWED).text
            # logger.debug("Max allowed inventory allowanaces: %s", max_allowed_limit)
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_NEED)))
            self.driver.find_element_by_css_selector(self.ROOM_NEED).click()
            self.driver.find_element_by_css_selector(self.ROOM_NEED).send_keys(int(max_allowed_limit) + 1)
            self.driver.find_element_by_css_selector(self.PHONE_NUMBER).send_keys("12345678965")
            self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.INVENTORY_ERROR_MESSAGE)),
                            "Inventory exceeded error is not visible.")
            inventory_error_msg = self.driver.find_element_by_css_selector(self.INVENTORY_ERROR_MESSAGE).text
            # logger.debug(inventory_error_msg)
            return inventory_error_msg

    def max_allowed_on_qrt_page(self):
        return self.driver.find_element_by_css_selector(self.MAX_ALLOWED).text

    def check_insufficient_availability_for_hotel(self):
        """ It will check Inventory insufficient error is visible, in case, if value of needed room is greater than the
        count of rooms avail limit."""
        if self.no_hotel_record_found_from_qrt_form():
            return "No Record Found!"
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
                            "Page is not fully loaded.")
            rooms_avail_limit = self.driver.find_element_by_css_selector(self.ROOM_AVAIL_COUNT_AT_QRT_FORM).text
            # logger.debug("Maximum rooms avail: %s", rooms_avail_limit)
            self.driver.find_element_by_css_selector(self.ROOM_NEED).send_keys(int(rooms_avail_limit) + 1)
            self.driver.find_element_by_css_selector(self.PHONE_NUMBER).send_keys("12345678965")
            self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.INVENTORY_ERROR_MESSAGE)),
                            "Inventory exceeded error is not visible.")
            insufficient_booking_error_msg = self.driver.find_element_by_css_selector(self.INVENTORY_ERROR_MESSAGE).text
            # logger.debug(insufficient_booking_error_msg)
            return insufficient_booking_error_msg

    def check_error_on_saving_zero_number_in_room_need(self):
        """ It will verify error "Can't save with room count as 0" is visible, in case, if value of needed room is
        zero"""
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
                        "Page is not fully loaded.")
        if self.no_hotel_record_found_from_qrt_form():
            return "No Record Found!"
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
                            "Page is not fully loaded.")
            self.driver.find_element_by_css_selector(self.ROOM_NEED).send_keys(0)
            self.driver.find_element_by_css_selector(self.PHONE_NUMBER).send_keys("12345678965")
            self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.INVENTORY_ERROR_MESSAGE)),
                            "Inventory error message is not visible.")
            inventory_error_message = self.driver.find_element_by_css_selector(self.INVENTORY_ERROR_MESSAGE).text
            # logger.debug(inventory_error_message)
            return inventory_error_message

    def click_on_hotel_name(self):
        """ It will click on first hotel listed under the column of hotels and gets the name of that hotel"""
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
                            "Page is not fully loaded.")
            hotel_name = self.driver.find_element_by_css_selector(self.FIRST_HOTEL)
            hotel = hotel_name.text.upper()
            hotel_name.click()
            return hotel

    def hotel_details_visibility_by_clicking_hotel_name(self):
        """It will return the hotel info."""
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_INFO)),
                            'Hotel info is not loaded!')
            hotel_info = self.driver.find_element_by_css_selector(self.HOTEL_INFO).text
            return hotel_info

    def hotel_map_visibility_by_clicking_view_hotel_on_map(self):
        """ It will display the map on clicking View Hotel on map button. We are getting the iframe count and base on
        that count, verify the map visibility"""
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BUTTON_VIEW_HOTEL_MAP)),
                            "Button is not visible")
            self.driver.find_element_by_css_selector(self.BUTTON_VIEW_HOTEL_MAP).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.MAP_IFRAME)))
            iframe_count = self.driver.find_elements_by_css_selector(self.MAP_IFRAME)
            return len(iframe_count)

    def hotel_map_invisibility_by_clicking_hide_map(self):
        """ It will hide the map by clicking on Hide Map button. We are getting the iframe count and base on
        that count, verify the map visibility"""
        if not (self.no_hotel_record_found_from_qrt_form()):
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BUTTON_HIDE_MAP)),
                            "Button is not visible")
            self.driver.find_element_by_css_selector(self.BUTTON_HIDE_MAP).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.MAP_IFRAME)))
            iframe_count = self.driver.find_elements_by_css_selector(self.MAP_IFRAME)
            return len(iframe_count)

    def click_on_voucher_number_to_preview(self):
        """ It will open the voucher preview by clicking on voucher number and gets the rooms used count in voucher
        preview"""
        if not (self.no_hotel_record_found_from_usage_history()):
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_AT_HISTORY)),
                            "Button is not visible")
            # element = driver.find_element_by_css('div[class*="loadingWhiteBox"]')
            # webdriver.ActionChains(driver).move_to_element(element).click(element).perform()

            voucher_button = self.driver.find_element_by_css_selector(self.TOP_CREATED_VOUCHER_NUMBER)
            self.actions.move_to_element(voucher_button).click(voucher_button).perform()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_MODAL)),
                            "Button is not visible")
            voucher_preview = self.driver.find_element_by_css_selector('.modal-header').text
            logger.debug(voucher_preview)
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.col-sm-4 strong')),
                            "Rooms used Text in voucher modal is not visible")
            rooms_used_at_voucher_preview = self.driver.find_element_by_css_selector(self.ROOMS_USED_AT_PREVIEW).text
            return rooms_used_at_voucher_preview

    def close_voucher_preview(self):
        """ It will close the voucher preview by clicking on close button and get the count of rooms used for first
        voucher"""
        if not (self.no_hotel_record_found_from_usage_history()):
            self.driver.find_element_by_css_selector(self.CLOSE_MODAL_BUTTON).click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_MODAL)),
                            "Close button has some issue")
            rooms_for_first_voucher = self.driver.find_element_by_css_selector(self.ROOMS_USED_FIRST_VOUCHER_ON_USAGE).text
            return rooms_for_first_voucher

    def max_allowed_limit_for_airline(self):
        """
        It will check that if number of used rooms are greater than or equal to max allowed allowances count then max
        allowed allowances error message should be shown on the page. Else, it will create a voucher successfully.
        :return: string
        """
        if self.no_hotel_record_found_from_qrt_form():
            return "No Record Found!"
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_BUTTON)),
                            "Page is not fully loaded.")
            max_allowed_limit = self.driver.find_element_by_css_selector(self.MAX_ALLOWED).text
            # logger.info("Max allowed inventory allowances: %s", max_allowed_limit)
            used_rooms = self.driver.find_element_by_css_selector(self.ROOM_USED_COUNT_AT_QRT_FORM).text
            # logger.debug("Used rooms: %s", used_rooms)
            if int(used_rooms) >= int(max_allowed_limit):
                self.fill_quick_room_transfer_fields(fill_quick_room_transfer_form())
                self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.INVENTORY_ERROR_MESSAGE)),
                                "Inventory exceeded error is not visible.")
                inventory_error_msg = self.driver.find_element_by_css_selector(self.INVENTORY_ERROR_MESSAGE).text
                # logger.debug(inventory_error_msg)
                return inventory_error_msg
            else:
                self.fill_quick_room_transfer_fields(fill_quick_room_transfer_form())
                self.click_on_save_button()
                return self.voucher_creation_success_response()
