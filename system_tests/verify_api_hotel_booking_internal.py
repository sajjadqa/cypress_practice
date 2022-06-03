import datetime
from uuid import UUID
from decimal import Decimal

import requests

from stormx_verification_framework import StormxSystemVerification


class TestApiHotelBookingInternal(StormxSystemVerification):
    """
    Verify the internal booking endpoint (`/api/v1/tvl/airline/{airline_id}/hotels`).
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBookingInternal, cls).setUpClass()


    def test_tvl_internal_book_hotels_soft_block(self):
        """
        verify StormX can book a hotel via Stormx API
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
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
        hotel_id = 'tvl-85690'

        event_date = self._get_event_date('America/Chicago')
        check_in_date = event_date.strftime('%Y-%m-%d')
        check_out_date = (event_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99.50
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['count'], 1)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['rate'], '99.50')
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['hard_block'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['block_type'], 'soft_block')
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_out_date'], check_out_date)
        UUID(booking_response_json['data']['voucher_id'], version=4)

        full_state = requests.get(url=url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        room_voucher = full_state['voucher']['hotel_voucher']['room_vouchers'][0]
        self.assertEqual(room_voucher['count'], 1)
        self.assertEqual(room_voucher['rate'], '99.50')
        self.assertEqual(room_voucher['hard_block'], False)
        self.assertEqual(room_voucher['block_type'], 'soft_block')

    def test_tvl_internal_book_hotels_hard_block(self):
        """
        verify StormX can book a hotel via Stormx API
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
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
        hotel_id = 'tvl-85690'

        event_date = self._get_event_date('America/Chicago')
        check_in_date = event_date.strftime('%Y-%m-%d')
        check_out_date = (event_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='hard_block',
            hotel_rate=99,
            number_of_nights=1
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['count'], 1)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['rate'], '99.00')
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['hard_block'], True)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['block_type'], 'hard_block')
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_out_date'], check_out_date)
        UUID(booking_response_json['data']['voucher_id'], version=4)
        self.assertIsNone(booking_response_json['data']['hotel_voucher']['hotel_message'])

        full_state = requests.get(url=url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        room_voucher = full_state['voucher']['hotel_voucher']['room_vouchers'][0]
        self.assertEqual(room_voucher['count'], 1)
        self.assertEqual(room_voucher['rate'], '99.00')
        self.assertEqual(room_voucher['hard_block'], True)
        self.assertEqual(room_voucher['block_type'], 'hard_block')

    def test_tvl_internal_book_hotels_hard_block_override_number_of_nights(self):
        """
        verify StormX can book a hotel via Stormx API
        and override the number_of_nights from passenger import
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='ORD',
            number_of_nights=2
        ))
        passenger_payload[1].update(dict(
            port_accommodation='ORD',
            number_of_nights=2
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        passenger2 = response_json['data'][1]
        hotel_id = 'tvl-85690'

        event_date = self._get_event_date('America/Chicago')
        check_in_date = event_date.strftime('%Y-%m-%d')
        check_out_date = (event_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='hard_block',
            hotel_rate=99,
            number_of_nights=1
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['rooms_booked'], 1)
        self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['count'], 1)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['rate'], '99.00')
        self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['hard_block'], True)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_out_date'], check_out_date)
        UUID(booking_response_json['data']['voucher_id'], version=4)

    def test_tvl_internal_book_hotels_multi_night(self):
        """
        verify StormX can book a hotel via Stormx API for 2 nights
        where number_of_nights are not provided
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='ORD',
            number_of_nights=2
        ))
        passenger_payload[1].update(dict(
            port_accommodation='ORD',
            number_of_nights=2
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        passenger2 = response_json['data'][1]
        hotel_id = 'tvl-85690'

        event_date = self._get_event_date('America/Chicago')
        check_in_date = event_date.strftime('%Y-%m-%d')
        check_out_date = (event_date + datetime.timedelta(days=2)).strftime('%Y-%m-%d')

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=3,
            block_type='hard_block',
            hotel_rate=79.99,
            number_of_nights=2
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['rooms_booked'], 3)
        self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in booking_response_json['data']['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], 3)
            self.assertEqual(room_voucher['rate'], '79.99')
            self.assertEqual(room_voucher['hard_block'], True)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_out_date'], check_out_date)
        UUID(booking_response_json['data']['voucher_id'], version=4)

    def test_tvl_internal_book_hotels_multi_night_number_of_nights_not_provided(self):
        """
        verify StormX can book a hotel via Stormx API for 2 nights
        where number_of_nights are not provided
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='ORD',
            number_of_nights=2
        ))
        passenger_payload[1].update(dict(
            port_accommodation='ORD',
            number_of_nights=2
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        passenger2 = response_json['data'][1]
        hotel_id = 'tvl-85690'

        event_date = self._get_event_date('America/Chicago')
        check_in_date = event_date.strftime('%Y-%m-%d')
        check_out_date = (event_date + datetime.timedelta(days=2)).strftime('%Y-%m-%d')

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=2,
            block_type='hard_block',
            hotel_rate=79.99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['rooms_booked'], 2)
        self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in booking_response_json['data']['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], 2)
            self.assertEqual(room_voucher['rate'], '79.99')
            self.assertEqual(room_voucher['hard_block'], True)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['check_out_date'], check_out_date)
        UUID(booking_response_json['data']['voucher_id'], version=4)

    def test_tvl_internal_book_hotels_diff_port(self):
        """
        verify StormX can book a hotel via Stormx API where port_accommodation
        is not the same as hotel port. this should break in future release.
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='LAX'
        ))
        passenger_payload[1].update(dict(
            port_accommodation='LAX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        passenger2 = response_json['data'][1]
        hotel_id = 'tvl-85690'

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='hard_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_BOOKING_REQUEST', 'Provided hotel_id is not in passenger port of accommodation', [])

    def test_validate_stormx_internal_booking_hotel_rate_good(self):
        """
        validate internal booking serializer
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()

        hotel_rates = [0.02, '0.02', 999, '999', 999.99, '999.99', 100, 85, 56.00, '9', '49.00', '49']
        for rate in hotel_rates:
            passenger_payload = self._generate_n_passenger_payload(2)

            passenger_payload[0].update(dict(
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
            hotel_id = 'tvl-85690'

            booking_payload = dict(
                context_ids=[passenger['context_id'], passenger2['context_id']],
                hotel_id=hotel_id,
                room_count=1,
                block_type='hard_block',
                hotel_rate=rate
            )

            booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
            booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
            self.assertEqual(booking_response.status_code, 200)
            booking_response_json = booking_response.json()
            self.assertIs(booking_response_json['error'], False)
            self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
            self.assertEqual(len(booking_response_json['data']['hotel_voucher']['room_vouchers']), 1)
            self.assertEqual(booking_response_json['data']['hotel_voucher']['room_vouchers'][0]['rate'], str(Decimal(rate).quantize(Decimal('.00'))))
            UUID(booking_response_json['data']['voucher_id'], version=4)

    def test_validate_stormx_internal_booking_hotel_rate_bad(self):
        """
        validate additional fields for stormx internal booking serializer
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='LAX'
        ))
        passenger_payload[1].update(dict(
            port_accommodation='LAX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        passenger2 = response_json['data'][1]
        hotel_id = 'tvl-85690'

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='hard_block',
            hotel_rate=0.00
        )
        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'Ensure this value is greater than or equal to 0.01.'}])

        booking_payload['hotel_rate'] = 0

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'Ensure this value is greater than or equal to 0.01.'}])

        booking_payload['hotel_rate'] = '0.00'
        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'Ensure this value is greater than or equal to 0.01.'}])

        booking_payload['hotel_rate'] = '0'

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'Ensure this value is greater than or equal to 0.01.'}])

        booking_payload['hotel_rate'] = 1000

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'Ensure that there are no more than 3 digits before the decimal point.'}])

        booking_payload['hotel_rate'] = '1000.00'

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'Ensure that there are no more than 5 digits in total.'}])

        booking_payload['hotel_rate'] = ''

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'A valid number is required.'}])

        del(booking_payload['hotel_rate'])
        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'hotel_rate', 'message': 'This field is required.'}])

    def test_validate_stormx_internal_booking_block_type(self):
        """
        test stormx internal block type hotel booking
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
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
        hotel_id = 'tvl-85690'

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'block_type', 'message': '"" is not a valid choice.'}])

        booking_payload['block_type'] = 'contract_block'

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'block_type', 'message': '"contract_block" is not a valid choice.'}])

        booking_payload['block_type'] = 1

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'block_type', 'message': '"1" is not a valid choice.'}])

        booking_payload['block_type'] = 0

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'block_type', 'message': '"0" is not a valid choice.'}])

        del(booking_payload['block_type'])

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 400)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel booking.', [{'field': 'block_type', 'message': 'This field is required.'}])

    def test_validate_stormx_internal_multi_tenant_booking(self):
        """
        validate multi tenant scenarios for stormx internal hotel endpoint
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
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
        hotel_id = 'tvl-85690'

        booking_payload = dict(
            context_ids=[passenger['context_id'], passenger2['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='hard_block',
            hotel_rate='89.99'
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/71/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 404)
        booking_response_json = booking_response.json()
        self._validate_error_message(booking_response_json, 404, 'Not Found', 'PASSENGER_NOT_FOUND', 'Not all Passengers found for given context_id list.', [])

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        UUID(booking_response_json['data']['voucher_id'], version=4)
