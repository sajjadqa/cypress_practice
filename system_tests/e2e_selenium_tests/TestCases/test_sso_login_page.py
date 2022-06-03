import unittest
from e2e_selenium_tests.PageObjectClasses.hotel_page import set_values_to_add_new_hotel_user
from e2e_selenium_tests.PageObjectClasses.airline_page import set_values_to_new_airline_fields, \
    set_values_to_add_new_airline_user
from e2e_selenium_tests.PageObjectClasses.transports_page import set_values_to_add_new_transport_user
from e2e_selenium_tests.PageObjectClasses.tva_users_page import set_values_to_add_new_tvl_user
from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings
from e2e_selenium_tests.BaseClasses.constant import IDP_URL, STORMX_URL
from e2e_selenium_tests.BaseClasses.constant import SINGLE_SIGN_ON_ENABLED


AIRLINE_USERS_DATA = []
TVA_USERS_DATA = []
HOTEL_ID = '88143'
TRANSPORT_ID = '93905'

USERS = {'tvl_it_support_user_name': 'support',
         'tvl_it_support)user_password': 'test',
         'invalid_password': 'invalid@password',
         'new_password': 'Tvlinc123!@#@'
         }

PORT = {'port_name': 'MSP Minneapolis Saint Paul International Airport',
        'port_prefix': 'MSP',
        'port_id': '285'
        }

NON_SSO_AIRLINE = {'airline_name': 'PRP Purple Rain Airlines',
                   'airline_prefix': 'PRP',
                   'airline_id': '294'
                   }

SSO_AIRLINE = {'airline_name': 'United Airlines',
               'airline_prefix': 'airline_name.split()[0]',
               'airline_id': '26',
               'sso_user_name': 'u999999',
               'sso_user_password': 'u999999pass'
               }


class TestSsoLogin(TestBaseClass):
    @unittest.skipIf(SINGLE_SIGN_ON_ENABLED is False, "SSO not enabled yet!")
    def setUp(self):
        super(TestSsoLogin, self).setUp()

    @ignore_warnings
    def test_successful_sso_login(self):
        """
        Verify that user is successfully logged in with valid sso user credentials and Employee at port role users are
        redirected to quick rooms transfer page.
        """
        self.login_user(SSO_AIRLINE['sso_user_name'], SSO_AIRLINE['sso_user_password'])
        self.sso_login_user(SSO_AIRLINE['sso_user_name'], SSO_AIRLINE['sso_user_password'])
        # self.verify_quick_room_transfer_page()
        self.verify_airline_dashboard_page()
        self.sso_login_page.verify_employe_at_port_dashboard()
        self.sso_login_page.open_new_tab()
        self.verify_airline_dashboard_page()
        self.sso_login_page.verify_employe_at_port_dashboard()

    @ignore_warnings
    def test_sso_login_with_invalid_credentials(self):
        """
        Verify that user is not logged in with invalid credentials and error message is being displayed.
        """
        self.login_user(SSO_AIRLINE['sso_user_name'], USERS['invalid_password'])
        self.sso_login_user(SSO_AIRLINE['sso_user_name'], USERS['invalid_password'])
        self.assertIn('Incorrect username or password', self.sso_login_page.perform_error_validation(),
                      "Failed invalid credentials test")

    @ignore_warnings
    def test_sso_logout(self):
        """
        Verify that special logout processes for SSO users. Keep normal logout process working for non-SSO users.
        :return:
        """
        self.login_user(SSO_AIRLINE['sso_user_name'], SSO_AIRLINE['sso_user_password'])
        self.sso_login_user(SSO_AIRLINE['sso_user_name'], SSO_AIRLINE['sso_user_password'])
        self.verify_airline_dashboard_page()
        self.sso_login_page.verify_employe_at_port_dashboard()
        self.sso_login_page.logout_user(sso_logout=True)
        self.browser.get(IDP_URL)
        self.sso_login_page.verify_browser_on_the_page()
        self.browser.get(STORMX_URL)
        self.login_page.verify_browser_on_the_page()

    @ignore_warnings
    def test_user_creation_with_same_login_id_pattern_as_sso_enabled_users(self):
        """
        Block all users from being created in the UI, and API that have the sso enabled user format. Only allow users
        to be created in this format when coming from SSO.
        This limitation is for all hotels, transports and airlines - except for united airlines.
        :return:
        """
        if self.verify_initial_setup():
            self.airline_page.open_airline_details_page_via_api(airline_id=NON_SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            user_roles = self.airline_page.get_airline_user_roles()
            for role in user_roles[1:]:
                self.airline_page.fill_data_in_new_airline_user(set_values_to_add_new_airline_user
                                                                (port_to_service=PORT['port_prefix'], user_role=role,
                                                                 sso_user_format=True), PORT['port_id'])
                self.assertEqual(self.airline_page.click_on_save_user_button(sso_user_format=True),
                                 "This user name is not allowed. Please select another user name for the new user.")
            self.go_to_hotel_page()
            self.hotel_page.search_hotel_on_hotel_listing(HOTEL_ID)
            self.hotel_page.open_hotel_details_page(HOTEL_ID)
            self.hotel_page.click_on_users_tab_from_hotel_details()
            user_roles = self.hotel_page.get_hotel_user_roles()
            for role in user_roles[1:]:
                self.hotel_page.fill_data_in_new_hotel_user(set_values_to_add_new_hotel_user(sso_user_format=True,
                                                                                             user_role=role))
                self.assertEqual(self.hotel_page.click_on_save_user_button(sso_user_format=True),
                                 "This user name is not allowed. Please select another user name for the new user.")
            self.go_to_transport_page()
            self.transport_page.open_transport_detail_page_via_api(transport=TRANSPORT_ID)
            self.transport_page.click_on_users_tab_from_transport_details()
            self.transport_page.fill_data_in_new_transport_user(set_values_to_add_new_transport_user
                                                                (sso_user_format=True))
            self.assertEqual(self.transport_page.click_on_save_user_button(sso_user_format=True),
                             "This user name is not allowed. Please select another user name for the new user.")
            self.go_to_tva_users_page()
            self.tva_users_page.click_on_add_new_user_button()
            user_roles = self.tva_users_page.get_tvl_users_roles()
            for role, value in user_roles:
                self.tva_users_page.fill_data_in_new_tvl_user_form(
                    set_values_to_add_new_tvl_user(sso_user_format=True), value)
                self.assertEqual(self.tva_users_page.click_on_save_user_button(sso_user_format=True),
                                 "This user name is not allowed. Please select another user name for the new user.")
                self.tva_users_page.click_on_add_new_user_button()

    @ignore_warnings
    def test_disable_add_new_user_for_tvl_it_support_user(self):
        """
        Verify that add new user functionality should be disabled for SSO enabled airline.
        Verify that add new user functionality should be enabled for other than sso enabled airline.
        TVL IT Support users:
            Add users for sso airline: Not allowed
            Add users for non sso airline: allowed
        :return:
        """
        if self.verify_initial_setup():
            self.airline_page.open_airline_details_page_via_api(airline_id=SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            self.assertTrue(self.sso_login_page.disable_add_new_user_for_sso_airlines(super_user=True),
                            "All fields are not disabled on add new user section")
            self.go_to_airline_page()
            self.airline_page.open_airline_details_page_via_api(airline_id=NON_SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            self.assertTrue(self.sso_login_page.enable_add_new_user_for_other_airlines(),
                            "All fields are not enabled on add new user section")

    @ignore_warnings
    def test_sso_users_delete_edit_functionality_for_tvl_it_support_user(self):
        """
        Verify that edit user information should be disabled for sso enabled airline.
         Only, Role field will be editable for TVL IT support user.
          TVL IT Support users:
            Update users: Only allowed to update role for all user types
            Delete users: Allowed
        :return:
        """
        if self.verify_initial_setup():
            self.airline_page.open_airline_details_page_via_api(airline_id=SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            self.sso_login_page.click_edit_user_button_for_it_support_user()
            self.assertTrue(self.sso_login_page.verify_sso_user_non_editable_for_tvl_users(it_user=True))
            self.assertTrue(self.sso_login_page.click_delete_user_button_for_it_support_user(
                user_id=SSO_AIRLINE['sso_user_name']))

    @ignore_warnings
    def test_disable_user_information_for_tvl_users(self):
        """
        TVL all other users

            Add users: Not allowed
            Update users: Not allowed
            Delete users: Not allowed
        :return:
        """
        if self.verify_initial_setup():
            self.go_to_tva_users_page()
            self.tva_users_page.click_on_add_new_user_button()
            user_roles = self.tva_users_page.get_tvl_users_roles()
            for role, value in user_roles:
                user_name, password = self.tva_users_page.fill_data_in_new_tvl_user_form(
                    set_values_to_add_new_tvl_user(), value)
                self.tva_users_page.click_on_save_user_button()
                tva_users_list = (user_name, password, role)
                TVA_USERS_DATA.append(tva_users_list)
                self.tva_users_page.click_on_add_new_user_button()
            self.airline_page.logout_user()
            """Login with Senior Management user credentials"""
            self.login_user(TVA_USERS_DATA[4][0], TVA_USERS_DATA[4][1], new_password=USERS['new_password'])
            self.go_to_airline_page()
            self.verify_airline_page()
            self.airline_page.open_airline_details_page_via_api(airline_id=SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            self.assertTrue(self.sso_login_page.disable_add_new_user_for_sso_airlines(super_user=True),
                            "All fields are not disabled on add new user section")
            self.assertTrue(self.sso_login_page.verify_sso_user_non_editable_for_tvl_users(),
                            "TVL users other than IT support user are allowed to update role for all user types")
            self.assertTrue(self.sso_login_page.disable_user_edit_button_for_sso_airline(),
                            "Edit user button  shouldn't be shown for TVL users other than IT support user.")
            self.assertTrue(self.sso_login_page.disable_user_delete_button_for_sso_airline(),
                            "TVL users other than IT support user are not allowed to delete users.")
            self.airline_page.logout_user()
            """Login with Read Only User credentials"""
            self.login_user(TVA_USERS_DATA[3][0], TVA_USERS_DATA[3][1], new_password=USERS['new_password'])
            self.go_to_airline_page()
            self.verify_airline_page()
            self.airline_page.open_airline_details_page_via_api(airline_id=SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            self.assertTrue(self.sso_login_page.disable_add_new_user_for_sso_airlines(),
                            "All fields are not disabled on add new user section")
            self.assertTrue(self.sso_login_page.disable_user_edit_button_for_sso_airline(),
                            "Edit user button  shouldn't be shown for TVL users other than IT support user.")
            self.assertTrue(self.sso_login_page.disable_user_delete_button_for_sso_airline(),
                            "TVL users other than IT support user are not allowed to delete users.")
            self.airline_page.logout_user(read_only_user=True)
            """Login with Supervisor credentials"""
            self.login_user(TVA_USERS_DATA[2][0], TVA_USERS_DATA[2][1], new_password=USERS['new_password'])
            self.go_to_airline_page()
            self.verify_airline_page()
            self.airline_page.open_airline_details_page_via_api(airline_id=SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            self.assertTrue(self.sso_login_page.disable_add_new_user_for_sso_airlines(),
                            "All fields are not disabled on add new user section")
            self.assertTrue(self.sso_login_page.disable_user_edit_button_for_sso_airline(),
                            "Edit user button  shouldn't be shown for TVL users other than IT support user.")
            self.assertTrue(self.sso_login_page.disable_user_delete_button_for_sso_airline(),
                            "TVL users other than IT support user are not allowed to delete users.")
            self.airline_page.logout_user(supervisor_or_operator_user=True)
            """Login with Operator credentials"""
            self.login_user(TVA_USERS_DATA[1][0], TVA_USERS_DATA[1][1], new_password=USERS['new_password'])
            self.go_to_airline_page()
            self.verify_airline_page()
            self.airline_page.open_airline_details_page_via_api(airline_id=SSO_AIRLINE['airline_id'])
            self.airline_page.click_on_users_tab_from_airline_details()
            self.assertTrue(self.sso_login_page.disable_add_new_user_for_sso_airlines(),
                            "All fields are not disabled on add new user section")
            self.assertTrue(self.sso_login_page.disable_user_edit_button_for_sso_airline,
                            "Edit user button  shouldn't be shown for TVL users other than IT support user.")
            self.assertTrue(self.sso_login_page.disable_user_delete_button_for_sso_airline(),
                            "TVL users other than IT support user are not allowed to delete users.")

    def verify_initial_setup(self):
        try:
            self.login_user(new_password=USERS['new_password'])
            self.verify_tvl_login_dashboard()
            self.verify_dashboard_page()
            self.go_to_airline_page()
            self.verify_airline_page()
            return True
        except Exception as e:
            print("Something unexpected happened in test, exiting normally. For details see the exception"
                  " message below")
            print(str(e))
            return False

    def tearDown(self):
        self.browser.close()
