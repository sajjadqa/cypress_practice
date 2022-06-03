import unittest

import requests

from stormx_verification_framework import (
    StormxSystemVerification,
    passenger_sanitized_fields,
    pretty_print_json,
    log_error_system_tests_output
)


class TestPassengerApp(StormxSystemVerification):
    """
    Verify that some backend aspects of the passenger app are functioning properly.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestPassengerApp, cls).setUpClass()

    def test_passenger_offer__meal_only(self):
        """
        verify passenger landing page has correct information embedded in it for the scenario:
          * airline offers hotel only. Passenger accepts the hotel. Passenger revisits the offer link again after that.

        This test focuses mostly on confirmation payloads in their various places.
        """

        customer = 'Delta Air Lines'
        headers = self._generate_passenger_headers()

        # airline generates offer ----
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=False, meal_accommodation=True)
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']

        # passenger visits offer link ----
        response = requests.get(passenger_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNotNone(embedded_json['confirmation'])
        self.assertIsNone(embedded_json['confirmation']['hotel_voucher'])
        self.assertEqual(embedded_json['confirmation']['passengers'][0]['meal_vouchers'][0]['amount'], '12.00')
        self.assertEqual(embedded_json['confirmation']['passengers'][0]['meal_vouchers'][1]['amount'], '10.99')

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

    # TODO: Move Lyft test out separate, so it is not part of the normal performance tests.
    @unittest.skip('skipping transportation test')
    def test_passenger_offer__hotel_and_transport_accept(self):
        """
        verify passenger can book a ride with lift
        """
        if self.selected_environment_name != 'dev':
            raise unittest.SkipTest('only tested locally. not configured in AWS-deployed environments yet')

        customer = 'Delta Air Lines'
        headers = self._generate_passenger_headers()

        # airline generates offer ----
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=True,
                                               transport_accommodation=True)
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
        context_ids = [p['context_id'] for p in embedded_json['other_passengers']]
        context_ids.insert(0, embedded_json['passenger']['context_id'])

        # passenger looks at hotel offerings ----
        desired_room_count = 2
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        # passenger books hotel ----
        picked_hotel = hotel_offerings[0]
        booking_response_data = self._passenger_book_hotel(passenger, picked_hotel, context_ids,
                                                           room_count=desired_room_count)

        auth_keys = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
        )

        # simulate passenger app requests related to rides ----

        url = '/api/v1/offer/tvl/ride/airport-pickup-estimate'
        response = requests.get(self._api_host + url, headers=headers, params=auth_keys)
        if response.status_code != 200:
            display_response(response)
        self.assertEqual(response.status_code, 200)
        # TODO: assert more

        url = '/api/v1/offer/tvl/ride/airport-pickup-options'
        response = requests.get(self._api_host + url, headers=headers, params=auth_keys)
        self.assertEqual(response.status_code, 200)
        # TODO: assert more
        #display_response(response)
        selected_pickup_location = response.json()['data']['zones'][0]['locations'][0]


        url = '/api/v1/offer/tvl/ride/airport-to-hotel-ride'
        ride_request_payload = {
            'location_id': selected_pickup_location['id']
        }
        response = requests.post(self._api_host + url, headers=headers, params=auth_keys, json=ride_request_payload)
        #display_response(response)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertFalse(response_json['error'])
        self.assertGreaterEqual(len(response_json['data']['ride_id']), 10)  # sanity check on the id
        self.assertEqual(response_json['data']['status'], 'pending')
        # TODO: assert destination, origin, and passenger details

        url = '/api/v1/offer/tvl/ride/status'
        response = requests.get(self._api_host + url, headers=headers, params=auth_keys)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        #display_response(response)
        # TODO: assert more

        # url = '/api/v1/tvl/webhooks/lyft'
        # headers_from_lyft_system = {
        #     'Accept': '*/*',
        #     'Accept-Encoding': 'gzip,deflate',
        #     'Connection': 'close',
        #     # 'Content-Length':,  # don't bother setting for testing.
        #     'Content-Type': 'application/json',
        #     'Host': 'yourapihere.com',  # TODO: fill in?
        #     'Lyft-Environment': 'sandbox',  # TODO: verify
        #     'User-Agent': 'lyft/webhooks v1',
        #     'X-Lyft-Signature': 'sha256=36kDT4a6W0glwWud/fz079/wQsHlPGie+C73ESbRf2Q=',  # TODO: set different.
        # }
        # payload = {}
        # response = requests.post(self._api_host + url, headers=headers_from_lyft_system, json=payload)
        # self.assertEqual(response.status_code, 200)
        # # TODO: assert morecall some webhooks too.
        #
        # url = '/api/v1/offer/tvl/ride/cancel'
        # response = requests.post(self._api_host + url, headers=headers, params=auth_keys)
        # self.assertEqual(response.status_code, 200)
        # # TODO: assert more

    def test_bad_offer_message(self):
        """
        ensures system reports the right HTTP 404 status code and error message
        when an offer is not found.
        """
        url = self._api_host + '/offer'
        headers = self._generate_passenger_headers()

        expected_embedded_message = \
            'The offer could not be found, has been canceled, or has expired. ' \
            'Please check that the full URL was entered.'

        # bad auth keys ----
        bad_auth_key_pair = dict(
            ak1='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            ak2='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        )
        response = requests.get(url, headers=headers, params=bad_auth_key_pair)
        self.assertEqual(response.status_code, 404)
        self.assertIn(expected_embedded_message, response.text)

        # no auth keys ----
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn(expected_embedded_message, response.text)

        # bad query parameters ----
        garbage_params = dict(
            abcd='1234'
        )
        response = requests.get(url, headers=headers, params=garbage_params)
        self.assertEqual(response.status_code, 404)
        self.assertIn(expected_embedded_message, response.text)

    def test_bad_text_message_redirect(self):
        headers = self._generate_passenger_headers()
        expected_embedded_message = 'Invalid or expired link.'

        # good signing, bad offer (garbage that came from someone messing around on the short url site.) ---
        url = self._api_host + '/offer/sms-redirect/eyJzIjoiQW9zTUQ5YmNKIn0.Dr_cqQ.iKhDHUovjwAih7lkWgbfU6i1vwE'
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn(expected_embedded_message, response.text)

        # bad signing, garbage redirect that did not come from short url site.. ----
        url = self._api_host + '/offer/sms-redirect/aaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn(expected_embedded_message, response.text)
