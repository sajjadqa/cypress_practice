import unittest
from selenium import webdriver
from e2e_selenium_tests.PageObjectClasses import transports_page
from e2e_selenium_tests.PageObjectClasses import login_page
from e2e_selenium_tests.PageObjectClasses import sso_login_page
from e2e_selenium_tests.PageObjectClasses import dashboard_page, stormx_api_methods
from e2e_selenium_tests.PageObjectClasses import quick_room_transfer_page, hotel_page, airline_page, quick_voucher_page, \
    room_count_report_page, tva_users_page, vouchers_listing_page, port_allowances, configuration_page
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL, RUN_TESTS_HEADLESS
# from system_tests.run_selenium_tests import RUN_TESTS_HEADLESS
"""Without headless option chromium crashed"""
from stormx_verification_framework import StormxSystemVerification


class TestBaseClass(StormxSystemVerification):

    def setUp(self):
        super(TestBaseClass, self).setUp()
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        if RUN_TESTS_HEADLESS:
            options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)
        self.browser.get(STORMX_URL)
        self.browser.maximize_window()
        self.login_page = login_page.LoginMainPage(self.browser)
        self.sso_login_page = sso_login_page.SsoLoginMainPage(self.browser)
        self.dashboard_page = dashboard_page.DashBoardMainPage(self.browser)
        self.hotel_page = hotel_page.HotelMainPage(self.browser)
        self.room_count_report_page = room_count_report_page.RoomCountReportMainPage(self.browser)
        self.quick_voucher_page = quick_voucher_page.QuickVoucherMainPage(self.browser)
        self.quick_room_transfer = quick_room_transfer_page.QuickRoomMainPage(self.browser)
        self.airline_page = airline_page.AirlineMainPage(self.browser)
        self.tva_users_page = tva_users_page.TvaUsersMainPage(self.browser)
        self.transport_page = transports_page.TransportMainPage(self.browser)
        self.voucher_listing_page = vouchers_listing_page.VoucherListingMainPage(self.browser)
        self.port_allowance_page = port_allowances.PortAllowances(self.browser)
        self.configurations_page = configuration_page.Configurations(self.browser)

    def login_user(self, user_name="support", password="test", new_password=""):
        """
        :param new_password: string
        :param user_name: string
        :param password: string
        :return:
        """
        self.login_page.verify_browser_on_the_page()
        self.login_page.provide_credentials(user_name, password)
        self.assertTrue(self.login_page.click_on_login_button(new_password),
                        "There is a problem while logging-in. UN: " + user_name + " P:" + password)
        self.login_page.get_page_html_source()

    def api_login(self, username, password, resetpassword, desired_page):
        cookies_dict = {}
        cookies = self.login_to_stormx(username, password, resetpassword)
        # cookies = stormx_api_methods.StormxApiMethods.login_to_stormx(username, password, resetpassword)
        for cookie in cookies:
            cookie_dict = {
                'name': cookie.name,
                'value': cookie.value,
                'path': cookie.path,
                'expires': cookie.expires
            }
            cookies_dict.update(cookie_dict)
            self.browser.add_cookie(cookie_dict)
        self.browser.get(desired_page)
        return cookies

    def api_logout(self, cookies):
        stormx_api_methods.StormxApiMethods().logout(cookies=cookies)

    def search_hotel_by_api(self, hotel_id, cookies, port_id):
        api_response = stormx_api_methods.StormxApiMethods().search_hotel(hotel_id=hotel_id, cookies=cookies,
                                                                          port_id=port_id)
        self.assertEqual(api_response['results'][0]['hotel_id'], hotel_id)

    def logout_user(self, url):
        self.browser.get(url)

    def select_port_filter_by_url(self, url):
        self.browser.get(url)
        return self.hotel_page.select_port_filter_by_url()

    def sso_login_user(self, user_name="", password=""):
        self.sso_login_page.verify_browser_on_the_page()
        self.sso_login_page.provide_credentials(user_name, password)
        self.sso_login_page.click_on_login_button()
        # self.sso_login_page.get_page_html_source()

    def go_to_voucher_listing_page(self):
        self.dashboard_page.click_on_voucher_tab()
        self.voucher_listing_page.verify_browser_on_the_page()

    def go_to_quick_voucher_page(self):
        self.dashboard_page.click_on_quick_voucher_button()
        self.quick_voucher_page.verify_browser_on_the_page()
        self.quick_voucher_page.get_page_html_source()

    def go_to_room_count_report_page(self):
        self.dashboard_page.click_on_reports_tab()
        self.dashboard_page.click_on_room_count_report()
        self.room_count_report_page.verify_browser_on_the_page()
        self.room_count_report_page.get_page_html_source()

    def go_to_hotel_page(self):
        self.dashboard_page.click_on_hotel_tab()
        self.hotel_page.verify_browser_on_the_page()
        self.hotel_page.get_page_html_source()

    def go_to_transport_page(self):
        self.dashboard_page.click_on_transport_tab()
        self.transport_page.verify_browser_on_the_page()
        self.transport_page.get_page_html_source()

    def go_to_quick_room_transfer_page(self):
        self.dashboard_page.click_on_quick_room_transfer_tab()
        self.quick_room_transfer.verify_browser_on_the_page()
        self.quick_room_transfer.get_page_html_source()

    def go_to_airline_page(self):
        self.dashboard_page.click_on_airline_tab()
        self.airline_page.verify_browser_on_the_page()
        self.assertTrue(self.airline_page.verify_default_selected_status_filter_airlines_on_page(),
                        "Inactive airlines are shown on airline page loading. "
                        "It should be shown only Active status airlines on page loading.")

    def go_to_port_allowance_page(self):
        self.dashboard_page.click_on_ports_tab()
        self.dashboard_page.click_on_port_allowances_tab()
        self.port_allowance_page.verify_browser_on_the_page()
        self.port_allowance_page.get_page_html_source()

    def go_to_tva_users_page(self):
        self.dashboard_page.click_on_tva_users_tab()
        self.tva_users_page.verify_browser_on_the_page()

    def go_to_rate_caps_page(self, double_click=False):
        self.dashboard_page.click_on_configurations_button(double_click)
        self.configurations_page.verify_browser_on_the_page()
        self.configurations_page.click_on_rate_caps_tab()

    def verify_tvl_login_dashboard(self):
        self.assertIn("Ops Dashboard", self.login_page.get_page_html_source(), "Dashboard page is not fully loaded!")

    def verify_other_airline_users_dashboard(self):
        self.assertIn("MY DASHBOARD", self.login_page.get_page_html_source(), "Dashboard page is not fully loaded!")

    def verify_quick_room_transfer_page(self):
        self.assertIn("Quick Room Transfer | Travelliance", self.quick_room_transfer.get_page_html_source(),
                      "Quick Room Transfer page is not fully loaded!")

    def verify_hotel_page(self):
        self.assertIn("Hotels | Travelliance", self.hotel_page.get_page_html_source(), "Hotel page is not fully loaded")

    def verify_room_count_report_page(self):
        self.assertIn("Room Counts | Travelliance", self.room_count_report_page.get_page_html_source(),
                      "Room count report page is not fully loaded")

    def verify_quick_voucher_page(self):
        self.assertIn("'template/voucher/edit.html'", self.quick_voucher_page.get_page_html_source(),
                      "Quick voucher page is not fully loaded.")

    def verify_dashboard_page(self):
        self.dashboard_page.verify_browser_on_the_page()

    def verify_airline_dashboard_page(self):
        self.dashboard_page.verify_airline_dashboard_page()

    def verify_airline_page(self):
        self.assertIn("Airlines | Travelliance", self.airline_page.get_page_html_source(),
                      "Airline page is not fully loaded")
        self.assertTrue(self.airline_page.verify_default_selected_status_filter_airlines_on_page(),
                        "Inactive airlines are shown on airline page loading. "
                        "It should be shown only Active status airlines on page loading.")

    def verify_configurations_page(self):
        self.assertIn("Global Configurations | Travelliance", self.configurations_page.get_page_html_source(),
                      "Configurations page is not fully loaded.")
