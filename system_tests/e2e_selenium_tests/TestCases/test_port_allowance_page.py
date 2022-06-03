from e2e_selenium_tests.PageObjectClasses import stormx_api_methods
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL, LOGOUT_URL
from e2e_selenium_tests.PageObjectClasses.airline_page import set_values_to_add_new_airline_user
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings, get_hotel_block_fields, get_system_current_date_time, \
    get_availability_date
from e2e_selenium_tests.TestCases.base_test import TestBaseClass

HOTEL_PAGE = '/admin/hotels.php'
PORT_ALLOWANCE_PAGE = '/admin/port_allowance.php'
AIRLINE_DASHBOARD = '/admin/index.php'
HOTEL_SEARCH_PARAMS = '?page=&pid={}&hid='


class TestPortAllowance(TestBaseClass):
    PORT_NAME = "CID The Eastern Iowa Airport"
    PORT_ID = 802
    PORT_PREFIX = PORT_NAME.split()[0]
    AIRLINE_NAME = "PRP Purple Rain Airlines"
    AIRLINE_NAME_WITHOUT_PREFIX = "Purple Rain Airlines"
    AIRLINE_PREFIX = AIRLINE_NAME.split()[0]
    AIRLINE_ID = 294
    AIRLINE_USER_NAME = ""
    AIRLINE_USER_PASSWORD = ""
    ROLE = ""
    NEW_PASSWORD = "Tvlinc123!@#@"
    AIRLINE_EMPLOYEE_AT_PORT_USERNAME = "jqasia"
    AIRLINE_EMPLOYEE_AT_PORT_PASSWORD = "Tvlinc123!@#"
    PORT_MODAL = 'data.selected_port'
    PORT_MODAL_HOTEL_LISTING = 'filter.pid'
    PORT_PLACEHOLDER = 'Type port name or prefix'
    PORT_DROPDOWN_MODAL = 'filter.pid'
    AIRLINE_MODAL = 'data.selected_airline'
    AIRLINE_PLACEHOLDER = 'Choose Airline'
    ALLOWANCE = '125'
    TEMP_ALLOWANCE = '5'
    INVALID_TEMP_ALLOWANCE = '0'
    TOTAL_ALLOWANCE = ''

    def setUp(self):
        super(TestPortAllowance, self).setUp()

    @ignore_warnings
    def test_add_new_port_allowance(self):
        """
    For TVA IT Support user:

        Test add new allowance.
        Test verify newly added allowances on allowances listing page.
        Test Invalid value for temporary allowance.
        Test temporary allowance saved successfully.
        Test total allowance should be equal to Allowance plus temporary addition.
        Test newly added temporary allowances records with allowances listing records.
        Test add duplicate allowance should show an error message.
        Test delete allowances functionality.
     :return:
     """
        self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                       desired_page=STORMX_URL + PORT_ALLOWANCE_PAGE)
        self.port_allowance_page.verify_browser_on_the_page()
        self.port_allowance_page.click_on_add_new_allowance_button()
        self.port_allowance_page.select_port(self.PORT_PREFIX, self.PORT_MODAL, self.PORT_PLACEHOLDER)
        self.port_allowance_page.fill_data_on_port_allowance_form(self.AIRLINE_NAME, self.ALLOWANCE)
        dates = get_system_current_date_time("America/Chicago")
        self.assertEqual(self.port_allowance_page.click_on_save_allowance_button(), 'Allowance saved successfully.')
        # dates = get_system_current_date_time("America/Chicago")
        self.assertTrue(self.port_allowance_page.verify_newly_added_allowances_on_allowances_listing
                        (self.PORT_PREFIX, self.AIRLINE_NAME_WITHOUT_PREFIX, self.ALLOWANCE, self.ALLOWANCE, dates),
                        "Newly added allowances records are not matched with allowances listing count")
        self.assertEqual(self.port_allowance_page.add_temporary_allowances(self.INVALID_TEMP_ALLOWANCE,
                                                                           boundary_value=True),
                         "Invalid value for temporary allowance.")
        self.assertEqual(self.port_allowance_page.add_temporary_allowances(self.TEMP_ALLOWANCE),
                         "Temporary allowance saved successfully.")
        self.assertEqual(int(self.port_allowance_page.total_allowance_calculation()), (int(self.TEMP_ALLOWANCE) +
                                                                                       int(self.ALLOWANCE)))
        total_allowance = int(self.TEMP_ALLOWANCE) + int(self.ALLOWANCE)
        self.assertTrue(self.port_allowance_page.verify_newly_added_allowances_on_allowances_listing
                        (self.PORT_PREFIX, self.AIRLINE_NAME_WITHOUT_PREFIX, self.ALLOWANCE, str(total_allowance),
                         get_system_current_date_time("America/Chicago")),
                        "Newly added allowances records are not matched with allowances listing count")
        self.port_allowance_page.click_on_add_new_allowance_button()
        self.port_allowance_page.select_port(self.PORT_PREFIX, self.PORT_MODAL, self.PORT_PLACEHOLDER)
        self.port_allowance_page.fill_data_on_port_allowance_form(self.AIRLINE_NAME, self.ALLOWANCE)
        self.assertEqual(self.port_allowance_page.click_on_save_allowance_button(check_duplicate=True),
                         'A record with same port and airline already exists.')
        self.port_allowance_page.click_on_close_button()
        self.assertEqual(self.port_allowance_page.delete_allowance(), "Record successfully deleted.")

    @ignore_warnings
    def test_port_allowance_for_airline_user(self):
        """
    For Airline user:

        Test max allowed should be equal to hotel avail count if hotel avail is less than total allowance.
        Test max allowed should be equal to total allowances if hotel avail is greater than total allowance..

        :return:
        """
        self.support_cookies = self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                                              desired_page=STORMX_URL + HOTEL_PAGE)
        self.verify_hotel_page()
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_DROPDOWN_MODAL,
                                                                       self.PORT_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID,airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0')
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), self.AIRLINE_PREFIX), True)
        self.go_to_port_allowance_page()
        self.port_allowance_page.click_on_add_new_allowance_button()
        self.port_allowance_page.select_port(self.PORT_PREFIX, self.PORT_MODAL, self.PORT_PLACEHOLDER)
        self.port_allowance_page.fill_data_on_port_allowance_form(self.AIRLINE_NAME, self.ALLOWANCE)
        dates = get_system_current_date_time("America/Chicago")
        self.assertEqual(self.port_allowance_page.click_on_save_allowance_button(), 'Allowance saved successfully.')
        # dates = get_system_current_date_time("America/Chicago")
        self.assertTrue(self.port_allowance_page.verify_newly_added_allowances_on_allowances_listing
                        (self.PORT_PREFIX, self.AIRLINE_NAME_WITHOUT_PREFIX, self.ALLOWANCE, self.ALLOWANCE, dates),
                        "Newly added allowances records are not matched with allowances listing count")
        self.TOTAL_ALLOWANCE = self.port_allowance_page.total_allowance_calculation()
        self.go_to_airline_page()
        # self.airline_page.airline_search_filter(airline_name=self.AIRLINE_ID)
        # self.airline_page.open_airline_details_page()
        self.airline_page.open_airline_details_page_via_api(airline_id=self.AIRLINE_ID)
        self.airline_page.click_on_ports_tab_from_airline_details()
        self.airline_page.select_serviced_port(self.PORT_PREFIX)
        self.airline_page.click_on_add_port_button()
        self.assertIn(self.PORT_NAME, self.airline_page.get_serviced_port_list(), "Port is not added yet.")
        self.airline_page.refresh_page()
        self.airline_page.click_on_users_tab_from_airline_details()
        self.AIRLINE_USER_NAME, self.AIRLINE_USER_PASSWORD, self.ROLE = self.airline_page. \
            fill_data_in_new_airline_user(set_values_to_add_new_airline_user(port_to_service=self.PORT_PREFIX,
                                                                             user_role="Employee at Port"),
                                          str(self.PORT_ID))
        self.airline_page.click_on_save_user_button()
        self.assertListEqual(self.airline_page.get_user_creation_error_messages(), [])
        # self.airline_page.logout_user()
        self.logout_user(LOGOUT_URL)
        self.api_login(username=self.AIRLINE_USER_NAME, password=self.AIRLINE_USER_PASSWORD,
                       resetpassword=self.NEW_PASSWORD, desired_page=STORMX_URL + AIRLINE_DASHBOARD)
        # self.login_user(self.AIRLINE_USER_NAME, self.AIRLINE_USER_PASSWORD, self.NEW_PASSWORD)
        self.verify_airline_dashboard_page()
        self.go_to_quick_room_transfer_page()
        self.quick_room_transfer.click_on_refresh_button()
        self.assertGreater(self.TOTAL_ALLOWANCE, self.quick_room_transfer.max_allowed_on_qrt_page(),
                           "Max allowed should be less than Total allowances in this case.")
        self.logout_user(LOGOUT_URL)
        # self.sso_login_page.logout_user()
        # self.login_user()
        self.support_cookies = self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                                              desired_page=STORMX_URL + HOTEL_PAGE)
        self.verify_hotel_page()
        self.HOTEL_ID = self.select_port_filter_by_url(STORMX_URL + HOTEL_PAGE + HOTEL_SEARCH_PARAMS.
                                                       format(self.PORT_ID))
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0')
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), self.AIRLINE_PREFIX), True)
        self.logout_user(LOGOUT_URL)
        self.api_login(username=self.AIRLINE_USER_NAME, password=self.NEW_PASSWORD,
                       resetpassword=self.NEW_PASSWORD, desired_page=STORMX_URL + AIRLINE_DASHBOARD)
        self.verify_airline_dashboard_page()
        self.go_to_quick_room_transfer_page()
        self.quick_room_transfer.click_on_refresh_button()
        self.assertEqual(self.TOTAL_ALLOWANCE, self.quick_room_transfer.max_allowed_on_qrt_page(),
                         "Max allowed should be equal to Total allowances in this case.")

    def tearDown(self):
        self.browser.close()
