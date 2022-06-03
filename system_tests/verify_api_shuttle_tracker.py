import requests

from stormx_verification_framework import StormxSystemVerification

# The simulation has been set up so that CLT should have hotel inventory
# that has one hotel with shuttle tracker.
SHUTTLE_TRACKER_AIRPORT = 'CLT'
AIRLINE_WITH_SHUTTLE_TRACKER_ENABLED = 'Purple Rain Airlines'
AIRLINE_WITH_SHUTTLE_TRACKER_DISABLED = 'American Airlines'


class TestApiShuttleTracker(StormxSystemVerification):
    """
    Verify shuttle tracker behavior.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiShuttleTracker, cls).setUpClass()


    # TODO: enable these tests after new database snapshot is distilled.

    def test_shuttle_tracker_airline_api_enabled(self):
        """
        verify airline API presents `shuttle_tracker_url` when feature enabled for an airline.
        """

        customer = AIRLINE_WITH_SHUTTLE_TRACKER_ENABLED
        port = SHUTTLE_TRACKER_AIRPORT
        headers = self._generate_airline_headers(customer=customer)
        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)
        passenger_context_ids = [p['context_id'] for p in passengers]
        room_count = 1

        # verify shuttle_tracker_url is not available in hotel listings (for now)
        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)
        self.assertEqual(len(hotels), 1,
                         msg='was expecting exactly one hotel to be available in ' + port)
        hotel = hotels[0]
        self.assertNotIn('shuttle_tracker_url', hotel)  # TODO: provide some day.
        # self.assertTrue(hotel['shuttle_tracker_url'].startswith('https://'))

        # verify shuttle_tracker_url is available in the booking response
        booking_params = dict(
            provider='tvl',
        )
        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(hotel['hotel_id']),
            room_count=str(room_count),
        )
        booking_response_json = requests.post(self._api_host + '/api/v1/hotels', headers=headers,
                                              params=booking_params, json=booking_payload).json()
        self.assertIs(booking_response_json['error'], False)
        self.assertTrue(booking_response_json['data']['hotel_voucher']['shuttle_tracker_url'].startswith('http'))

        # verify shuttle_tracker_url is available in passenger full state
        url = self._api_host + '/api/v1/passenger/{context_id}/state'.format(context_id=passenger_context_ids[0])
        full_state_json = requests.get(url=url, headers=headers).json()
        self.assertTrue(full_state_json['data']['voucher']['hotel_voucher']['shuttle_tracker_url'].startswith('http'))

    def test_shuttle_tracker_airline_api_disabled(self):
        """
        verify airline API does not present `shuttle_tracker_url` when feature disabled for an airline.
        """

        customer = AIRLINE_WITH_SHUTTLE_TRACKER_DISABLED
        port = SHUTTLE_TRACKER_AIRPORT
        headers = self._generate_airline_headers(customer=customer)
        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)
        passenger_context_ids = [p['context_id'] for p in passengers]
        room_count = 1

        # verify shuttle_tracker_url is not available in hotel listings
        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)
        self.assertEqual(len(hotels), 1,
                         msg='was expecting exactly one hotel to be available in ' + port)
        hotel = hotels[0]
        self.assertNotIn('shuttle_tracker_url', hotel)

        # verify shuttle_tracker_url is not available in the booking response
        booking_params = dict(
            provider='tvl',
        )
        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(hotel['hotel_id']),
            room_count=str(room_count),
        )
        booking_response_json = requests.post(self._api_host + '/api/v1/hotels', headers=headers,
                                              params=booking_params, json=booking_payload).json()
        self.assertIs(booking_response_json['error'], False)
        self.assertIsNone(booking_response_json['data']['hotel_voucher']['shuttle_tracker_url'])

        # verify shuttle_tracker_url is not available in passenger full state
        url = self._api_host + '/api/v1/passenger/{context_id}/state'.format(context_id=passenger_context_ids[0])
        full_state_json = requests.get(url=url, headers=headers).json()
        self.assertIsNone(full_state_json['data']['voucher']['hotel_voucher']['shuttle_tracker_url'])

    def test_shuttle_tracker_passenger_api_enabled(self):
        """
        verify passenger API presents `shuttle_tracker_url` when it is enabled.
        """

        customer = AIRLINE_WITH_SHUTTLE_TRACKER_ENABLED
        port = SHUTTLE_TRACKER_AIRPORT
        headers = self._generate_airline_headers(customer=customer)
        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)
        passenger_context_ids = [p['context_id'] for p in passengers]
        passenger = passengers[0]

        room_count = 1
        port = passengers[0]['port_accommodation']

        # verify shuttle_tracker_url is not available in hotel listings (for now)
        hotels = self._get_passenger_hotel_offerings(passenger)
        self.assertEqual(len(hotels), 1,
                         msg='was expecting exactly one hotel to be available in ' + port)
        hotel = hotels[0]
        self.assertNotIn('shuttle_tracker_url', hotel)  # TODO: provide some day.

        # verify shuttle_tracker_url is available in the booking response
        booking_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
        )
        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(hotel['hotel_id']),
            room_count=str(room_count)
        )
        offer_url = self._api_host + '/api/v1/offer/hotels'
        booking_response_json = requests.post(offer_url, headers=headers, params=booking_params, json=booking_payload).json()
        self.assertIs(booking_response_json['error'], False)
        self.assertTrue(booking_response_json['data']['hotel_voucher']['shuttle_tracker_url'].startswith('http'))

    def test_shuttle_tracker_passenger_api_disabled(self):
        """
        verify passenger API does not present `shuttle_tracker_url` when it is disabled.
        """

        customer = AIRLINE_WITH_SHUTTLE_TRACKER_DISABLED
        port = SHUTTLE_TRACKER_AIRPORT
        headers = self._generate_airline_headers(customer=customer)
        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)
        passenger_context_ids = [p['context_id'] for p in passengers]
        passenger = passengers[0]

        room_count = 1
        port = passengers[0]['port_accommodation']

        # verify shuttle_tracker_url is not available in hotel listings (for now)
        hotels = self._get_passenger_hotel_offerings(passenger)
        self.assertEqual(len(hotels), 1,
                         msg='was expecting exactly one hotel to be available in ' + port)
        hotel = hotels[0]
        self.assertNotIn('shuttle_tracker_url', hotel)  # TODO: provide some day.

        # verify shuttle_tracker_url is not available in the booking response
        booking_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
        )
        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(hotel['hotel_id']),
            room_count=str(room_count)
        )
        offer_url = self._api_host + '/api/v1/offer/hotels'
        booking_response_json = requests.post(offer_url, headers=headers, params=booking_params, json=booking_payload).json()
        self.assertIs(booking_response_json['error'], False)
        self.assertIsNone(booking_response_json['data']['hotel_voucher']['shuttle_tracker_url'])
