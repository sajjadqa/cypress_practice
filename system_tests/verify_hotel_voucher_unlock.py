from decimal import Decimal
from uuid import UUID

import requests

from stormx_verification_framework import (
    StormxSystemVerification,
    uses_expedia,
)


class TestHotelVoucherUnlock(StormxSystemVerification):
    """
    Verify hotel voucher credit card unlocking and viewing functionality.
    This focuses on the endpoints:
        * `/api/v1/tvl/hotel_voucher_unlock`
        * `/api/v1/tvl/hotel_voucher_details`
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestHotelVoucherUnlock, cls).setUpClass()
        cls.finance_user = cls.create_new_tva_user(role="Finance", group_id=2, is_active=True)

    def test_tvl_hotel_voucher_good_headers_bad_post_data(self):
        """
        validating good header entries for hotel_voucher_unlock and hotel_voucher_details
        but with missing and bad post data
        """
        urls = [
            self._api_host + '/api/v1/tvl/hotel_voucher_unlock',
            self._api_host + '/api/v1/tvl/hotel_voucher_details'
        ]

        hotel_user_id = '10029'  # Hotel User for DAYS INN MESA (101307 PHX)
        headers = self._generate_tvl_stormx_user_headers(user_id=hotel_user_id)

        for url in urls:
            resp = requests.post(url=url, headers=headers)  # no post data
            self.assertEqual(resp.status_code, 404)
            resp_json = resp.json()
            self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

            resp = requests.post(url=url, headers=headers, json={})  # empty post data
            self.assertEqual(resp.status_code, 404)
            resp_json = resp.json()
            self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

            resp = requests.post(url=url, headers=headers, json={'meaningless': 'field'})  # meaningless post data
            self.assertEqual(resp.status_code, 404)
            resp_json = resp.json()
            self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

    def test_tvl_hotel_voucher_bad_token(self):
        """
        validating bad token header entries for hotel_voucher_unlock and hotel_voucher_details
        """
        urls = [
            self._api_host + '/api/v1/tvl/hotel_voucher_unlock',
            self._api_host + '/api/v1/tvl/hotel_voucher_details'
        ]

        bad_headers = self._generate_tvl_stormx_user_headers_bad(user_id='1')  # bad token will ignore user_id
        missing_user_id_headers = self._generate_tvl_stormx_headers()

        for url in urls:
            resp = requests.post(url=url)  # missing headers
            self.assertEqual(resp.status_code, 403)
            resp_json = resp.json()
            self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

            resp = requests.post(url=url, headers=bad_headers)  # headers with wrong token
            self.assertEqual(resp.status_code, 403)
            resp_json = resp.json()
            self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

            resp = requests.post(url=url, headers=missing_user_id_headers)  # missing user_id with good token headers
            self.assertEqual(resp.status_code, 403)
            resp_json = resp.json()
            self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

    def test_tvl_hotel_voucher_bad_token_good_user(self):
        """
        validating bad token entries for hotel_voucher_unlock and hotel_voucher_details
        but with a valid user_id
        """
        urls = [
            self._api_host + '/api/v1/tvl/hotel_voucher_unlock',
            self._api_host + '/api/v1/tvl/hotel_voucher_details'
        ]

        hotel_user_id = '10029'  # Hotel User for DAYS INN MESA (101307 PHX)
        headers = self._generate_tvl_stormx_user_headers_bad(user_id=hotel_user_id)

        for url in urls:
            resp = requests.post(url=url, headers=headers)
            self.assertEqual(resp.status_code, 403)
            resp_json = resp.json()
            self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

    def test_tvl_hotel_voucher_unlock_validate_serializer(self):
        """
        validating hotel_voucher_unlock serializer
        """
        url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'

        hotel_user_id = '10029'  # Hotel User for DAYS INN MESA (101307 PHX)
        headers = self._generate_tvl_stormx_user_headers(user_id=hotel_user_id)

        post_data_sets = [
            {'hotel_id': '', 'check_in_key': ''},
            {'hotel_id': ''},
            {'check_in_key': ''},
            {'hotel_id': 12345, 'check_in_key': ''},
            {'hotel_id': '', 'check_in_key': '12345'},
            {'hotel_id': 101307, 'check_in_key': '123456'},
            {'hotel_id': 101307, 'check_in_key': '1234'},
            {'hotel_id': 0, 'check_in_key': '12345'},
            {'hotel_id': '10130a', 'check_in_key': '12345'},
            {'hotel_id': None, 'check_in_key': '12345'},
            {'hotel_id': '10130a', 'check_in_key': None},
            {'hotel_id': None, 'check_in_key': None},
        ]

        for post_data in post_data_sets:
            resp = requests.post(url=url, headers=headers, json=post_data)
            self.assertEqual(resp.status_code, 404)
            resp_json = resp.json()
            self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

    def test_tvl_hotel_voucher_details_validate_serializer(self):
        """
        validating hotel_voucher_details serializer
        """
        url = self._api_host + '/api/v1/tvl/hotel_voucher_details'

        hotel_user_id = '10029'  # Hotel User for DAYS INN MESA (101307 PHX)
        headers = self._generate_tvl_stormx_user_headers(user_id=hotel_user_id)

        post_data_sets = [
            {'voucher_uuid': ''},
            {'voucher_uuid': None},
            {'voucher_uuid': 'thisisnotauuid'},
            {'voucher_uuid': '69c2ffb9a49f4182871566003c8ab58'},
        ]

        for post_data in post_data_sets:
            resp = requests.post(url=url, headers=headers, json=post_data)
            self.assertEqual(resp.status_code, 404)
            resp_json = resp.json()
            self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

    def test_tvl_hotel_voucher_user_access(self):
        """
        validating user access levels for hotel_voucher_unlock and hotel_voucher_details
        """
        users = [
            '9426',  # USER ACCESS 10
            '9269',  # USER ACCESS 50
            '9856',  # USER ACCESS 70
            '8712'  # USER ACCESS 90 SR MGR
        ]

        users_can_view = [
            '9856',  # USER ACCESS 70
            '8712',  # USER ACCESS 90 SR MGR
            '176',  # USER ACCESS 90 IT
            str(self.finance_user['user_id'])  # USER ACCESS 100
        ]

        users_cannot_view = [
            '9426',  # USER ACCESS 10
            '9269'  # USER ACCESS 50
        ]

        hotel_user_good = '10029'  # Hotel User for Crowne Plaza PHX Airport (101307 PHX)
        hotel_id_good = 101307

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        voucher_hotel_details_url = self._api_host + '/api/v1/tvl/hotel_voucher_details'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='PHX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_id = 'tvl-' + str(hotel_id_good)

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        UUID(booking_response_json['data']['voucher_id'], version=4)
        voucher_uuid = booking_response_json['data']['voucher_id']
        check_in_key = booking_response_json['data']['hotel_voucher']['hotel_key']

        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=hotel_user_good)

        unlock_payload = dict(
            hotel_id=hotel_id_good,
            check_in_key=check_in_key
        )

        detail_payload = dict(
            voucher_uuid=voucher_uuid
        )

        for user in users:
            user_headers = self._generate_tvl_stormx_user_headers(user_id=user)
            resp = requests.post(url=voucher_hotel_unlock_url, headers=user_headers, json=unlock_payload)
            self.assertEqual(resp.status_code, 403)
            resp_json = resp.json()
            self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=unlock_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

        for user in users_can_view:
            user_headers = self._generate_tvl_stormx_user_headers(user_id=user)
            resp = requests.post(url=voucher_hotel_details_url, headers=user_headers, json=detail_payload)
            self.assertEqual(resp.status_code, 200)
            cc_json = resp.json()
            self._validate_hotel_voucher_cc(cc_json['data'])

        for user in users_cannot_view:
            user_headers = self._generate_tvl_stormx_user_headers(user_id=user)
            resp = requests.post(url=voucher_hotel_details_url, headers=user_headers, json=detail_payload)
            self.assertEqual(resp.status_code, 403)
            resp_json = resp.json()
            self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_good, json=detail_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

    def _validate_hotel_voucher_cc(self, cc_data):
        """
        param cc_data: cc data json resp object
        return: None
        """
        fields = ['nights', 'expiration', 'flight', 'amount', 'rooms', 'tax', 'card_number', 'cvc2', 'port',
                  'passengers', 'currency_code', 'check_in_date', 'rates', 'fees', 'airline_name']

        for field in fields:
            self.assertIn(field, cc_data)

        self.assertEqual(len(cc_data['card_number']), 16)
        self.assertEqual(len(cc_data['cvc2']), 4)
        self.assertEqual(len(cc_data['expiration']), 7)
        self.assertGreaterEqual(len(cc_data['rates']), 1)

        for rate in cc_data['rates']:
            self.assertIn('rate', rate)
            self.assertIn('count', rate)

        self.assertIn('-', cc_data['voucher_id'])
        UUID(cc_data['voucher_id'], version=4)

        self.assertIn(cc_data['hotel_payment_type'], ['vcc', 'direct_bill'])

    def test_tvl_hotel_voucher_unlock(self):
        """
        validate hotel_voucher_unlock can unlock credit cards
        validate hotel_user can only unlock cards for there hotel
        validate hotel_user can only unlock cards that are locked
        """
        hotel_user_good = '10029'  # Hotel User for Crowne Plaza PHX Airport (101307 PHX)
        hotel_user_bad = '10028'  # Hotel User for DAYS INN MESA (100038 PHX)
        hotel_id_good = 101307
        hotel_id_bad = 100038

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='PHX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_id = 'tvl-' + str(hotel_id_good)

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        UUID(booking_response_json['data']['voucher_id'], version=4)
        check_in_key = booking_response_json['data']['hotel_voucher']['hotel_key']

        stormx_user_headers_bad = self._generate_tvl_stormx_user_headers(user_id=hotel_user_bad)
        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=hotel_user_good)

        bad_post_data = dict(
            hotel_id=hotel_id_bad,
            check_in_key=check_in_key
        )

        good_post_data = dict(
            hotel_id=hotel_id_good,
            check_in_key=check_in_key
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=bad_post_data)
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_bad, json=good_post_data)
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=good_post_data)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=good_post_data)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 200, 'OK', 'HOTEL_VOUCHER_ALREADY_UNLOCKED', 'Hotel payment cannot be unlocked. Hotel payment is already unlocked.', [])

    def test_tvl_hotel_voucher_details(self):
        """
        validate hotel_voucher_details can view cards
        validate hotel users can only view cards from there hotel
        validate hotel users can only view cards that are unlocked
        """
        hotel_user_good = '10029'  # Hotel User for Crowne Plaza PHX Airport (101307 PHX)
        hotel_user_bad = '10028'  # Hotel User for DAYS INN MESA (100038 PHX)
        hotel_id_good = 101307

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        voucher_hotel_details_url = self._api_host + '/api/v1/tvl/hotel_voucher_details'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='PHX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_id = 'tvl-' + str(hotel_id_good)

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        UUID(booking_response_json['data']['voucher_id'], version=4)
        voucher_uuid = booking_response_json['data']['voucher_id']
        check_in_key = booking_response_json['data']['hotel_voucher']['hotel_key']

        stormx_user_headers_bad = self._generate_tvl_stormx_user_headers(user_id=hotel_user_bad)
        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=hotel_user_good)

        unlock_payload = dict(
            hotel_id=hotel_id_good,
            check_in_key=check_in_key
        )

        details_payload = {
            'voucher_uuid': voucher_uuid
        }

        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_good, json=details_payload)
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=unlock_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_bad, json=details_payload)
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_good, json=details_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

    def test_tvl_hotel_voucher_canceled(self):
        """
        validate payment cannot be unlocked for canceled vouchers
        validate payment cannot be viewed for canceled vouchers
        """
        hotel_user_good = '10029'  # Hotel User for Crowne Plaza PHX Airport (101307 PHX)
        hotel_id_good = 101307

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        voucher_hotel_details_url = self._api_host + '/api/v1/tvl/hotel_voucher_details'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='PHX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_id = 'tvl-' + str(hotel_id_good)

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        UUID(booking_response_json['data']['voucher_id'], version=4)
        voucher_uuid = booking_response_json['data']['voucher_id']
        check_in_key = booking_response_json['data']['hotel_voucher']['hotel_key']

        cancel_resp = requests.put(url=url + '/' + passenger['context_id'] + '/cancel', headers=headers)
        self.assertEqual(cancel_resp.status_code, 200)

        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=hotel_user_good)

        unlock_payload = dict(
            hotel_id=hotel_id_good,
            check_in_key=check_in_key
        )

        detail_payload = dict(
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_good, json=detail_payload)
        self.assertEqual(resp.status_code, 404)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 404, 'Not Found', '', '', [])

    def test_tvl_cannot_unlock_canceled_voucher(self):
        """
        validate api cannot cancel a voucher that has unlocked payment
        """
        hotel_user_good = '10029'  # Hotel User for Crowne Plaza PHX Airport (101307 PHX)
        hotel_id_good = 101307

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        voucher_hotel_details_url = self._api_host + '/api/v1/tvl/hotel_voucher_details'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='PHX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_id = 'tvl-' + str(hotel_id_good)

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
        UUID(booking_response_json['data']['voucher_id'], version=4)
        voucher_uuid = booking_response_json['data']['voucher_id']
        check_in_key = booking_response_json['data']['hotel_voucher']['hotel_key']

        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=hotel_user_good)

        unlock_payload = dict(
            hotel_id=hotel_id_good,
            check_in_key=check_in_key
        )

        detail_payload = dict(
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=unlock_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_good, json=detail_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

        cancel_resp = requests.put(url=url + '/' + passenger['context_id'] + '/cancel', headers=headers)
        self.assertEqual(cancel_resp.status_code, 400)
        cancel_resp_json = cancel_resp.json()
        self._validate_error_message(cancel_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL',
                                     'Passenger cannot cancel offer. The credit card has already been unlocked by the hotel.', [])

    def test_tvl_hotel_voucher_multi_block_and_fees(self):
        """
        test validating cc data looks good for multi block and fees
        """
        hotel_user_good = '11258'
        hotel_id_good = 86000
        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        voucher_hotel_details_url = self._api_host + '/api/v1/tvl/hotel_voucher_details'

        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-' + str(hotel_id_good)  # ORD
        event_date = self._get_event_date('America/Chicago')  # Chicago timezone port
        self.add_hotel_availability(hotel_id_good, 294, event_date, ap_block_type=2,
                                    block_price='39.99', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_good, 294, event_date, ap_block_type=2,
                                    block_price='29.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='ORD', pet=True)

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(len(resp_json['data']['hotel_voucher']['room_vouchers']), 2)
        self.assertEqual(len(resp_json['data']['hotel_voucher']['fees']), 1)

        hotel_voucher = resp_json['data']['hotel_voucher']
        check_in_key = hotel_voucher['hotel_key']
        voucher_uuid = resp_json['data']['voucher_id']

        fees_sum = Decimal('0.00')
        for fee in hotel_voucher['fees']:
            if fee['type'] == 'pet':
                self.assertEqual(fee['rate'], hotel_voucher['pets_fee'])
                self.assertEqual(fee['type'], 'pet')
                self.assertEqual(fee['count'], 2)
                self.assertGreater(Decimal(fee['rate']), 0)
                self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
                fees_sum += Decimal(fee['total'])

        expected_total = str(fees_sum + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['room_vouchers'][1]['rate']) + Decimal(hotel_voucher['tax']))
        self.assertEqual(hotel_voucher['total_amount'], expected_total)

        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=hotel_user_good)

        unlock_payload = dict(
            hotel_id=hotel_id_good,
            check_in_key=check_in_key
        )

        detail_payload = dict(
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=unlock_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

        cc = cc_json['data']
        self.assertEqual(len(cc['rates']), 2)
        fees_sum = Decimal('0.00')
        for fee in cc['fees']:
            if fee['type'] == 'pet':
                self.assertEqual(fee['rate'], hotel_voucher['pets_fee'])
                self.assertEqual(fee['type'], 'pet')
                self.assertEqual(fee['count'], 2)
                self.assertGreater(Decimal(fee['rate']), 0)
                self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
                fees_sum += Decimal(fee['total'])
        expected_total = '%.4f' % (fees_sum + Decimal(cc['rates'][0]['rate']) + Decimal(cc['rates'][1]['rate']) + Decimal(cc['tax']))
        self.assertEqual(cc['amount'], expected_total)

        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_good, json=detail_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self._validate_hotel_voucher_cc(cc_json['data'])

        cc = cc_json['data']
        self.assertEqual(len(cc['rates']), 2)
        fees_sum = Decimal('0.00')
        for fee in cc['fees']:
            if fee['type'] == 'pet':
                self.assertEqual(fee['rate'], hotel_voucher['pets_fee'])
                self.assertEqual(fee['type'], 'pet')
                self.assertEqual(fee['count'], 2)
                self.assertGreater(Decimal(fee['rate']), 0)
                self.assertEqual(Decimal(fee['total']), fee['count'] * Decimal(fee['rate']))
                fees_sum += Decimal(fee['total'])
        expected_total = '%.4f' % (fees_sum + Decimal(cc['rates'][0]['rate']) + Decimal(cc['rates'][1]['rate']) + Decimal(cc['tax']))
        self.assertEqual(cc['amount'], expected_total)

    @uses_expedia
    def test_external_voucher_cannot_view_or_unlock_cc_info(self):
        """
        validate a CC for an external voucher cannot be unlocked or viewed
        """
        user = '8712'
        hotel_user = '10029'
        user_headers = self._generate_tvl_stormx_user_headers(user_id=user)
        hotel_user_headers = self._generate_tvl_stormx_user_headers(user_id=hotel_user)
        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        voucher_hotel_details_url = self._api_host + '/api/v1/tvl/hotel_voucher_details'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        passengers = self._create_2_passengers(customer=customer, port_accommodation=port)

        hotel_response = requests.get(hotel_url + '?room_count=1&port=' + port + '&provider=ean', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0)

        ean_offer = hotel_response_json['data'][0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=1
        )

        booking_response = requests.post(url=hotel_url, headers=headers, data=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        ean_voucher = booking_response_json['data']

        self.assertEqual(ean_voucher['hotel_voucher']['provider'], 'ean')
        self.assertEqual(ean_voucher['hotel_voucher']['hotel_id'], ean_offer)
        self.assertEqual(len(ean_voucher['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(ean_voucher['hotel_voucher']['room_vouchers'][0]['count'], 1)
        self.assertEqual({passenger['context_id'] for passenger in passengers},
                         {passenger['context_id'] for passenger in ean_voucher['passengers']})

        unlock_payload = dict(
            hotel_id=101307,
            check_in_key=ean_voucher['hotel_voucher']['confirmation_id']
        )

        detail_payload = dict(
            voucher_uuid=ean_voucher['voucher_id']
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=hotel_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)  # serializer forces length 5 check_in_key

        resp = requests.post(url=voucher_hotel_details_url, headers=user_headers, json=detail_payload)
        self.assertEqual(resp.status_code, 403)
        resp_json = resp.json()
        self.assertEqual(resp_json, {'detail': 'You do not have permission to perform this action.'})

    def test_tvl_hotel_voucher_unlock_no_spoil_no_nosho(self):
        """
        validates hotel_voucher cannot be unlocked passing up spoil or nosho
        as checkin key when it is not a spoiled voucher or no show voucher
        """
        hotel_user = '10029'
        hotel_id = 101307
        tvl_hotel_id = 'tvl-' + str(hotel_id)

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='PHX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=tvl_hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], tvl_hotel_id)
        voucher_uuid = booking_response_json['data']['voucher_id']
        UUID(voucher_uuid, version=4)

        stormx_user_headers = self._generate_tvl_stormx_user_headers(user_id=hotel_user)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='SPOIL',
            unlock_reason='spoilage',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='NOSHO',
            unlock_reason='no_show',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='SPOIL',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='NOSHO',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

    def test_meal_transaction_unlock_reason(self):
        """
        validate unlock_reason is null for meal_transaction
        """
        customer = 'Purple Rain Airlines'

        passengers = self._create_2_passengers(customer=customer, port_accommodation='PHX', hotel_accommodation=False)
        embedded_json = self._get_landing_page_embedded_json(requests.get(url=passengers[0]['offer_url']))
        card = embedded_json['confirmation']['passengers'][0]['meal_vouchers'][0]

        merchant_info = dict(
            merchant_acceptor_id='313756560881',
            merchant_description='PANDA EXPRESS #2301',
            merchant_city='PHOENIX',
            merchant_state='AZ',
            merchant_zip='85034',
            merchant_country_code='USA',
            sic_mcc_code='5814'
        )

        transaction = self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('10.00'), **merchant_info)['transaction_queue_message']['data']
        self.assertEqual(transaction['type'], 'meal')
        self.assertIsNone(transaction['unlock_reason'])
        self.assertEqual(transaction['context_ids'], [passengers[0]['context_id']])

    def test_hotel_transaction_unlock_reason_default(self):
        """
        validate hotel transaction unlock reason default
        """
        customer = 'Purple Rain Airlines'
        airline_headers = self._generate_airline_headers(customer)

        airline_id = 294
        hotel_id = 95378  # Hilton - Phoenix Airport
        hotel_user_id = 10060  # active user at Hilton - Phoenix Airport
        room_count = 1
        stormx_user_headers = self._generate_tvl_stormx_user_headers(user_id=str(hotel_user_id))

        availability_date = self._get_event_date('America/Phoenix')
        self.add_hotel_availability(hotel_id, airline_id, availability_date, blocks=1, block_price='200.00', ap_block_type=1, room_type=1, pay_type=0)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='PHX')
        hotel_url = self._api_host + '/api/v1/hotels'
        booking_payload = dict(
            context_ids=[p['context_id'] for p in passengers],
            hotel_id='tvl-' + str(hotel_id),
            room_count=room_count
        )

        booking_response = requests.post(hotel_url, headers=airline_headers, json=booking_payload)
        check_in_key = booking_response.json()['data']['hotel_voucher']['hotel_key']

        unlock_payload = dict(hotel_id=hotel_id, check_in_key=check_in_key)
        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 200)

        cc_json = resp.json()
        self.assertEqual(cc_json['meta']['error_code'], '')
        card_number = cc_json['data']['card_number']
        currency_code = cc_json['data']['currency_code']
        voucher_total_amount = Decimal(cc_json['data']['amount'])

        merchant_info = dict(
            merchant_acceptor_id='483200924999',
            merchant_description='HILTON PHOENIX AIRPORT',
            merchant_city='PHOENIX',
            merchant_state='AZ',
            merchant_zip='85034',
            merchant_country_code='USA',
            sic_mcc_code='7011'
        )

        transaction = self.charge_single_use_card(card_number, currency_code, voucher_total_amount, **merchant_info)['transaction_queue_message']['data']
        self.assertEqual(transaction['type'], 'hotel')
        self.assertEqual(transaction['unlock_reason'], 'default')
        self.assertEqual(transaction['context_ids'], booking_payload['context_ids'])

    def test_tvl_hotel_voucher_unlock_no_spoil_no_nosho_feature_not_enabled(self):
        """
        validates hotel_voucher cannot be unlocked passing up spoil or nosho
        as checkin key when it is not a spoiled voucher or no show voucher
        when the feature is not enabled
        """
        hotel_user = '10029'
        hotel_id = 101307
        tvl_hotel_id = 'tvl-' + str(hotel_id)

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'

        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            port_accommodation='PHX'
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=tvl_hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/71/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], tvl_hotel_id)
        voucher_uuid = booking_response_json['data']['voucher_id']
        UUID(voucher_uuid, version=4)

        stormx_user_headers = self._generate_tvl_stormx_user_headers(user_id=hotel_user)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='SPOIL',
            unlock_reason='spoilage',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='NOSHO',
            unlock_reason='no_show',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='SPOIL',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key='NOSHO',
            voucher_uuid=voucher_uuid
        )

        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers, json=unlock_payload)
        self.assertEqual(resp.status_code, 404)

    def test_tvl_hotel_voucher_unlock_by_ops(self):
        """
        validate certain ops users hotel_voucher_unlock can unlock credit cards
        """
        hotel_id_good = 101307

        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        stormx_headers = self._generate_tvl_stormx_headers()

        stormx_users = [
            str(self.finance_user['user_id']),  # 100
            '176'  # 90
        ]

        for stormx_user in stormx_users:
            passenger_payload = self._generate_n_passenger_payload(1)

            passenger_payload[0].update(dict(
                port_accommodation='PHX'
            ))

            response = requests.post(url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)

            passenger = response_json['data'][0]
            hotel_id = 'tvl-' + str(hotel_id_good)

            booking_payload = dict(
                context_ids=[passenger['context_id']],
                hotel_id=hotel_id,
                room_count=1,
                block_type='soft_block',
                hotel_rate=99
            )

            booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
            booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
            self.assertEqual(booking_response.status_code, 200)
            booking_response_json = booking_response.json()
            self.assertIs(booking_response_json['error'], False)
            self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)
            UUID(booking_response_json['data']['voucher_id'], version=4)
            check_in_key = booking_response_json['data']['hotel_voucher']['hotel_key']

            stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=stormx_user)

            good_post_data = dict(
                hotel_id=hotel_id_good,
                check_in_key=check_in_key
            )

            resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=good_post_data)
            self.assertEqual(resp.status_code, 200)
            cc_json = resp.json()
            self._validate_hotel_voucher_cc(cc_json['data'])

            resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=good_post_data)
            self.assertEqual(resp.status_code, 200)
            resp_json = resp.json()
            self._validate_error_message(resp_json, 200, 'OK', 'HOTEL_VOUCHER_ALREADY_UNLOCKED', 'Hotel payment cannot be unlocked. Hotel payment is already unlocked.', [])
