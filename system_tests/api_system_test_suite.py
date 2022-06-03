from stormx_verification_framework import StormxSystemVerification
from verify_airline_and_passenger_api import TestAirlineAndPassengerAPI
from verify_tvl_internal_api import TestTvlInternalAPI
from verify_passenger_pay import TestPassengerPay
from verify_api_health import TestApiHealth
from verify_api_ping import TestApiPing
from verify_api_hotel_amenities import TestApiHotelAmenities
from verify_api_hotel_booking import TestApiHotelBooking
from verify_api_hotel_booking_blocks import TestApiHotelBookingBlocks
from verify_api_hotel_booking_cancel import TestApiHotelBookingCancel
from verify_api_hotel_booking_decline import TestApiHotelBookingDecline
from verify_api_hotel_booking_direct_billing import TestApiHotelBookingDirectBilling
from verify_api_hotel_booking_expedia import TestApiHotelBookingExpedia
from verify_api_hotel_booking_internal import TestApiHotelBookingInternal
from verify_api_hotel_booking_pets import TestApiHotelBookingPets
from verify_api_hotel_images import TestApiHotelImages
from verify_api_hotel_search import TestApiHotelSearch
from verify_api_hotel_search_internal import TestApiHotelSearchInternal
from verify_api_meals_icoupon import TestApiMealsICoupon
from verify_api_notifications import TestApiNotifications
from verify_api_passenger_import import TestApiPassengerImport
from verify_api_custom_fields import TestApiCustomFields
from verify_api_passenger_retrieval import TestApiPassengerRetrieval
from verify_api_shuttle_tracker import TestApiShuttleTracker
from verify_hotel_portal import TestHotelPortal
from verify_hotel_voucher_unlock import TestHotelVoucherUnlock
from verify_meal_voucher_active_date_range import TestMealVoucherActiveDateRange
from verify_passenger_app import TestPassengerApp
from verify_qr_codes import TestQrCodes
from verify_taxes import TestTaxes
from verify_hotel_allowances import TestHotelAllowances


def api_suite(environment_name, unittest):
    StormxSystemVerification.selected_environment_name = environment_name
    TestAirlineAndPassengerAPI.selected_environment_name = environment_name  # TODO: remove hacky monkey patching
    TestTvlInternalAPI.selected_environment_name = environment_name
    TestPassengerPay.selected_environment_name = environment_name
    TestApiHealth.selected_environment_name = environment_name
    TestApiPing.selected_environment_name = environment_name
    TestApiHotelAmenities.selected_environment_name = environment_name
    TestApiHotelBooking.selected_environment_name = environment_name
    TestApiHotelBookingBlocks.selected_environment_name = environment_name
    TestApiHotelBookingCancel.selected_environment_name = environment_name
    TestApiHotelBookingDecline.selected_environment_name = environment_name
    TestApiHotelBookingDirectBilling.selected_environment_name = environment_name
    TestApiHotelBookingExpedia.selected_environment_name = environment_name
    TestApiHotelBookingInternal.selected_environment_name = environment_name
    TestApiHotelBookingPets.selected_environment_name = environment_name
    TestApiHotelImages.selected_environment_name = environment_name
    TestApiHotelSearch.selected_environment_name = environment_name
    TestApiHotelSearchInternal.selected_environment_name = environment_name
    TestApiMealsICoupon.selected_environment_name = environment_name
    TestApiNotifications.selected_environment_name = environment_name
    TestApiPassengerImport.selected_environment_name = environment_name
    TestApiCustomFields.selected_environment_name = environment_name
    TestApiPassengerRetrieval.selected_environment_name = environment_name
    TestHotelPortal.selected_environment_name = environment_name
    TestApiShuttleTracker.selected_environment_name = environment_name
    TestHotelVoucherUnlock.selected_environment_name = environment_name
    TestMealVoucherActiveDateRange.selected_environment_name = environment_name
    TestPassengerApp.selected_environment_name = environment_name
    TestQrCodes.selected_environment_name = environment_name
    TestTaxes.selected_environment_name = environment_name

    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(TestAirlineAndPassengerAPI))
    tests.addTest(unittest.makeSuite(TestTvlInternalAPI))
    tests.addTest(unittest.makeSuite(TestPassengerPay))
    tests.addTest(unittest.makeSuite(TestApiHealth))
    tests.addTest(unittest.makeSuite(TestApiPing))
    tests.addTest(unittest.makeSuite(TestApiHotelAmenities))
    tests.addTest(unittest.makeSuite(TestApiHotelBooking))
    tests.addTest(unittest.makeSuite(TestApiHotelBookingBlocks))
    tests.addTest(unittest.makeSuite(TestApiHotelBookingCancel))
    tests.addTest(unittest.makeSuite(TestApiHotelBookingDecline))
    tests.addTest(unittest.makeSuite(TestApiHotelBookingDirectBilling))
    tests.addTest(unittest.makeSuite(TestApiHotelBookingExpedia))
    tests.addTest(unittest.makeSuite(TestApiHotelBookingInternal))
    tests.addTest(unittest.makeSuite(TestApiHotelBookingPets))
    tests.addTest(unittest.makeSuite(TestApiHotelImages))
    tests.addTest(unittest.makeSuite(TestApiHotelSearch))
    tests.addTest(unittest.makeSuite(TestApiHotelSearchInternal))
    tests.addTest(unittest.makeSuite(TestApiNotifications))
    tests.addTest(unittest.makeSuite(TestApiPassengerImport))
    tests.addTest(unittest.makeSuite(TestApiCustomFields))
    tests.addTest(unittest.makeSuite(TestApiPassengerRetrieval))
    tests.addTest(unittest.makeSuite(TestHotelVoucherUnlock))
    tests.addTest(unittest.makeSuite(TestMealVoucherActiveDateRange))
    tests.addTest(unittest.makeSuite(TestPassengerApp))
    tests.addTest(unittest.makeSuite(TestQrCodes))
    tests.addTest(unittest.makeSuite(TestTaxes))
    tests.addTest(unittest.makeSuite(TestHotelAllowances))

    return tests
