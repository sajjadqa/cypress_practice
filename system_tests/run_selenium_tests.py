#! /usr/bin/env python3
"""

"""
import unittest
import sys
sys.path.insert(1, '/vagrant/Stormx')
sys.path.insert(1, '/vagrant')


from stormx_ui_test_suite import (
    stormx_ui_suite,
    TestRateCaps,
    TestQuickRoomTransfer,
    TestHotel,
    TestAirline,
    TestRoomCountReport,
    TestPortAllowance,
    TestQuickVoucher,
    TestLoginPage,
    TestSsoLogin,
    TestExpediaHotels
    )

from system_tests.stormx_verification_framework import (
    SUPPORTED_ENVIRONMENTS,
    StormxSystemVerification
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
            'php_host': 'https://{environment_name}ui.tvlinc.com'.format(environment_name=environment_name)
        }

    print('Stormx URL under test: ' +
          SUPPORTED_ENVIRONMENTS[environment_name]['php_host'])

    if len(sys.argv) > 3 and sys.argv[3] == 'all':
        runner = unittest.TextTestRunner()
        runner.run(stormx_ui_suite(environment_name, unittest))
    else:
        TestRateCaps.selected_environment_name = environment_name
        TestRoomCountReport.selected_environment_name = environment_name
        TestHotel.selected_environment_name = environment_name
        TestExpediaHotels.selected_environment_name = environment_name
        TestQuickRoomTransfer.selected_environment_name = environment_name
        TestPortAllowance.selected_environment_name = environment_name
        TestQuickVoucher.selected_environment_name = environment_name
        TestAirline.selected_environment_name = environment_name
        TestLoginPage.selected_environment_name = environment_name
        TestSsoLogin.selected_environment_name = environment_name
        # del sys.argv[3]
        del sys.argv[2]
        del sys.argv[1]

        unittest.main()
