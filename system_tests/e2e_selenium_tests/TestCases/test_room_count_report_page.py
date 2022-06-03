import unittest

from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings, get_hotel_block_fields, get_system_current_date_time
from e2e_selenium_tests.TestCases.base_test import TestBaseClass

ROOM_COUNT_REPORT_PAGE = '/admin/issued_adjustments_report.php'
HOTEL_PAGE = '/admin/hotels.php'
HOTEL_SEARCH_PARAMS = '?page=&pid=&hid={}'


class TestRoomCountReport(TestBaseClass):
    PORT_NAME = 'SYD Sydney Airport'
    PORT_PREFIX = PORT_NAME.split()[0]
    PORT_CURRENCY = "AUD"
    NON_COMM_PORT = 'AKL Auckland'
    NON_COMM_PORT_PREFIX = NON_COMM_PORT.split()[0]
    NON_PORT_CURRENCY = "NZD"
    AIRLINE_NAME = 'PRP Purple Rain Airlines'
    AIRLINE_FULL_NAME = AIRLINE_NAME.strip()[4:]
    AIRLINE_PREFIX = AIRLINE_NAME.split()[0]
    COMM_HOTEL = 'Abcot Inn'
    COMM_HOTEL_ID = '82750'
    NON_COMM_HOTEL = 'Airport Gateway Hotel'
    PAY_BY = "Net Pay"
    VOUCHER_RATE = '52.00'
    VOUCHER_COUNT = '120'
    CSA = "33"
    ACTUAL_COUNT = "55"
    NOTES = "Automated testing..."
    USER = "Support"
    BEFORE_GROUP_BY_COUNT = ""
    AFTER_GROUP_BY_COUNT = ""
    DICTIONARY_OF_HISTORY = ""
    DICTIONARY_OF_ROOM_COUNT = ""
    DATE = ""
    NEW_PASSWORD = "Tvlinc123!@#@"

    NON_COMM_PORT = {'port_name': 'AKL Auckland',
                     'port_prefix': 'AKL',
                     'port_id': '15'
                     }

    GROUP_BY_DATA = {'airline': 'PRP Purple Rain Airlines',
                     'port': 'AKL Auckland',
                     'port_prefix': 'AKL',
                     'comm_hotel': 'Apollo Hotel Auckland',
                     'comm_hotel_pay_type': 'Travelliance AMEX',
                     'non_comm_hotel': 'Auckland Rose Park Hotel',
                     'non_comm_hotel_pay_type': 'Direct Bill to TVL',
                     'rate_type': ['AP', 'PP', 'HB', 'CB'],
                     'rate': '103.00',
                     'count': '50',
                     'pay_by': 'Net Pay'
                     }

    def setUp(self):
        super(TestRoomCountReport, self).setUp()

    @ignore_warnings
    def test_comm_able_room_count_adjust_rate(self):
        """
        Verify that user should be able to add adjust room count.
        Steps:
        * Login with valid credentials.
        * Go to Room Count Report page.
        * Click on add new voucher button.
        * Fill all fields on add voucher form.
        * Click on Save button.
        * Verify that voucher created successfully message should be shown on add voucher modal.
        * Click on close button to close the voucher modal.
        * Search the newly added voucher data on room count listing page.
        * Click on Adjust Rate button.
        * Fill all required fields data of adjust rate.
        * Click on Save button and close the modal.
        * Search the newly added adjusted rate data on room count listing page.
        * Click on History button.
        * Verify the newly added adjusted rate data on room count history page.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(airline=self.AIRLINE_NAME,
                                                                     port=self.PORT_PREFIX, hotel=self.COMM_HOTEL,
                                                                     pay_by=self.PAY_BY, rates_type="AP",
                                                                     voucher_rate=self.VOUCHER_RATE,
                                                                     voucher_count=self.VOUCHER_COUNT)
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.assertTrue(self.room_count_report_page.verify_newly_added_room_count_on_room_count_listing(
            date=self.DATE, port=self.PORT_PREFIX, airline=self.AIRLINE_FULL_NAME, hotel=self.COMM_HOTEL,
            rate=self.VOUCHER_RATE, rate_type="AP", issued=self.VOUCHER_COUNT),
            "Newly added voucher data does'nt match with room count report")
        self.room_count_report_page.click_on_adjust_rate_button(port=self.PORT_PREFIX, rate_type="AP",
                                                                hotel=self.COMM_HOTEL)
        self.assertEqual(self.room_count_report_page.rate_code_on_adjust_room_count(), self.PORT_CURRENCY)
        self.room_count_report_page.fill_adjust_room_count_form(self.CSA, self.ACTUAL_COUNT, self.NOTES)
        # self.DICTIONARY_OF_ROOM_COUNT = self.room_count_report_page.generate_dictionary_of_room_count_fields()
        self.room_count_report_page.save_and_close_modal(adjust_room_count_modal=True)
        self.assertTrue(self.room_count_report_page.verify_newly_added_room_count_on_room_count_listing(
            date=self.DATE, port=self.PORT_PREFIX, airline=self.AIRLINE_FULL_NAME, hotel=self.COMM_HOTEL,
            rate=self.VOUCHER_RATE, issued=self.VOUCHER_COUNT, actual_rate=self.VOUCHER_RATE, csa=self.CSA,
            actual_count=self.ACTUAL_COUNT, rate_type="AP", adjust_room_count=True),
            "Newly added split room count data does'nt match with room count report")
        self.room_count_report_page.click_on_room_count_history_button(port=self.PORT_PREFIX, rate_type="AP",
                                                                       hotel=self.COMM_HOTEL)
        self.assertTrue(self.room_count_report_page.verify_newly_added_room_count_on_history(
            get_system_current_date_time("America/Chicago", room_count_history=True), self.USER,
            self.VOUCHER_RATE, self.VOUCHER_COUNT, self.VOUCHER_RATE, self.CSA, self.ACTUAL_COUNT, self.NOTES),
            "Newly added room count records are not matched with room count history count")

    @ignore_warnings
    def test_non_comm_room_count_adjust_rate(self):
        """
            Test add new voucher for non commission-able room count report.
                - Verify that voucher type should be selected according to pay type on add voucher.
                - Verify newly added voucher data on room count listing page.
                - Add data on adjust room count form and verify the updated data on room count listing.
                - Verify the posted count on adjust room count page.
                - Verify newly added data on room count history dialog box.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.room_count_report_page.click_on_search_button()
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(airline=self.AIRLINE_NAME,
                                                                     port=self.NON_COMM_PORT_PREFIX,
                                                                     hotel=self.NON_COMM_HOTEL, pay_by=self.PAY_BY,
                                                                     voucher_rate=self.VOUCHER_RATE, rates_type="AP"
                                                                     , voucher_count=self.VOUCHER_COUNT,
                                                                     non_comm=True)
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.assertTrue(self.room_count_report_page.verify_newly_added_room_count_on_room_count_listing(
            date=self.DATE, port=self.NON_COMM_PORT_PREFIX, airline=self.AIRLINE_FULL_NAME,
            hotel=self.NON_COMM_HOTEL, rate=self.VOUCHER_RATE, issued=self.VOUCHER_COUNT, rate_type="AP",
            non_comm=True), "Newly added voucher data does'nt match with room count report")
        self.room_count_report_page.click_on_adjust_rate_button(port=self.NON_COMM_PORT_PREFIX, rate_type="AP",
                                                                hotel=self.NON_COMM_HOTEL, non_comm=True)
        self.assertEqual(self.room_count_report_page.rate_code_on_adjust_room_count(), self.NON_PORT_CURRENCY)
        self.room_count_report_page.fill_adjust_room_count_form(self.CSA, self.ACTUAL_COUNT, self.NOTES)
        # self.assertTrue(self.room_count_report_page.commission_able_working(comm_able=True), "ERROR")
        self.room_count_report_page.save_and_close_modal(adjust_room_count_modal=True)
        self.assertTrue(self.room_count_report_page.verify_newly_added_room_count_on_room_count_listing(
            date=self.DATE, port=self.NON_COMM_PORT_PREFIX, airline=self.AIRLINE_FULL_NAME,
            hotel=self.NON_COMM_HOTEL, rate=self.VOUCHER_RATE, issued=self.VOUCHER_COUNT, rate_type="AP",
            actual_rate=self.VOUCHER_RATE, csa=self.CSA, actual_count=self.ACTUAL_COUNT, adjust_room_count=True,
            non_comm=True), "Newly added split room count data does'nt match with room count report")
        self.room_count_report_page.click_on_room_count_history_button(port=self.NON_COMM_PORT_PREFIX,
                                                                       rate_type="AP", hotel=self.NON_COMM_HOTEL,
                                                                       non_comm=True)
        self.assertTrue(self.room_count_report_page.verify_newly_added_room_count_on_history(
            get_system_current_date_time("America/Chicago", room_count_history=True), self.USER,
            self.VOUCHER_RATE, self.VOUCHER_COUNT, self.VOUCHER_RATE, self.CSA, self.ACTUAL_COUNT, self.NOTES),
            "Newly added room count records are not matched with room count history count")
        self.room_count_report_page.save_and_close_modal(room_count_history=True)
        self.room_count_report_page.click_on_adjust_rate_button(port=self.NON_COMM_PORT_PREFIX, rate_type="AP",
                                                                hotel=self.NON_COMM_HOTEL, non_comm=True)
        self.room_count_report_page.fill_adjust_room_count_form(csa="", actual_count="10", notes=self.NOTES)
        self.assertTrue(self.room_count_report_page.commission_able_working(comm_able=True), "ERROR")

    @ignore_warnings
    def test_total_issued_count_calculation(self):
        """
        Verify that total issued count on room count listing should be equal to sum of issued count of all vouchers.
        Verify that total csa count on room count listing should be equal to sum of csa count of all vouchers.
        Verify that total actual count on room count listing should be equal to sum of actual count of all vouchers.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.room_count_report_page.click_on_search_button()
        self.assertEqual(self.room_count_report_page.total_issued_count_on_listing(),
                         self.room_count_report_page.calculate_total_issued_count())
        self.assertEqual(self.room_count_report_page.calculate_total_csa_count(),
                         self.room_count_report_page.total_csa_count_on_listing())
        self.assertEqual(self.room_count_report_page.total_actual_count_on_listing(),
                         self.room_count_report_page.calculate_total_actual_count())

    @ignore_warnings
    def test_non_commission_able_working(self):
        """
        Verify that room count data row should be shown in pink colour on changing adjust count from commission-able to
         non commission-able.
        Verify that room count data row should not be shown in pink colour on changing adjust count from
        non-commission-able to commission-able.
        Verify the Rate code is driven from hotel profile on adjust room count page.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.room_count_report_page.click_on_search_button()
        self.room_count_report_page.click_on_adjust_rate_button(port=self.PORT_PREFIX, rate_type="AP",
                                                                hotel=self.COMM_HOTEL)
        rate_code_on_adjust_rate_modal = self.room_count_report_page.rate_code_on_adjust_room_count()
        self.assertTrue(self.room_count_report_page.commission_able_working(comm_able=True),
                        "There is an issue while changing record from Non-Comm to comm-able.")
        self.room_count_report_page.click_on_adjust_rate_button(port=self.PORT_PREFIX, rate_type="AP",
                                                                hotel=self.COMM_HOTEL, non_comm=True)
        self.room_count_report_page.fill_adjust_room_count_form(csa="", actual_count="10", notes=self.NOTES)
        self.assertTrue(self.room_count_report_page.commission_able_working(comm_able=True),
                        "There is an issue while changing record from Comm-able to non-comm.")
        self.go_to_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.COMM_HOTEL_ID)
        self.browser.get(STORMX_URL + HOTEL_PAGE + HOTEL_SEARCH_PARAMS.format(self.COMM_HOTEL_ID))
        self.hotel_page.open_hotel_details_page(self.COMM_HOTEL_ID)
        self.hotel_page.click_on_tva_settings_tab_from_hotel_details()
        self.assertEqual(rate_code_on_adjust_rate_modal, self.hotel_page.hotel_default_currency(),
                         "Hotels's default currency is different from adjust room count currency code.")

    @ignore_warnings
    def test_ap_rate_type_group_by_data(self):
        """
        Make sure ap rate type rows are grouping together.... Rows group by Date, Airline, port,
        hotel,Rate type(PP OR AP,HB,CB), commission-able.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(self.GROUP_BY_DATA['airline'],
                                                                     self.GROUP_BY_DATA['port_prefix'],
                                                                     self.GROUP_BY_DATA['comm_hotel'],
                                                                     self.GROUP_BY_DATA['pay_by'],
                                                                     self.GROUP_BY_DATA['rate_type'][0],
                                                                     self.GROUP_BY_DATA['rate'],
                                                                     self.GROUP_BY_DATA['count']
                                                                     )
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.BEFORE_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][0],
            self.GROUP_BY_DATA['comm_hotel'])
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(self.GROUP_BY_DATA['airline'],
                                                                     self.GROUP_BY_DATA['port_prefix'],
                                                                     self.GROUP_BY_DATA['comm_hotel'],
                                                                     self.GROUP_BY_DATA['pay_by'],
                                                                     self.GROUP_BY_DATA['rate_type'][2],
                                                                     self.GROUP_BY_DATA['rate'],
                                                                     self.GROUP_BY_DATA['count']
                                                                     )
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.AFTER_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][0],
            self.GROUP_BY_DATA['comm_hotel'])
        self.assertGreater(self.AFTER_GROUP_BY_COUNT, self.BEFORE_GROUP_BY_COUNT, '')
        self.room_count_report_page.click_on_search_button()
        self.BEFORE_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][0],
            self.GROUP_BY_DATA['comm_hotel'])
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(self.GROUP_BY_DATA['airline'],
                                                                     self.GROUP_BY_DATA['port_prefix'],
                                                                     self.GROUP_BY_DATA['comm_hotel'],
                                                                     self.GROUP_BY_DATA['pay_by'],
                                                                     self.GROUP_BY_DATA['rate_type'][3],
                                                                     self.GROUP_BY_DATA['rate'],
                                                                     self.GROUP_BY_DATA['count']
                                                                     )
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.AFTER_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][0],
            self.GROUP_BY_DATA['comm_hotel'])
        self.assertGreater(self.AFTER_GROUP_BY_COUNT, self.BEFORE_GROUP_BY_COUNT,
                           'Records should be grouped by in this scenario.')
        self.BEFORE_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][0],
            self.GROUP_BY_DATA['comm_hotel'])
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(self.GROUP_BY_DATA['airline'],
                                                                     self.GROUP_BY_DATA['port_prefix'],
                                                                     self.GROUP_BY_DATA['comm_hotel'],
                                                                     self.GROUP_BY_DATA['pay_by'],
                                                                     self.GROUP_BY_DATA['rate_type'][1],
                                                                     self.GROUP_BY_DATA['rate'],
                                                                     self.GROUP_BY_DATA['count']
                                                                     )
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.AFTER_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][0],
            self.GROUP_BY_DATA['comm_hotel'])
        self.assertEqual(self.AFTER_GROUP_BY_COUNT, self.BEFORE_GROUP_BY_COUNT,
                         'Records should not be grouped by in this scenario')

    @ignore_warnings
    def test_pp_rate_type_group_by_data(self):
        """
        Make sure pp rate type rows are grouping together.... Rows group by Date, Airline, port,
        hotel,Rate type(PP OR AP,HB,CB), commission-able.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(self.GROUP_BY_DATA['airline'],
                                                                     self.GROUP_BY_DATA['port_prefix'],
                                                                     self.GROUP_BY_DATA['non_comm_hotel'],
                                                                     self.GROUP_BY_DATA['pay_by'],
                                                                     self.GROUP_BY_DATA['rate_type'][1],
                                                                     self.GROUP_BY_DATA['rate'],
                                                                     self.GROUP_BY_DATA['count']
                                                                     )
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.BEFORE_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][1],
            self.GROUP_BY_DATA['non_comm_hotel'])
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(self.GROUP_BY_DATA['airline'],
                                                                     self.GROUP_BY_DATA['port_prefix'],
                                                                     self.GROUP_BY_DATA['non_comm_hotel'],
                                                                     self.GROUP_BY_DATA['pay_by'],
                                                                     self.GROUP_BY_DATA['rate_type'][1],
                                                                     self.GROUP_BY_DATA['rate'],
                                                                     self.GROUP_BY_DATA['count']
                                                                     )
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.AFTER_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][1],
            self.GROUP_BY_DATA['non_comm_hotel'])
        self.assertGreater(self.AFTER_GROUP_BY_COUNT, self.BEFORE_GROUP_BY_COUNT, '')
        self.BEFORE_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][1],
            self.GROUP_BY_DATA['non_comm_hotel'])
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.DATE = self.room_count_report_page.select_date_from_room_count_voucher()
        self.room_count_report_page.fill_add_voucher_room_count_form(self.GROUP_BY_DATA['airline'],
                                                                     self.GROUP_BY_DATA['port_prefix'],
                                                                     self.GROUP_BY_DATA['comm_hotel'],
                                                                     self.GROUP_BY_DATA['pay_by'],
                                                                     self.GROUP_BY_DATA['rate_type'][0],
                                                                     self.GROUP_BY_DATA['rate'],
                                                                     self.GROUP_BY_DATA['count']
                                                                     )
        self.room_count_report_page.save_and_close_modal(voucher_modal=True)
        self.room_count_report_page.click_on_search_button()
        self.AFTER_GROUP_BY_COUNT = self.room_count_report_page.group_by_records_functionality(
            self.GROUP_BY_DATA['rate'], self.GROUP_BY_DATA['port_prefix'], self.GROUP_BY_DATA['rate_type'][1],
            self.GROUP_BY_DATA['non_comm_hotel'])
        self.assertEqual(self.AFTER_GROUP_BY_COUNT, self.BEFORE_GROUP_BY_COUNT, '')

    @unittest.expectedFailure
    @ignore_warnings
    def test_download_room_count_report(self):
        """
        Verify that user should be able to download split room count report.
        TODO: Verify when a download has completed?

        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.room_count_report_page.click_on_search_button()
        self.room_count_report_page.download_room_count_report()
        self.assertTrue(self.room_count_report_page.verify_every_download())

    def verify_initial_setup(self):
        try:
            self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                           desired_page=STORMX_URL + ROOM_COUNT_REPORT_PAGE)
            self.verify_room_count_report_page()
            return True, ''
        except Exception as e:
            print("Something unexpected happened in test, exiting normally. For details see the exception"
                  " message below")
            print(str(e))
            return False, str(e)

    def tearDown(self):
        self.browser.close()
