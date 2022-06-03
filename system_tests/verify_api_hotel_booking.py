import datetime
import json
import requests
from uuid import UUID
from decimal import Decimal

from stormx_verification_framework import (
    StormxSystemVerification,
    display_response,
    log_error_system_tests_output,
    passenger_sanitized_fields,
    pretty_print_json,
    should_skip_local_test,
    uses_expedia,
)

hotel_sanitized_fields = ['rate', 'tax', 'provider']

confirmation_sanitized_fields = ['tax', 'total_amount', 'room_vouchers', 'id', 'fees', 'provider', 'hotel_message', 'hotel_allowances_voucher_total', 'taxes']


class TestApiHotelBooking(StormxSystemVerification):
    """
    Verify general hotel booking behavior.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBooking, cls).setUpClass()

    def _test_passenger_book_hotel(self, airport_iata_code, expected_provider):
        """
        verify that a passenger (the leader of a group) can book a hotel for his group,
        and that the other people in the group (the "followers") cannot book after the
        leader.

        In this scenario, we need at least two hotel offerings, so that the passengers
        can attempt to pick different hotels.
        """
        url = self._api_host + '/api/v1/offer/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_passenger_headers()

        passengers = self._create_2_passengers(customer=customer, port_accommodation=airport_iata_code)
        leader_of_passenger_group = passengers[1]
        follower_of_passenger_group = passengers[0]
        passenger_ids = [p['context_id'] for p in passengers]

        # both leader and follower check the offerings on their cell phones together----
        leader_hotel_offerings = self._get_passenger_hotel_offerings(leader_of_passenger_group)
        self.assertGreaterEqual(len(leader_hotel_offerings), 2)
        follower_hotel_offerings = self._get_passenger_hotel_offerings(follower_of_passenger_group)
        self.assertGreaterEqual(len(follower_hotel_offerings), 2)

        # leader books hotel ----
        leader_picked_hotel = leader_hotel_offerings[-1]  # the last hotel in the list
        leader_query_parameters = dict(
            ak1=leader_of_passenger_group['ak1'],
            ak2=leader_of_passenger_group['ak2'],
        )
        leader_booking_payload = dict(
            context_ids=passenger_ids,
            hotel_id=leader_picked_hotel['hotel_id'],
            room_count=1,
        )
        response = requests.post(url, headers=headers, params=leader_query_parameters, json=leader_booking_payload)
        if response.status_code != 200:
            self.fail('unexpected response: ' + str(response.status_code) + ' ' + response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertNotIn('room_vouchers', response_json['data']['hotel_voucher'])
        self.assertNotIn('total_amount', response_json['data']['hotel_voucher'])
        self.assertNotIn('tax', response_json['data']['hotel_voucher'])
        self.assertNotIn('id', response_json['data']['hotel_voucher'])
        self.assertNotIn('voucher_id', response_json['data'])
        self.assertNotIn('hotel_message', response_json['data']['hotel_voucher'])

        for passenger in response_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])

        # follower tries to book hotel ----
        follower_picked_hotel = leader_hotel_offerings[0]  # the first hotel in the list
        follower_query_parameters = dict(
            ak1=follower_of_passenger_group['ak1'],
            ak2=leader_of_passenger_group['ak2'],
            room_count=1
        )
        follower_booking_payload = dict(
            context_ids=passenger_ids.reverse(),
            hotel_id=follower_picked_hotel['hotel_id'],
            room_count=1,
        )
        response = requests.get(url, headers=headers, params=follower_query_parameters, json=follower_booking_payload)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 401, 'Unauthorized', '', '', [])

        url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)

        response1 = requests.get(url=url1, headers=headers).json()
        response2 = requests.get(url=url2, headers=headers).json()
        self.assertEqual(len(response1['data']['voucher']['meal_vouchers']), 2)
        self.assertEqual(len(response2['data']['voucher']['meal_vouchers']), 2)
        self.assertGreater(len(response1['data']['voucher']['hotel_voucher']), 0)
        self.assertGreater(len(response2['data']['voucher']['hotel_voucher']), 0)

        self.assertEqual(response1['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response1['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response1['data']['passenger']['transport_accommodation_status'])

        self.assertEqual(response2['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response2['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response2['data']['passenger']['transport_accommodation_status'])

        self.assertEqual(response1['data']['passenger']['port_accommodation'], airport_iata_code)
        self.assertEqual(response2['data']['passenger']['port_accommodation'], airport_iata_code)

        # this is just to verify that we are actually exercising the provider we intended.
        self.assertEqual(response1['data']['voucher']['hotel_voucher']['provider'], expected_provider)
        self.assertEqual(response2['data']['voucher']['hotel_voucher']['provider'], expected_provider)

    def test_passenger_book_hotel__tvl_inventory(self):
        # book in airports with TVL inventory.
        self._test_passenger_book_hotel(airport_iata_code='LAX', expected_provider='tvl')

    @uses_expedia
    def test_passenger_book_hotel__ean_inventory(self):
        # book in airports with no TVL inventory.
        airport_iata_code = self.select_airport_for_expedia_testing([
            ('TUS', 'America/Phoenix'),
            ('LGW', 'Europe/London')
        ])
        self._test_passenger_book_hotel(airport_iata_code=airport_iata_code,
                                        expected_provider='ean')

    def test_book_with_expired_hotel_id(self):
        """
        verifies system's response to attempting to book expired / unknown external hotel_ids.
        """
        expected_error_message = 'Passenger cannot cancel a meal-only voucher.'

        customer = 'Purple Rain Airlines'
        passengers = self._create_2_passengers(customer, hotel_accommodation=True)

        # attempt passenger booking ----
        headers = self._generate_passenger_headers()
        pax_hotel_url = self._api_host + '/api/v1/offer/hotels'
        leader_query_parameters = dict(
            ak1=passengers[0]['ak1'],
            ak2=passengers[0]['ak2'],
        )
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id='ean-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            room_count=1
        )
        booking_response = requests.post(pax_hotel_url, headers=headers, params=leader_query_parameters, json=booking_payload)
        self.assertEqual(booking_response.status_code, 404)
        booking_response_json = booking_response.json()
        self.assertEqual(booking_response_json['meta']['error_code'], 'HOTEL_OFFER_EXPIRED_OR_NOT_FOUND')
        self.assertEqual(booking_response_json['meta']['error_description'], 'Expired or invalid hotel offer. Please refresh your hotel inventory list and then try booking again.')

        # attempt agent booking ----
        headers = self._generate_airline_headers(customer)
        agent_hotel_url = self._api_host + '/api/v1/hotels'
        agent_booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id='ean-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            room_count=1
        )
        booking_response = requests.post(agent_hotel_url, headers=headers, json=agent_booking_payload)
        self.assertEqual(booking_response.status_code, 404)
        booking_response_json = booking_response.json()
        self.assertEqual(booking_response_json['meta']['error_code'], 'HOTEL_OFFER_EXPIRED_OR_NOT_FOUND')
        self.assertEqual(booking_response_json['meta']['error_description'], 'Expired or invalid hotel offer. Please refresh your hotel inventory list and then try booking again.')

    def test_passenger_book_hotel_no_meals(self):
        """
        verify passenger can book hotel via pax api with no meals
        """
        url = self._api_host + '/api/v1/offer/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_passenger_headers()

        passengers = self._create_2_passengers(customer=customer, meal_accommodation=False)
        leader_of_passenger_group = passengers[1]
        follower_of_passenger_group = passengers[0]
        passenger_ids = [p['context_id'] for p in passengers]

        # both leader and follower check the offerings on their cell phones together----
        leader_hotel_offerings = self._get_passenger_hotel_offerings(leader_of_passenger_group)
        self.assertGreaterEqual(len(leader_hotel_offerings), 2)
        follower_hotel_offerings = self._get_passenger_hotel_offerings(follower_of_passenger_group)
        self.assertGreaterEqual(len(follower_hotel_offerings), 2)

        # leader books hotel ----
        leader_picked_hotel = leader_hotel_offerings[-1]  # the last hotel in the list
        leader_query_parameters = dict(
            ak1=leader_of_passenger_group['ak1'],
            ak2=leader_of_passenger_group['ak2'],
        )
        leader_booking_payload = dict(
            context_ids=passenger_ids,
            hotel_id=leader_picked_hotel['hotel_id'],
            room_count=1,
        )
        response = requests.post(url, headers=headers, params=leader_query_parameters, json=leader_booking_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertNotIn('room_vouchers', response_json['data']['hotel_voucher'])
        self.assertNotIn('total_amount', response_json['data']['hotel_voucher'])
        self.assertNotIn('tax', response_json['data']['hotel_voucher'])
        self.assertNotIn('voucher_id', response_json['data'])

        for passenger in response_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

        # follower tries to book hotel ----
        follower_picked_hotel = leader_hotel_offerings[0]  # the first hotel in the list
        follower_query_parameters = dict(
            ak1=follower_of_passenger_group['ak1'],
            ak2=leader_of_passenger_group['ak2'],
            room_count=1
        )
        follower_booking_payload = dict(
            context_ids=passenger_ids.reverse(),
            hotel_id=follower_picked_hotel['hotel_id'],
            room_count=1,
        )
        response = requests.get(url, headers=headers, params=follower_query_parameters, json=follower_booking_payload)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 401, 'Unauthorized', '', '', [])

        url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)

        response1 = requests.get(url=url1, headers=headers).json()
        response2 = requests.get(url=url2, headers=headers).json()
        self.assertEqual(len(response1['data']['voucher']['meal_vouchers']), 0)
        self.assertEqual(len(response2['data']['voucher']['meal_vouchers']), 0)
        self.assertIsNotNone(response1['data']['voucher']['hotel_voucher'])
        self.assertIsNotNone(response2['data']['voucher']['hotel_voucher'])

        self.assertEqual(response1['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response1['data']['passenger']['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(response1['data']['passenger']['transport_accommodation_status'])

        self.assertEqual(response2['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response2['data']['passenger']['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(response2['data']['passenger']['transport_accommodation_status'])

    def test_airline_book_hotel(self):
        """
        verify that an airline can book a hotel for a passenger.
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK')
        passenger_context_ids = [p['context_id'] for p in passengers]

        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

        room_count = 1
        port = passengers[0]['port_accommodation']

        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)

        # verify every result has at least the requested number of rooms available.
        for hotel in hotels:
            self.assertGreaterEqual(hotel['available'], room_count)
            self.assertEqual('tvl', hotel['hotel_id'].split('-', 1)[0])
            self.assertEqual(hotel['provider'], 'tvl')
        self.assertGreaterEqual(len(hotels), 1)
        picked_hotel_id = hotels[0]['hotel_id']  # the first hotel.

        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(picked_hotel_id),
            room_count=str(room_count),
        )

        response = requests.post(url, headers=headers, json=booking_payload)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertIn('room_vouchers', response_json['data']['hotel_voucher'])
        self.assertIn('total_amount', response_json['data']['hotel_voucher'])
        self.assertIn('tax', response_json['data']['hotel_voucher'])
        self.assertIn('voucher_id', response_json['data'])
        self.assertIn('modified_date', response_json['data'])
        self.assertEqual(response_json['data']['status'], 'finalized')
        self.assertEqual('tvl', response_json['data']['hotel_voucher']['hotel_id'].split('-', 1)[0])
        self.assertEqual(response_json['data']['hotel_voucher']['provider'], 'tvl')
        self.assertIsNone(response_json['data']['hotel_voucher']['hotel_message'])
        self.assertEqual(response_json['data']['hotel_voucher']['hotel_allowances_voucher_total'], '0.00')

        for passenger in response_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertIsNone(passenger['declined_date'])
            self.assertIsNone(passenger['canceled_date'])

            self.assertGreater(len(passenger['meal_vouchers']), 0)
            for meal_voucher in passenger['meal_vouchers']:
                self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
                self.assertEqual(meal_voucher['billing_zip_code'], '60173')
                self.assertEqual(meal_voucher['provider'], 'tvl')

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response_json['data']['voucher_id'], headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        for passenger in voucher_resp_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertIsNone(passenger['declined_date'])
            self.assertIsNone(passenger['canceled_date'])

            self.assertGreater(len(passenger['meal_vouchers']), 0)
            for meal_voucher in passenger['meal_vouchers']:
                self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
                self.assertEqual(meal_voucher['billing_zip_code'], '60173')
                self.assertEqual(meal_voucher['provider'], 'tvl')

        hotel_voucher = voucher_resp_json['data']['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

        url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)

        response1 = requests.get(url=url1, headers=headers).json()
        response2 = requests.get(url=url2, headers=headers).json()

        self.assertEqual(len(response1['data']['voucher']['meal_vouchers']), 2)
        for meal_voucher in response1['data']['voucher']['meal_vouchers']:
            self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
            self.assertEqual(meal_voucher['billing_zip_code'], '60173')
            self.assertEqual(meal_voucher['provider'], 'tvl')

        self.assertEqual(len(response2['data']['voucher']['meal_vouchers']), 2)
        for meal_voucher in response2['data']['voucher']['meal_vouchers']:
            self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
            self.assertEqual(meal_voucher['billing_zip_code'], '60173')
            self.assertEqual(meal_voucher['provider'], 'tvl')

        self.assertGreater(len(response1['data']['voucher']['hotel_voucher']), 0)
        self.assertGreater(len(response2['data']['voucher']['hotel_voucher']), 0)
        self.assertEqual('tvl', response1['data']['voucher']['hotel_voucher']['hotel_id'].split('-', 1)[0])
        self.assertEqual('tvl', response2['data']['voucher']['hotel_voucher']['hotel_id'].split('-', 1)[0])
        self.assertEqual(response1['data']['voucher']['hotel_voucher']['provider'], 'tvl')
        self.assertEqual(response2['data']['voucher']['hotel_voucher']['provider'], 'tvl')

        self.assertEqual(response1['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response1['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response1['data']['passenger']['transport_accommodation_status'])

        self.assertEqual(response2['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response2['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response2['data']['passenger']['transport_accommodation_status'])

        self.assertIsNone(response1['data']['voucher']['hotel_voucher']['hotel_message'])
        self.assertIsNone(response2['data']['voucher']['hotel_voucher']['hotel_message'])

        for meal in response1['data']['voucher']['meal_vouchers']:
            UUID(meal['id'], version=4)
            self.assertEqual(meal['provider'], 'tvl')

        for meal in response2['data']['voucher']['meal_vouchers']:
            UUID(meal['id'], version=4)
            self.assertEqual(meal['provider'], 'tvl')

        self.assertEqual(response1['data']['voucher']['hotel_voucher']['hotel_allowances_voucher_total'], '0.00')
        self.assertEqual(response2['data']['voucher']['hotel_voucher']['hotel_allowances_voucher_total'], '0.00')

    def test_airline_book_hotel_no_meal_provider(self):
        """
        verify that an airline can book a hotel for a passenger and no meal provider is returned
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='PHX')
        passenger_context_ids = [p['context_id'] for p in passengers]

        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

        room_count = 1
        port = passengers[0]['port_accommodation']

        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)

        # verify every result has at least the requested number of rooms available.
        for hotel in hotels:
            self.assertGreaterEqual(hotel['available'], room_count)
            self.assertEqual('tvl', hotel['hotel_id'].split('-', 1)[0])
            self.assertEqual(hotel['provider'], 'tvl')
        self.assertGreaterEqual(len(hotels), 1)
        picked_hotel_id = hotels[0]['hotel_id']  # the first hotel.

        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(picked_hotel_id),
            room_count=str(room_count),
        )

        response = requests.post(url, headers=headers, json=booking_payload)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertIn('room_vouchers', response_json['data']['hotel_voucher'])
        self.assertIn('total_amount', response_json['data']['hotel_voucher'])
        self.assertIn('tax', response_json['data']['hotel_voucher'])
        self.assertIn('voucher_id', response_json['data'])
        self.assertIn('modified_date', response_json['data'])
        self.assertEqual(response_json['data']['status'], 'finalized')
        self.assertEqual('tvl', response_json['data']['hotel_voucher']['hotel_id'].split('-', 1)[0])
        self.assertEqual(response_json['data']['hotel_voucher']['provider'], 'tvl')
        self.assertIsNone(response_json['data']['hotel_voucher']['hotel_message'])
        self.assertEqual(response_json['data']['hotel_voucher']['hotel_allowances_voucher_total'], '0.00')

        for passenger in response_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertIsNone(passenger['declined_date'])
            self.assertIsNone(passenger['canceled_date'])

            self.assertGreater(len(passenger['meal_vouchers']), 0)
            for meal_voucher in passenger['meal_vouchers']:
                self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
                self.assertEqual(meal_voucher['billing_zip_code'], '60173')
                self.assertEqual(meal_voucher['provider'], 'tvl')

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response_json['data']['voucher_id'], headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        for passenger in voucher_resp_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertIsNone(passenger['declined_date'])
            self.assertIsNone(passenger['canceled_date'])

            self.assertGreater(len(passenger['meal_vouchers']), 0)
            for meal_voucher in passenger['meal_vouchers']:
                self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
                self.assertEqual(meal_voucher['billing_zip_code'], '60173')
                self.assertEqual(meal_voucher['provider'], 'tvl')

        url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)

        response1 = requests.get(url=url1, headers=headers).json()
        response2 = requests.get(url=url2, headers=headers).json()

        self.assertEqual(len(response1['data']['voucher']['meal_vouchers']), 2)
        for meal_voucher in response1['data']['voucher']['meal_vouchers']:
            self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
            self.assertEqual(meal_voucher['billing_zip_code'], '60173')
            self.assertEqual(meal_voucher['provider'], 'tvl')

        self.assertEqual(len(response2['data']['voucher']['meal_vouchers']), 2)
        for meal_voucher in response2['data']['voucher']['meal_vouchers']:
            self.assertEqual(meal_voucher['card_type'], 'MASTERCARD')
            self.assertEqual(meal_voucher['billing_zip_code'], '60173')
            self.assertEqual(meal_voucher['provider'], 'tvl')

        self.assertGreater(len(response1['data']['voucher']['hotel_voucher']), 0)
        self.assertGreater(len(response2['data']['voucher']['hotel_voucher']), 0)
        self.assertEqual('tvl', response1['data']['voucher']['hotel_voucher']['hotel_id'].split('-', 1)[0])
        self.assertEqual('tvl', response2['data']['voucher']['hotel_voucher']['hotel_id'].split('-', 1)[0])
        self.assertEqual(response1['data']['voucher']['hotel_voucher']['provider'], 'tvl')
        self.assertEqual(response2['data']['voucher']['hotel_voucher']['provider'], 'tvl')

        self.assertEqual(response1['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response1['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response1['data']['passenger']['transport_accommodation_status'])

        self.assertEqual(response2['data']['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(response2['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response2['data']['passenger']['transport_accommodation_status'])

        self.assertIsNone(response1['data']['voucher']['hotel_voucher']['hotel_message'])
        self.assertIsNone(response2['data']['voucher']['hotel_voucher']['hotel_message'])

        for meal in response1['data']['voucher']['meal_vouchers']:
            UUID(meal['id'], version=4)
            self.assertEqual(meal['provider'], 'tvl')

        for meal in response2['data']['voucher']['meal_vouchers']:
            UUID(meal['id'], version=4)
            self.assertEqual(meal['provider'], 'tvl')

        self.assertEqual(response1['data']['voucher']['hotel_voucher']['hotel_allowances_voucher_total'], '0.00')
        self.assertEqual(response2['data']['voucher']['hotel_voucher']['hotel_allowances_voucher_total'], '0.00')

        hotel_voucher = response1['data']['voucher']['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

        hotel_voucher = response2['data']['voucher']['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

    def test_airline_book_tvl_with_hotel_message(self):
        """
        verify that an airline can book a hotel with tvl inventory
        with a hotel_message
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        expected_hotel_messages = ['wake up call at 7:00 AM please', '', None]
        for expected_hotel_message in expected_hotel_messages:
            passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK')
            passenger_context_ids = [p['context_id'] for p in passengers]

            room_count = 1
            port = passengers[0]['port_accommodation']

            hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)
            picked_hotel_id = hotels[0]['hotel_id']

            booking_payload = dict(
                context_ids=passenger_context_ids,
                hotel_id=str(picked_hotel_id),
                room_count=str(room_count),
                hotel_message=expected_hotel_message
            )

            response = requests.post(url, headers=headers, json=booking_payload)
            if response.status_code != 200:
                display_response(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.reason, 'OK')
            response_json = response.json()
            self.assertIs(response_json['error'], False)
            self.assertEqual(response_json['data']['hotel_voucher']['provider'], 'tvl')
            self.assertEqual(response_json['data']['hotel_voucher']['hotel_message'], expected_hotel_message)
            UUID(response_json['data']['voucher_id'], version=4)

            voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response_json['data']['voucher_id'], headers=headers)
            self.assertEqual(voucher_resp.status_code, 200)
            voucher_resp_json = voucher_resp.json()
            self.assertIs(voucher_resp_json['error'], False)
            self.assertEqual(voucher_resp_json['data']['hotel_voucher']['provider'], 'tvl')
            self.assertEqual(voucher_resp_json['data']['hotel_voucher']['hotel_message'], expected_hotel_message)
            UUID(voucher_resp_json['data']['voucher_id'], version=4)

            url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
            url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
            headers = self._generate_airline_headers(customer=customer)

            response1 = requests.get(url=url1, headers=headers).json()
            response2 = requests.get(url=url2, headers=headers).json()

            self.assertEqual(response1['data']['voucher']['hotel_voucher']['provider'], 'tvl')
            self.assertEqual(response2['data']['voucher']['hotel_voucher']['provider'], 'tvl')
            self.assertEqual(response1['data']['voucher']['hotel_voucher']['hotel_message'], expected_hotel_message)
            self.assertEqual(response2['data']['voucher']['hotel_voucher']['hotel_message'], expected_hotel_message)

    @uses_expedia
    def test_airline_book_ean_with_hotel_message(self):
        """
        verify that an airline can book a hotel with ean inventory
        with a hotel_message
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        port = self.select_airport_for_expedia_testing([
            ('JFK', 'America/New_York'),
            ('LGW', 'Europe/London')
        ])

        expected_hotel_messages = ['wake up call at 7:00 AM please', '', None]
        for expected_hotel_message in expected_hotel_messages:
            passengers = self._create_2_passengers(customer=customer, port_accommodation=port)
            passenger_context_ids = [p['context_id'] for p in passengers]

            room_count = 1

            hotels = requests.get(url=url + '?port='+ port +'&room_count=1&provider=ean', headers=headers).json()

            self.assertGreater(len(hotels['data']), 0)
            picked_hotel_id = hotels['data'][0]['hotel_id']

            booking_payload = dict(
                context_ids=passenger_context_ids,
                hotel_id=str(picked_hotel_id),
                room_count=str(room_count),
                hotel_message=expected_hotel_message
            )

            response = requests.post(url, headers=headers, json=booking_payload)
            if response.status_code != 200:
                display_response(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.reason, 'OK')
            response_json = response.json()
            self.assertIs(response_json['error'], False)
            self.assertEqual(response_json['data']['hotel_voucher']['provider'], 'ean')
            self.assertEqual(response_json['data']['hotel_voucher']['hotel_message'], expected_hotel_message)
            UUID(response_json['data']['voucher_id'], version=4)

            voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response_json['data']['voucher_id'], headers=headers)
            self.assertEqual(voucher_resp.status_code, 200)
            voucher_resp_json = voucher_resp.json()
            self.assertIs(voucher_resp_json['error'], False)
            self.assertEqual(voucher_resp_json['data']['hotel_voucher']['provider'], 'ean')
            self.assertEqual(voucher_resp_json['data']['hotel_voucher']['hotel_message'], expected_hotel_message)
            UUID(voucher_resp_json['data']['voucher_id'], version=4)

            url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
            url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
            headers = self._generate_airline_headers(customer=customer)

            response1 = requests.get(url=url1, headers=headers).json()
            response2 = requests.get(url=url2, headers=headers).json()

            self.assertEqual(response1['data']['voucher']['hotel_voucher']['provider'], 'ean')
            self.assertEqual(response2['data']['voucher']['hotel_voucher']['provider'], 'ean')
            self.assertEqual(response1['data']['voucher']['hotel_voucher']['hotel_message'], expected_hotel_message)
            self.assertEqual(response2['data']['voucher']['hotel_voucher']['hotel_message'], expected_hotel_message)

    def test_passenger_book_tvl_with_hotel_message(self):
        """
        verify that an airline can book a hotel with tvl inventory
        with a hotel_message and validate hotel_message is null
        hotel_message is not allowed on passenger app
        """
        hotel_message = 'wake up call at 7:00 AM please'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK')
        passenger_context_ids = [p['context_id'] for p in passengers]

        room_count = 1
        port = passengers[0]['port_accommodation']

        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)
        picked_hotel_id = hotels[0]['hotel_id']

        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(picked_hotel_id),
            room_count=str(room_count),
            hotel_message=hotel_message
        )

        offer_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']

        response = requests.post(offer_url, headers=headers, json=booking_payload)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['data']['hotel_voucher']['hotel_id'], picked_hotel_id)
        self.assertNotIn('hotel_message', response_json['data']['hotel_voucher'])

        url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)

        response1 = requests.get(url=url1, headers=headers).json()
        response2 = requests.get(url=url2, headers=headers).json()

        self.assertEqual(response1['data']['voucher']['hotel_voucher']['provider'], 'tvl')
        self.assertEqual(response2['data']['voucher']['hotel_voucher']['provider'], 'tvl')
        self.assertIsNone(response1['data']['voucher']['hotel_voucher']['hotel_message'])
        self.assertIsNone(response2['data']['voucher']['hotel_voucher']['hotel_message'])

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response1['data']['passenger']['voucher_id'], headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        self.assertIs(voucher_resp_json['error'], False)
        self.assertEqual(voucher_resp_json['data']['hotel_voucher']['provider'], 'tvl')
        self.assertIsNone(voucher_resp_json['data']['hotel_voucher']['hotel_message'])
        UUID(voucher_resp_json['data']['voucher_id'], version=4)

    def test_validate_hotel_message_length(self):
        """
        validate hotel_message length cannot exceed 128
        """
        hotel_message = 'a' * 129

        url = self._api_host + '/api/v1/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK')
        passenger_context_ids = [p['context_id'] for p in passengers]

        room_count = 1
        port = passengers[0]['port_accommodation']

        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)
        picked_hotel_id = hotels[0]['hotel_id']

        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(picked_hotel_id),
            room_count=str(room_count),
            hotel_message=hotel_message
        )

        response = requests.post(url, headers=headers, json=booking_payload)
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.',
                                     [{'field': 'hotel_message', 'message': 'Ensure this field has no more than 128 characters.'}])

    @uses_expedia
    def test_airline_book_ean_with_null_hotel_message(self):
        """
        verify that an airline can book a hotel with ean inventory
        without sending a hotel_message
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        port = self.select_airport_for_expedia_testing([
            ('JFK', 'America/New_York'),
            ('LGW', 'Europe/London')
        ])

        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)
        passenger_context_ids = [p['context_id'] for p in passengers]

        room_count = 1

        hotels = requests.get(url=url + '?port=' + port + '&room_count=1&provider=ean', headers=headers).json()
        self.assertGreater(len(hotels['data']), 0, msg='no expedia in port ' + repr(port))

        picked_hotel_id = hotels['data'][0]['hotel_id']

        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(picked_hotel_id),
            room_count=str(room_count)
        )

        response = requests.post(url, headers=headers, json=booking_payload)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['data']['hotel_voucher']['provider'], 'ean')
        self.assertIsNone(response_json['data']['hotel_voucher']['hotel_message'])
        UUID(response_json['data']['voucher_id'], version=4)

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response_json['data']['voucher_id'], headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        self.assertIs(voucher_resp_json['error'], False)
        self.assertEqual(voucher_resp_json['data']['hotel_voucher']['provider'], 'ean')
        self.assertIsNone(voucher_resp_json['data']['hotel_voucher']['hotel_message'])
        UUID(voucher_resp_json['data']['voucher_id'], version=4)

        url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)

        response1 = requests.get(url=url1, headers=headers).json()
        response2 = requests.get(url=url2, headers=headers).json()

        self.assertEqual(response1['data']['voucher']['hotel_voucher']['provider'], 'ean')
        self.assertEqual(response2['data']['voucher']['hotel_voucher']['provider'], 'ean')
        self.assertIsNone(response1['data']['voucher']['hotel_voucher']['hotel_message'])
        self.assertIsNone(response2['data']['voucher']['hotel_voucher']['hotel_message'])

    def test_open_offer_link_then_agent_book(self):
        """
        validate offer_opened_date is not null before an agent booking
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK')
        passenger_context_ids = [p['context_id'] for p in passengers]
        room_count = 1
        port = passengers[0]['port_accommodation']

        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)
        picked_hotel_id = hotels[0]['hotel_id']  # the first hotel.

        booking_payload = dict(
            context_ids=passenger_context_ids,
            hotel_id=str(picked_hotel_id),
            room_count=str(room_count),
        )

        # visit offer link
        resp = requests.get(url=passengers[0]['offer_url'])
        embedded_json = self._get_landing_page_embedded_json(resp)
        expected_offer_opened_date = embedded_json['passenger']['offer_opened_date']

        response = requests.post(url, headers=headers, json=booking_payload)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('voucher_id', response_json['data'])
        self.assertEqual(response_json['data']['status'], 'finalized')

        validate_offer_opened_date1 = False
        validate_offer_opened_date2 = False
        for passenger in response_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)

            if passenger['context_id'] == passengers[0]['context_id']:
                self.assertEqual(expected_offer_opened_date, passenger['offer_opened_date'])
                validate_offer_opened_date1 = True
            else:
                self.assertIsNone(passenger['offer_opened_date'])
                validate_offer_opened_date2 = True

            self.assertIsNone(passenger['declined_date'])
            self.assertIsNone(passenger['canceled_date'])
        self.assertTrue(validate_offer_opened_date1)
        self.assertTrue(validate_offer_opened_date2)

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response_json['data']['voucher_id'], headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        self.assertIn('voucher_id', voucher_resp_json['data'])
        self.assertEqual(voucher_resp_json['data']['status'], 'finalized')

        validate_offer_opened_date1 = False
        validate_offer_opened_date2 = False
        for passenger in voucher_resp_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)

            if passenger['context_id'] == passengers[0]['context_id']:
                self.assertEqual(expected_offer_opened_date, passenger['offer_opened_date'])
                validate_offer_opened_date1 = True
            else:
                self.assertIsNone(passenger['offer_opened_date'])
                validate_offer_opened_date2 = True

            self.assertIsNone(passenger['declined_date'])
            self.assertIsNone(passenger['canceled_date'])
        self.assertTrue(validate_offer_opened_date1)
        self.assertTrue(validate_offer_opened_date2)

    def test_voucher_response(self):
        delta_customer = 'Delta Air Lines'
        aa_customer = 'American Airlines'

        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'

        delta_headers = self._generate_airline_headers(delta_customer)
        aa_headers = self._generate_airline_headers(aa_customer)

        delta_passenger_payload = self._generate_n_passenger_payload(1)
        delta_passenger_payload[0].update({
            'hotel_accommodation': False
        })
        aa_passenger_payload = self._generate_n_passenger_payload(1)

        delta_import_response = requests.post(url=offer_url, headers=delta_headers, json=delta_passenger_payload)
        self.assertEqual(delta_import_response.status_code, 201)
        delta_import_response_json = delta_import_response.json()

        aa_import_response = requests.post(url=offer_url, headers=aa_headers, json=aa_passenger_payload)
        self.assertEqual(aa_import_response.status_code, 201)
        aa_import_response_json = aa_import_response.json()

        delta_passenger = delta_import_response_json['data'][0]
        aa_passenger = aa_import_response_json['data'][0]

        hotel_offerings = self._get_passenger_hotel_offerings(aa_passenger)
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[aa_passenger['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=aa_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        delta_voucher_url = self._api_host + '/api/v1/voucher/' + str(delta_passenger['voucher_id'])
        aa_voucher_url = self._api_host + '/api/v1/voucher/' + str(booking_response.json()['data']['voucher_id'])

        delta_voucher_resp = requests.get(url=delta_voucher_url, headers=delta_headers)
        delta_voucher_resp_json = delta_voucher_resp.json()
        self.assertEqual(delta_voucher_resp_json['error'], False)
        self.assertEqual(delta_voucher_resp.status_code, 200)
        self.assertEqual(delta_voucher_resp_json['data']['voucher_id'], delta_passenger['voucher_id'])

        aa_voucher_resp = requests.get(url=aa_voucher_url, headers=aa_headers)
        aa_voucher_resp_json = aa_voucher_resp.json()
        self.assertEqual(aa_voucher_resp_json['error'], False)
        self.assertEqual(aa_voucher_resp.status_code, 200)
        self.assertEqual(aa_voucher_resp_json['data']['voucher_id'], booking_response.json()['data']['voucher_id'])

        # multi tenant functionality tests
        aa_delta_resp = requests.get(url=delta_voucher_url, headers=aa_headers)
        delta_aa_resp = requests.get(url=aa_voucher_url, headers=delta_headers)
        self.assertEqual(aa_delta_resp.status_code, 404)
        self.assertEqual(delta_aa_resp.status_code, 404)

    def test_passenger_offer__hotel_and_meal_accept(self):
        """
        verify passenger landing page has correct information embedded in it for the scenario:
          * airline offers hotel AND meal. Passenger accepts the hotel. Passenger revisits the offer link again after that.

        Note: important scenario. regression for this scenario has happened at least twice.

        This test focuses mostly on confirmation payloads in their various places.
        """

        customer = 'Delta Air Lines'
        headers = self._generate_passenger_headers()

        # airline generates offer ----
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=True, meal_accommodation=True)
        passenger = passengers[0]
        other_passenger = passengers[1]
        passenger_offer_url = passenger['offer_url']

        # passenger visits offer link ----
        response = requests.get(passenger_offer_url, headers=headers)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNone(embedded_json['confirmation'])

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

        context_ids = [p['context_id'] for p in embedded_json['other_passengers']]
        context_ids.insert(0, embedded_json['passenger']['context_id'])

        # passenger looks at hotel offerings ----
        desired_room_count = 2
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        # passenger books hotel ----
        picked_hotel = hotel_offerings[0]
        booking_response_data = self._passenger_book_hotel(passenger, picked_hotel, context_ids, room_count=desired_room_count)
        self.assertEqual(booking_response_data['hotel_voucher']['hotel_id'], picked_hotel['hotel_id'])
        self.assertEqual(booking_response_data['passengers'][0]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(booking_response_data['passengers'][0]['meal_vouchers'][1]['amount'], '10.99')
        self.assertEqual(booking_response_data['passengers'][1]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(booking_response_data['passengers'][1]['meal_vouchers'][1]['amount'], '10.99')
        for p in booking_response_data['passengers']:
            for meal_voucher in p['meal_vouchers']:
                self.assertEqual(meal_voucher['currency_code'], 'USD')
                self.assertEqual(len(meal_voucher['card_number']), 16)
                self.assertGreaterEqual(len(meal_voucher['cvc2']), 3)
                self.assertEqual(len(meal_voucher['expiration']), 7)
                qr_code_image_response = requests.get(meal_voucher['qr_code_url'], headers=headers)
                self.assertEqual(qr_code_image_response.status_code, 200)

        # passenger visits offer link again ----
        response = requests.get(passenger_offer_url, headers=headers)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNotNone(embedded_json['confirmation'])
        self.assertEqual(embedded_json['confirmation']['hotel_voucher']['hotel_id'], picked_hotel['hotel_id'])
        self.assertEqual(embedded_json['confirmation']['hotel_voucher']['rooms_booked'], desired_room_count)
        self.assertEqual(embedded_json['confirmation']['passengers'][0]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(embedded_json['confirmation']['passengers'][0]['meal_vouchers'][1]['amount'], '10.99')
        self.assertEqual(embedded_json['confirmation']['passengers'][1]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(embedded_json['confirmation']['passengers'][1]['meal_vouchers'][1]['amount'], '10.99')
        for p in embedded_json['confirmation']['passengers']:
            for meal_voucher in p['meal_vouchers']:
                self.assertEqual(meal_voucher['currency_code'], 'USD')
                self.assertEqual(len(meal_voucher['card_number']), 16)
                self.assertGreaterEqual(len(meal_voucher['cvc2']), 3)
                self.assertEqual(len(meal_voucher['expiration']), 7)
                qr_code_image_response = requests.get(meal_voucher['qr_code_url'], headers=headers)
                self.assertEqual(qr_code_image_response.status_code, 200)

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

        self.assertNotIn('voucher_id', embedded_json['confirmation'])
        for field in confirmation_sanitized_fields:
            self.assertNotIn(field, embedded_json['confirmation']['hotel_voucher'])

        # other passenger visits their own offer link ----
        other_passenger = passengers[1]
        other_passenger_offer_url = other_passenger['offer_url']
        response = requests.get(other_passenger_offer_url, headers=headers)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNotNone(embedded_json['confirmation'])

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

        self.assertNotIn('voucher_id', embedded_json['confirmation'])
        for field in confirmation_sanitized_fields:
            self.assertNotIn(field, embedded_json['confirmation']['hotel_voucher'])

    def test_passenger_offer__hotel_and_meal_decline(self):
        """
        verify passenger landing page has correct information embedded in it for the scenario:
          * airline offers hotel AND meal. Passenger declines the hotel. Passenger revisits the offer link again after that.

        Note: important scenario. regression for this scenario has happened at least once.

        This test focuses mostly on confirmation payloads in their various places.
        """
        customer = 'Delta Air Lines'
        headers = self._generate_passenger_headers()

        # airline generates offer ----
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=True, meal_accommodation=True)
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']

        # passenger visits offer link ----
        response = requests.get(passenger_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNone(embedded_json['confirmation'])
        context_ids = [p['context_id'] for p in embedded_json['other_passengers']]
        context_ids.insert(0, embedded_json['passenger']['context_id'])

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

        # passenger declines hotel offer ----
        declining_response_data = self._passenger_decline_offer(passenger)
        self.assertIsNone(declining_response_data['hotel_voucher'])
        self.assertEqual(declining_response_data['passengers'][0]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(declining_response_data['passengers'][0]['meal_vouchers'][1]['amount'], '10.99')
        self.assertEqual(declining_response_data['passengers'][1]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(declining_response_data['passengers'][1]['meal_vouchers'][1]['amount'], '10.99')
        for p in declining_response_data['passengers']:
            for meal_voucher in p['meal_vouchers']:
                self.assertEqual(meal_voucher['currency_code'], 'USD')
                self.assertEqual(len(meal_voucher['card_number']), 16)
                self.assertGreaterEqual(len(meal_voucher['cvc2']), 3)
                self.assertEqual(len(meal_voucher['expiration']), 7)
                qr_code_image_response = requests.get(meal_voucher['qr_code_url'], headers=headers)
                self.assertEqual(qr_code_image_response.status_code, 200)

        # passenger visits offer link again ----
        response = requests.get(passenger_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNotNone(embedded_json['confirmation'])
        self.assertIsNone(embedded_json['confirmation']['hotel_voucher'])
        self.assertEqual(embedded_json['confirmation']['passengers'][0]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(embedded_json['confirmation']['passengers'][0]['meal_vouchers'][1]['amount'], '10.99')
        self.assertEqual(embedded_json['confirmation']['passengers'][1]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(embedded_json['confirmation']['passengers'][1]['meal_vouchers'][1]['amount'], '10.99')
        for p in embedded_json['confirmation']['passengers']:
            for meal_voucher in p['meal_vouchers']:
                self.assertEqual(meal_voucher['currency_code'], 'USD')
                self.assertEqual(len(meal_voucher['card_number']), 16)
                self.assertGreaterEqual(len(meal_voucher['cvc2']), 3)
                self.assertEqual(len(meal_voucher['expiration']), 7)

        self.assertNotIn('voucher_id', embedded_json['confirmation'])
        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

    def test_passenger_offer__hotel_only_accept(self):
        """
        verify passenger landing page has correct information embedded in it for the scenario:
          * airline offers hotel only. Passenger accepts the hotel. Passenger revisits the offer link again after that.

        This test focuses mostly on confirmation payloads in their various places.
        """

        customer = 'Delta Air Lines'
        headers = self._generate_passenger_headers()

        # airline generates offer ----
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=True, meal_accommodation=False, meals=[])
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']

        # passenger visits offer link ----
        response = requests.get(passenger_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNone(embedded_json['confirmation'])
        context_ids = [p['context_id'] for p in embedded_json['other_passengers']]
        context_ids.insert(0, embedded_json['passenger']['context_id'])

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

        # passenger looks at hotel offerings ----
        desired_room_count = 2
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        # passenger books hotel ----
        picked_hotel = hotel_offerings[0]
        booking_response_data = self._passenger_book_hotel(passenger, picked_hotel, context_ids,
                                                           room_count=desired_room_count)
        self.assertEqual(booking_response_data['hotel_voucher']['hotel_id'], picked_hotel['hotel_id'])
        for p in booking_response_data['passengers']:
            self.assertEqual(p['meal_vouchers'], [])

        # passenger visits offer link again ----
        response = requests.get(passenger_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertEqual(embedded_json['confirmation']['hotel_voucher']['hotel_id'], picked_hotel['hotel_id'])
        self.assertEqual(embedded_json['confirmation']['hotel_voucher']['rooms_booked'], desired_room_count)
        for p in embedded_json['confirmation']['passengers']:
            self.assertEqual(p['meal_vouchers'], [])

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

        self.assertNotIn('voucher_id', embedded_json['confirmation'])
        for field in confirmation_sanitized_fields:
            self.assertNotIn(field, embedded_json['confirmation']['hotel_voucher'])

    def test_handicap_can_book_through_pax_app_roh_temp(self):
        """
        verify handicap can book through pax app temporarily using ROH inventory
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            handicap=True,
            notify=True
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'
        pax_headers = self._generate_passenger_headers()

        hotel_availability = self._get_passenger_hotel_offerings(passenger)
        picked_hotel = hotel_availability[0]['hotel_id']

        booking_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2']
        )
        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=picked_hotel,
            room_count=1,
        )
        response = requests.post(hotel_url, headers=pax_headers, params=booking_query_parameters, json=booking_payload)
        self.assertEqual(response.status_code, 200)
        booking_response_json = response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(len(booking_response_json['data']['passengers']), 1)
        self.assertEqual(booking_response_json['data']['passengers'][0]['context_id'], passenger['context_id'])
        self.assertEqual(booking_response_json['data']['passengers'][0]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(booking_response_json['data']['status'], 'finalized')

    def test_handicap_and_non_handicap_same_pnr_can_book_through_pax_app_roh_temp(self):
        """
        verify handicap and non handicap can book through pax app temporarily using ROH inventory on same PNR
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            handicap=True,
            notify=True
        ))
        passenger_payload[1].update(dict(
            pax_record_locator=passenger_payload[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload[0]['pax_record_locator_group']
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        if response_json['data'][0]['context_id'] == passenger_payload[0]['context_id']:
            passenger = response_json['data'][0]
            passenger2 = response_json['data'][1]
        else:
            passenger = response_json['data'][1]
            passenger2 = response_json['data'][0]

        self.assertEqual(passenger['handicap'], True)
        self.assertEqual(passenger2['handicap'], False)

        hotel_url = self._api_host + '/api/v1/offer/hotels'
        pax_headers = self._generate_passenger_headers()

        hotel_availability = self._get_passenger_hotel_offerings(passenger)
        picked_hotel = hotel_availability[0]['hotel_id']

        booking_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2']
        )
        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=picked_hotel,
            room_count=1,
        )
        response = requests.post(hotel_url, headers=pax_headers, params=booking_query_parameters, json=booking_payload)
        self.assertEqual(response.status_code, 200)
        booking_response_json = response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(len(booking_response_json['data']['passengers']), 2)
        self.assertEqual(booking_response_json['data']['passengers'][0]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(booking_response_json['data']['passengers'][1]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(booking_response_json['data']['status'], 'finalized')

        booked_pax_1 = False
        booked_pax_2 = False
        for pax in booking_response_json['data']['passengers']:
            if pax['context_id'] == passenger['context_id']:
                booked_pax_1 = True
            else:
                self.assertEqual(pax['context_id'], passenger2['context_id'])
                booked_pax_2 = True

        self.assertTrue(booked_pax_1)
        self.assertTrue(booked_pax_2)

    def test_at_least_1_handicap_pax_forces_handicap_booking_airline_api(self):
        """
        verify system is checking for valid handicap booking scenarios
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        airline_client = self.get_airline_api_client(customer)
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            handicap=True
        ))

        passengers = airline_client.import_passengers(passengers=passenger_payload)
        passenger = passengers[0]
        passenger2 = passengers[1]

        room_count = 2
        hotels = airline_client.get_hotels(handicap=True, room_count=room_count, port='LAX')
        self.assertGreater(len(hotels), 0, msg='no handicapped hotel listings.')

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotels[0]['hotel_id'],
            room_count=1
        )

        voucher = airline_client.book_hotel(**booking_payload)
        UUID(voucher['voucher_id'], version=4)

    def test_handicap_booking(self):
        """
        verify system can perform a handicap booking via Airline API
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            handicap=True,
            notify=False,
            port_accommodation='ORD'
        ))

        passenger_payload[1].update(dict(
            port_accommodation='ORD'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        passenger2 = response_json['data'][1]

        hotel_url = self._api_host + '/api/v1/hotels?handicap=true&room_count=1&port=ORD'
        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_response_json['data'][0]['hotel_id'],
            room_count=1
        )

        booking_url = self._api_host + '/api/v1/hotels'

        booking_response = requests.post(booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        UUID(booking_response_json['data']['voucher_id'], version=4)

    def test_multi_night_booking_2_nights(self):
        """
        validate multi night booking for a 2 night stay
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 2
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=JFK&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=2)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk,
            number_of_nights=number_of_nights
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

        hotel_voucher = voucher['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

    def test_multi_night_booking_insufficient_rooms_day_1(self):
        """
        validate multi night booking for a 2 night stay with 5 rooms and 11 pax
        should fail if day one does not have sufficient enough inventory
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_sna = 'tvl-87489'
        event_date_jfk = self._get_event_date('America/Los_Angeles')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_sna.split('-')[1], 294, event_date_jfk, ap_block_type=1,
                                    block_price='100.99', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_sna.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1,
                                    block_price='100.99', blocks=6, pay_type='0')

        # setup some variables
        room_count = 5
        number_of_nights = 2

        # # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=SNA&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertNotIn(hotel_id_sna, hotel_ids)

        # create passengers with 2 nights
        # passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=2)
        passengers_payload = self._generate_n_passenger_payload(11)
        for passenger in passengers_payload:
            passenger['port_accommodation'] = 'SNA'
            passenger['number_of_nights'] = 2
        passengers = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload).json()['data']

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_sna,
            number_of_nights=number_of_nights
        )

        # book multi night stay and validate it fails
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 400)
        self._validate_error_message(hotel_booking_resp.json(), 400, 'Bad Request', 'INSUFFICIENT_INVENTORY',
                                     'Not enough inventory found for Hilton Irvine/Orange County Airport hotel', [])

    def test_multi_night_booking_2_nights_different_pnr_groups(self):
        """
        validate multi night booking for a 2 night stay for passengers on different PNR groups
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 2
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=JFK&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=2)
        passengers2 = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=2)
        self.assertNotEqual(passengers[0]['pax_record_locator_group'], passengers2[0]['pax_record_locator_group'])

        # setup booking payload
        booking_payload = dict(
            context_ids=[passengers[0]['context_id'], passengers2[0]['context_id']],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

    def test_multi_night_booking_2_nights_different_pnr_groups_override_number_of_nights(self):
        """
        validate multi night booking for a 2 night stay for passengers on different PNR groups
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 2
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=JFK&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=2)
        passengers2 = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=1)
        self.assertNotEqual(passengers[0]['pax_record_locator_group'], passengers2[0]['pax_record_locator_group'])

        # setup booking payload
        booking_payload = dict(
            context_ids=[passengers[0]['context_id'], passengers2[0]['context_id']],
            room_count=room_count,
            hotel_id=hotel_id_jfk,
            number_of_nights=2
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

    def test_multi_night_booking_2_nights_number_of_nights_not_provided(self):
        """
        validate multi night booking for a 2 night stay is valid
        without passing up number_of_nights
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1,
                                    block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 2
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=JFK&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=number_of_nights)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

    def test_booking_1_night_number_of_nights_not_provided(self):
        """
        validate that a single night booking is valid without passing up number_of_nights
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 1
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=JFK&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=number_of_nights)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

    def test_multi_night_booking_2_nights_via_pax_app(self):
        """
        validate multi night booking for a 2 night stay via the pa≈ app
        """
        customer = 'Purple Rain Airlines'

        # set up multi night inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 2
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=number_of_nights)
        offer_hotel_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=offer_hotel_url + '&room_count=' + str(room_count)).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)
        for hotel in hotel_search_resp['data']:
            self.assertEqual(hotel['proposed_check_in_date'], check_in_date)
            self.assertEqual(hotel['proposed_check_out_date'], check_out_date)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=offer_hotel_url, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

        full_state_url = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)
        full_state_resp = requests.get(url=full_state_url, headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_json = full_state_resp.json()['data']
        voucher_id = full_state_json['passenger']['voucher_id']
        self.assertEqual(len(full_state_json['voucher']['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in full_state_json['voucher']['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], 1)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_out_date'], check_out_date)

        voucher_url = self._api_host + '/api/v1/voucher/' + voucher_id
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_json = voucher_resp.json()['data']
        self.assertEqual(len(voucher_json['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in voucher_json['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], 1)
        self.assertEqual(voucher_json['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher_json['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher_json['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher_json['hotel_voucher']['check_out_date'], check_out_date)

    def test_multi_night_booking_2_nights_2_rooms_via_pax_app(self):
        """
        validate multi night booking for a 2 night stay via the pa≈ app
        """
        customer = 'Purple Rain Airlines'

        # set up multi night inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 2
        number_of_nights = 2
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=number_of_nights)
        offer_hotel_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=offer_hotel_url + '&room_count=' + str(room_count)).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)
        for hotel in hotel_search_resp['data']:
            self.assertEqual(hotel['proposed_check_in_date'], check_in_date)
            self.assertEqual(hotel['proposed_check_out_date'], check_out_date)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=offer_hotel_url, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

        full_state_url = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)
        full_state_resp = requests.get(url=full_state_url, headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_json = full_state_resp.json()['data']
        voucher_id = full_state_json['passenger']['voucher_id']
        self.assertEqual(len(full_state_json['voucher']['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in full_state_json['voucher']['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_out_date'], check_out_date)

        voucher_url = self._api_host + '/api/v1/voucher/' + voucher_id
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_json = voucher_resp.json()['data']
        self.assertEqual(len(voucher_json['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in voucher_json['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher_json['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher_json['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher_json['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher_json['hotel_voucher']['check_out_date'], check_out_date)

    def test_booking_1_night_via_pax_app(self):
        """
        validate single night booking via the pa≈ app
        """
        customer = 'Purple Rain Airlines'

        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 1
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=number_of_nights)
        offer_hotel_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=offer_hotel_url + '&room_count=' + str(room_count)).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)
        for hotel in hotel_search_resp['data']:
            self.assertEqual(hotel['proposed_check_in_date'], check_in_date)
            self.assertEqual(hotel['proposed_check_out_date'], check_out_date)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=offer_hotel_url, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

        full_state_url = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)
        full_state_resp = requests.get(url=full_state_url, headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_json = full_state_resp.json()['data']
        voucher_id = full_state_json['passenger']['voucher_id']
        self.assertEqual(len(full_state_json['voucher']['hotel_voucher']['room_vouchers']), 1)
        for room_voucher in full_state_json['voucher']['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], 1)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_out_date'], check_out_date)

        voucher_url = self._api_host + '/api/v1/voucher/' + voucher_id
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_json = voucher_resp.json()['data']
        self.assertEqual(len(voucher_json['hotel_voucher']['room_vouchers']), 1)
        for room_voucher in voucher_json['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], 1)
        self.assertEqual(voucher_json['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher_json['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher_json['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher_json['hotel_voucher']['check_out_date'], check_out_date)

    def test_booking_1_night_2_rooms_via_pax_app(self):
        """
        validate single night booking via the pa≈ app
        """
        customer = 'Purple Rain Airlines'

        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 2
        number_of_nights = 1
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=number_of_nights)
        offer_hotel_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=offer_hotel_url + '&room_count=' + str(room_count)).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)
        for hotel in hotel_search_resp['data']:
            self.assertEqual(hotel['proposed_check_in_date'], check_in_date)
            self.assertEqual(hotel['proposed_check_out_date'], check_out_date)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=offer_hotel_url, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

        full_state_url = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)
        full_state_resp = requests.get(url=full_state_url, headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_json = full_state_resp.json()['data']
        voucher_id = full_state_json['passenger']['voucher_id']
        self.assertEqual(len(full_state_json['voucher']['hotel_voucher']['room_vouchers']), 1)
        for room_voucher in full_state_json['voucher']['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(full_state_json['voucher']['hotel_voucher']['check_out_date'], check_out_date)

        voucher_url = self._api_host + '/api/v1/voucher/' + voucher_id
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_json = voucher_resp.json()['data']
        self.assertEqual(len(voucher_json['hotel_voucher']['room_vouchers']), 1)
        for room_voucher in voucher_json['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher_json['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(voucher_json['hotel_voucher']['rooms_booked'], room_count)
        self.assertEqual(voucher_json['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher_json['hotel_voucher']['check_out_date'], check_out_date)

    def test_multi_night_booking_3_nights(self):
        """
        validate multi night booking for a 3 night stay
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_jfk = 'tvl-85376'
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)
        event_date_jfk_day3 = event_date_jfk + datetime.timedelta(days=2)
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day2, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk.split('-')[1], 294, event_date_jfk_day3, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 3
        check_in_date = event_date_jfk.strftime('%Y-%m-%d')
        check_out_date = (event_date_jfk_day3 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=JFK&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_jfk, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=2)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_jfk,
            number_of_nights=number_of_nights
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_jfk)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

    @uses_expedia
    def test_ean_hotel_passenger_note(self):
        """
        validates the hotel passenger_note field for ean hotel searches,
        bookings, and full state requests.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger/'
        expected_passenger_note = ''

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        # get an inventory and validate passenger noteis empty string
        hotel_response = requests.get(hotel_url + '?room_count=1&port='+ port +'&provider=ean', headers=headers).json()
        self.assertGreater(len(hotel_response['data']), 0, msg='no expedia inventory for port ' + repr(port))
        for hotel in hotel_response['data']:
            self.assertIn('passenger_note', hotel)
            self.assertEqual(hotel['passenger_note'], expected_passenger_note)

        # import passengers and set up booking parameters
        hotel_id1 = hotel_response['data'][0]['hotel_id']
        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)
        booking_payload = dict(hotel_id=hotel_id1, room_count=1, context_ids=[passenger['context_id'] for passenger in passengers])

        # book hotel validate response, and validate full state for booking
        booking_resp = requests.post(url=hotel_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()['data']['hotel_voucher']
        self.assertEqual(booking_resp_json['hotel_id'], hotel_id1)
        self.assertIn('passenger_note', booking_resp_json)
        self.assertEqual(booking_resp_json['passenger_note'], expected_passenger_note)
        full_state_resp = requests.get(url=passenger_url + passengers[0]['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()['data']
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['hotel_id'], hotel_id1)
        self.assertIn('passenger_note', full_state_resp_json['voucher']['hotel_voucher'])
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['passenger_note'], expected_passenger_note)

    def test_tvl_hotel_passenger_note(self):
        """
        validates the hotel passenger_note field for tvl hotel searches,
        bookings, and full state requests.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger/'

        port_id = 16
        port_id2 = 191
        hotel_id1 = 80657
        hotel_id2 = 98719
        hsp_id_hotel_1 = 985
        hsp_id2_hotel_1 = 17297
        hsp_id_hotel_2 = 16651
        expected_passenger_note = 'I am a passenger note.'
        expected_passenger_note2 = 'I am a passenger note as well!'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id1, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(hotel_id2, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # update serviced port passenger notes
        self.update_hotel_serviced_port(hsp_id_hotel_1, port_id, hotel_id1, passenger_notes=None)
        self.update_hotel_serviced_port(hsp_id_hotel_2, port_id, hotel_id2, passenger_notes=expected_passenger_note)
        self.update_hotel_serviced_port(hsp_id2_hotel_1, port_id2, hotel_id1, passenger_notes=expected_passenger_note2)

        # validate passenger notes
        validated_hotel1_passenger_note = False
        validated_hotel2_passenger_note = False
        hotel_response = requests.get(hotel_url + '?room_count=1&port=LAX', headers=headers).json()
        for hotel in hotel_response['data']:
            self.assertIn('passenger_note', hotel)
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id1):
                self.assertEqual(hotel['passenger_note'], '')
                validated_hotel1_passenger_note = True
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id2):
                self.assertEqual(hotel['passenger_note'], expected_passenger_note)
                validated_hotel2_passenger_note = True
        self.assertTrue(validated_hotel1_passenger_note)
        self.assertTrue(validated_hotel2_passenger_note)

        # validate passenger notes are port specific
        validated_hotel_passenger_note = False
        hotel_response = requests.get(hotel_url + '?room_count=1&port=SNA', headers=headers).json()
        for hotel in hotel_response['data']:
            self.assertIn('passenger_note', hotel)
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id1):
                self.assertEqual(hotel['passenger_note'], expected_passenger_note2)
                validated_hotel_passenger_note = True
        self.assertTrue(validated_hotel_passenger_note)

        # import passengers
        passengers = self._create_2_passengers(customer=customer, port_accommodation='LAX')
        passengers2 = self._create_2_passengers(customer=customer, port_accommodation='LAX')
        passengers3 = self._create_2_passengers(customer=customer, port_accommodation='SNA')

        # setup booking payloads
        booking_payload1 = dict(hotel_id='tvl-' + str(hotel_id1), room_count=1, context_ids=[passenger['context_id'] for passenger in passengers])
        booking_payload2 = dict(hotel_id='tvl-' + str(hotel_id2), room_count=1, context_ids=[passenger['context_id'] for passenger in passengers2])
        booking_payload3 = dict(hotel_id='tvl-' + str(hotel_id1), room_count=1, context_ids=[passenger['context_id'] for passenger in passengers3])

        # book hotel validate response, and validate full state for booking 1
        booking_resp = requests.post(url=hotel_url, headers=headers, json=booking_payload1)
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()['data']['hotel_voucher']
        self.assertEqual(booking_resp_json['hotel_id'], 'tvl-' + str(hotel_id1))
        self.assertIn('passenger_note', booking_resp_json)
        self.assertEqual(booking_resp_json['passenger_note'], '')
        full_state_resp = requests.get(url=passenger_url + passengers[0]['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()['data']
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['hotel_id'], 'tvl-' + str(hotel_id1))
        self.assertIn('passenger_note', full_state_resp_json['voucher']['hotel_voucher'])
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['passenger_note'], '')

        # book hotel validate response, and validate full state for booking 2
        booking_resp = requests.post(url=hotel_url, headers=headers, json=booking_payload2)
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()['data']['hotel_voucher']
        self.assertEqual(booking_resp_json['hotel_id'], 'tvl-' + str(hotel_id2))
        self.assertIn('passenger_note', booking_resp_json)
        self.assertEqual(booking_resp_json['passenger_note'], expected_passenger_note)
        full_state_resp = requests.get(url=passenger_url + passengers2[0]['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()['data']
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['hotel_id'], 'tvl-' + str(hotel_id2))
        self.assertIn('passenger_note', full_state_resp_json['voucher']['hotel_voucher'])
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['passenger_note'], expected_passenger_note)

        # book hotel validate response, and validate full state for booking 3
        booking_resp = requests.post(url=hotel_url, headers=headers, json=booking_payload3)
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()['data']['hotel_voucher']
        self.assertEqual(booking_resp_json['hotel_id'], 'tvl-' + str(hotel_id1))
        self.assertIn('passenger_note', booking_resp_json)
        self.assertEqual(booking_resp_json['passenger_note'], expected_passenger_note2)
        full_state_resp = requests.get(url=passenger_url + passengers3[0]['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()['data']
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['hotel_id'], 'tvl-' + str(hotel_id1))
        self.assertIn('passenger_note', full_state_resp_json['voucher']['hotel_voucher'])
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['passenger_note'], expected_passenger_note2)

    def test_child_can_book_hotel(self):
        """
        verifies system allows child to book hotel room via airline api
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            life_stage='child'
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)
        self.assertEqual(response_json['data'][0]['life_stage'], 'child')
        passenger = response_json['data'][0]

        hotel_offerings = self._airline_get_passenger_hotel_offerings(customer, passenger['port_accommodation'], 1)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        hotel_resp = self._airline_book_hotel(customer, picked_hotel, [passenger['context_id']])
        self.assertEqual(len(hotel_resp['passengers']), 1)
        self.assertEqual(hotel_resp['passengers'][0]['hotel_accommodation_status'], 'accepted')
        UUID(hotel_resp['voucher_id'], version=4)

    def test_validate_hotel_booking_room_count(self):
        """
        verifies system is validating room_count field for hotel booking on both passenger and airline API
        verifies system allows for a passenger to book more rooms then pnr length on airline API
        verifies system does not allow passenger to book more rooms then pnr length on passenger API
        """
        expected_error_message_pax_max_rooms = [{'field': 'room_count', 'message': 'Rooms requested exceeds max rooms allowed.'}]
        expected_error_message_airline_rooms = [{'field': 'room_count', 'message': 'Ensure this value is less than or equal to 100.'}]

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)
        passenger = response_json['data'][0]

        airline_hotel_url = self._api_host + '/api/v1/hotels'
        passenger_hotel_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']

        hotel_offerings = self._airline_get_passenger_hotel_offerings(customer, passenger['port_accommodation'], 5)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        bad_booking_payload = {
            'context_ids': [passenger['context_id']],
            'hotel_id': hotel_offerings[0]['hotel_id'],
            'room_count': 101
        }

        booking_payload = {
            'context_ids': [passenger['context_id']],
            'hotel_id': hotel_offerings[0]['hotel_id'],
            'room_count': 5
        }

        hotel_resp1 = requests.post(url=passenger_hotel_url, data=booking_payload)
        self.assertEqual(hotel_resp1.status_code, 400)
        hotel_resp_json = hotel_resp1.json()
        log_error_system_tests_output(pretty_print_json(hotel_resp_json))
        self._validate_error_message(hotel_resp_json, 400, 'Bad Request', 'MAX_ROOMS_EXCEEDED', 'Rooms requested exceeds max rooms allowed.', [])

        hotel_resp2 = requests.post(url=passenger_hotel_url, data=bad_booking_payload)
        self.assertEqual(hotel_resp2.status_code, 400)
        hotel_resp_json = hotel_resp2.json()
        log_error_system_tests_output(pretty_print_json(hotel_resp_json))
        self._validate_error_message(hotel_resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', expected_error_message_airline_rooms)

        hotel_resp3 = requests.post(url=airline_hotel_url, data=bad_booking_payload, headers=headers)
        self.assertEqual(hotel_resp3.status_code, 400)
        hotel_resp_json = hotel_resp3.json()
        log_error_system_tests_output(pretty_print_json(hotel_resp_json))
        self._validate_error_message(hotel_resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', expected_error_message_airline_rooms)

        hotel_resp4 = requests.post(url=airline_hotel_url, data=booking_payload, headers=headers)
        self.assertEqual(hotel_resp4.status_code, 200)
        hotel_resp_json = hotel_resp4.json()['data']
        self.assertEqual(len(hotel_resp_json['passengers']), 1)
        self.assertEqual(hotel_resp_json['passengers'][0]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(hotel_resp_json['hotel_voucher']['hotel_id'], hotel_offerings[0]['hotel_id'])
        self.assertEqual(hotel_resp_json['hotel_voucher']['rooms_booked'], 5)
        UUID(hotel_resp_json['voucher_id'], version=4)

    def test_validate_hotel_id_with_provider_prefix(self):
        """
        validate provider prefix for hotel_id
        """
        headers = self._generate_airline_headers('Purple Rain Airlines')

        payload = {
            'hotel_id': 'tv-12345',
            'room_count': 1,
            'context_ids': ['conny']
        }

        resp = requests.post(url=self._api_host + '/api/v1/hotels', headers=headers, data=payload)
        self.assertEqual(resp.status_code, 400, '')
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'hotel_id', 'message': 'invalid hotel_id'}])

        payload = {
            'hotel_id': 'ean-12345',
            'room_count': 1,
            'context_ids': ['conny']
        }

        resp = requests.post(url=self._api_host + '/api/v1/hotels', headers=headers, data=payload)
        self.assertEqual(resp.status_code, 400, '')
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'hotel_id', 'message': 'invalid hotel_id'}])

        payload = {
            'hotel_id': 'tvl-02345',
            'room_count': 1,
            'context_ids': ['conny']
        }

        resp = requests.post(url=self._api_host + '/api/v1/hotels', headers=headers, data=payload)
        self.assertEqual(resp.status_code, 400, '')
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'hotel_id', 'message': 'invalid hotel_id'}])

        payload = {
            'hotel_id': 'tvl-93ac3c45-3c27-4432-a9f5-4c1ad279c9fa',
            'room_count': 1,
            'context_ids': ['conny']
        }

        resp = requests.post(url=self._api_host + '/api/v1/hotels', headers=headers, data=payload)
        self.assertEqual(resp.status_code, 400, '')
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'hotel_id', 'message': 'invalid hotel_id'}])

        payload = {
            'hotel_id': 'tvl--3ac3c45-3c27-4432-a9f5-4c1ad279c9fa',
            'room_count': 1,
            'context_ids': ['conny']
        }

        resp = requests.post(url=self._api_host + '/api/v1/hotels', headers=headers, data=payload)
        self.assertEqual(resp.status_code, 400, '')
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'hotel_id', 'message': 'invalid hotel_id'}])

    def test_hotel_id_404(self):
        """
        verifies system returns 404 for hotel_id not found
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        url = self._api_host + '/api/v1/hotels'
        offer_url = self._api_host + '/api/v1/offer/hotels'

        passengers = self._create_2_passengers(customer=customer)  # validation done in helper method

        payload = {
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']],
            'hotel_id': 'tvl-999999999',
            'room_count': 1
        }

        response = requests.post(url, headers=headers, json=payload)
        self.assertEqual(response.status_code, 404)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 404, 'Not Found', 'HOTEL_NOT_FOUND', 'Hotel not found for hotel_id: tvl-999999999', [])

        response = requests.post(offer_url + '?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2'], json=payload)
        self.assertEqual(response.status_code, 404)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 404, 'Not Found', 'HOTEL_NOT_FOUND', 'Hotel not found for hotel_id: tvl-999999999', [])

    def test_hotel_passenger_invalid_status(self):
        """
        verifies system returns 400 for a hotel booking with a passenger not in a status of offered
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        url = self._api_host + '/api/v1/hotels'
        offer_url = self._api_host + '/api/v1/offer/hotels'

        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=False)  # validation done in helper method

        payload = {
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']],
            'hotel_id': 'tvl-999999999',
            'room_count': 1
        }

        response = requests.post(url, headers=headers, json=payload)
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        # not using utility here because order of id's in error_description is not always consistent
        self.assertEqual(response_json['error'], True)
        self.assertEqual(response_json['meta']['status'], 400)
        self.assertEqual(response_json['meta']['message'], 'Bad Request')
        self.assertEqual(response_json['meta']['error_code'], 'PASSENGER_INVALID_STATUS')

        response = requests.post(offer_url + '?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2'], json=payload)
        self.assertEqual(response.status_code, 401)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 401, 'Unauthorized', '', '', [])

    def test_hotel_passenger_info_mismatch(self):
        """
        verifies system returns 400 for a hotel booking with a passengers not in same port
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        url = self._api_host + '/api/v1/hotels'

        passengers = self._create_2_passengers(customer=customer)  # validation done in helper method
        passengers2 = self._create_2_passengers(customer=customer, port_accommodation='DFW')

        payload = {
            'context_ids': [passengers[0]['context_id'], passengers2[1]['context_id']],
            'hotel_id': 'tvl-999999999',
            'room_count': 1
        }

        response = requests.post(url, headers=headers, json=payload)
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', 'Not all passengers are disrupted in the same port.', [])

    def test_hotel_passenger_not_found(self):
        """
        verifies system returns 404 for a hotel booking with a passengers not found
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        url = self._api_host + '/api/v1/hotels'

        passengers = self._create_2_passengers(customer=customer)  # validation done in helper method

        payload = {
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id'], 'randy-moss'],
            'hotel_id': 'tvl-999999999',
            'room_count': 1
        }

        response = requests.post(url, headers=headers, json=payload)
        self.assertEqual(response.status_code, 404)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 404, 'Not Found', 'PASSENGER_NOT_FOUND', 'Not all Passengers found for given context_id list.', [])

    def test_hotel_invalid_booking_request(self):
        """
        verifies system returns 400 for a hotel booking without context_id of authenticated passenger
        """
        customer = 'Purple Rain Airlines'
        url = self._api_host + '/api/v1/offer/hotels'

        passengers = self._create_2_passengers(customer=customer)  # validation done in helper method

        payload = {
            'context_ids': ['randy-moss'],
            'hotel_id': 'tvl-999999999',
            'room_count': 1
        }

        response = requests.post(url + '?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2'], json=payload)
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_BOOKING_REQUEST', 'Passenger accepting the offer if not in the list of context ids.', [])

    def test_validate_hotel_on_airport_and_property_code(self):
        """
        system test validating that hotel_on_airport is on responses and property_code is not
        """
        customer = 'Purple Rain Airlines'

        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'

        headers = self._generate_airline_headers(customer)
        passenger_payload = self._generate_n_passenger_payload(1)

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        hotel_offerings = self._get_passenger_hotel_offerings(passenger)
        self.assertGreater(len(hotel_offerings), 0)
        for hotel in hotel_offerings:
            self.assertIn('hotel_on_airport', hotel)
            self.assertNotIn('property_code', hotel)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        self.assertIn('hotel_on_airport', booking_response.json()['data']['hotel_voucher'])
        self.assertNotIn('property_code', booking_response.json()['data']['hotel_voucher'])

        voucher_url = self._api_host + '/api/v1/voucher/' + str(booking_response.json()['data']['voucher_id'])

        voucher_resp = requests.get(url=voucher_url, headers=headers)
        voucher_resp_json = voucher_resp.json()
        self.assertEqual(voucher_resp_json['error'], False)
        self.assertEqual(voucher_resp.status_code, 200)
        self.assertEqual(voucher_resp_json['data']['voucher_id'], booking_response.json()['data']['voucher_id'])
        self.assertIn('hotel_on_airport', voucher_resp_json['data']['hotel_voucher'])
        self.assertNotIn('property_code', voucher_resp_json['data']['hotel_voucher'])
        self.assertEqual(voucher_resp_json['data']['hotel_voucher']['fees'], [])

        full_state = requests.get(url=offer_url + '/' + passenger['context_id'] + '/state', headers=headers).json()
        self.assertIn('hotel_on_airport', full_state['data']['voucher']['hotel_voucher'])
        self.assertNotIn('property_code', full_state['data']['voucher']['hotel_voucher'])
        self.assertEqual(full_state['data']['voucher']['hotel_voucher']['fees'], [])

    def test_validate_booking_number_of_nights(self):
        """
        validate number_of_nights must be equal to 1 when booking
        """
        headers = self._generate_airline_headers('Purple Rain Airlines')
        passengers = self._create_2_passengers('Purple Rain Airlines', number_of_nights=1, port_accommodation='LAX')
        hotel_url = self._api_host + '/api/v1/hotels'

        hotels = self._airline_get_passenger_hotel_offerings('Purple Rain Airlines', 'LAX', 1)
        hotel_id = hotels[0]['hotel_id']

        payload = dict(
            context_ids=[passengers[0]['context_id'], passengers[1]['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            number_of_nights='a string'
        )

        resp = requests.post(url=hotel_url, headers=headers, json=payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'number_of_nights', 'message': 'A valid integer is required.'}])

        payload['number_of_nights'] = 0
        resp = requests.post(url=hotel_url, headers=headers, json=payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'number_of_nights', 'message': 'Ensure this value is greater than or equal to 1.'}])

        payload['number_of_nights'] = 10
        resp = requests.post(url=hotel_url, headers=headers, json=payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel booking.', [{'field': 'number_of_nights', 'message': 'Ensure this value is less than or equal to 7.'}])

    def test_handicap_hotel_aa_hack__tvl_inventory(self):
        """
        verify aa handicap hotel hack for search and booking
        """
        hotel_id = 'tvl-98771'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=EUG&handicap=true'
        passenger_url = self._api_host + '/api/v1/passenger'

        # verify no inventory
        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertEqual(len(hotel_response_json['data']), 0)

        # add ROH inventory for EUG
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98771, 71, event_date, ap_block_type=1, block_price='75.00', blocks=1, pay_type='0')

        # search for handicap rooms and ensure you get ROH
        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertEqual(len(hotel_response_json['data']), 1)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], hotel_id)

        # import handicap pax at EUG
        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            port_accommodation='EUG',
            handicap=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=1,
            hotel_id=hotel_id
        )

        # booking a handicap pax on ROH inv
        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['hotel_id'], hotel_id)

        # full state verify booking success and pax is handicap
        full_state = requests.get(url=passenger_url + '/' + response_json['data'][0]['context_id'] + '/state', headers=headers).json()
        hotel_voucher = full_state['data']['voucher']['hotel_voucher']
        self.assertEqual(hotel_voucher['hotel_id'], hotel_id)
        self.assertEqual(full_state['data']['passenger']['handicap'], True)

        # verify no inventory
        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertEqual(len(hotel_response_json['data']), 0)

    def test_tvl_booking_confirmation_id_and_hotel_key(self):
        """
        validate an expedia booking with 2 pax in 1 room
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers = self._create_2_passengers(customer=customer)

        hotel_response = requests.get(hotel_url + '?room_count=1&port=LAX&provider=tvl', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0)

        tvl_offer = hotel_response_json['data'][0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=tvl_offer,
            room_count=1
        )

        booking_response = requests.post(url=hotel_url, headers=headers, data=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        tvl_voucher = booking_response_json['data']

        self.assertEqual(tvl_voucher['hotel_voucher']['provider'], 'tvl')
        self.assertIsNone(tvl_voucher['hotel_voucher']['confirmation_id'])
        self.assertEqual(len(tvl_voucher['hotel_voucher']['hotel_key']), 5)

    def test_tvl_booking_1_young_adult_1_room(self):
        """
        document current behavior when a young_adult travelling alone tries to book a hotel room. (for now, it is allowed)
        """
        # TODO: should a young_adult be able to stay in a property without a supervising adult in another room?
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        port = 'PHX'

        passengers = self._generate_n_passenger_payload(1, port_accommodation=port, life_stage='young_adult')
        import_response = requests.post(self._api_host + '/api/v1/passenger', headers=headers, json=passengers)
        self.assertEqual(import_response.status_code, 201)
        passengers = import_response.json()['data']

        query_parameters = {
            'room_count': '1',
            'port': port,
            'provider': 'tvl'
        }

        hotel_response = requests.get(hotel_url, headers=headers, params=query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0,
                           msg='no inventory in ' + repr(port))

        ean_offer = hotel_response_json['data'][0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=1
        )

        booking_response = requests.post(url=hotel_url, headers=headers, data=booking_payload)
        if booking_response.status_code != 200:
            self.fail('unexpected response: ' + str(booking_response.status_code) + ' ' + booking_response.text)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        if booking_response_json['meta']['error_code'] != '':
            self.fail('unexpected response: ' + json.dumps(booking_response.json(), sort_keys=True, indent=4))
        self.assertFalse(booking_response_json['error'])

    @uses_expedia
    @should_skip_local_test  # TODO: improve on this.
    def test_external_booking_many_ports(self):
        """
        validate external bookings with many ports and providers
        """
        failed_ports = []
        failed_ports_message = ''

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        providers = ['ean']  # EXTERNAL PROVIDER LIST to run test against

        # PORTS LIST to run test against
        ports = [
            'BWI', 'DTW', 'SAT', 'COS', 'ELP', 'MCI', 'MTJ', 'OKC', 'ALB', 'AVP', 'BUF', 'DAY', 'EWR', 'MDT', 'MHT',
            'ROC', 'SYR', 'BHM', 'CHS', 'GSO', 'ILM', 'MSY', 'ORF', 'PNS', 'RIC', 'SAV', 'SDF', 'BOI', 'GEG', 'LGB',
            'ONT', 'PSP', 'RNO'
        ]

        for provider in providers:
            for port in ports:
                try:
                    passengers = self._create_2_passengers(customer=customer, port_accommodation=port)

                    hotel_response = requests.get(hotel_url + '?room_count=1&port=' + port + '&provider=' + provider,
                                                  headers=headers)
                    self.assertEqual(hotel_response.status_code, 200)
                    hotel_response_json = hotel_response.json()
                    self.assertGreater(len(hotel_response_json['data']), 0)

                    offer = hotel_response_json['data'][0]['hotel_id']

                    booking_payload = dict(
                        context_ids=[passenger['context_id'] for passenger in passengers],
                        hotel_id=offer,
                        room_count=1
                    )

                    booking_response = requests.post(url=hotel_url, headers=headers, data=booking_payload)
                    self.assertEqual(booking_response.status_code, 200)

                    booking_response_json = booking_response.json()
                    self.assertEqual(booking_response_json['meta']['error_code'], '')
                    ean_voucher = booking_response_json['data']

                    self.assertEqual(ean_voucher['hotel_voucher']['provider'], 'ean')
                    self.assertEqual(ean_voucher['hotel_voucher']['hotel_id'], offer)
                    # self.assertEqual(ean_voucher['hotel_voucher']['tax'], '0.00')  # TODO: change once breaks
                    # self.assertEqual(ean_voucher['hotel_voucher']['total_amount'], '0.00')  # TODO: change once breaks
                    self.assertEqual(len(ean_voucher['hotel_voucher']['room_vouchers']), 1)
                    self.assertEqual(ean_voucher['hotel_voucher']['room_vouchers'][0]['count'], 1)
                    # self.assertEqual(ean_voucher['hotel_voucher']['room_vouchers'][0]['rate'], '0.00')

                    self.assertTrue(ean_voucher['hotel_voucher']['confirmation_id'].isdigit())
                    self.assertEqual(len(ean_voucher['hotel_voucher']['confirmation_id']), 13)
                    # should not be present when we have a confirmation number
                    self.assertIsNone(ean_voucher['hotel_voucher']['hotel_key'])

                    self.assertEqual({passenger['context_id'] for passenger in passengers},
                                     {passenger['context_id'] for passenger in ean_voucher['passengers']})

                except AssertionError as e:  # continue test on failure and log failing port
                    failed_ports.append(port)
                    failed_ports_message += 'provider: ' + provider + ' port: ' + port + ' reason: ' + str(e) + '\n'

        # validation that all ports passed test (log results to console if failed)
        if len(failed_ports) != 0:
            print(failed_ports_message)
        self.assertEqual(len(failed_ports), 0)

    def test_two_passengers_different_pnr_group_different_accommodations(self):
        """
        validate passengers can enter the system on separate pnr groups with different accommodations
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger/'
        voucher_url = self._api_host + '/api/v1/voucher/'

        # voucher_ids
        voucher_id1 = None  # used by group 1
        voucher_id2 = None  # used by group 2

        passengers_payload_group_1 = self._generate_n_passenger_payload(2)
        passengers_payload_group_2 = self._generate_n_passenger_payload(2)

        passengers_payload_group_1[0].update(dict(
            meal_accommodation=True,
            hotel_accommodation=True,
            meals=[
                {'meal_amount': 12.00, 'currency_code': 'USD', 'number_of_days': 1},
                {'meal_amount': 11.50, 'currency_code': 'USD', 'number_of_days': 2}
            ]
        ))
        passengers_payload_group_1[1].update(dict(
            meal_accommodation=False,
            hotel_accommodation=True,
            meals=[]
        ))
        passengers_payload_group_2[0].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            pnr_create_date=passengers_payload_group_1[0]['pnr_create_date'],
            pax_record_locator=passengers_payload_group_1[0]['pax_record_locator'],
            meals=[
                {'meal_amount': 10.50, 'currency_code': 'USD', 'number_of_days': 3}
            ]
        ))
        passengers_payload_group_2[1].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            pnr_create_date=passengers_payload_group_1[0]['pnr_create_date'],
            pax_record_locator=passengers_payload_group_1[0]['pax_record_locator'],
            meals=[
                {'meal_amount': 12.00, 'currency_code': 'USD', 'number_of_days': 1},
                {'meal_amount': 9.50, 'currency_code': 'GBP', 'number_of_days': 2},
                {'meal_amount': 5, 'currency_code': 'USD', 'number_of_days': 3}
            ]
        ))

        passengers_payload = [
            passengers_payload_group_1[0], passengers_payload_group_1[1],
            passengers_payload_group_2[0], passengers_payload_group_2[1]
        ]

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertEqual(len(resp_json['data']), 4)

        passenger_1 = None
        passenger_2 = None
        passenger_3 = None
        passenger_4 = None
        for passenger in resp_json['data']:
            if passenger['context_id'] == passengers_payload_group_1[0]['context_id']:
                passenger_1 = passenger
            elif passenger['context_id'] == passengers_payload_group_1[1]['context_id']:
                passenger_2 = passenger
            elif passenger['context_id'] == passengers_payload_group_2[0]['context_id']:
                passenger_3 = passenger
            else:
                passenger_4 = passenger
                self.assertEqual(passenger['context_id'], passengers_payload_group_2[1]['context_id'])
        self.assertIsNotNone(passenger_1)
        self.assertIsNotNone(passenger_2)
        self.assertIsNotNone(passenger_3)
        self.assertIsNotNone(passenger_4)

        # validate passenger import response
        self.assertEqual(passenger_1['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_1['meal_accommodation_status'], 'offered')
        self.assertIsNone(passenger_1['voucher_id'])
        self.assertEqual(passenger_2['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_2['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(passenger_2['voucher_id'])
        self.assertEqual(passenger_3['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(passenger_3['meal_accommodation_status'], 'accepted')
        self.assertIsNotNone(passenger_3['voucher_id'])
        self.assertEqual(passenger_4['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(passenger_4['meal_accommodation_status'], 'accepted')
        self.assertIsNotNone(passenger_4['voucher_id'])
        self.assertEqual(passenger_3['voucher_id'], passenger_4['voucher_id'])
        voucher_id2 = passenger_3['voucher_id']

        voucher_id = passenger_3['voucher_id']
        voucher_resp = requests.get(url=voucher_url + voucher_id, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        self.assertEqual(len(voucher_resp_json['data']['passengers']), 2)

        passenger_3 = None
        passenger_4 = None
        for passenger in voucher_resp_json['data']['passengers']:
            if passenger['context_id'] == passengers_payload_group_2[0]['context_id']:
                passenger_3 = passenger
            else:
                passenger_4 = passenger
                self.assertEqual(passenger['context_id'], passengers_payload_group_2[1]['context_id'])
        self.assertIsNotNone(passenger_3)
        self.assertIsNotNone(passenger_4)

        # validate passengers on voucher 2 resp
        self.assertEqual(passenger_3['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(passenger_3['meal_accommodation_status'], 'accepted')
        self.assertEqual(len(passenger_3['meal_vouchers']), 1)
        self.assertEqual(passenger_3['meal_vouchers'][0]['amount'], '10.50')
        self.assertEqual(passenger_3['meal_vouchers'][0]['currency_code'], 'USD')
        self.assertEqual(passenger_4['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(passenger_4['meal_accommodation_status'], 'accepted')
        self.assertEqual(len(passenger_4['meal_vouchers']), 3)

        meal_1 = None
        meal_2 = None
        meal_3 = None
        for meal in passenger_4['meal_vouchers']:
            if meal['amount'] == '12.00':
                meal_1 = meal
            elif meal['amount'] == '9.50':
                meal_2 = meal
            else:
                meal_3 = meal
                self.assertEqual(meal['amount'], '5.00')
        self.assertIsNotNone(meal_1)
        self.assertIsNotNone(meal_2)
        self.assertIsNotNone(meal_3)

        # validate meal cards
        self.assertEqual(meal_1['currency_code'], 'USD')
        self.assertEqual(meal_2['currency_code'], 'GBP')
        self.assertEqual(meal_3['currency_code'], 'USD')
        self.assertLess(datetime.datetime.strptime(meal_1['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_2['active_to'], '%Y-%m-%d %H:%M'))
        self.assertLess(datetime.datetime.strptime(meal_1['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_3['active_to'], '%Y-%m-%d %H:%M'))
        self.assertLess(datetime.datetime.strptime(meal_2['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_3['active_to'], '%Y-%m-%d %H:%M'))

        # book group 1
        hotels = self._get_passenger_hotel_offerings(passenger_1, room_count=1)
        self.assertGreaterEqual(len(hotels), 1)

        picked_hotel = hotels[0]
        booking_response_data = self._airline_book_hotel(customer, picked_hotel, [passenger_1['context_id'], passenger_2['context_id']], room_count=1)
        UUID(booking_response_data['voucher_id'], version=4)
        voucher_id1 = booking_response_data['voucher_id']

        # validate voucher 1
        voucher_resp = requests.get(url=voucher_url + voucher_id1, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()

        passenger_1 = None
        passenger_2 = None
        for passenger in voucher_resp_json['data']['passengers']:
            if passenger['context_id'] == passengers_payload_group_1[0]['context_id']:
                passenger_1 = passenger
            else:
                passenger_2 = passenger
                self.assertEqual(passenger['context_id'], passengers_payload_group_1[1]['context_id'])
        self.assertIsNotNone(passenger_1)
        self.assertIsNotNone(passenger_2)

        self.assertEqual(passenger_1['hotel_accommodation_status'], 'accepted')
        self.assertEqual(passenger_1['meal_accommodation_status'], 'accepted')
        self.assertEqual(len(passenger_1['meal_vouchers']), 2)
        self.assertEqual(passenger_2['hotel_accommodation_status'], 'accepted')
        self.assertEqual(passenger_2['meal_accommodation_status'], 'not_offered')
        self.assertEqual(len(passenger_2['meal_vouchers']), 0)

        meal_1 = None
        meal_2 = None
        for meal in passenger_1['meal_vouchers']:
            if meal['amount'] == '12.00':
                meal_1 = meal
            else:
                meal_2 = meal
                self.assertEqual(meal['amount'], '11.50')
        self.assertIsNotNone(meal_1)
        self.assertIsNotNone(meal_2)

        self.assertEqual(meal_1['currency_code'], 'USD')
        self.assertEqual(meal_2['currency_code'], 'USD')
        self.assertLess(datetime.datetime.strptime(meal_1['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_2['active_to'], '%Y-%m-%d %H:%M'))

        # validate all passengers via full state
        # passenger 1
        full_state_resp = requests.get(url=passenger_url + passenger_1['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        passenger_1 = full_state_resp_json['data']

        self.assertEqual(passenger_1['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(passenger_1['passenger']['meal_accommodation_status'], 'accepted')
        self.assertEqual(len(passenger_1['voucher']['meal_vouchers']), 2)
        self.assertEqual(passenger_1['passenger']['voucher_id'], voucher_id1)

        meal_1 = None
        meal_2 = None
        for meal in passenger_1['voucher']['meal_vouchers']:
            if meal['amount'] == '12.00':
                meal_1 = meal
            else:
                meal_2 = meal
                self.assertEqual(meal['amount'], '11.50')
        self.assertIsNotNone(meal_1)
        self.assertIsNotNone(meal_2)

        self.assertEqual(meal_1['currency_code'], 'USD')
        self.assertEqual(meal_2['currency_code'], 'USD')
        self.assertLess(datetime.datetime.strptime(meal_1['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_2['active_to'], '%Y-%m-%d %H:%M'))

        # passenger 2
        full_state_resp = requests.get(url=passenger_url + passenger_2['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        passenger_2 = full_state_resp_json['data']

        self.assertEqual(passenger_2['passenger']['hotel_accommodation_status'], 'accepted')
        self.assertEqual(passenger_2['passenger']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(len(passenger_2['voucher']['meal_vouchers']), 0)
        self.assertEqual(passenger_1['passenger']['voucher_id'], voucher_id1)

        # passenger 3
        full_state_resp = requests.get(url=passenger_url + passenger_3['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        passenger_3 = full_state_resp_json['data']

        self.assertEqual(passenger_3['passenger']['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(passenger_3['passenger']['meal_accommodation_status'], 'accepted')
        self.assertEqual(len(passenger_3['voucher']['meal_vouchers']), 1)
        self.assertEqual(passenger_3['voucher']['meal_vouchers'][0]['amount'], '10.50')
        self.assertEqual(passenger_3['voucher']['meal_vouchers'][0]['currency_code'], 'USD')
        self.assertEqual(passenger_3['passenger']['voucher_id'], voucher_id2)

        # passenger 4
        full_state_resp = requests.get(url=passenger_url + passenger_4['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        passenger_4 = full_state_resp_json['data']

        self.assertEqual(passenger_4['passenger']['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(passenger_4['passenger']['meal_accommodation_status'], 'accepted')
        self.assertEqual(len(passenger_4['voucher']['meal_vouchers']), 3)
        self.assertEqual(passenger_4['passenger']['voucher_id'], voucher_id2)

        meal_1 = None
        meal_2 = None
        meal_3 = None
        for meal in passenger_4['voucher']['meal_vouchers']:
            if meal['amount'] == '12.00':
                meal_1 = meal
            elif meal['amount'] == '9.50':
                meal_2 = meal
            else:
                meal_3 = meal
                self.assertEqual(meal['amount'], '5.00')
        self.assertIsNotNone(meal_1)
        self.assertIsNotNone(meal_2)
        self.assertIsNotNone(meal_3)

        self.assertEqual(meal_1['currency_code'], 'USD')
        self.assertEqual(meal_2['currency_code'], 'GBP')
        self.assertEqual(meal_3['currency_code'], 'USD')
        self.assertLess(datetime.datetime.strptime(meal_1['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_2['active_to'], '%Y-%m-%d %H:%M'))
        self.assertLess(datetime.datetime.strptime(meal_1['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_3['active_to'], '%Y-%m-%d %H:%M'))
        self.assertLess(datetime.datetime.strptime(meal_2['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(meal_3['active_to'], '%Y-%m-%d %H:%M'))
        self.assertLess(datetime.datetime.strptime(meal_1['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(passenger_3['voucher']['meal_vouchers'][0]['active_to'], '%Y-%m-%d %H:%M'))
        self.assertLess(datetime.datetime.strptime(meal_2['active_to'], '%Y-%m-%d %H:%M'), datetime.datetime.strptime(passenger_3['voucher']['meal_vouchers'][0]['active_to'], '%Y-%m-%d %H:%M'))
