from uuid import UUID
from decimal import Decimal

import requests


from stormx_verification_framework import (
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output
)


class TestApiHotelBookingPets(StormxSystemVerification):
    """
    Verify some of the pet and service pet scenarios for hotel bookings.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBookingPets, cls).setUpClass()

    def test_pet_booking(self):
        """
        verifies system can book a pet room
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=1,
            hotel_id='tvl-80657'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(len(hotel_voucher['fees']), 1)
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))

        full_state = requests.get(url=passenger_url + '/' + response_json['data'][0]['context_id'] + '/state', headers=headers).json()
        hotel_voucher = full_state['data']['voucher']['hotel_voucher']
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))

    def test_pet_and_service_pet_booking(self):
        """
        verifies system can book a pet room and service pet
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('America/Chicago')
        self.add_hotel_availability(87521, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='LGW',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True,
            service_pet=True
        ))

        passenger_payload[1].update(dict(
            port_accommodation='LGW',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True,
            service_pet=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=2,
            hotel_id='tvl-87521'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(len(hotel_voucher['fees']), 2)

        validated_pet_fee = False
        validated_service_pet_fee = False
        fees_sum = Decimal('0.00')
        for fee in hotel_voucher['fees']:
            if fee['type'] == 'pet':
                self.assertEqual(fee['rate'], hotel_voucher['pets_fee'])
                self.assertEqual(fee['type'], 'pet')
                self.assertEqual(fee['count'], 2)
                self.assertGreater(Decimal(fee['rate']), 0)
                self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
                fees_sum += Decimal(fee['total'])
                validated_pet_fee = True
            else:
                self.assertEqual(fee['rate'], hotel_voucher['service_pets_fee'])
                self.assertEqual(fee['type'], 'service_pet')
                self.assertEqual(fee['count'], 1)
                self.assertGreater(Decimal(fee['rate']), 0)
                self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
                fees_sum += Decimal(fee['total'])
                validated_service_pet_fee = True
        self.assertEqual(hotel_voucher['total_amount'], str(fees_sum + Decimal(hotel_voucher['room_vouchers'][0]['rate']) * 2 + Decimal(hotel_voucher['tax'])))
        self.assertTrue(validated_pet_fee)
        self.assertTrue(validated_service_pet_fee)

    def test_pet_and_service_pet_booking_aa(self):
        """
        verifies system can book a pet room and service pet
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('America/Chicago')
        self.add_hotel_availability(87521, 71, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='LGW',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True,
            service_pet=True
        ))

        passenger_payload[1].update(dict(
            port_accommodation='LGW',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True,
            service_pet=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=2,
            hotel_id='tvl-87521'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(len(hotel_voucher['fees']), 2)

        validated_pet_fee = False
        validated_service_pet_fee = False
        fees_sum = Decimal('0.00')
        for fee in hotel_voucher['fees']:
            if fee['type'] == 'pet':
                self.assertEqual(fee['rate'], hotel_voucher['pets_fee'])
                self.assertEqual(fee['type'], 'pet')
                self.assertEqual(fee['count'], 2)
                self.assertGreater(Decimal(fee['rate']), 0)
                self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
                fees_sum += Decimal(fee['total'])
                validated_pet_fee = True
            else:
                self.assertEqual(fee['rate'], hotel_voucher['service_pets_fee'])
                self.assertEqual(fee['type'], 'service_pet')
                self.assertEqual(fee['count'], 1)
                self.assertGreater(Decimal(fee['rate']), 0)
                self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
                fees_sum += Decimal(fee['total'])
                validated_service_pet_fee = True
        self.assertEqual(hotel_voucher['total_amount'], str(fees_sum + Decimal(hotel_voucher['room_vouchers'][0]['rate']) * 2 + Decimal(hotel_voucher['tax'])))
        self.assertTrue(validated_pet_fee)
        self.assertTrue(validated_service_pet_fee)

    def test_pet_booking_pax_app(self):
        """
        verifies system can book a pet room through pax app
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=1,
            hotel_id='tvl-80657'
        )

        ak1 = response_json['data'][0]['ak1']
        ak2 = response_json['data'][0]['ak2']

        book_resp = requests.post(hotel_url + '?ak1=' + ak1 + '&ak2=' + ak2, headers=pax_headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        self.assertNotIn('fees', book_resp_json['data']['hotel_voucher'])

        full_state = requests.get(url=passenger_url + '/' + response_json['data'][0]['context_id'] + '/state', headers=headers).json()
        voucher_id = full_state['data']['passenger']['voucher_id']
        hotel_voucher = full_state['data']['voucher']['hotel_voucher']
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(fee['total']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + voucher_id, headers=headers).json()
        hotel_voucher = voucher_resp['data']['hotel_voucher']
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(fee['total']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

    def test_pet_booking_fee_count_equal_room_count(self):
        """
        verifies system can book a pet room
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(3)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))
        passenger_payload[1].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))
        passenger_payload[2].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=2,
            hotel_id='tvl-80657'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(len(hotel_voucher['fees']), 1)
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 2)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))

    def test_pet_booking_fee_count_more_than_room_count(self):
        """
        verifies system can book a pet room
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(3)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))
        passenger_payload[1].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))
        passenger_payload[2].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=1,
            hotel_id='tvl-80657'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(len(hotel_voucher['fees']), 1)
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))

    def test_pet_booking_fee_count_less_than_room_count(self):
        """
        verifies system can book a pet room
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(3)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))
        passenger_payload[1].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=False
        ))
        passenger_payload[2].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=2,
            hotel_id='tvl-80657'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(len(hotel_voucher['fees']), 1)
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))

    def test_pet_booking_aa_tvl_inventory(self):
        """
        test aa pet booking
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 71, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=1,
            hotel_id='tvl-80657'
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        hotel_voucher = book_resp_json['data']['hotel_voucher']
        self.assertEqual(len(hotel_voucher['fees']), 1)
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))

        full_state = requests.get(url=passenger_url + '/' + response_json['data'][0]['context_id'] + '/state', headers=headers).json()
        hotel_voucher = full_state['data']['voucher']['hotel_voucher']
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))

    def test_pet_and_service_pet_booking__ean_inventory(self):
        """
        pet and service_pet booking/search for expedia
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/hotels'

        for pax_scenario in [dict(service_pet=False, pet=True),
                             dict(service_pet=True, pet=False),
                             dict(service_pet=True, pet=True)]:

            port = self.select_airport_for_expedia_testing([('LAX', 'America/Los_Angeles'),
                                                            ('LGW', 'Europe/London')])
            passenger_payload = self._generate_n_passenger_payload(1,
                                                                   port_accommodation=port,
                                                                   ticket_level='business',
                                                                   pax_status='nonPremium',
                                                                   **pax_scenario)
            failure_message = 'failed for scenario ' + repr(pax_scenario) + ' in port ' + repr(port) + '.'
            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)
            passengers = response_json['data']

            hotel_response = requests.get(hotel_url, headers=headers, params={'room_count': '1',
                                                                              'port': port,
                                                                              'provider': 'ean',
                                                                              'pet': pax_scenario['pet'],
                                                                              'service_pet': pax_scenario['service_pet']})

            # TODO: change once pet feature is implemented in expedia
            if not pax_scenario['pet']:
                self.assertEqual(hotel_response.status_code, 200, msg='test setup ' + failure_message)
                hotel_response_json = hotel_response.json()
                self.assertGreater(len(hotel_response_json['data']), 0, msg='test setup ' + failure_message)

                selected_hotel = hotel_response_json['data'][0]
                payload = dict(
                    context_ids=[passenger['context_id'] for passenger in passengers],
                    room_count=1,
                    hotel_id=selected_hotel['hotel_id']
                )
                book_resp = requests.post(hotel_url, headers=headers, json=payload)
                self.assertEqual(book_resp.status_code, 200, msg=failure_message)
                book_resp_json = book_resp.json()
                self.assertEqual(book_resp_json['error'], False)
                voucher_id = book_resp_json['data']['voucher_id']
                UUID(voucher_id, version=4)
            else:
                self.assertEqual(hotel_response.status_code, 200, msg='test setup ' + failure_message)
                hotel_response_json = hotel_response.json()
                self.assertEqual(len(hotel_response_json['data']), 0, msg='test setup ' + failure_message)

    def test_pet_booking_pax_app_aa(self):
        """
        system test validating pet booking on pax app for AA
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 71, event_date, ap_block_type=2, block_price='20.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in response_json['data']],
            room_count=1,
            hotel_id='tvl-80657'
        )

        ak1 = response_json['data'][0]['ak1']
        ak2 = response_json['data'][0]['ak2']

        book_resp = requests.post(hotel_url + '?ak1=' + ak1 + '&ak2=' + ak2, headers=pax_headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()
        self.assertIs(book_resp_json['error'], False)
        self.assertNotIn('fees', book_resp_json['data']['hotel_voucher'])

        full_state = requests.get(url=passenger_url + '/' + response_json['data'][0]['context_id'] + '/state', headers=headers).json()
        voucher_id = full_state['data']['passenger']['voucher_id']
        hotel_voucher = full_state['data']['voucher']['hotel_voucher']
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(fee['total']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + voucher_id, headers=headers).json()
        hotel_voucher = voucher_resp['data']['hotel_voucher']
        fee = hotel_voucher['fees'][0]
        self.assertEqual(fee['type'], 'pet')
        self.assertEqual(fee['count'], 1)
        self.assertGreater(Decimal(fee['rate']), 0)
        self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(fee['total']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))
