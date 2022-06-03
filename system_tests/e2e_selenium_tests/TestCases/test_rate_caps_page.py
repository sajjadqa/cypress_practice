from e2e_selenium_tests.PageObjectClasses.hotel_page import set_values_to_new_hotel_fields
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
from e2e_selenium_tests.TestCases.base_test import TestBaseClass
from e2e_selenium_tests.BaseClasses.helper import ignore_warnings, get_hotel_block_fields


class TestRateCaps(TestBaseClass):
    PORT_NAME = "SYD Sydney Airport"
    PORT_PREFIX = PORT_NAME.split()[0]
    PORT_MODAL = 'filter.pid'
    PORT_DROPDOWN_PLACEHOLDER = 'Type port name or prefix'
    AIRLINE_NAME = "PRP Purple Rain Airlines"
    AIRLINE_PREFIX = AIRLINE_NAME.split()[0]
    HOTEL_ID = "107513"
    HOTEL_NAME = 'Felix Hotel'
    NEW_PASSWORD = "Tvlinc123!@#@"
    CURRENCY = "AUD - Australian Dollars"
    CURRENCY_PREFIX = CURRENCY.split()[0]
    RATE_CAP_WARNING = "50.00"
    EDIT_RATE_CAP_WARNING = "55"

    def setUp(self):
        super(TestRateCaps, self).setUp()

    @ignore_warnings
    def test_add_new_rate_cap(self):
        """
        Add new rate cap per currency.
        Verify that newly added rate cap per currency should be visible on listing page.
        :return:
        """
        verified, msg = self.verify_initial_setup()
        self.assertTrue(verified, msg)
        self.configurations_page.delete_rate_caps()
        self.configurations_page.add_new_rate_cap(self.CURRENCY, self.RATE_CAP_WARNING)
        self.configurations_page.click_on_save_rate_cap_button()
        self.configurations_page.verify_newly_added_rate_caps_on_listing(currency=self.CURRENCY_PREFIX,
                                                                         rate_cap=self.RATE_CAP_WARNING,
                                                                         updated_by="Support", region="America/Chicago")

    @ignore_warnings
    def test_edit_delete_rate_caps(self):
        """
        Rate cap per currency:
        -Rate should be editable for existing rate caps....per the button on the right (pencil looking button)
        -Rate caps should be able to be removed completely.
        :return:
        """
        self.test_add_new_rate_cap()
        self.configurations_page.verify_newly_added_rate_caps_on_listing(currency=self.CURRENCY_PREFIX,
                                                                         rate_cap=self.RATE_CAP_WARNING,
                                                                         updated_by="Support", region="America/Chicago")
        self.configurations_page.edit_rate_caps(edit_rate=self.EDIT_RATE_CAP_WARNING)
        self.configurations_page.verify_newly_added_rate_caps_on_listing(currency=self.CURRENCY_PREFIX,
                                                                         rate_cap=self.EDIT_RATE_CAP_WARNING,
                                                                         updated_by="Support", region="America/Chicago")
        self.configurations_page.delete_rate_caps()

    @ignore_warnings
    def test_rate_cap_warning_on_hotel_profile(self):
        """
        Edit availability modal ---- user will be warned IF the hotel currency is set with a rate cap AND the value in
        rate is higher than the rate cap.
        Example: hotel has AUD as currency.  AUD rate cap is 50.  User enters 51 for the rate.  User is warned even
        before they save.

        Hotel Profile - Daily SoftBlock:
        The Rate field is where this is being checked. IF entry on this field exceeds the rate cap THEN red text field
        happens.

        Hotel Profile - Daily Contracted Blocks:
        The Rate field is where this is being checked. IF entry on this field exceeds the rate cap THEN red text field
        happens.

        Hotel Profile - Contracted Rates:
        In any Monday - Sunday fields user will get their warning (red textbox) indicating the rate cap has exceeded.
        -applies to Rooms Rates
        -applies to RT or ROH
        -applies to Special Rates
        :return:
        """
        self.test_add_new_rate_cap()
        self.go_to_hotel_page()
        self.verify_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.hotel_page.click_on_edit_availability_button()
        self.assertEqual(self.hotel_page.fill_data_to_form_on_edit_avails(get_hotel_block_fields(),
                                                                          rate_caps_warning=True),
                         "Warning! Rate cap has been Exceeded.")
        self.hotel_page.click_on_close_button()
        self.hotel_page.open_hotel_details_page(self.HOTEL_ID)
        self.hotel_page.click_on_daily_soft_block_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_soft_blocks_rate_field(rate_val=self.EDIT_RATE_CAP_WARNING)
                        , "Rate cap warning doesn't work for soft blocks rate field.")
        self.hotel_page.click_on_daily_contracted_block_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_daily_contracted_blocks_rate_field(
            rate_val=self.EDIT_RATE_CAP_WARNING), "Rate cap warning doesn't work for contracted blocks rate field.")
        self.hotel_page.click_on_room_rate_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_contracted_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING),
            "Rate cap warning doesn't work for room rate ROH days for contracted rate field.")
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_special_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING),
            "Rate cap warning doesn't work for room rate ROH days for special rate field.")
        self.hotel_page.refresh_page()
        self.hotel_page.click_on_room_rate_tab_from_hotel_details()
        self.hotel_page.change_rate_type()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_contracted_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING),
            "Rate cap warning doesn't work for room rate RT days for contracted rate field.")
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_special_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING),
            "Rate cap warning doesn't work for room rate RT days for special rate field.")
        self.delete_added_rate_caps(double_click=True)

    @ignore_warnings
    def test_rate_cap_warning_on_room_count_report(self):
        """
        Room Count Report - +Voucher:
        +Voucher gives the user the ability to create inventory and a voucher in the same step. This is typically used
        for vouchers in the past. This feature will still give a check on the Rate Cap value and warn the user IF they
        attempt to enter a rate that exceeds the Rate Cap Value for the hotel they select.
        :return:
        """
        self.test_add_new_rate_cap()
        self.go_to_room_count_report_page()
        self.verify_room_count_report_page()
        self.room_count_report_page.click_on_add_voucher_room_count()
        self.assertEqual(self.room_count_report_page.rate_cap_warning_on_room_count_add_voucher(port=self.PORT_PREFIX,
                                                                                                hotel=self.HOTEL_NAME,
                                                                                                voucher_rate=self.
                                                                                                EDIT_RATE_CAP_WARNING),
                         "Warning! Rate cap has been Exceeded.")
        self.room_count_report_page.close_add_voucher_modal()
        self.delete_added_rate_caps(double_click=True)

    @ignore_warnings
    def test_rate_caps_warning_for_no_currency_hotel(self):
        """
        -IF no currency associated to hotel THEN no warning.
        -Having no Rate Cap for a currency means there isn't a possible way to get a warning
        -Rates are all still able to be entered above the cap.... just a warning is what is wanted.
        :return:
        """
        self.test_add_new_rate_cap()
        self.go_to_hotel_page()
        self.verify_hotel_page()
        self.hotel_page.click_on_add_new_hotel_button()
        self.hotel_page.fill_data_in_new_hotel_form(set_values_to_new_hotel_fields())
        self.assertTrue(self.hotel_page.click_on_hotel_save_button(),
                        'There is an error while saving hotel data. '
                        'Some mandatory field data is not saved correctly')
        self.HOTEL_ID = self.hotel_page.get_hotel_id()
        self.assertIn(self.HOTEL_ID, self.hotel_page.get_current_url_of_hotel_page())
        self.hotel_page.click_on_serviced_ports_tab_from_hotel_details()
        self.hotel_page.select_serviced_port(self.PORT_PREFIX)
        self.hotel_page.click_on_add_port_button()
        self.assertIn(self.PORT_PREFIX, self.hotel_page.get_serviced_port_list(), "Serviced Port is not added.")
        self.hotel_page.click_on_daily_soft_block_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_soft_blocks_rate_field(rate_val=self.EDIT_RATE_CAP_WARNING,
                                                                                    no_currency=True)
                        , "Rate cap warning doesn't work for soft blocks rate field.")
        self.hotel_page.click_on_daily_contracted_block_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_daily_contracted_blocks_rate_field(
            rate_val=self.EDIT_RATE_CAP_WARNING, no_currency=True),
            "Rate cap warning doesn't work for contracted blocks rate field.")
        self.hotel_page.click_on_room_rate_tab_from_hotel_details()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_contracted_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING, no_currency=True),
            "Rate cap warning doesn't work for room rate ROH days for contracted rate field.")
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_special_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING, no_currency=True),
            "Rate cap warning doesn't work for room rate ROH days for special rate field.")
        self.hotel_page.refresh_page()
        self.hotel_page.click_on_room_rate_tab_from_hotel_details()
        self.hotel_page.change_rate_type()
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_contracted_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING, no_currency=True),
            "Rate cap warning doesn't work for room rate RT days for contracted rate field.")
        self.assertTrue(self.hotel_page.rate_caps_warning_on_room_rate_special_rate_days_field(
            rate_val=self.EDIT_RATE_CAP_WARNING, no_currency=True),
            "Rate cap warning doesn't work for room rate RT days for special rate field.")
        self.go_to_hotel_page()
        self.verify_hotel_page()
        self.hotel_page.search_hotel_on_hotel_listing(self.HOTEL_ID)
        self.hotel_page.click_on_edit_availability_button()
        self.assertTrue(self.hotel_page.fill_data_to_form_on_edit_avails(get_hotel_block_fields(),
                                                                         rate_caps_warning=True, no_currency=True),
                        "Rate caps warning shouldn't be shown for this hotel. As, no currency is associated to hotel "
                        "THEN no warning.")
        self.hotel_page.click_on_close_button()
        self.delete_added_rate_caps(double_click=True)

    def delete_added_rate_caps(self, double_click=False):
        self.go_to_rate_caps_page(double_click)
        self.verify_configurations_page()
        self.configurations_page.delete_rate_caps()

    def verify_initial_setup(self):
        try:
            self.api_login(username="support", password="test", resetpassword=self.NEW_PASSWORD,
                           desired_page=STORMX_URL)
            self.verify_tvl_login_dashboard()
            self.verify_dashboard_page()
            self.go_to_rate_caps_page()
            self.verify_configurations_page()
            return True, ''
        except Exception as e:
            print("Something unexpected happened in test, exiting normally. For details see the exception"
                  " message below")
            print(str(e))
            return False, str(e)

    def tearDown(self):
        self.browser.close()
