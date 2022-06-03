
import copy
import json
import unittest

import requests

from StormxApp.tests.data_utilities import (
    generate_context_id,
    generate_pax_record_locator,
    generate_pax_record_locator_group,
    generate_flight_number,
    MOST_PASSENGERS_IN_LARGEST_AIRCRAFT
)

import pytz
import datetime
from uuid import UUID
from decimal import Decimal
from StormxApp.constants import StormxConstants


from stormx_verification_framework import (
    random_chunk,
    display_response,
    CUSTOMER_TOKENS,
    TEMPLATE_DATE,
    PASSENGER_TEMPLATE,
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output
)


class TestTvlInternalAPI(StormxSystemVerification):
    """
    Verify StormX internal API endpoints (i.e., /api/v1/tvl/....)
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestTvlInternalAPI, cls).setUpClass()

    @unittest.skip
    def test_DEMO(self):
        """
        verifies system will not allow the cancel service to run if passenger is in a declined state
        """

        url = self._api_host + '/api/v1/tvl/BLABLABLA'



        ROLE_POSSIBILITIES = [
            # 'Airline',
            # 'Transport',
            # 'Hotel',
            # 'Hotel Corporate',
            # 'Hotel Sales',
            # 'Hotel Finance',
            'IT Support',
            'Senior Management',
            'Supervisor',
            'Operator',
            'Read Only User'
            ''
        ]

        for role in ROLE_POSSIBILITIES:
            print(role)
            new_user_info = self.create_new_tva_user(role=role)
            print(new_user_info)
            self.assertEqual(new_user_info['CREATION_RESPONSE']['response']['message'], 'New user created successfully. ')
            print()
            print()
