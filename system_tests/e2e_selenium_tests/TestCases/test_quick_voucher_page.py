import datetime
from datetime import timedelta
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings, get_hotel_block_fields, get_availability_date


HOTEL_PAGE = '/admin/hotels.php'
today_m_5_days = get_availability_date('America/Chicago') - datetime.timedelta(days=5)


class TestQuickVoucher(TestBaseClass):
    PORT_NAME = "PWK Chicago Executive Airport"
    PORT_PREFIX = PORT_NAME.split()[0]
    AIRLINE_NAME = "PRP Purple Rain Airlines"
    AIRLINE_PREFIX = AIRLINE_NAME.split()[0]
    AIRLINE_ID = '294'
    PORT_MODAL = 'filter.pid'
    PORT_DROPDOWN_PLACEHOLDER = 'Type port name or prefix'
    NEW_PASSWORD = "Tvlinc123!@#@"

    def setUp(self):
        super(TestQuickVoucher, self).setUp()

    @ignore_warnings
    def test_add_new_quick_voucher(self):
        """
        Verify that user should be able to add new quick voucher.
        Steps:
        * Login with valid credentials.
        * Go to Hotel listing page.
        * Select desired port.
        * If selected port has hotel then click on edit availability button for first hotel.
        * Fill all fields on edit avail form.
        * Click on Update button.
        * Search the newly added hotel's blocks on hotel listing page.
        * Go to Quick Voucher modal.
        * Fill all required fields data on voucher modal.
        * Click on Save voucher button.
        * Get the current date time according to region(Chicago), (5AM change handled).
        * Get the voucher checkin date from voucher preview.
        * Compare the voucher checkin date time with current date time according to region.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0')
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), self.AIRLINE_PREFIX), True)
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME)
        voucher_creation_date = self.quick_voucher_page.click_on_save_quick_voucher_button()
        self.quick_voucher_page.voucher_finalization_alert()
        self.assertAlmostEqual(voucher_creation_date, self.quick_voucher_page.get_voucher_checkin_date(),
                               delta=timedelta(minutes=1))

    @ignore_warnings
    def test_quick_voucher_accessibility_room_type(self):
        """
        Verify that user should be able to add new quick voucher for accessibility room type.
        Steps:
        * Login with valid credentials.
        * Go to Hotel listing page.
        * Select desired port.
        * If selected port has hotel then click on edit availability button for first hotel.
        * Fill all fields on edit avail form for accessibility room type.
        * Click on Update button.
        * Search the newly added hotel's blocks on hotel listing page.
        * Go to Quick Voucher modal.
        * Fill all required fields data on voucher modal with room type as an Accessibility Room.
        * Get the sum of all hard blocks on voucher modal before creating voucher.
        * Click on Save voucher button.
        * Get the current date time according to region(Chicago), (5AM change handled).
        * Get the voucher checkin date from voucher preview.
        * Compare the voucher checkin date time with current date time according to region.
        * Compare the accessibility room count before and after voucher creation. It should not be equal.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=1,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=2)
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing(get_hotel_block_fields(),
                                                                                         self.AIRLINE_PREFIX,
                                                                                         accessibility_room=True,
                                                                                         is_hard_block=True), True)
        accessibility_room_count_before_voucher_creation = self.hotel_page.accessibility_room_count_from_hotel_page\
            (self.AIRLINE_PREFIX)
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME,
                                                           accessibility_room=True)
        voucher_creation_date = self.quick_voucher_page.click_on_save_quick_voucher_button()
        self.quick_voucher_page.voucher_finalization_alert()
        self.assertAlmostEqual(voucher_creation_date, self.quick_voucher_page.get_voucher_checkin_date(),
                               delta=timedelta(minutes=1))
        self.go_to_hotel_page()
        self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        accessibility_room_count_after_voucher_creation = self.hotel_page.accessibility_room_count_from_hotel_page\
            (self.AIRLINE_PREFIX)
        self.assertLess(accessibility_room_count_after_voucher_creation,
                        accessibility_room_count_before_voucher_creation,
                        "Rooms count is not changed. Voucher has not utilized accessibility room.")

    @ignore_warnings
    def test_quick_voucher__hard_block_first(self):
        """
        Verify that hard blocks should be used first in add new quick voucher for accessibility room type.
        Steps:
        * Login with valid credentials.
        * Go to Hotel listing page.
        * Select desired port.
        * If selected port has hotel then click on edit availability button for first hotel.
        * Fill all fields on edit avail form for accessibility room type and hard blocks.
        * Click on Update button.
        * Search the newly added hotel's blocks on hotel listing page.
        * Click on edit availability button for first hotel.
        * Fill all fields on edit avail form for accessibility room type and soft blocks.
        * Click on Update button.
        * Go to Quick Voucher modal.
        * Fill all required fields data on voucher modal with room type as an Accessibility Room.
        * Get the sum of all hard blocks on voucher modal before creating voucher.
        * Click on Save voucher button.
        * Get the current date time according to region(Chicago), (5AM change handled).
        * Get the voucher checkin date from voucher preview.
        * Compare the voucher checkin date time with current date time according to region.
        * Go to Quick Voucher modal again.
        * Fill all required fields data on voucher modal with room type as an Accessibility Room.
        * Get the sum of all hard blocks on voucher modal.
        * Get the sum of all soft blocks on voucher modal.
        * Verify that hard blocks sum before creating the voucher should be less than the hard blocks sum after
        creating the voucher.
        * Verify that sum of soft blocks before creating the voucher should be equal to the sum of soft blocks after
        creating the voucher.
        :return:
        """

        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=1,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=2)
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing(get_hotel_block_fields(),
                                                                                         self.AIRLINE_PREFIX,
                                                                                         accessibility_room=True,
                                                                                         is_hard_block=True), True)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=2)
        # stormx_api_methods.StormxApiMethods().add_hotel_availability(hotel_id=self.HOTEL_ID,
        #                                                              airline_id=self.AIRLINE_ID,
        #                                                              availability_date=get_availability_date
        #                                                              ('America/Chicago'),
        #                                                              cookies=self.support_cookies, ap_block_type=0,
        #                                                              block_price='30.00', blocks=100, pay_type='0',
        #                                                              room_type=2)
        self.hotel_page.click_on_search_hotel_button()
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME,
                                                           accessibility_room=True)
        hard_blocks_sum_before_voucher_creation = self.quick_voucher_page.\
            get_hotel_hard_blocks_avail_info_list_from_quick_voucher_modal()
        soft_blocks_sum_before_voucher_creation = self.quick_voucher_page.\
            get_hotel_soft_blocks_avail_info_list_from_quick_voucher_modal()
        voucher_creation_date = self.quick_voucher_page.click_on_save_quick_voucher_button()
        self.quick_voucher_page.voucher_finalization_alert()
        self.assertAlmostEqual(voucher_creation_date, self.quick_voucher_page.get_voucher_checkin_date(),
                               delta=timedelta(minutes=1))
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME,
                                                           accessibility_room=True)
        hard_blocks_sum_after_voucher_creation = self.quick_voucher_page.\
            get_hotel_hard_blocks_avail_info_list_from_quick_voucher_modal()
        soft_blocks_sum_after_voucher_creation = self.quick_voucher_page. \
            get_hotel_soft_blocks_avail_info_list_from_quick_voucher_modal()
        self.assertLess(hard_blocks_sum_after_voucher_creation, hard_blocks_sum_before_voucher_creation)
        self.assertEqual(soft_blocks_sum_after_voucher_creation, soft_blocks_sum_before_voucher_creation)

    @ignore_warnings
    def test_quick_voucher__airline_block_first(self):
        """
        Scenario:
        * setup: add inventory hardblock, then softblock, then airline_softblock.
          then use quick voucher method and make sure that hardblock and airline_softblock are the two blocks used. .
        * TVL staff creates a Quick Voucher.
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=1,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing(get_hotel_block_fields(),
                                                                                         self.AIRLINE_PREFIX,
                                                                                         is_hard_block=True
                                                                                         ), True)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=0,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        rooms_count_specific_airline_before_voucher_creation = self.hotel_page.rooms_count_of_specific_airline \
            (self.AIRLINE_PREFIX)
        rooms_count_without_airline_before_voucher_creation = self.hotel_page.rooms_count_without_airline()
        hard_blocks_count_before_voucher_creation = self.hotel_page.hard_blocks_room_count(self.AIRLINE_PREFIX)
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME, room_count=35)
        voucher_creation_date = self.quick_voucher_page.click_on_save_quick_voucher_button()
        self.quick_voucher_page.voucher_finalization_alert()
        self.assertAlmostEqual(voucher_creation_date, self.quick_voucher_page.get_voucher_checkin_date(),
                               delta=timedelta(minutes=1))
        self.go_to_hotel_page()
        self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        rooms_count_without_airline_after_voucher_creation = self.hotel_page.rooms_count_without_airline()
        rooms_count_specific_airline_after_voucher_creation = self.hotel_page.rooms_count_of_specific_airline \
            (self.AIRLINE_PREFIX)
        hard_blocks_count_after_voucher_creation = self.hotel_page.hard_blocks_room_count(self.AIRLINE_PREFIX)
        self.assertEqual(rooms_count_without_airline_after_voucher_creation,
                         rooms_count_without_airline_before_voucher_creation)
        self.assertLess(rooms_count_specific_airline_after_voucher_creation,
                        rooms_count_specific_airline_before_voucher_creation)
        self.assertLess(hard_blocks_count_after_voucher_creation, hard_blocks_count_before_voucher_creation)

    @ignore_warnings
    def test_quick_voucher__airline_block_first_no_hard_block(self):
        """
        Scenario:
        * setup: add inventory soft block, then airline_soft block.
          then use quick voucher method and make sure that airline soft block is used. .
        * TVL staff creates a Quick Voucher.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing(get_hotel_block_fields(),
                                                                                         self.AIRLINE_PREFIX), True)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=0,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        rooms_count_specific_airline_before_voucher_creation = self.hotel_page.\
            rooms_count_of_specific_airline(self.AIRLINE_PREFIX)
        rooms_count_without_airline_before_voucher_creation = self.hotel_page.rooms_count_without_airline()
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME)
        voucher_creation_date = self.quick_voucher_page.click_on_save_quick_voucher_button()
        self.quick_voucher_page.voucher_finalization_alert()
        self.assertAlmostEqual(voucher_creation_date, self.quick_voucher_page.get_voucher_checkin_date(),
                               delta=timedelta(minutes=1))
        self.go_to_hotel_page()
        self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        rooms_count_without_airline_after_voucher_creation = self.hotel_page.rooms_count_without_airline()
        rooms_count_specific_airline_after_voucher_creation = self.hotel_page.rooms_count_of_specific_airline\
            (self.AIRLINE_PREFIX)
        self.assertEqual(rooms_count_without_airline_after_voucher_creation,
                         rooms_count_without_airline_before_voucher_creation)
        self.assertLess(rooms_count_specific_airline_after_voucher_creation,
                        rooms_count_specific_airline_before_voucher_creation)

    @ignore_warnings
    def test_quick_voucher__exceeding_inventory(self):
        """
        Scenario:
        * setup: add inventory to a hotel.
        * TVL staff creates a Quick Voucher with 999 rooms, and make sure that an error message is shown on save voucher
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        expected_error = 'you are requesting 999 , available room are'
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=get_availability_date('America/Chicago'), ap_block_type=0,
                                    block_price='30.00', blocks=100, pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        self.assertTrue(self.hotel_page.verify_newly_added_hotel_blocks_on_hotel_listing
                        (get_hotel_block_fields(), self.AIRLINE_PREFIX), True)
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME,
                                                           exceed_inventory=True)
        self.quick_voucher_page.click_on_save_quick_voucher_button()
        self.assertIn(expected_error, self.quick_voucher_page.get_hotel_inventory_exceed_error())

    @ignore_warnings
    def test_quick_voucher__with_past_inventory(self):
        """
        Scenario:
        * setup: add inventory to a hotel, five days back from today.
        * TVL staff creates a Quick Voucher for the day five days back from today.
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.HOTEL_ID = self.hotel_page.select_port_from_hotel_listing(self.PORT_PREFIX, self.PORT_MODAL,
                                                                       self.PORT_DROPDOWN_PLACEHOLDER)
        self.add_hotel_availability(hotel_id=self.HOTEL_ID, airline_id=self.AIRLINE_ID,
                                    availability_date=today_m_5_days, ap_block_type=0, block_price='30.00', blocks=100,
                                    pay_type='0', room_type=1)
        self.hotel_page.click_on_search_hotel_button()
        self.go_to_quick_voucher_page()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.fill_data_on_quick_voucher(self.PORT_PREFIX, self.AIRLINE_NAME, past_date=True)
        self.quick_voucher_page.click_on_save_quick_voucher_button()
        # TODO: Unable to verify past inventory from frontend.

    def verify_initial_setup(self):
        try:
            self.support_cookies = self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                                                  desired_page=STORMX_URL + HOTEL_PAGE)
            self.verify_hotel_page()
            return True, ''
        except Exception as e:
            print("Something unexpected happened in test, exiting normally. For details see the exception"
                  " message below")
            print(str(e))
            return False, str(e)

    def tearDown(self):
        self.browser.close()
