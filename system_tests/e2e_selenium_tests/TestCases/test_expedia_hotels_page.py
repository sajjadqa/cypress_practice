from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
from e2e_selenium_tests.PageObjectClasses.hotel_page import set_values_to_new_hotel_fields, set_values_to_add_new_hotel_user
from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings


NEW_PASSWORD = "Tvlinc123!@#@"
HOTEL_PAGE = '/admin/hotels.php'
HOTEL_SEARCH_PARAMS = '?page=&pid=&hid={}'
EXPEDIA_HOTEL_ID = '114747'


class TestExpediaHotels(TestBaseClass):
    def setUp(self):
        super(TestExpediaHotels, self).setUp()

    @ignore_warnings
    def test_link_to_expedia_hotel(self):
        """
        Verify that user should be able to link available expedia hotel to the hotel.

        Steps:
        * Login with valid credentials.
        * Go to hotel listing page and search the desired hotel there.
        * Click on Search for hotel on Expedia button.
        * Click on available hotel's link button.
        * Close the Expedia dialog modal.
        * Open the hotel detail page.
        * Verify that added expedia hotel id should be shown on hotel details page.
        * It will also check if the expedia rapid id is already attached to other hotels.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.search_hotel_on_hotel_listing(EXPEDIA_HOTEL_ID)
        self.assertTrue(self.hotel_page.visibility_of_search_hotel_on_expedia_button(),
                        "Expedia rapid id is already attached with this hotel.")
        self.EXPEDIA_RAPID_ID = self.hotel_page.search_hotel_on_expedia()
        self.hotel_page.close_expedia_modal()
        self.hotel_page.open_hotel_details_page(EXPEDIA_HOTEL_ID)
        hotel_details_expedia_rapid_id = self.hotel_page.expedia_rapid_id_on_hotel_details()
        self.assertIn(hotel_details_expedia_rapid_id, self.EXPEDIA_RAPID_ID,
                      "There is a problem while attaching expedia rapid id to hotel profile.")
        self.hotel_page.remove_expedia_rapid_id_from_hotel_profile()

    @ignore_warnings
    def test_search_expedia_hotel_with_no_port(self):
        """
        Verify that an error should be shown while search on expedia if hotel doesn't have any port attached.
        :return:
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
        self.go_to_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.browser.get(STORMX_URL + HOTEL_PAGE + HOTEL_SEARCH_PARAMS.format(self.HOTEL_ID))
        self.assertTrue(self.hotel_page.visibility_of_search_hotel_on_expedia_button(),
                        "Expedia rapid id is already attached with this hotel.")
        self.assertEqual(self.hotel_page.search_expedia_hotel_with_no_port(), "Error occurred while trying to fetch "
                                                                              "Expedia hotels. Please make sure port is"
                                                                              " assigned to this hotel and try again. "
                                                                              "If the issue still persists contact "
                                                                              "Travelliance IT support.")

    @ignore_warnings
    def test_link_multiple_expedia_rapid_id_to_hotel(self):
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.search_hotel_by_api(hotel_id=EXPEDIA_HOTEL_ID, cookies=self.support_cookies, port_id=None)
        self.browser.get(STORMX_URL + HOTEL_PAGE + HOTEL_SEARCH_PARAMS.format(EXPEDIA_HOTEL_ID))
        self.assertTrue(self.hotel_page.visibility_of_search_hotel_on_expedia_button(),
                        "Expedia rapid id is already attached with this hotel.")
        self.EXPEDIA_RAPID_ID = self.hotel_page.search_hotel_on_expedia()
        self.assertEqual(self.hotel_page.link_multiple_expedia_rapid_ids_to_hotel(duplicate_id=self.EXPEDIA_RAPID_ID),
                         "Another Expedia rapid ID ({}) is assigned to this hotel.".format(self.EXPEDIA_RAPID_ID))
        self.hotel_page.close_expedia_modal()
        self.hotel_page.open_hotel_details_page(EXPEDIA_HOTEL_ID)
        hotel_details_expedia_rapid_id = self.hotel_page.expedia_rapid_id_on_hotel_details()
        self.assertIn(hotel_details_expedia_rapid_id, self.EXPEDIA_RAPID_ID,
                      "There is a problem while attaching expedia rapid id to hotel profile.")
        self.hotel_page.remove_expedia_rapid_id_from_hotel_profile()

    @ignore_warnings
    def test_exclude_expedia_flag(self):
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.search_hotel_on_hotel_listing(EXPEDIA_HOTEL_ID)
        self.assertTrue(self.hotel_page.visibility_of_search_hotel_on_expedia_button(),
                        "Expedia rapid id is already attached with this hotel.")
        self.hotel_page.select_exclude_expedia_flag()
        self.assertTrue(self.hotel_page.visiblility_of_search_hotel_on_expedia_buttons(EXPEDIA_HOTEL_ID),
                        "Expedia exclude flag is not working, it is showing both expedia and TVL hotels on listing")
        self.hotel_page.select_exclude_expedia_flag()
        self.EXPEDIA_RAPID_ID = self.hotel_page.search_hotel_on_expedia()
        self.hotel_page.close_expedia_modal()
        self.hotel_page.select_exclude_expedia_flag()
        self.assertTrue(self.hotel_page.visiblility_of_search_hotel_on_expedia_buttons(EXPEDIA_HOTEL_ID,
                                                                                       exclude_expedia=True),
                        "Expedia exclude flag is not working, it is showing both expedia and TVL hotels on listing")
        self.hotel_page.select_exclude_expedia_flag()
        self.hotel_page.open_hotel_details_page(EXPEDIA_HOTEL_ID)
        self.hotel_page.remove_expedia_rapid_id_from_hotel_profile()

    @ignore_warnings
    def test_search_expedia_hotels_without_login_cookies(self):
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.search_hotel_on_hotel_listing(EXPEDIA_HOTEL_ID)
        self.assertTrue(self.hotel_page.visibility_of_search_hotel_on_expedia_button(),
                        "Expedia rapid id is already attached with this hotel.")
        self.api_logout(cookies=self.support_cookies)
        self.assertEqual(self.hotel_page.search_hotel_on_expedia_without_login(),
                         "You are not logged in. Please click here to login.")

    @ignore_warnings
    def test_link_to_expedia_hotel_without_login_cookies(self):
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.hotel_page.search_hotel_on_hotel_listing(EXPEDIA_HOTEL_ID)
        self.assertTrue(self.hotel_page.visibility_of_search_hotel_on_expedia_button(),
                        "Expedia rapid id is already attached with this hotel.")
        self.hotel_page.click_on_search_hotel_on_expedia_button()
        self.api_logout(cookies=self.support_cookies)
        self.assertEqual(self.hotel_page.link_expedia_hotel_without_login(),
                         "You are not logged in. Please click here to login.")

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
