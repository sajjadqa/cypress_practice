import sys
from e2e_selenium_tests.TestCases.test_quick_room_transfer_page import TestQuickRoomTransfer
from e2e_selenium_tests.TestCases.test_hotel_page import TestHotel
from e2e_selenium_tests.TestCases.test_airline_page import TestAirline
from e2e_selenium_tests.TestCases.test_quick_voucher_page import TestQuickVoucher
from e2e_selenium_tests.TestCases.test_room_count_report_page import TestRoomCountReport
from e2e_selenium_tests.TestCases.test_sso_login_page import TestSsoLogin
from e2e_selenium_tests.TestCases.test_port_allowance_page import TestPortAllowance
from e2e_selenium_tests.TestCases.test_rate_caps_page import TestRateCaps
from e2e_selenium_tests.TestCases.test_login_page import TestLoginPage
from e2e_selenium_tests.TestCases.test_expedia_hotels_page import TestExpediaHotels


def stormx_ui_suite(environment_name, unittest):
    TestLoginPage.selected_environment_name = environment_name
    TestHotel.selected_environment_name = environment_name
    TestRateCaps.selected_environment_name = environment_name
    TestRoomCountReport.selected_environment_name = environment_name
    TestQuickRoomTransfer.selected_environment_name = environment_name
    TestPortAllowance.selected_environment_name = environment_name
    TestQuickVoucher.selected_environment_name = environment_name
    TestAirline.selected_environment_name = environment_name
    TestSsoLogin.selected_environment_name = environment_name
    TestExpediaHotels.selected_environment_name = environment_name

    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(TestLoginPage))
    tests.addTest(unittest.makeSuite(TestRateCaps))
    tests.addTest(unittest.makeSuite(TestRoomCountReport))
    tests.addTest(unittest.makeSuite(TestQuickRoomTransfer))
    tests.addTest(unittest.makeSuite(TestHotel))
    tests.addTest(unittest.makeSuite(TestExpediaHotels))
    tests.addTest(unittest.makeSuite(TestPortAllowance))
    tests.addTest(unittest.makeSuite(TestQuickVoucher))
    tests.addTest(unittest.makeSuite(TestAirline))
    tests.addTest(unittest.makeSuite(TestSsoLogin))
    return tests

