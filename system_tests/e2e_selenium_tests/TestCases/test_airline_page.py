from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.PageObjectClasses.airline_page import set_values_to_new_airline_fields, \
    set_values_to_add_new_airline_user
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
AIRLINE_USERS_DATA = []


class TestAirline(TestBaseClass):
    PORT_NAME = "PWK Chicago Executive Airport"
    PORT_PREFIX = PORT_NAME.split()[0]
    PORT_ID = '5032'
    USERS_DATA = []
    PASSWORD = []
    ROLE = []
    NEW_PASSWORD = "Tvlinc123!@#@"
    AIRLINE_ID = 294
    AIRLINE_PAGE = '/admin/airlines.php'
    AIRLINE_DASHBOARD = '/admin/index.php'

    def setUp(self):
        super(TestAirline, self).setUp()

    @ignore_warnings
    def test_add_new_airline_and_serviced_port(self):
        """
        Verify that user should be able to add new airline successfully.

        Steps:
        * Login with valid credentials.
        * Go to Airline listing page.
        * Click on Add New Airline button.
        * Fill all fields on add new airline form.
        * Click on Save button.
        * Verify that new airline's id is present in current url.
        * Click on Serviced Ports tab.
        * Add port from serviced ports dropdown.
        * Verify that newly added port is shown on the page header of ports contacts.
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.airline_page.click_on_add_new_airline_button()
        self.airline_page.fill_data_in_new_airline_form(set_values_to_new_airline_fields())
        self.assertTrue(self.airline_page.click_on_airline_save_button()[0],
                        'There is an error while saving new airline data. '
                        'Some mandatory field data is not saved correctly')
        self.assertIn(self.airline_page.click_on_airline_save_button()[1],
                      self.airline_page.get_current_url_of_airline_page())
        self.airline_page.click_on_ports_tab_from_airline_details()
        self.airline_page.select_serviced_port(self.PORT_PREFIX)
        self.airline_page.click_on_add_port_button()
        self.assertIn(self.airline_page.get_port_name_from_service_ports_section(),
                      self.airline_page.get_serviced_port_list())
        self.airline_page.refresh_page()

    @ignore_warnings
    def test_add_additional_contacts_for_airline(self):
        """
        Verify that user should be able to add new contact on additional contacts page.
        Steps:
        * Click on Additional Contacts button from Serviced port tab.
        * Add contacts data and click on add contact button.
        * Verify that "Last updated:" text is visible with new added contact entry.
        """
        self.test_add_new_airline_and_serviced_port()
        self.airline_page.click_on_ports_tab_from_airline_details()
        self.airline_page.click_on_additional_contacts_button()
        self.airline_page.select_contact_port(self.PORT_PREFIX)
        self.assertIn("Last updated:", self.airline_page.fill_data_in_contacts_form(set_values_to_new_airline_fields()))
        self.airline_page.verify_additional_contact_under_port_contacts_section()
        expected_error = 'There are no contacts attached with this port.'
        self.assertEqual(self.airline_page.delete_additional_contact_from_ports_contact_section(), expected_error)

    @ignore_warnings
    def test_successful_airline_users_creation(self):
        """
        Steps:
        * Add new airline.
        * Click on Users tab.
        * Add new user data.
        * Check if there is any error.
        * If no error found user is created successfully, else, there is some error in user creation.
        """
        self.test_add_new_airline_and_serviced_port()
        self.airline_page.click_on_users_tab_from_airline_details()
        user_roles = self.airline_page.get_airline_user_roles()
        for role in user_roles[1:]:
            user_name, password, user_role = self.airline_page. \
                fill_data_in_new_airline_user(set_values_to_add_new_airline_user(port_to_service=self.PORT_PREFIX,
                                                                                 user_role=role), str(self.PORT_ID))
            self.airline_page.click_on_save_user_button()
            airline_users_list = (user_name, password, user_role)
            self.USERS_DATA.append(airline_users_list)
        self.assertListEqual(self.airline_page.get_user_creation_error_messages(), [])

    @ignore_warnings
    def test_airline_employee_at_port_dashboard(self):
        """
        Verify that airline's user employee at port should redirect to airline dashboard after login.
        """
        self.test_successful_airline_users_creation()
        self.airline_page.logout_user()
        self.api_login(username=self.USERS_DATA[0][0], password=self.USERS_DATA[0][1], resetpassword=self.NEW_PASSWORD,
                       desired_page=STORMX_URL + self.AIRLINE_DASHBOARD)
        self.verify_airline_dashboard_page()

    @ignore_warnings
    def test_blog_messages(self):
        """
        Verify that user is able to add blog message and it should be shown an error on page if empty message is saved.
        Steps:
        * Login with valid credentials.
        * Go to Airline page.
        * Click on Blog Message button.
        * Click on save button with some blog message in the textarea.
        * Click on save message button with empty message.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.airline_page.click_on_blog_messages_button()
        self.assertEqual(self.airline_page.adding_new_blog_message(), "Testing Blog Messages!",
                         "Newly added message is not showing on blog listing.")
        self.assertEqual(self.airline_page.empty_blog_message_save(), "New message is a required field.")
        self.assertTrue(self.airline_page.blog_messages_unread(), "Blog message unread functionality is not working.")
        self.assertFalse(self.airline_page.blog_messages_read(), "Blog message read functionality is not working.")

    @ignore_warnings
    def test_disable_buttons_for_airline_users(self):
        """
        Hide the + and the Send Avails/Rate email buttons for all airline users.
        Hide the PNR button on voucher listing page for all airline users.
        :return:
        """
        if self.verify_initial_setup():
            self.airline_page.click_on_add_new_airline_button()
            self.airline_page.fill_data_in_new_airline_form(set_values_to_new_airline_fields())
            self.assertIn(self.airline_page.click_on_airline_save_button()[1],
                          self.airline_page.get_current_url_of_airline_page())
            self.airline_page.click_on_ports_tab_from_airline_details()
            self.airline_page.select_serviced_port(self.PORT_PREFIX)
            self.airline_page.click_on_add_port_button()
            self.assertIn(self.PORT_NAME, self.airline_page.get_serviced_port_list(), 'Port is not added yet.')
            self.airline_page.refresh_page()
            self.airline_page.click_on_users_tab_from_airline_details()
            user_roles = self.airline_page.get_airline_user_roles()
            for role in user_roles[1:]:
                user_name, password, user_role = self.airline_page. \
                    fill_data_in_new_airline_user(set_values_to_add_new_airline_user(port_to_service=self.PORT_ID,
                                                                                     user_role=role), self.PORT_ID)
                self.airline_page.click_on_save_user_button()
                airline_users_list = (user_name, password, user_role)
                AIRLINE_USERS_DATA.append(airline_users_list)
            self.assertListEqual(self.airline_page.get_user_creation_error_messages(), [])
            self.airline_page.logout_user()
            """Login with Employee at Port credentials"""
            self.login_user(AIRLINE_USERS_DATA[0][0], AIRLINE_USERS_DATA[0][1], new_password=self.NEW_PASSWORD)
            self.verify_airline_dashboard_page()
            # self.verify_quick_room_transfer_page()
            # self.sso_login_page.verify_employe_at_port_dashboard()
            self.go_to_hotel_page()
            self.assertTrue(self.hotel_page.hide_buttons_on_hotel_listing_for_airline_user(),
                            "Add new Hotel and Send AVail buttons are still visible for airline user.")
            self.go_to_voucher_listing_page()
            self.assertTrue(self.voucher_listing_page.hide_pnr_button_for_airline_users(),
                            "PNR button is still visible for airline user.")
            self.sso_login_page.logout_user()
            """Login with Port Manager credentials"""
            self.login_user(AIRLINE_USERS_DATA[1][0], AIRLINE_USERS_DATA[1][1], new_password=self.NEW_PASSWORD)
            self.verify_airline_dashboard_page()
            self.go_to_hotel_page()
            self.assertTrue(self.hotel_page.hide_buttons_on_hotel_listing_for_airline_user(),
                            "Add new Hotel and Send AVail buttons are still visible for airline user.")
            self.go_to_voucher_listing_page()
            self.assertTrue(self.voucher_listing_page.hide_pnr_button_for_airline_users(),
                            "PNR button is still visible for airline user.")
            self.sso_login_page.logout_user()
            """Login with Corporate Representative credentials"""
            self.login_user(AIRLINE_USERS_DATA[2][0], AIRLINE_USERS_DATA[2][1], new_password=self.NEW_PASSWORD)
            self.verify_airline_dashboard_page()
            self.go_to_hotel_page()
            self.assertTrue(self.hotel_page.hide_buttons_on_hotel_listing_for_airline_user(),
                            "Add new Hotel and Send AVail buttons are still visible for airline user.")
            self.go_to_voucher_listing_page()
            self.assertTrue(self.voucher_listing_page.hide_pnr_button_for_airline_users(),
                            "PNR button is still visible for airline user.")
            self.sso_login_page.logout_user()
            """Login with Account Finance credentials"""
            self.login_user(AIRLINE_USERS_DATA[3][0], AIRLINE_USERS_DATA[3][1], new_password=self.NEW_PASSWORD)
            self.verify_airline_dashboard_page()
            self.go_to_hotel_page()
            self.assertTrue(self.hotel_page.hide_buttons_on_hotel_listing_for_airline_user(),
                            "Add new Hotel and Send AVail buttons are still visible for airline user.")
            self.go_to_voucher_listing_page()
            self.assertTrue(self.voucher_listing_page.hide_pnr_button_for_airline_users(),
                            "PNR button is still visible for airline user.")
            self.sso_login_page.logout_user()

    def verify_initial_setup(self):
        try:
            self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                           desired_page=STORMX_URL + self.AIRLINE_PAGE)
            self.verify_airline_page()
            return True, ''
        except Exception as e:
            print("Something unexpected happened in test, exiting normally. For details see the exception"
                  " message below")
            print(str(e))
            return False, str(e)

    def tearDown(self):
        self.browser.close()
