from e2e_selenium_tests.PageObjectClasses import stormx_api_methods
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
from e2e_selenium_tests.PageObjectClasses.hotel_page import set_values_to_new_hotel_fields, \
    set_values_to_add_new_hotel_user
from e2e_selenium_tests.BaseClasses.helper import get_hotel_block_fields, get_availability_date
from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings
from e2e_selenium_tests.PageObjectClasses.tva_users_page import set_values_to_add_new_tvl_user


PORT_MODAL = 'filter.pid'
PORT_DROPDOWN_PLACEHOLDER = 'Type port name or prefix'
HOTEL_ROOM_TYPE = 'Accessibility Room'
PAY_TYPE = 'Airline Pay'
_HOTEL_ID = "108672"
HOTEL_ID = ""
EAN_ID = ""
TVA_USERS_DATA = []
NEW_PASSWORD = "Tvlinc123!@#@"
HOTEL_PAGE = '/admin/hotels.php'
HOTEL_SEARCH_PARAMS = '?page=&pid=&hid={}'
EXPEDIA_HOTEL_ID = '114747'


USERS = {'tvl_it_support_user_name': 'support',
         'tvl_it_support)user_password': 'test',
         'invalid_password': 'invalid@password',
         'new_password': 'Tvlinc123!@#@'
         }

AIRLINE_DATA = {'airline_name': 'PRP Purple Rain Airlines',
                'airline_prefix': 'PRP',
                'airline_id': '294'
                }

PORT = {'port_name': "LIT Clinton National Airport",
        'port_prefix': 'LIT',
        'port_id': '966'
        }


class TestHotel(TestBaseClass):
    def setUp(self):
        super(TestHotel, self).setUp()

    @ignore_warnings
    def test_add_new_hotel(self):
        """
        Verify that user should be able to add new hotel successfully.

        Steps:
        * Login with valid credentials.
        * Go to Hotel listing page.
        * Click on Add New Hotel button.
        * Fill all fields on add new hotel form.
        * Click on Save button.
        * Verify that new hotel's id is present in current url.
        * Click on Serviced Ports tab.
        * Add port from serviced ports dropdown.
        * Verify that newly added port is shown under serviced ports section.
        * Click on Users tab.
        * Add new user data.
        * Check if there is any error.
        * If no error found user is created successfully, else, there is some error in user creation.
        * Click on Taxes tab.
        * Click on edit tax button of first tax entry.
        * Click on Add tax button.
        * Verify that newly added tax is visible on tax history section. # TODO
        * Click on Amenities tab.
        * Add first amenity hours, fee and notes.
        * Click on Save button.
        * Verify that "Amenity information saved successfully." is visible on page.
        * Go to Hotel listing page.
        * Search the newly created hotel with hotel id.
        * Click on View Hotel Amenity button.
        * Search first added hotel's amenity name on view hotel amenity modal.
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.click_on_add_new_hotel_button()
        self.hotel_page.fill_data_in_new_hotel_form(set_values_to_new_hotel_fields())
        self.assertTrue(self.hotel_page.click_on_hotel_save_button(),
                        'There is an error while saving hotel data. '
                        'Some mandatory field data is not saved correctly')
        self.HOTEL_ID = self.hotel_page.get_hotel_id()
        self.assertIn(self.HOTEL_ID, self.hotel_page.get_current_url_of_hotel_page())
        self.assertEqual(self.hotel_page.hotel_logo_uploading(), 'Uploaded successfully.')
        self.assertEqual(self.hotel_page.hotel_rfp_contract_uploading(), 'Uploaded successfully.')
        self.assertEqual(self.hotel_page.hotel_credit_application_uploading(), 'Uploaded successfully.')
        self.assertEqual(self.hotel_page.hotel_self_billing_contract_uploading(), 'Uploaded successfully.')
        self.hotel_page.click_on_serviced_ports_tab_from_hotel_details()
        self.hotel_page.select_serviced_port(PORT['port_prefix'])
        self.hotel_page.click_on_add_port_button()
        self.assertIn(PORT['port_name'], self.hotel_page.get_serviced_port_list(), "Serviced Port is not added.")
        self.hotel_page.click_on_users_tab_from_hotel_details()
        user_roles = self.hotel_page.get_hotel_user_roles()
        for role in user_roles[1:]:
            self.hotel_page.fill_data_in_new_hotel_user(set_values_to_add_new_hotel_user(user_role=role))
            self.hotel_page.click_on_save_user_button()
            self.assertListEqual(self.airline_page.get_user_creation_error_messages(), [],
                                 "Errors are shown on page while adding new user.")
        self.hotel_page.click_on_amenities_tab_from_hotel_details()
        self.hotel_page.add_amenities_of_hotel()
        amenity_name = self.hotel_page.click_on_save_amenities_button()
        self.hotel_page.click_on_daily_soft_block_tab_from_hotel_details()
        self.hotel_page.select_date_from_daily_soft_block_form()
        self.hotel_page.fill_data_to_soft_block_form(AIRLINE_DATA['airline_name'], HOTEL_ROOM_TYPE, PAY_TYPE)
        self.assertTrue(self.hotel_page.click_on_soft_block_save_button())
        self.assertFalse(self.hotel_page.edit_soft_block_rate(),
                         "There is an error while saving daily soft blocks data. Please try later.")
        self.go_to_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.assertIn(amenity_name, self.hotel_page.get_added_amenities_list_from_view_hotel_amenities_section())

    @ignore_warnings
    def test_hotel_tax(self):
        """
        Add hotel inventory.
        Go to hotel's detail page.
        Add fixed tax type.
        Go to Quick voucher page.
        Verify that newly added fixed tax value should be shown on quick voucher modal with hotel's rate section.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.search_hotel_on_hotel_listing(_HOTEL_ID)
        self.browser.get(STORMX_URL + HOTEL_PAGE + HOTEL_SEARCH_PARAMS.format(_HOTEL_ID))
        self.add_hotel_availability(hotel_id=_HOTEL_ID, airline_id=AIRLINE_DATA['airline_id'],
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0')
        self.hotel_page.open_hotel_details_page(hotel_id=_HOTEL_ID)
        self.hotel_page.click_on_tax_tab_from_hotel_details()
        self.assertFalse(self.hotel_page.add_new_tax_entry())
        self.hotel_page.refresh_page()
        self.hotel_page.click_on_tax_tab_from_hotel_details()
        hotel_tax_value = self.hotel_page.get_taxes_per_hotel()
        self.assertEqual(hotel_tax_value[1].text, self.hotel_page.TAX_STATUS_VALUE)
        self.assertEqual(hotel_tax_value[2].text, self.hotel_page.TAX_TYPE_VALUE)
        self.assertEqual(hotel_tax_value[5].text, self.hotel_page.TAX_AMOUNT_VALUE)
        self.assertEqual(hotel_tax_value[6].text, self.hotel_page.TAX_ORDER_VALUE)
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(PORT['port_prefix'], AIRLINE_DATA['airline_name'])
        self.assertIn(self.hotel_page.TAX_AMOUNT_VALUE, self.quick_voucher_page.get_tax_list_on_quick_voucher())

    @ignore_warnings
    def test_hotel_active_inactive_button_enable_for_it_support_users(self):
        """
        TVL IT Support users
            Active_button: Enable
        :return:
         """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.click_on_add_new_hotel_button()
        self.hotel_page.fill_data_in_new_hotel_form(set_values_to_new_hotel_fields())
        self.assertTrue(self.hotel_page.click_on_hotel_save_button())
        self.HOTEL_ID = self.hotel_page.get_hotel_id()
        self.assertIn(self.HOTEL_ID, self.hotel_page.get_current_url_of_hotel_page())
        self.hotel_page.click_on_tva_settings_tab_from_hotel_details()
        self.assertEqual("Hotel information saved successfully.",
                         self.hotel_page.click_on_hotel_inactive_button(it_support_user=True))

    @ignore_warnings
    def test_disable_hotel_active_button_for_non_it_support_users(self):
        """
        TVL all other users
            Active_button: Disable
        :return:
         """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.click_on_add_new_hotel_button()
        self.hotel_page.fill_data_in_new_hotel_form(set_values_to_new_hotel_fields())
        self.assertTrue(self.hotel_page.click_on_hotel_save_button())
        self.HOTEL_ID = self.hotel_page.get_hotel_id()
        self.assertIn(self.HOTEL_ID, self.hotel_page.get_current_url_of_hotel_page())
        self.go_to_tva_users_page()
        self.tva_users_page.click_on_add_new_user_button()
        user_roles = self.tva_users_page.get_tvl_users_roles()
        for role, value in user_roles:
            user_name, password = self.tva_users_page.fill_data_in_new_tvl_user_form\
                (set_values_to_add_new_tvl_user(), value)
            self.assertNotEqual(self.tva_users_page.click_on_save_user_button(),
                                "Username already in use. Please try different username.",
                                "There is an error while creating this user.")
            tva_users_list = (user_name, password, role)
            TVA_USERS_DATA.append(tva_users_list)
            self.tva_users_page.click_on_add_new_user_button()
        self.airline_page.logout_user()
        """Login with Senior Management user credentials"""
        # self.login_user(TVA_USERS_DATA[4][0], TVA_USERS_DATA[4][1], new_password=USERS['new_password'])
        self.api_login(username=TVA_USERS_DATA[4][0], password=TVA_USERS_DATA[4][1],
                       resetpassword=USERS['new_password'], desired_page=STORMX_URL + HOTEL_PAGE)
        self.verify_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.hotel_page.open_hotel_details_page(self.HOTEL_ID)
        self.hotel_page.click_on_tva_settings_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.click_on_hotel_inactive_button())
        self.airline_page.logout_user()
        """Login with Read Only User credentials"""
        # self.login_user(TVA_USERS_DATA[3][0], TVA_USERS_DATA[3][1], new_password=USERS['new_password'])
        self.api_login(username=TVA_USERS_DATA[3][0], password=TVA_USERS_DATA[3][1],
                       resetpassword=USERS['new_password'], desired_page=STORMX_URL + HOTEL_PAGE)
        self.verify_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.hotel_page.open_hotel_details_page(self.HOTEL_ID)
        self.hotel_page.click_on_tva_settings_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.click_on_hotel_inactive_button())
        self.airline_page.logout_user(read_only_user=True)
        """Login with Supervisor credentials"""
        # self.login_user(TVA_USERS_DATA[2][0], TVA_USERS_DATA[2][1], new_password=USERS['new_password'])
        self.api_login(username=TVA_USERS_DATA[2][0], password=TVA_USERS_DATA[2][1],
                       resetpassword=USERS['new_password'], desired_page=STORMX_URL + HOTEL_PAGE)
        self.verify_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.hotel_page.open_hotel_details_page(self.HOTEL_ID)
        self.hotel_page.click_on_tva_settings_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.click_on_hotel_inactive_button())
        self.airline_page.logout_user(supervisor_or_operator_user=True)
        """Login with Operator credentials"""
        # self.login_user(TVA_USERS_DATA[1][0], TVA_USERS_DATA[1][1], new_password=USERS['new_password'])
        self.api_login(username=TVA_USERS_DATA[1][0], password=TVA_USERS_DATA[1][1],
                       resetpassword=USERS['new_password'], desired_page=STORMX_URL + HOTEL_PAGE)
        self.verify_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.hotel_page.open_hotel_details_page(self.HOTEL_ID)
        self.hotel_page.click_on_tva_settings_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.click_on_hotel_inactive_button())
        self.airline_page.logout_user(supervisor_or_operator_user=True)
        """ Login with Finance credentials """
        # self.login_user(TVA_USERS_DATA[0][0], TVA_USERS_DATA[0][1], new_password=USERS['new_password'])
        self.api_login(username=TVA_USERS_DATA[0][0], password=TVA_USERS_DATA[0][1],
                       resetpassword=USERS['new_password'], desired_page=STORMX_URL + HOTEL_PAGE)
        self.verify_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.hotel_page.open_hotel_details_page(self.HOTEL_ID)
        self.hotel_page.click_on_tva_settings_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.click_on_hotel_inactive_button())

    @ignore_warnings
    def test_add_ap_soft_blocks(self):
        """
        Verify that user should be able to add the hotel soft blocks successfully.

        Steps:
        * Login with valid credentials.
        * Go to Hotel listing page.
        * Select desired port.
        * If selected port has hotel then click on edit availability button for first hotel.
        * Fill all fields on edit avail form.
        * Click on Update button.
        * Search the newly added hotel's blocks on hotel listing page.
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.select_port_filter_from_hotel_listing()
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=AIRLINE_DATA['airline_id'],
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0')
        self.hotel_page.click_on_search_hotel_button()
        # self.verify_port_hotels_and_fill_blocks_on_edit_avail_form()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), AIRLINE_DATA['airline_prefix']), True)

    @ignore_warnings
    def test_add_pp_soft_blocks(self):
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.select_port_filter_from_hotel_listing()
        self.verify_port_hotels_and_fill_blocks_on_edit_avail_form(pp_block_type=True)
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), AIRLINE_DATA['airline_prefix'], pp_block_type=True), True)

    @ignore_warnings
    def test_add_accessibility_room_type_soft_block(self):
        """
        Verify that user should be able to add the hotel soft blocks with accessibility room type successfully.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.select_port_filter_from_hotel_listing()
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=AIRLINE_DATA['airline_id'],
                                    availability_date=get_availability_date('America/Chicago'),ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=2)
        self.hotel_page.click_on_search_hotel_button()
        # self.verify_port_hotels_and_fill_blocks_on_edit_avail_form(accessibility_room=True)
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), AIRLINE_DATA['airline_prefix'], accessibility_room=True), True)

    @ignore_warnings
    def test_add_hard_blocks(self):
        """
        Verify that user should be able to add the hotel hard blocks successfully.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.select_port_filter_from_hotel_listing()
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=AIRLINE_DATA['airline_id'],
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=1,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        # self.verify_port_hotels_and_fill_blocks_on_edit_avail_form(True)
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), AIRLINE_DATA['airline_prefix'], is_hard_block=True), True)

    @ignore_warnings
    def test_add_accessibility_room_type_hard_blocks(self):
        """
        Verify that user should be able to add the hotel hard blocks with accessibility room type successfully.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.select_port_filter_from_hotel_listing()
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=AIRLINE_DATA['airline_id'],
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=1,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=2)
        self.hotel_page.click_on_search_hotel_button()
        # self.verify_port_hotels_and_fill_blocks_on_edit_avail_form(is_hard_block=True, accessibility_room=True)
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), AIRLINE_DATA['airline_prefix'], is_hard_block=True,
                         accessibility_room=True), True)

    @ignore_warnings
    def test_add_additional_contacts_for_hotel(self):
        """
        Verify that user should be able to add new contact on additional contacts page.
        Steps:
        * Click on Additional Contacts button from Hotel listing page.
        * Add contacts data and click on add contact button.
        * Verify that "Last updated:" text is visible with new added contact entry.
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.select_port_filter_from_hotel_listing()
        self.hotel_page.click_on_additional_contacts_button()
        self.assertIn("Last updated:", self.hotel_page.
                      fill_data_in_contacts_form(set_values_to_new_hotel_fields()))
        self.hotel_page.delete_additional_contact()

    @ignore_warnings
    def test_selected_hotel_status_filter_data_on_listing(self):
        """
        Verify that when we select In-active status filter, active hotels shouldn't be shown on listing.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.select_status_filter(status="In-Active")
        self.assertTrue(self.hotel_page.verify_default_selected_status_filter_hotels_on_page(),
                        "There are some active hotel on listing.")
        self.hotel_page.select_status_filter(status="Active")
        self.assertTrue(self.hotel_page.verify_default_selected_status_filter_hotels_on_page(),
                        "There are some in-active hotel on listing.")

    @ignore_warnings
    def test_state_mandatory_field_for_usa_country(self):
        """
        Verify that for USA country, state must be a mandatory field while adding new hotel.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.click_on_add_new_hotel_button()
        self.hotel_page.fill_data_in_new_hotel_form(set_values_to_new_hotel_fields(), usa_country_check=True)
        self.assertTrue(self.hotel_page.click_on_hotel_save_button(usa_country_check=True),
                        "State must be a mandatory field for USA country.")

    def verify_port_hotels_and_fill_blocks_on_edit_avail_form(self, is_hard_block=False, accessibility_room=False,
                                                              pp_block_type=False):
        if self.hotel_page.no_hotel_record_found_from_hotel_listing():
            print("Sorry! we did not find any hotels.")
        else:
            self.hotel_page.click_on_edit_availability_button()
            self.hotel_page.fill_hotel_block_form(get_hotel_block_fields(), AIRLINE_DATA['airline_name'],
                                                  is_hard_block, accessibility_room, no_airline=False,
                                                  pp_block_type=pp_block_type)

    def select_port_filter_from_hotel_listing(self):
        return self.hotel_page.select_port_from_hotel_listing(PORT['port_prefix'], PORT_MODAL, PORT_DROPDOWN_PLACEHOLDER)

    def verify_initial_setup(self):
        try:
            self.support_cookies = self.api_login(username="support", password="test", resetpassword=NEW_PASSWORD,
                                                  desired_page=STORMX_URL + HOTEL_PAGE)
            self.verify_hotel_page()
            return True, ""
        except Exception as e:
            print("Something unexpected happened in test, exiting normally. For details see the exception"
                  " message below")
            print(str(e))
            return False, e

    def tearDown(self):
        self.browser.close()
