
import requests

from uuid import UUID

from stormx_verification_framework import (
    display_response,
    TEMPLATE_DATE,
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output,
    should_skip_local_test,
    uses_expedia,
)


class TestAirlineAndPassengerAPI(StormxSystemVerification):
    """
    Verify StormX Airline API and StormX Passenger API functionality.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestAirlineAndPassengerAPI, cls).setUpClass()

    def test_queue_demo(self):
        '''
        TODO: delete this test and replace with some real tests.

        NOTE: test is skipped if queues are not set up for the environment.

        assumption for test: no one else is running system tests against the same environment, and there is not a crazy amount of activity.
        it is possible that other messages could be in the queue from other people using the system.
        '''
        #messages = self.read_messages_from_customer_queue('purple_rain_airline_queue')
        messages = self.read_messages_from_customer_queue('purple_rain_transaction_queue')
        # print(messages)
        #self.purge_customer_queue('purple_rain_transaction_queue')


    def test_validate_stormx_internal_airline_id(self):
        """
        validate only airlines with api access can access stormx internal endpoints
        """
        self.maxDiff = None  # allow larger diffs of JSON.
        airline_id = '34'  # South African Airways
        stormx_headers = self._generate_tvl_stormx_headers()
        stormx_headers_bad = self._generate_tvl_stormx_headers_bad()
        passenger_url = self._api_host + '/api/v1/tvl/airline/' + airline_id + '/passenger/tester'
        pnr_url = self._api_host + '/api/v1/tvl/airline/' + airline_id + '/pnr'
        hotel_url = self._api_host + '/api/v1/tvl/airline/' + airline_id + '/hotels'

        resp = requests.get(url=passenger_url, headers=stormx_headers_bad)
        self.assertEqual(resp.status_code, 403)
        resp_json = resp.json()
        self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

        resp = requests.get(url=passenger_url, headers=stormx_headers)

        resp_json = resp.json()
        self.assertEqual(resp_json, {
            "data": None,
            "error": True,
            "meta": {
                "error_code": "AIRLINE_NOT_HMT_ENABLED",
                "error_description": "Airline is not HMT-enabled or airline does not exist.",
                "error_detail": [],
                "href": "http://api.stormx.test/api/v1/tvl/airline/34/passenger/tester",
                "message": "Not Found",
                "method": "GET",
                "status": 404
            }
        })
        self.assertEqual(resp.status_code, 404)

        resp = requests.get(url=pnr_url, headers=stormx_headers_bad)
        self.assertEqual(resp.status_code, 403)
        resp_json = resp.json()
        self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

        resp = requests.get(url=pnr_url, headers=stormx_headers)
        resp_json = resp.json()
        self.assertEqual(resp_json, {
            "data": None,
            "error": True,
            "meta": {
                "error_code": "AIRLINE_NOT_HMT_ENABLED",
                "error_description": "Airline is not HMT-enabled or airline does not exist.",
                "error_detail": [],
                "href": "http://api.stormx.test/api/v1/tvl/airline/34/pnr",
                "message": "Not Found",
                "method": "GET",
                "status": 404
            }
        })
        self.assertEqual(resp.status_code, 404)

        resp = requests.get(url=hotel_url, headers=stormx_headers_bad)
        self.assertEqual(resp.status_code, 403)
        resp_json = resp.json()
        self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

        resp = requests.post(url=hotel_url, headers=stormx_headers)

        resp_json = resp.json()
        # sort 'error_detail' to make comparison deterministic.
        resp_json['meta']['error_detail'] = sorted(resp_json['meta']['error_detail'], key=lambda item: (item['field'], item['message']))
        self.assertEqual(resp_json, {
            "data": None,
            "error": True,
            "meta": {
                "error_code": "AIRLINE_NOT_HMT_ENABLED",
                "error_description": "Airline is not HMT-enabled or airline does not exist.",
                "error_detail": [],
                "href": "http://api.stormx.test/api/v1/tvl/airline/34/hotels",
                "message": "Not Found",
                "method": "POST",
                "status": 404
            }
        })
        self.assertEqual(resp.status_code, 404)

    # TODO: add system test: visit text message offer, or simulate the most economical way.
    # TODO: add system test: elaborate set of tests combining query string parameters for hotel search.
    # TODO: add system test: elaborate set of tests combining query string parameters for pax app.
    # TODO: add system test: max rooms allowed for hotel booking endpoints (pax and airline).
    # TODO: add system test: notification system tests for embedded json (pax app test)
    # TODO: add system test: accommodation level statuses system tests for embedded json (pax app test)
    # TODO: add system test: visit offer link via text after sms_auth_key is created during notification process
    # TODO: add system test: cancel hotel after hotel has been unlocked and validate error message
    # TODO: add system_test: voucher_response where a pax has meal vouchers and another does not
    # TODO: notification and meal voucher sanitized fields with tests
    # TODO: update system tests to check for voucher status and voucher modified_date for book/decline/cancel
    # TODO: update system tests to check for meal_voucher.id UUID

    @uses_expedia
    def test_alaska_expedia_access(self):
        """
        validates Alaska Airlines can query for Expedia Inventory
        """
        customer = 'Alaska Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        hotel_resp = requests.get(url=hotel_url + '?room_count=1&port='+ port +'&provider=ean', headers=headers)
        self.assertEqual(hotel_resp.status_code, 200)
        hotel_json = hotel_resp.json()['data']
        self.assertGreater(len(hotel_json), 0, msg='no expedia hotels in ' + repr(port))

        for hotel in hotel_json:
            self.assertEqual(hotel['provider'], 'ean')

        passengers = self._create_2_passengers('Alaska Airlines', port_accommodation=port)
        for passenger in passengers:
            self.assertEqual(passenger['airline_id'], 261)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=1,
            hotel_id=hotel_json[0]['hotel_id']
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()['data']
        UUID(book_resp_json['voucher_id'], version=4)
        self.assertEqual(book_resp_json['hotel_voucher']['provider'], 'ean')

    def test_alaska_pax_app_no_premium_settings(self):
        """
        verifies Alaska Airlines has no premium settings configured
        """
        customer = 'Alaska Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'
        offer_hotel_url = self._api_host + '/api/v1/offer/hotels'

        # add inventory
        event_date = self._get_event_date('America/New_York')
        self.add_hotel_availability(97224, 261, event_date, ap_block_type=1, block_price='20.00', blocks=2, pay_type='0')
        self.add_hotel_availability(97228, 261, event_date, ap_block_type=1, block_price='30.00', blocks=2, pay_type='0')
        self.add_hotel_availability(85440, 261, event_date, ap_block_type=1, block_price='35.00', blocks=2, pay_type='0')
        self.add_hotel_availability(85441, 261, event_date, ap_block_type=1, block_price='25.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            port_accommodation='EWR'
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        self.assertEqual(passenger['airline_id'], 261)

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response = requests.get(offer_hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertEqual(len(hotel_response_json['data']), 4)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['airport_code'], 'EWR')

        self.assertEqual(hotel_response_json['data'][0]['premium'], False)
        self.assertEqual(hotel_response_json['data'][1]['premium'], False)
        self.assertEqual(hotel_response_json['data'][2]['premium'], True)

        payload = dict(
            context_ids=[passenger['context_id']],
            room_count=1,
            hotel_id='tvl-85440'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()['data']
        UUID(book_resp_json['voucher_id'], version=4)
        self.assertEqual(book_resp_json['hotel_voucher']['provider'], 'tvl')
