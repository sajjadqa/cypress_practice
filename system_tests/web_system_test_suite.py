from stormx_verification_framework import SUPPORTED_ENVIRONMENTS, StormxSystemVerification
from verify_php_app import TestStormxUI

from verify_port_allowance import TestPortAllowance
from verify_php_passenger_pay_api import TestPassengerPayAPI
from verify_quick_room_transfer import TestQuickRoomTransfer
from verify_user_password_reset import UserPasswordResetTestCase
from verify_system_ports import TestSystemPorts
from verify_expedia_linking import TestExpediaLinking
from verify_blog_messages import TestBlogMessages
from verify_hotel_passenger_notes import TestHotelPassengerNotes
from verify_additional_contacts import TestAdditionalContacts
from verify_reconcilliation import TestReconcilliation
from verify_hmt_recon import TestHMTRecon
from verify_rate_cap import TestRateCap
from verify_availability_on_port_timezone import AvailabilityOnPortTimezone
from verify_hotel_contracts import TestHotelContracts
from verify_avails import TestAvailability
from verify_php_hotel_amenities import TestPhpAmenities
from verify_transport_only_voucher import TestTransportOnlyVoucher


def web_suite(environment_name, unittest):
    StormxSystemVerification.selected_environment_name = environment_name
    # TODO: remove hacky monkey patching
    TestPassengerPayAPI.selected_environment_name = environment_name
    # TODO: remove hacky monkey patching
    TestStormxUI.selected_environment_name = environment_name
    # TODO: remove hacky monkey patching
    TestPortAllowance.selected_environment_name = environment_name
    # TODO: remove hacky monkey patching
    TestQuickRoomTransfer.selected_environment_name = environment_name
    UserPasswordResetTestCase.selected_environment_name = environment_name
    TestSystemPorts.selected_environment_name = environment_name
    TestExpediaLinking.selected_environment_name = environment_name
    TestBlogMessages.selected_environment_name = environment_name
    AvailabilityOnPortTimezone.selected_environment_name = environment_name
    TestHotelPassengerNotes.selected_environment_name = environment_name
    TestHMTRecon.selected_environment_name = environment_name
    TestRateCap.selected_environment_name = environment_name
    TestReconcilliation.selected_environment_name = environment_name
    TestHotelContracts.selected_environment_name = environment_name

    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(TestPassengerPayAPI))
    tests.addTest(unittest.makeSuite(TestStormxUI))
    tests.addTest(unittest.makeSuite(TestPortAllowance))
    tests.addTest(unittest.makeSuite(TestQuickRoomTransfer))
    tests.addTest(unittest.makeSuite(UserPasswordResetTestCase))
    tests.addTest(unittest.makeSuite(TestExpediaLinking))
    tests.addTest(unittest.makeSuite(TestSystemPorts))
    tests.addTest(unittest.makeSuite(TestBlogMessages))
    tests.addTest(unittest.makeSuite(AvailabilityOnPortTimezone))
    tests.addTest(unittest.makeSuite(TestHotelPassengerNotes))
    tests.addTest(unittest.makeSuite(TestAdditionalContacts))
    tests.addTest(unittest.makeSuite(TestReconcilliation))
    tests.addTest(unittest.makeSuite(TestHMTRecon))
    tests.addTest(unittest.makeSuite(TestRateCap))
    tests.addTest(unittest.makeSuite(TestHotelContracts))
    tests.addTest(unittest.makeSuite(TestAvailability))
    tests.addTest(unittest.makeSuite(TestPhpAmenities))
    tests.addTest(unittest.makeSuite(TestTransportOnlyVoucher))
    

    return tests
