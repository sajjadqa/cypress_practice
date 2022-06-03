import requests

from stormx_verification_framework import StormxSystemVerification


class TestApiPing(StormxSystemVerification):
    """
    Verify `/api/v1/ping` endpoint behavior.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiPing, cls).setUpClass()

    def test_ping__airlines_have_access(self):
        """
        verify that our customers can at least authenticate and access 'ping' endpoint.
        """
        url = self._api_host + '/api/v1/ping'

        VALID_CUSTOMERS_TO_CHECK = [
            'American Airlines',
            'Delta Air Lines',
            'United Airlines',
            'United Airlines - Crew Rooms',
            'United Airlines - Employee Rooms',
            'Purple Rain Airlines',
            'British Airways',
            'WestJet',
            'Norwegian',
            'Air France',
            'Virgin Australia',
            'Spirit',
            'Air New Zealand International',
            'Vueling',
            'Air Canada',
            'Alaska Airlines',
            'Wizz Air',
            'Eurowings',
            'Frontier Airlines',
            'Qantas',
            'Azul Airlines',
            'Swoop Airlines',
            'Cebu Pacific',
            'Play',
            'Japan Airlines',
        ]
        for customer in VALID_CUSTOMERS_TO_CHECK:
            headers = self._generate_airline_headers(customer=customer)
            response = requests.get(url, headers=headers)
            self.assertEqual(response.status_code, 200, msg=repr(customer) + ' access failed.')
            # TODO: verify json.

    def test_ping__unknown_users_are_blocked(self):
        """
        verify that unknown users cannot access the system.
        """
        url = self._api_host + '/api/v1/ping'
        headers = self._generate_airline_headers(customer='INVALID_CREDENTIALS')
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 403)  # TODO: should be a 401 for an unknown user, not a 403, IMO.
