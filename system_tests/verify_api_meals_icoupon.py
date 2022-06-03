import requests
from uuid import UUID

from stormx_verification_framework import (
    StormxSystemVerification,
    display_response,
    log_error_system_tests_output,
    passenger_sanitized_fields,
    pretty_print_json,
    should_skip_local_test,
    uses_expedia,
)


class TestApiMealsICoupon(StormxSystemVerification):
    """
    Verify general hotel booking behavior.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiMealsICoupon, cls).setUpClass()

    def test_airline_book_hotel_with_icoupon_and_tvl_meals(self):
        """
        verify that an airline can book a hotel for a passenger.
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        url = self._api_host + '/api/v1/hotels'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers_payload = self._generate_2_passenger_payload(
            customer=customer,
            port_accommodation='LHR',
            meal_accommodation=True,
        )
        passengers_payload[0]['meals'] = [
            {'currency_code': 'GBP', 'meal_amount': '8.00', 'number_of_days': 1},  # no provider listed.
            {'currency_code': 'GBP', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 1},
        ]
        passengers_payload[1]['meals'] = [
            {'currency_code': 'GBP', 'meal_amount': '10.00', 'provider': 'icoupon', 'number_of_days': 1},
            {'currency_code': 'GBP', 'meal_amount': '11.00', 'provider': 'tvl', 'number_of_days': 1},
        ]
        passenger_context_ids = [p['context_id'] for p in passengers_payload]
        passenger_1_context_id = passenger_context_ids[0]
        passenger_2_context_id = passenger_context_ids[1]
        response = requests.post(passenger_url, headers=headers,
                                 json=passengers_payload)  # TODO: replace with API client.
        #display_response(response)
        self.assertEqual(response.status_code, 201)
        passengers = response.json()['data']

        for passenger in passengers:
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')

        port = passengers[0]['port_accommodation']
        room_count = 1
        hotels = self._airline_get_passenger_hotel_offerings(customer, port, room_count)
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
        for passenger in response_json['data']['passengers']:
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertEqual(len(passenger['meal_vouchers']), 2)
            for meal in passenger['meal_vouchers']:
                UUID(meal['id'], version=4)

        passengers = response_json['data']['passengers']
        passenger_1 = next(filter(lambda p: p['context_id'] == passenger_1_context_id, passengers))
        passenger_2 = next(filter(lambda p: p['context_id'] == passenger_2_context_id, passengers))

        meal_8 = next(filter(lambda m: m['amount'] == '8.00', passenger_1['meal_vouchers']))
        meal_9 = next(filter(lambda m: m['amount'] == '9.00', passenger_1['meal_vouchers']))
        meal_10 = next(filter(lambda m: m['amount'] == '10.00', passenger_2['meal_vouchers']))
        meal_11 = next(filter(lambda m: m['amount'] == '11.00', passenger_2['meal_vouchers']))

        self.assertEqual(meal_8['provider'], 'tvl')
        self.assertEqual(meal_8['currency_code'], 'GBP')
        self.assertEqual(meal_8['billing_zip_code'], '55343')
        self.assertEqual(len(meal_8['active_from']), 16)
        self.assertEqual(len(meal_8['active_to']), 16)
        self.assertEqual(len(meal_8['cvc2']), 4)
        self.assertEqual(meal_8['time_zone'], 'Europe/London')
        self.assertEqual(meal_8['card_type'], 'MASTERCARD')
        self.assertEqual(len(meal_8['expiration']), 7)
        self.assertGreater(len(meal_8['qr_code_url']), 100)
        self.assertEqual(len(meal_8['id']), 36)

        self.assertEqual(meal_9['provider'], 'icoupon')
        self.assertEqual(meal_9['currency_code'], 'GBP')
        self.assertEqual(meal_9['billing_zip_code'], None)
        self.assertEqual(len(meal_9['active_from']), 16)
        self.assertEqual(len(meal_9['active_to']), 16)
        self.assertIs(meal_9['cvc2'], None)
        self.assertEqual(meal_9['time_zone'], 'Europe/London')
        self.assertIs(meal_9['card_type'], None)
        self.assertIs(meal_9['expiration'], None)
        self.assertGreater(len(meal_9['qr_code_url']), 100)
        self.assertEqual(len(meal_9['id']), 36)

        self.assertEqual(meal_10['provider'], 'icoupon')
        self.assertEqual(meal_10['currency_code'], 'GBP')
        self.assertEqual(meal_10['billing_zip_code'], None)
        self.assertEqual(len(meal_10['active_from']), 16)
        self.assertEqual(len(meal_10['active_to']), 16)
        self.assertIs(meal_10['cvc2'], None)
        self.assertEqual(meal_10['time_zone'], 'Europe/London')
        self.assertIs(meal_10['card_type'], None)
        self.assertIs(meal_10['expiration'], None)
        self.assertGreater(len(meal_10['qr_code_url']), 100)
        self.assertEqual(len(meal_10['id']), 36)

        self.assertEqual(meal_11['provider'], 'tvl')
        self.assertEqual(meal_11['currency_code'], 'GBP')
        self.assertEqual(meal_11['billing_zip_code'], '55343')
        self.assertEqual(len(meal_11['active_from']), 16)
        self.assertEqual(len(meal_11['active_to']), 16)
        self.assertEqual(len(meal_11['cvc2']), 4)
        self.assertEqual(meal_11['time_zone'], 'Europe/London')
        self.assertEqual(meal_11['card_type'], 'MASTERCARD')
        self.assertEqual(len(meal_11['expiration']), 7)
        self.assertGreater(len(meal_11['qr_code_url']), 100)
        self.assertEqual(len(meal_11['id']), 36)

        # verify voucher endpoint for passenger 1 ----
        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + response_json['data']['voucher_id'],
                                    headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        passengers = voucher_resp_json['data']['passengers']
        passenger_1 = next(filter(lambda p: p['context_id'] == passenger_1_context_id, passengers))
        meal_8 = next(filter(lambda m: m['amount'] == '8.00', passenger_1['meal_vouchers']))
        meal_9 = next(filter(lambda m: m['amount'] == '9.00', passenger_1['meal_vouchers']))
        for meal in passenger_1['meal_vouchers']:
            UUID(meal['id'], version=4)

        self.assertEqual(meal_8['provider'], 'tvl')
        self.assertEqual(meal_8['currency_code'], 'GBP')
        self.assertEqual(meal_8['billing_zip_code'], '55343')
        self.assertEqual(len(meal_8['active_from']), 16)
        self.assertEqual(len(meal_8['active_to']), 16)
        self.assertEqual(len(meal_8['cvc2']), 4)
        self.assertEqual(meal_8['time_zone'], 'Europe/London')
        self.assertEqual(meal_8['card_type'], 'MASTERCARD')
        self.assertEqual(len(meal_8['expiration']), 7)
        self.assertGreater(len(meal_8['qr_code_url']), 100)
        self.assertEqual(len(meal_8['id']), 36)

        self.assertEqual(meal_9['provider'], 'icoupon')
        self.assertEqual(meal_9['currency_code'], 'GBP')
        self.assertEqual(meal_9['billing_zip_code'], None)
        self.assertEqual(len(meal_9['active_from']), 16)
        self.assertEqual(len(meal_9['active_to']), 16)
        self.assertIs(meal_9['cvc2'], None)
        self.assertEqual(meal_9['time_zone'], 'Europe/London')
        self.assertIs(meal_9['card_type'], None)
        self.assertIs(meal_9['expiration'], None)
        self.assertGreater(len(meal_9['qr_code_url']), 100)
        self.assertEqual(len(meal_9['id']), 36)

        # verify meal vouchers on passenger 1 full state
        url1 = self._api_host + '/api/v1/passenger/{context_id}/state'.format(context_id=passenger_1_context_id)
        headers = self._generate_airline_headers(customer=customer)
        response1 = requests.get(url=url1, headers=headers).json()
        meal_vouchers = response1['data']['voucher']['meal_vouchers']
        self.assertEqual(len(meal_vouchers), 2)
        for meal in meal_vouchers:
            UUID(meal['id'], version=4)
        meal_8 = next(filter(lambda m: m['amount'] == '8.00', meal_vouchers))
        meal_9 = next(filter(lambda m: m['amount'] == '9.00', meal_vouchers))

        self.assertEqual(meal_8['provider'], 'tvl')
        self.assertEqual(meal_8['currency_code'], 'GBP')
        self.assertEqual(meal_8['billing_zip_code'], '55343')
        self.assertEqual(len(meal_8['active_from']), 16)
        self.assertEqual(len(meal_8['active_to']), 16)
        self.assertEqual(len(meal_8['cvc2']), 4)
        self.assertEqual(meal_8['time_zone'], 'Europe/London')
        self.assertEqual(meal_8['card_type'], 'MASTERCARD')
        self.assertEqual(len(meal_8['expiration']), 7)
        self.assertGreater(len(meal_8['qr_code_url']), 100)
        self.assertEqual(len(meal_8['id']), 36)

        self.assertEqual(meal_9['provider'], 'icoupon')
        self.assertEqual(meal_9['currency_code'], 'GBP')
        self.assertEqual(meal_9['billing_zip_code'], None)
        self.assertEqual(len(meal_9['active_from']), 16)
        self.assertEqual(len(meal_9['active_to']), 16)
        self.assertIs(meal_9['cvc2'], None)
        self.assertEqual(meal_9['time_zone'], 'Europe/London')
        self.assertIs(meal_9['card_type'], None)
        self.assertIs(meal_9['expiration'], None)
        self.assertGreater(len(meal_9['qr_code_url']), 100)
        self.assertEqual(len(meal_9['id']), 36)

    def test_icoupon_enabled_flag(self):
        """
        verify that airlines without iCoupon are blocked from importing iCoupon meals.
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'  # airline with iCoupon disabled
        headers = self._generate_airline_headers(customer=customer)

        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='LHR', meal_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'GBP', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'FEATURE_NOT_SUPPORTED', 'iCoupon is currently not enabled.', [])

    def test_meal_provider_interface_is_available_for_icoupon_disabled_airline(self):
        """
        validate that the enabled flag is respected for iCoupon
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'  # customer which does not have iCoupon enabled.
        airline_client = self.get_airline_api_client(customer)

        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='LAX', meal_accommodation=True)
        passengers = airline_client.import_passengers(passengers_payload)
        hotels = airline_client.get_hotels(port='LAX', room_count=1)
        context_ids = [passenger['context_id'] for passenger in passengers]
        voucher = airline_client.book_hotel(context_ids=context_ids, hotel_id=hotels[0]['hotel_id'], room_count=1)
        for meal in voucher['passengers'][0]['meal_vouchers']:
            self.assertEqual(meal['provider'], 'tvl')

    def test_validate_icoupon_expected_currency(self):
        """
        validate that expected currency is being implemented for iCoupon
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # meal only validation
        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='LHR', meal_accommodation=True, hotel_accommodation=False)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'USD', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'MEAL_CANNOT_BE_PROCESSED',
                                     'The requested meal currency USD is not the same as the expected local currency GBP', [])

        # potential booking validation
        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='BUD', meal_accommodation=True, hotel_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'GBP', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'MEAL_CANNOT_BE_PROCESSED',
                                     'The requested meal currency GBP is not the same as the expected local currency HUF', [])

    def test_validate_icoupon_number_of_days(self):
        """
        validate that max number_of_days is respected for iCoupon
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='LHR', meal_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'GBP', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 2},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'FEATURE_NOT_SUPPORTED', 'iCoupon meal vouchers only support number_of_days=1.', [])

    def test_icoupon_offer_decline(self):
        """
        validate iCoupon works on offer/decline
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # add inventory
        event_date = self._get_event_date('Europe/London')
        self.add_hotel_availability(86329, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # airline booking validation
        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='LHR', meal_accommodation=True, hotel_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'GBP', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)
        passenger = response.json()['data'][0]

        # public decline
        decline_url = self._api_host + '/api/v1/offer/decline?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        response = requests.put(decline_url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_icoupon_airline_decline(self):
        """
        validate iCoupon works on airline api decline
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # add inventory
        event_date = self._get_event_date('Europe/London')
        self.add_hotel_availability(86329, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # airline booking validation
        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='LHR', meal_accommodation=True, hotel_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'GBP', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)
        passenger = response.json()['data'][0]

        # decline
        decline_offer_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/decline'
        response = requests.put(decline_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_icoupon_offer_hotel(self):
        """
        validate iCoupon works on offer/hotel
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # add inventory
        event_date = self._get_event_date('Europe/Budapest')
        self.add_hotel_availability(108748, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # airline booking validation
        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='BUD', meal_accommodation=True, hotel_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'HUF', 'meal_amount': '9.00', 'provider': 'icoupon', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)
        passenger = response.json()['data'][0]

        payload = dict(
            context_ids=[passenger['context_id']],
            room_count=1,
            hotel_id='tvl-108748'
        )

        # public hotels
        offer_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        response = requests.post(offer_url, headers=headers, json=payload)
        self.assertEqual(response.status_code, 200)

    def test_meal_validator(self):
        """
        validates various meal voucher validation on import
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # validate HUF not supported with default provider (first pax first meal)
        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='BUD', meal_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'HUF', 'meal_amount': '9.00', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[0].meals[0].currency_code', 'message': '"HUF" is not a valid choice.'}])

        # validate HUF not supported with TVL provider (first pax second meal)
        passengers_payload = self._generate_n_passenger_payload(1, customer=customer, port_accommodation='BUD', meal_accommodation=True)
        passengers_payload[0]['meals'] = [
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
            {'currency_code': 'HUF', 'meal_amount': '9.00', 'number_of_days': 1, 'provider': 'tvl'},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[0].meals[1].currency_code', 'message': '"HUF" is not a valid choice.'}])

        # validate currency field required (second pax first meal)
        passengers_payload = self._generate_n_passenger_payload(2, customer=customer, port_accommodation='BUD', meal_accommodation=True)
        passengers_payload[1]['meals'] = [
            {'meal_amount': '9.00', 'number_of_days': 1},
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[1].meals[0].currency_code', 'message': 'This field is required.'}])

        # validate currency field cannot be NULL (second pax second meal)
        passengers_payload = self._generate_n_passenger_payload(3, customer=customer, port_accommodation='BUD', meal_accommodation=True)
        passengers_payload[1]['meals'] = [
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
            {'meal_amount': '9.00', 'number_of_days': 1, 'currency_code': None}
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[1].meals[1].currency_code', 'message': 'This field may not be null.'}])

        # validate currency field cannot be MOM (third pax second meal)
        passengers_payload = self._generate_n_passenger_payload(3, customer=customer, port_accommodation='BUD', meal_accommodation=True)
        passengers_payload[2]['meals'] = [
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
            {'meal_amount': '9.00', 'number_of_days': 1, 'currency_code': 'MOM'}
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[2].meals[1].currency_code', 'message': '"MOM" is not a valid choice.'}])

        # validate currency field cannot be CUP for TVL (third pax second meal)
        passengers_payload = self._generate_n_passenger_payload(3, customer=customer, port_accommodation='CAE', meal_accommodation=True)
        passengers_payload[2]['meals'] = [
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
            {'meal_amount': '9.00', 'number_of_days': 1, 'currency_code': 'MOM'}
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[2].meals[1].currency_code', 'message': '"MOM" is not a valid choice.'}])

        # validate currency field cannot be CUP for TVL (third pax second meal)
        passengers_payload = self._generate_n_passenger_payload(3, customer=customer, port_accommodation='CAE', meal_accommodation=True)
        passengers_payload[2]['meals'] = [
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
            {'meal_amount': '9.00', 'number_of_days': 1, 'currency_code': 'COP'},
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[2].meals[1].currency_code', 'message': '"COP" is not a valid choice.'}])

        # validate currency field cannot be CUP for TVL (third pax third meal)
        passengers_payload = self._generate_n_passenger_payload(3, customer=customer, port_accommodation='CAE', meal_accommodation=True)
        passengers_payload[2]['meals'] = [
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
            {'currency_code': 'USD', 'meal_amount': '9.00', 'number_of_days': 1},
            {'meal_amount': '9.00', 'number_of_days': 1, 'currency_code': 'COP'}
        ]

        response = requests.post(passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[2].meals[2].currency_code', 'message': '"COP" is not a valid choice.'}])
