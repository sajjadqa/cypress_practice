#! /usr/bin/env python3
"""
These are standalone system tests that can be pointed at local or staging servers.

These tests require that a valid server be stood up.
These tests currently require that you manually set up the American Airlines and Delta Air Lines customers as documented in `$StormxAPI/aws/provision_servers.sh`.
These tests currently require that the server also contain reasonable inventory before the tests start.
These tests currently require that the WEX credit card system is funded with plenty of money.
TODO: try to remove/automate some of the above constraints/dependencies.

WARNING: the tests rely on randomness and generating shorter unique numbers, and may occasionally fail.
         Some of the number generators have an extra ~1/100,000,000 or so chance of failing each time a
         test case is run without clearing out the database.


DEVELOPER TIPS:

* when developing unit tests, temporarily use the `display_response(response)`
  utility to pretty print a response object.


"""
import sys
import unittest

from web_system_test_suite import (
    web_suite,
    TestPassengerPayAPI,
    TestStormxUI,
    TestPortAllowance,
    TestQuickRoomTransfer,
    UserPasswordResetTestCase,
    TestSystemPorts,
    TestExpediaLinking,
    SUPPORTED_ENVIRONMENTS,
    StormxSystemVerification,
    TestBlogMessages,
    AvailabilityOnPortTimezone,
    TestHotelPassengerNotes,
    TestAdditionalContacts,
    TestReconcilliation,
    TestHMTRecon,
    TestRateCap,
    TestHotelContracts,
    TestAvailability,
    TestPhpAmenities,
    TestTransportOnlyVoucher,
)

from api_system_test_suite import (
    api_suite,
    TestAirlineAndPassengerAPI,
    TestTvlInternalAPI,
    TestPassengerPay,
    TestApiHealth,
    TestApiPing,
    TestApiHotelAmenities,
    TestApiHotelBooking,
    TestApiHotelBookingBlocks,
    TestApiHotelBookingCancel,
    TestApiHotelBookingDecline,
    TestApiHotelBookingDirectBilling,
    TestApiHotelBookingExpedia,
    TestApiHotelBookingInternal,
    TestApiHotelBookingPets,
    TestApiHotelImages,
    TestApiHotelSearch,
    TestApiHotelSearchInternal,
    TestApiMealsICoupon,
    TestApiNotifications,
    TestApiPassengerImport,
    TestApiCustomFields,
    TestApiPassengerRetrieval,
    TestApiShuttleTracker,
    TestHotelPortal,
    TestHotelVoucherUnlock,
    TestMealVoucherActiveDateRange,
    TestPassengerApp,
    TestQrCodes,
    TestTaxes,
    TestHotelAllowances
)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('ERROR: must provide environment name.\n\nCanned environments:\n\t' +
              '\n\t'.join(
                  tuple(sorted(SUPPORTED_ENVIRONMENTS.keys()))) + '\n\n'
              '...Or you may supply your own environment name.\n' +
              'Example: "superman" would be the environment name of the URL https://supermanapi.tvlinc.com .\n'
              )
        sys.exit(1)
    environment_name = sys.argv[1]
    if environment_name not in SUPPORTED_ENVIRONMENTS:
        SUPPORTED_ENVIRONMENTS[environment_name] = {
            'host': 'https://{environment_name}api.tvlinc.com'.format(environment_name=environment_name),
            'php_host': 'https://{environment_name}ui.tvlinc.com'.format(environment_name=environment_name),
            'purple_rain_airline_queue': None,
            'purple_rain_transaction_queue': None,
        }
    print('API URL under test: ' +
          SUPPORTED_ENVIRONMENTS[environment_name]['host'])
    print('PHP URL under test: ' +
          SUPPORTED_ENVIRONMENTS[environment_name]['php_host'])

    if SUPPORTED_ENVIRONMENTS[environment_name]['purple_rain_airline_queue']:
        print('Purple Rain airline queue under test: ' +
              SUPPORTED_ENVIRONMENTS[environment_name]['purple_rain_airline_queue']['name'])
    else:
        print('Purple Rain airline queue under test: ' + 'N/A')

    if SUPPORTED_ENVIRONMENTS[environment_name]['purple_rain_transaction_queue']:
        print('Purple Rain transaction queue under test: ' +
              SUPPORTED_ENVIRONMENTS[environment_name]['purple_rain_transaction_queue']['name'])
    else:
        print('Purple Rain transaction queue under test: ' + 'N/A')

    if len(sys.argv) > 2 and sys.argv[2] == 'api':
        runner = unittest.TextTestRunner()
        runner.run(api_suite(environment_name, unittest))
    elif len(sys.argv) > 2 and sys.argv[2] == 'web':
        runner = unittest.TextTestRunner()
        runner.run(web_suite(environment_name, unittest))
    else:
        StormxSystemVerification.selected_environment_name = environment_name
        # TODO: remove hacky monkey patching
        TestAirlineAndPassengerAPI.selected_environment_name = environment_name
        # TODO: remove hacky monkey patching
        TestStormxUI.selected_environment_name = environment_name
        # TODO: remove hacky monkey patching
        TestPassengerPayAPI.selected_environment_name = environment_name
        # TODO: remove hacky monkey patching
        TestPortAllowance.selected_environment_name = environment_name
        # TODO: remove hacky monkey patching
        TestQuickRoomTransfer.selected_environment_name = environment_name
        TestHotelContracts.selected_environment_name = environment_name
        UserPasswordResetTestCase.selected_environment_name = environment_name
        TestTvlInternalAPI.selected_environment_name = environment_name
        TestSystemPorts.selected_environment_name = environment_name
        TestExpediaLinking.selected_environment_name = environment_name
        TestBlogMessages.selected_environment_name = environment_name
        AvailabilityOnPortTimezone.selected_environment_name = environment_name
        TestAvailability.selected_environment_name = environment_name
        TestHotelPassengerNotes.selected_environment_name = environment_name
        TestAdditionalContacts.selected_environment_name = environment_name
        TestReconcilliation.selected_environment_name = environment_name
        TestHMTRecon.selected_environment_name = environment_name
        TestRateCap.selected_environment_name = environment_name
        TestPassengerPay.selected_environment_name = environment_name
        TestPhpAmenities.selected_environment_name = environment_name
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
        TestApiShuttleTracker.selected_environment_name = environment_name
        TestHotelVoucherUnlock.selected_environment_name = environment_name
        TestMealVoucherActiveDateRange.selected_environment_name = environment_name
        TestPassengerApp.selected_environment_name = environment_name
        TestQrCodes.selected_environment_name = environment_name
        TestTaxes.selected_environment_name = environment_name
        TestHotelAllowances.selected_environment_name = environment_name
        TestTransportOnlyVoucher.selected_environment_name = environment_name
        # remove so that unittest.main() will see standard unit test parameters and not get confused by the environment parameter.
        del sys.argv[1]

        unittest.main()
