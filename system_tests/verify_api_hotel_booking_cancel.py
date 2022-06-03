import requests
from uuid import UUID

from StormxApp.tests.data_utilities import (
    generate_pax_record_locator_group,
)

from stormx_verification_framework import (
    StormxSystemVerification,
    log_error_system_tests_output,
    pretty_print_json,
    uses_expedia,
)


class TestApiHotelBookingCancel(StormxSystemVerification):
    """
    Verify voucher cancellation.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBookingCancel, cls).setUpClass()

    def test_offer_cancel_hotel_with_meals_notifications_multiple_pax(self):
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[0].update(dict(
            notify=True
        ))
        passenger_payload[1].update(dict(
            notify=True,
            pax_record_locator=passenger_payload[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload[0]['pax_record_locator_group'],
            emails=['email1@tvl.blackhole.com'],
            phone_numbers=['+12223334444']
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passengers = import_response_json['data']

        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

        hotel_offerings = self._get_passenger_hotel_offerings(passengers[0])
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passengers[0]['context_id'], passengers[1]['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        booking_response_json = booking_response.json()['data']
        self.assertEqual(len(booking_response_json['passengers']), 2)
        for passenger in booking_response_json['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])

        passenger1 = booking_response_json['passengers'][0]
        passenger2 = booking_response_json['passengers'][1]

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertNotIn('voucher_id', cancel_response_json['data'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 2)
        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 6)
            self.assertEqual(len(passenger['meal_vouchers']), 2)
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_voucher')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger1['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger2['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])

    def test_cancel_hotel_multiple_passengers_booked(self):
        """
        verify all passengers on same pnr have a status of canceled after canceling a hotel
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(3)
        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]
        passenger2 = import_response_json['data'][1]
        passenger3 = import_response_json['data'][2]

        hotel_offerings = self._get_passenger_hotel_offerings(passenger)
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id'], passenger3['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        for passenger in booking_response.json()['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertEqual(passenger['transport_accommodation_status'], None)
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertIsNone(passenger['declined_date'])
            self.assertIsNone(passenger['canceled_date'])

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher']['id'])
        self.assertIsNotNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 3)

        voucher_id = cancel_response_json['data']['voucher_id']
        UUID(voucher_id, version=4)
        expected_canceled_date = cancel_response_json['data']['passengers'][0]['canceled_date']
        self.assertIsNotNone(expected_canceled_date)

        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 0)
            self.assertEqual(len(passenger['meal_vouchers']), 2)
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_voucher')
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertEqual(passenger['canceled_date'], expected_canceled_date)
            self.assertIsNone(passenger['declined_date'])

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + voucher_id, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        for passenger in voucher_resp_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_voucher')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertEqual(passenger['canceled_date'], expected_canceled_date)
            self.assertIsNone(passenger['declined_date'])

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(get_passenger_response['data']['transport_accommodation_status'], None)
        self.assertIn('offer_opened_date', get_passenger_response['data'])
        self.assertIn('declined_date', get_passenger_response['data'])
        self.assertIn('canceled_date', get_passenger_response['data'])
        self.assertIsNone(get_passenger_response['data']['offer_opened_date'])
        self.assertEqual(get_passenger_response['data']['canceled_date'], expected_canceled_date)
        self.assertIsNone(get_passenger_response['data']['declined_date'])

        get_passenger_url2 = self._api_host + '/api/v1/passenger/' + passenger2['context_id']
        get_passenger_response2 = requests.get(url=get_passenger_url2, headers=headers).json()
        self.assertEqual(get_passenger_response2['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response2['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(get_passenger_response2['data']['transport_accommodation_status'], None)
        self.assertIn('offer_opened_date', get_passenger_response2['data'])
        self.assertIn('declined_date', get_passenger_response2['data'])
        self.assertIn('canceled_date', get_passenger_response2['data'])
        self.assertIsNone(get_passenger_response2['data']['offer_opened_date'])
        self.assertEqual(get_passenger_response2['data']['canceled_date'], expected_canceled_date)
        self.assertIsNone(get_passenger_response2['data']['declined_date'])

        get_passenger_url3 = self._api_host + '/api/v1/passenger/' + passenger3['context_id']
        get_passenger_response3 = requests.get(url=get_passenger_url3, headers=headers).json()
        self.assertEqual(get_passenger_response3['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response3['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(get_passenger_response3['data']['transport_accommodation_status'], None)
        self.assertIn('offer_opened_date', get_passenger_response3['data'])
        self.assertIn('declined_date', get_passenger_response3['data'])
        self.assertIn('canceled_date', get_passenger_response3['data'])
        self.assertIsNone(get_passenger_response3['data']['offer_opened_date'])
        self.assertEqual(get_passenger_response3['data']['canceled_date'], expected_canceled_date)
        self.assertIsNone(get_passenger_response3['data']['declined_date'])

    def test_cancel_hotel_multiple_passengers_offered(self):
        """
        verify all passengers on same pnr have a status of canceled after
        canceling an offer without booking a hotel
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(3)
        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]
        passenger2 = import_response_json['data'][1]
        passenger3 = import_response_json['data'][2]

        for passenger in import_response_json['data']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')
            self.assertEqual(passenger['transport_accommodation_status'], None)

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 3)

        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 0)
            self.assertEqual(len(passenger['meal_vouchers']), 0)
            self.assertEqual(passenger['meal_accommodation_status'], 'canceled_offer')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_offer')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['transport_accommodation_status'], None)

        get_passenger_url2 = self._api_host + '/api/v1/passenger/' + passenger2['context_id']
        get_passenger_response2 = requests.get(url=get_passenger_url2, headers=headers).json()
        self.assertEqual(get_passenger_response2['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response2['data']['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response2['data']['transport_accommodation_status'], None)

        get_passenger_url3 = self._api_host + '/api/v1/passenger/' + passenger3['context_id']
        get_passenger_response3 = requests.get(url=get_passenger_url3, headers=headers).json()
        self.assertEqual(get_passenger_response3['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response3['data']['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response3['data']['transport_accommodation_status'], None)

    def test_cancel_hotel_multiple_passengers_booked_no_meals(self):
        """
        verify all passengers on same pnr have a status of canceled after canceling a hotel with no meals
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(3)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))
        passenger_payload[1].update(dict(
            meal_accommodation=False
        ))
        passenger_payload[2].update(dict(
            meal_accommodation=False
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]
        passenger2 = import_response_json['data'][1]
        passenger3 = import_response_json['data'][2]

        hotel_offerings = self._get_passenger_hotel_offerings(passenger)
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id'], passenger3['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNotNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 3)

        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 0)
            self.assertEqual(len(passenger['meal_vouchers']), 0)
            self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_voucher')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response['data']['transport_accommodation_status'], None)

        get_passenger_url2 = self._api_host + '/api/v1/passenger/' + passenger2['context_id']
        get_passenger_response2 = requests.get(url=get_passenger_url2, headers=headers).json()
        self.assertEqual(get_passenger_response2['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response2['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response2['data']['transport_accommodation_status'], None)

        get_passenger_url3 = self._api_host + '/api/v1/passenger/' + passenger3['context_id']
        get_passenger_response3 = requests.get(url=get_passenger_url3, headers=headers).json()
        self.assertEqual(get_passenger_response3['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response3['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response3['data']['transport_accommodation_status'], None)

    def test_cancel_hotel_multiple_passengers_offered_no_meals(self):
        """
        verify all passengers on same pnr have a status of canceled after
        canceling an offer without booking a hotel with no meals
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(3)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))
        passenger_payload[1].update(dict(
            meal_accommodation=False
        ))
        passenger_payload[2].update(dict(
            meal_accommodation=False
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]
        passenger2 = import_response_json['data'][1]
        passenger3 = import_response_json['data'][2]

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 3)

        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 0)
            self.assertEqual(len(passenger['meal_vouchers']), 0)
            self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_offer')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response['data']['transport_accommodation_status'], None)

        get_passenger_url2 = self._api_host + '/api/v1/passenger/' + passenger2['context_id']
        get_passenger_response2 = requests.get(url=get_passenger_url2, headers=headers).json()
        self.assertEqual(get_passenger_response2['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response2['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response2['data']['transport_accommodation_status'], None)

        get_passenger_url3 = self._api_host + '/api/v1/passenger/' + passenger3['context_id']
        get_passenger_response3 = requests.get(url=get_passenger_url3, headers=headers).json()
        self.assertEqual(get_passenger_response3['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response3['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response3['data']['transport_accommodation_status'], None)

    def test_cancel_hotel_single_passenger_booked_no_meals(self):
        """
        verify single passenger has a status of canceled after canceling a hotel with no meals
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['transport_accommodation_status'], None)

        hotel_offerings = self._get_passenger_hotel_offerings(passenger)
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        booking_response_json_pax_data = booking_response.json()['data']['passengers'][0]
        self.assertEqual(booking_response_json_pax_data['hotel_accommodation_status'], 'accepted')
        self.assertEqual(booking_response_json_pax_data['meal_accommodation_status'], 'not_offered')
        self.assertEqual(booking_response_json_pax_data['transport_accommodation_status'], None)

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIn('modified_date', cancel_response_json['data'])
        self.assertEqual(cancel_response_json['data']['status'], 'canceled')

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNotNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 1)

        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 0)
            self.assertEqual(len(passenger['meal_vouchers']), 0)
            self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_voucher')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response['data']['transport_accommodation_status'], None)

        canceled_state_resp = requests.get(url=get_passenger_url + '/state', headers=headers).json()
        self.assertEqual(canceled_state_resp['data']['passenger']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(canceled_state_resp['data']['voucher']['status'], 'canceled')
        self.assertIsNotNone(canceled_state_resp['data']['voucher']['hotel_voucher'])

    def test_cancel_hotel_single_passenger_offered_no_meals(self):
        """
        verify single passenger has a status of canceled after canceling a hotel offer with no meals
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 1)

        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 0)
            self.assertEqual(len(passenger['meal_vouchers']), 0)
            self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_offer')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(get_passenger_response['data']['transport_accommodation_status'], None)

    def test_cancel_hotel_multiple_passengers_offered_diff_group(self):
        """
        verify passengers on different pnr do not get canceled together
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(3)
        passenger_payload[2].update(dict(
            pax_record_locator_group=generate_pax_record_locator_group()
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)

        passenger = passenger_payload[0]
        passenger2 = passenger_payload[1]
        passenger3 = passenger_payload[2]

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 2)

        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 0)
            self.assertEqual(len(passenger['meal_vouchers']), 0)
            self.assertEqual(passenger['meal_accommodation_status'], 'canceled_offer')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_offer')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['transport_accommodation_status'], None)

        get_passenger_url2 = self._api_host + '/api/v1/passenger/' + passenger2['context_id']
        get_passenger_response2 = requests.get(url=get_passenger_url2, headers=headers).json()
        self.assertEqual(get_passenger_response2['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response2['data']['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response2['data']['transport_accommodation_status'], None)

        get_passenger_url3 = self._api_host + '/api/v1/passenger/' + passenger3['context_id']
        get_passenger_response3 = requests.get(url=get_passenger_url3, headers=headers).json()
        self.assertEqual(get_passenger_response3['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(get_passenger_response3['data']['meal_accommodation_status'], 'offered')
        self.assertEqual(get_passenger_response3['data']['transport_accommodation_status'], None)

    def test_meal_only_passenger_cannot_cancel(self):
        """
        verifies system will not allow the cancel service to run if passenger has a meal-only voucher
        """
        expected_error_message = 'Passenger cannot cancel a meal-only voucher.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer, hotel_accommodation=False)
        passenger = passengers[0]
        self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger['hotel_accommodation_status'], 'not_offered')
        self.assertIsNone(passenger['transport_accommodation_status'])
        self.assertIsNotNone(passenger['voucher_id'])

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        cancel_resp_json = cancel_resp.json()
        self.assertEqual(cancel_resp.status_code, 400)
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL', expected_error_message, [])

    def test_declined_passenger_cannot_cancel(self):
        """
        verifies system will not allow the cancel service to run if passenger is in a declined state
        """
        expected_error_message = 'Passenger cannot cancel offer. Passenger has already declined the offer.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer)
        passenger = passengers[0]
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        deny_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/decline?include_pnr=true&meals=true'
        deny_resp = requests.put(url=deny_url, headers=headers)
        self.assertEqual(deny_resp.status_code, 200)

        deny_resp_json = deny_resp.json()
        self.assertEqual(deny_resp_json['meta']['status'], 200)
        self.assertEqual(deny_resp_json['data']['passengers'][0]['meal_accommodation_status'], 'declined')
        self.assertEqual(deny_resp_json['data']['passengers'][0]['hotel_accommodation_status'], 'declined')
        self.assertIsNone(deny_resp_json['data']['passengers'][0]['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 400)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL', expected_error_message, [])

    def test_canceled_passenger_cannot_cancel(self):
        """
        verifies system will not allow the cancel service to run if passenger is in a canceled state
        """
        expected_error_message = 'Passenger cannot cancel offer. Passenger has already canceled the offer.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer)
        passenger = passengers[0]
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 200)

        cancel_resp_json = cancel_resp.json()
        self.assertEqual(cancel_resp_json['meta']['status'], 200)
        self.assertEqual(cancel_resp_json['data']['passengers'][0]['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(cancel_resp_json['data']['passengers'][0]['hotel_accommodation_status'], 'canceled_offer')
        self.assertIsNone(cancel_resp_json['data']['passengers'][0]['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 400)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL', expected_error_message, [])

    def test_meal_only_offer_cannot_cancel(self):
        """
        verifies system will not allow the cancel service to run if passenger has a meal-only voucher
        """
        expected_error_message = 'Passenger cannot cancel a meal-only voucher.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer, hotel_accommodation=False)
        passenger = passengers[0]
        self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger['hotel_accommodation_status'], 'not_offered')
        self.assertIsNone(passenger['transport_accommodation_status'])
        self.assertIsNotNone(passenger['voucher_id'])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 400)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL', expected_error_message, [])

    def test_declined_offer_cannot_cancel(self):
        """
        verifies system will not allow the cancel service to run if passenger is in a declined state
        """
        expected_error_message = 'Passenger cannot cancel offer. Passenger has already declined the offer.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer)
        passenger = passengers[0]
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        deny_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/decline?include_pnr=true&meals=true'
        deny_resp = requests.put(url=deny_url, headers=headers)
        self.assertEqual(deny_resp.status_code, 200)

        deny_resp_json = deny_resp.json()
        self.assertEqual(deny_resp_json['meta']['status'], 200)
        self.assertEqual(deny_resp_json['data']['passengers'][0]['meal_accommodation_status'], 'declined')
        self.assertEqual(deny_resp_json['data']['passengers'][0]['hotel_accommodation_status'], 'declined')
        self.assertIsNone(deny_resp_json['data']['passengers'][0]['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 400)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL', expected_error_message, [])

    def test_canceled_offer_cannot_cancel(self):
        """
        verifies system will not allow the cancel service to run if passenger is in a canceled state
        """
        expected_error_message = 'Passenger cannot cancel offer. Passenger has already canceled the offer.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer)
        passenger = passengers[0]
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 200)

        cancel_resp_json = cancel_resp.json()
        self.assertEqual(cancel_resp_json['meta']['status'], 200)
        self.assertEqual(cancel_resp_json['data']['passengers'][0]['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(cancel_resp_json['data']['passengers'][0]['hotel_accommodation_status'], 'canceled_offer')
        self.assertIsNone(cancel_resp_json['data']['passengers'][0]['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 400)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL', expected_error_message, [])

    def test_offer_cancel_401_and_404(self):
        """
        verifies system throws 401 and 404 when calling offer/cancel endpoint
        """
        expected_401_message = 'Unauthorized'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer, hotel_accommodation=False)
        passenger = passengers[0]
        passenger2 = passengers[1]

        cancel_url = self._api_host + '/api/v1/offer/cancel'
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 401)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 401, expected_401_message, '', '', [])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 401)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 401, expected_401_message, '', '', [])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak2=' + passenger['ak2']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 401)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 401, expected_401_message, '', '', [])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=googoogaga' + '&ak2=' + passenger2['ak2']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 401)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 401, expected_401_message, '', '', [])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1'] + '&ak2=' + passenger2['ak2']
        cancel_resp = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_resp.status_code, 401)
        cancel_resp_json = cancel_resp.json()
        log_error_system_tests_output(pretty_print_json(cancel_resp_json))
        self._validate_error_message(cancel_resp_json, 401, expected_401_message, '', '', [])

    def test_cancel_hotel_no_meals_and_notifications_single_pax_500_error(self):
        """
        reproducing a 500 error from canceling a hotel with notifications and no meals for AA
        """
        customer = 'American Airlines'  # must be AA (Purple Rain will not reproduce)
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            notify=True,
            meal_accommodation=False,
            phone_numbers=[]
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        hotel_offerings = self._get_passenger_hotel_offerings(passenger)
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        booking_response_json = booking_response.json()['data']
        self.assertEqual(booking_response_json['passengers'][0]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(booking_response_json['passengers'][0]['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(booking_response_json['passengers'][0]['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNotNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 1)
        self.assertEqual(len(canceled_passengers[0]['notifications']), 3)
        self.assertEqual(len(canceled_passengers[0]['meal_vouchers']), 0)
        self.assertEqual(canceled_passengers[0]['meal_accommodation_status'], 'not_offered')
        self.assertEqual(canceled_passengers[0]['hotel_accommodation_status'], 'canceled_voucher')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])

    @uses_expedia
    def test_ean_booking_cannot_cancel(self):
        """
        validate an expedia booking cannot be canceled
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger'

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)

        hotel_response = requests.get(hotel_url + '?room_count=1&port=' + port + '&provider=ean', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0, msg='no expedia inventory for ' + repr(port))

        ean_offer = hotel_response_json['data'][0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=1
        )

        booking_response = requests.post(url=hotel_url, headers=headers, data=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertEqual(booking_response_json['meta']['error_code'], '')
        ean_voucher = booking_response_json['data']

        self.assertEqual(ean_voucher['hotel_voucher']['provider'], 'ean')
        self.assertEqual(ean_voucher['hotel_voucher']['hotel_id'], ean_offer)
        # self.assertEqual(ean_voucher['hotel_voucher']['tax'], '0.00')  # TODO: change once breaks
        # self.assertEqual(ean_voucher['hotel_voucher']['total_amount'], '0.00')  # TODO: change once breaks
        self.assertEqual(len(ean_voucher['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(ean_voucher['hotel_voucher']['room_vouchers'][0]['count'], 1)
        # self.assertEqual(ean_voucher['hotel_voucher']['room_vouchers'][0]['rate'], '0.00')  # TODO: change once breaks
        self.assertEqual({passenger['context_id'] for passenger in passengers},
                         {passenger['context_id'] for passenger in ean_voucher['passengers']})

        cancel_response = requests.put(url=passenger_url + '/' + passengers[0]['context_id'] + '/cancel',
                                       headers=headers)
        self.assertEqual(cancel_response.status_code, 400)
        self._validate_error_message(cancel_response.json(), 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL',
                                     'This booking is non-refundable and cannot be canceled.', [])
