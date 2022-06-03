#!/usr/bin/env python3
# import logging
# logging.basicConfig(level=logging.INFO)
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# logging.getLogger('').addHandler(console)
# logger = logging.getLogger(__name__)
import unittest

from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
from e2e_selenium_tests.PageObjectClasses.airline_page import set_values_to_add_new_airline_user
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings, get_hotel_block_fields
from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.BaseClasses.helper import fill_quick_room_transfer_form

QUICK_ROOM_TRANSFER_PAGE = '/admin/quick-room-transfer.php'
AIRLINE_PAGE = '/admin/airlines.php'
AIRLINE_DASHBOARD = '/admin/index.php'


class TestQuickRoomTransfer(TestBaseClass):
    PORT_NAME = "LIT Clinton National Airport"
    PORT_ID = 966  # We need port id to request the page response for checking hotel's pay type
    PORT_PREFIX = PORT_NAME.split()[0]
    AIRLINE_NAME = "PRP Purple Rain Airlines"
    AIRLINE_NAME_WITHOUT_PREFIX = "Purple Rain Airlines"
    AIRLINE_PREFIX = AIRLINE_NAME.split()[0]
    AIRLINE_ID = 294  # We need airline id to request the page response for checking hotel's pay type
    AIRLINE_USER_NAME = ""
    AIRLINE_USER_PASSWORD = ""
    ROLE = ""
    NEW_PASSWORD = "Tvlinc123!@#@"
    AIRLINE_EMPLOYEE_AT_PORT_USERNAME = "jqasia"
    AIRLINE_EMPLOYEE_AT_PORT_PASSWORD = "Tvlinc123!@#"
    PORT_MODAL = 'data.selected_port'
    PORT_MODAL_HOTEL_LISTING = 'filter.pid'
    PORT_PLACEHOLDER = 'Type port name or prefix'
    AIRLINE_MODAL = 'data.selected_airline'
    AIRLINE_PLACEHOLDER = 'Choose Airline'

    def setUp(self):
        super(TestQuickRoomTransfer, self).setUp()

    @ignore_warnings
    def test_quick_room_transfer_voucher_for_tvl_users(self):
        """
        We'll check the complete basic flow of quick room transfer vouchers.
        Firstly, user went to the login page. System verified either user on login page or not.
        After that user enters valid login credentials and click on login button.
        System verified the credentials and navigate the user to the Dashboard page. Once the page is loaded
        successfully.
        Click on the Quick Room Transfer tab.
        User navigates to the QRT page. User selects the Port and Airline.
        On selecting port and airline system display all hotels which have rooms available for that port and airline for
        the current day. (It will display the previous day inventory before 5AM of current day)
        User enters the number of room needed, direct contact phone, EXT, Comments and flight number.
        Click on the Save button and a message of "Save was successful." should be displayed.
        After that voucher is created and  displayed in the Hotel Usage Today section.
        User clicks on the Return button to return the number of rooms availed.
        It will display the pop up of number of rooms returned, user enter the same number of rooms that are used in
        voucher and click on the Update button.
        After returned the number of availed/used rooms, system gets the list of vouchers created and search the
        above created voucher number in that list. If previously created voucher number is found in that list then
        test will be failed otherwise test will be passed.

        Steps:
        * Login with valid credentials.
        * Go to Quick Room Transfer page
        * Select desired port and airline
        * If the desired port and airline has rooms inventory then it will fill all required fields.
        * Click on Save button.
        * Click in Return button.
        * Give the same voucher's room amount in adjusted rooms field.
        * Click on Update button.
        * Search the created voucher number in all created voucher list.

        """
        self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                       desired_page=STORMX_URL + QUICK_ROOM_TRANSFER_PAGE)
        self.verify_page_title()
        self.select_port_and_airline_dropdown()
        self.verify_error_validation_insufficient_availability()
        self.verify_validation_error_on_saving_zero_number_in_need_field()
        self.verify_rooms_avail_count_on_qrt_and_hotel_listing()
        self.go_to_quick_room_transfer_page()
        self.select_port_and_airline_dropdown()
        self.verify_room_count_on_qrt_form_equal_to_sum_of_rooms_used_in_hotel_usage()
        self.verify_hotel_details_should_be_displayed_by_clicking_hotel_name()
        # self.verify_map_visibility()  #Todo: Map doesn't load for local environment.
        self.verify_voucher_modal_is_opened_by_clicking_voucher_number()

    @ignore_warnings
    def test_quick_room_transfer_voucher_for_airline_users(self):
        self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                       desired_page=STORMX_URL + AIRLINE_PAGE)
        self.airline_page.open_airline_details_page_via_api(airline_id=self.AIRLINE_ID)
        # self.airline_page.airline_search_filter(airline_name=self.AIRLINE_ID)
        # self.airline_page.open_airline_details_page()
        self.airline_page.click_on_ports_tab_from_airline_details()
        self.airline_page.select_serviced_port(self.PORT_PREFIX)
        self.airline_page.click_on_add_port_button()
        self.assertIn(self.PORT_NAME, self.airline_page.get_serviced_port_list(), "Port is not added successfully.")
        # self.assertIn(self.airline_page.get_port_name_from_service_ports_section(),
        #               self.airline_page.get_serviced_port_list())
        self.airline_page.refresh_page()
        self.airline_page.click_on_users_tab_from_airline_details()
        self.AIRLINE_USER_NAME, self.AIRLINE_USER_PASSWORD, self.ROLE = self.airline_page. \
            fill_data_in_new_airline_user(set_values_to_add_new_airline_user(port_to_service=self.PORT_PREFIX,
                                                                             user_role="Employee at Port"),
                                          str(self.PORT_ID))
        self.airline_page.click_on_save_user_button()
        self.assertListEqual(self.airline_page.get_user_creation_error_messages(), [])
        self.airline_page.logout_user()
        self.api_login(username=self.AIRLINE_USER_NAME, password=self.AIRLINE_USER_PASSWORD,
                       resetpassword=self.NEW_PASSWORD, desired_page=STORMX_URL + AIRLINE_DASHBOARD)
        # self.login_user(self.AIRLINE_USER_NAME, self.AIRLINE_USER_PASSWORD, self.NEW_PASSWORD)
        # self.verify_quick_room_transfer_page()
        self.verify_airline_dashboard_page()
        self.go_to_quick_room_transfer_page()
        self.verify_page_title()
        self.quick_room_transfer.find_and_select_port_from_dropdown(self.PORT_PREFIX, self.PORT_MODAL,
                                                                    self.PORT_PLACEHOLDER)
        self.verify_error_validation_insufficient_availability()
        self.verify_validation_error_on_saving_zero_number_in_need_field()
        self.verify_max_allowed_allowances_for_airline_users()
        self.verify_inventory_allowances_exceeded_for_airline_users()
        self.verify_room_count_on_qrt_form_equal_to_sum_of_rooms_used_in_hotel_usage()
        self.verify_hotel_details_should_be_displayed_by_clicking_hotel_name()
        # self.verify_map_visibility()  #Todo: Map doesn't load for local environment.
        self.verify_voucher_modal_is_opened_by_clicking_voucher_number()

    def verify_page_title(self):
        self.assertIn("Quick Room Transfer | Travelliance", self.quick_room_transfer.get_page_html_source(),
                      "Quick Room Transfer page is not fully loaded!")

    def fill_quick_room_transfer_fields_data(self):
        self.quick_room_transfer.fill_quick_room_transfer_fields(fill_quick_room_transfer_form())
        self.quick_room_transfer.click_on_save_button()

    def vouchers_rooms_return_to_inventory(self):
        self.quick_room_transfer.rooms_return_to_inventory_on_base_of_paytype(self.PORT_ID, self.AIRLINE_ID)

    def total_room_used_count_from_stat_bar(self):
        self.quick_room_transfer.click_on_refresh_button()
        room_used_count_at_qrt_form = self.quick_room_transfer.get_total_rooms_used_from_stats_bar()
        return room_used_count_at_qrt_form

    def total_room_used_count_from_usage_history(self):
        # self.select_port_and_airline_dropdown()
        self.quick_room_transfer.click_on_refresh_button()
        room_used_count_from_usage_history = self.quick_room_transfer.get_room_used_count_from_usage_history()
        return room_used_count_from_usage_history

    def total_room_avails_count_from_stat_bar(self):
        self.select_port_and_airline_dropdown()
        # self.quick_room_transfer.click_on_refresh_button()
        room_count_from_stat_bar = self.quick_room_transfer.get_total_rooms_avails_from_stats_bar()
        return room_count_from_stat_bar

    def airline_room_count_from_hotel_page(self):
        """
        It will get the total room count of specific airline from hotel listing page.
        :return: Int
        """
        self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL_HOTEL_LISTING,
                                                       self.PORT_PLACEHOLDER)
        room_count_on_hotel_listing = self.hotel_page.airline_room_count_from_hotel_page(self.AIRLINE_PREFIX)
        return room_count_on_hotel_listing

    def select_port_and_airline_dropdown(self):
        self.quick_room_transfer.find_and_select_port_from_dropdown(self.PORT_PREFIX, self.PORT_MODAL,
                                                                    self.PORT_PLACEHOLDER)
        self.quick_room_transfer.find_and_select_airline_from_dropdown(self.AIRLINE_PREFIX, self.AIRLINE_MODAL,
                                                                       self.AIRLINE_PLACEHOLDER)

    def hotel_details_visibility_by_clicking_hotel_name(self):
        self.select_port_and_airline_dropdown()
        self.quick_room_transfer.click_on_hotel_name()
        self.quick_room_transfer.hotel_details_visibility_by_clicking_hotel_name()

    def verify_map_visibility(self):
        """
        Verify that map should be displayed by clicking on the text 'View Hotel on Map' and verify that
        map should be hidden by clicking on the text 'Hide Map
        """
        map_visibility_iframe = [1, None]
        map_invisibility_iframe = [0, None]
        self.quick_room_transfer.click_on_hotel_name()
        self.assertIn(self.quick_room_transfer.hotel_map_visibility_by_clicking_view_hotel_on_map(),
                      map_visibility_iframe)
        self.assertIn(self.quick_room_transfer.hotel_map_invisibility_by_clicking_hide_map(), map_invisibility_iframe)

    def verify_rooms_avail_count_on_qrt_and_hotel_listing(self):
        """
        Verify that Rooms Avail count on QRT page should be equal to the count of Airline pay blocks on
        hotel listing page for specific port. In case, if airline pay blocks is defined for all airlines
        then system should display the sum of specific airline and all airline pay blocks.
        (Specific airline + Any Airline).
        """
        room_count_on_qrt = self.total_room_avails_count_from_stat_bar()
        self.go_to_hotel_page()
        self.assertIn("Hotels | Travelliance", self.hotel_page.get_page_html_source(), "Hotel page is not fully loaded")
        room_count_on_hotel_listing = self.airline_room_count_from_hotel_page()
        self.assertEqual(room_count_on_qrt, room_count_on_hotel_listing,
                         'Room count at hotel listing page and quick room transfer page is not validated!')

    def verify_validation_error_on_saving_zero_number_in_need_field(self):
        """Verify that validation error \"Can't save with room count as 0\" should be displayed, when user save the
        information with zero number in the Need field
        """
        expected_errors_ = ["Can't save with room count as 0", "No Record Found!"]
        self.quick_room_transfer.click_on_refresh_button()
        self.assertIn(
            self.quick_room_transfer.check_error_on_saving_zero_number_in_room_need(), expected_errors_)

    def verify_voucher_modal_is_opened_by_clicking_voucher_number(self):
        """
        Verify that voucher modal should be displayed by clicking on the voucher link and also modal
        should be closed by clicking on close button of voucher modal.
        """
        self.fill_quick_room_transfer_fields_data()
        self.vouchers_rooms_return_to_inventory()
        self.assertEqual(self.quick_room_transfer.click_on_voucher_number_to_preview(),
                         self.quick_room_transfer.close_voucher_preview())

    def verify_hotel_details_should_be_displayed_by_clicking_hotel_name(self):
        """
        Verify that hotel details should be displayed by clicking on the name of the hotel
        """
        self.assertEqual(self.quick_room_transfer.click_on_hotel_name(), self.quick_room_transfer.
                         hotel_details_visibility_by_clicking_hotel_name(), "Hotel names are mismatched!")

    def verify_error_validation_insufficient_availability(self):
        """
        Verify that validation error Hotel availability is insufficient for booking should be displayed,
        when user enter the no of rooms to be booked greater than the available room.
        """
        expected_errors = ['Hotel availability is insufficient for booking.', 'Inventory allowance exceeded. '
                                                                              'Please call (800) 642-7310 for '
                                                                              'assistance', 'No Record Found!']
        self.quick_room_transfer.click_on_refresh_button()
        self.assertIn(self.quick_room_transfer.check_insufficient_availability_for_hotel(), expected_errors)

    def verify_room_count_on_qrt_form_equal_to_sum_of_rooms_used_in_hotel_usage(self):
        """
        Verify that used room count displayed on quick room transfer form for specific port and airline
        should be equal to the sum of rooms used in Hotel usage today section
        """
        self.assertEqual(self.total_room_used_count_from_stat_bar(), self.total_room_used_count_from_usage_history())

    def verify_max_allowed_allowances_for_airline_users(self):
        expected_error = ['Inventory allowance exceeded. Please call (800) 642-7310 for assistance', 'No Record Found!',
                          'Save was successful.']
        self.quick_room_transfer.click_on_refresh_button()
        self.assertIn(self.quick_room_transfer.max_allowed_limit_for_airline(), expected_error)

    def verify_inventory_allowances_exceeded_for_airline_users(self):
        expected_error = ['Inventory allowance exceeded. Please call (800) 642-7310 for assistance', 'No Record Found!',
                          'Hotel availability is insufficient for booking.']
        self.assertIn(self.quick_room_transfer.check_inventory_allowance_exceeded(), expected_error)

    def tearDown(self):
        self.browser.close()
