import requests
import json
from stormx_verification_framework import StormxSystemVerification
from uuid import UUID
from decimal import Decimal


class TestHotelAllowances(StormxSystemVerification):
    """
    validate hotel allowances
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestHotelAllowances, cls).setUpClass()

    def test_validate_passenger_import_hotel_allowance_serializer(self):
        """
        validate 400 errors are returned for hotel allowance serializer on passenger import
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        # validate not_offered status on no allowances passed up
        passengers_payload = self._generate_n_passenger_payload(1)

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        passenger = resp.json()['data'][0]
        self.assertEqual(passenger['context_id'], passengers_payload[0]['context_id'])
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        passengers_payload = self._generate_n_passenger_payload(1)

        # validate hotel_allowances cannot be NULL
        passengers_payload[0].update(dict(
            hotel_allowances=None
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        passenger = resp.json()['data'][0]
        self.assertEqual(passenger['context_id'], passengers_payload[0]['context_id'])
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # validate hotel_allowances cannot be empty
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict()
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                     'All hotel_allowances must contain valid allowances.', [])

        # validate hotel_allowances.meals can be NULL
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=None)
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()['data'][0]['context_id'], passengers_payload[0]['context_id'])

        # validate hotel_allowances.amenity can be NULL
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=None)
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()['data'][0]['context_id'], passengers_payload[0]['context_id'])

        # validate hotel_allowances.meals can be NULL
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=None, amenity=None)
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()['data'][0]['context_id'], passengers_payload[0]['context_id'])

        # validate hotel_allowances.meals fields are required
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict())
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)

        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'message': 'This field is required.', 'field': '[0].hotel_allowances.meals.breakfast'},
                                      {'message': 'This field is required.','field': '[0].hotel_allowances.meals.dinner'},
                                      {'message': 'This field is required.', 'field': '[0].hotel_allowances.meals.lunch'}])

        # validate hotel_allowances.amenity fields are required
        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict())
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)

        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.', [{'field': '[0].hotel_allowances.amenity.amount', 'message': 'This field is required.'},
                                     {'field': '[0].hotel_allowances.amenity.currency_code', 'message': 'This field is required.'}])

        # validate hotel_allowances.amenity fields are required (second passenger)
        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[1].update(dict(
            hotel_allowances=dict(amenity=dict())
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.', [{'field': '[1].hotel_allowances.amenity.amount', 'message': 'This field is required.'},
                                     {'field': '[1].hotel_allowances.amenity.currency_code', 'message': 'This field is required.'}])

        # validate hotel_allowances.meals.breakfast field
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=-1, lunch=1, dinner=0))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure this value is greater than or equal to 0.', 'field': '[0].hotel_allowances.meals.breakfast'}])

        # validate hotel_allowances.meals.breakfast field for second passenger
        passengers_payload = self._generate_n_passenger_payload(3)
        passengers_payload[1].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=-1, lunch=1, dinner=0))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure this value is greater than or equal to 0.', 'field': '[1].hotel_allowances.meals.breakfast'}])

        # validate hotel_allowances.meals.breakfast and hotel_allowances.meals.amenity fields
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(
                meals=dict(breakfast=-1, lunch='test', dinner=None),
                amenity=dict(amount='test', currency_code='VND')
            )
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)

        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[0].hotel_allowances.amenity.amount',
                                       'message': 'A valid number is required.'},
                                      {'field': '[0].hotel_allowances.amenity.currency_code',
                                       'message': '"VND" is not a valid choice.'},
                                      {'field': '[0].hotel_allowances.meals.breakfast',
                                       'message': 'Ensure this value is greater than or equal to 0.'},
                                      {'field': '[0].hotel_allowances.meals.lunch',
                                       'message': 'A valid integer is required.'},
                                      {'field': '[0].hotel_allowances.meals.dinner',
                                       'message': 'This field may not be null.'}])

        # validate hotel allowance amenity field is case sensitive
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(
                amenity=dict(amount=10, currency_code='usd')
            )
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'message': '"usd" is not a valid choice.', 'field': '[0].hotel_allowances.amenity.currency_code'}])

    def test_validate_hotel_search_hotel_allowance_serializer(self):
        """
        validate 400 errors are returned for hotel allowance serializer on hotel search
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        # validate hotel_allowances must be a JSON encoded string
        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances=True
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params).json()
        self._validate_error_message(resp, 400, 'Bad Request', 'INVALID_JSON',
                                     'There was an error parsing the JSON data. Please verify the data is in valid JSON form.', [])

        # validate required fields
        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances='{}'
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params).json()
        self._validate_error_message(resp, 400, 'Bad Request', 'INVALID_ACCOMMODATION', 'meals or amenity is required for hotel_allowances.', [])

        # validate hotel_allowances.meals
        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances=json.dumps(dict(meals='test'))
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params).json()
        self._validate_error_message(resp, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.',
                                     [{'field': 'hotel_allowances.meals', 'message': 'Must be a valid boolean.'}])

        # validate hotel_allowances.amenity
        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances=json.dumps(dict(amenity='test'))
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params).json()
        self._validate_error_message(resp, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel search.',
                                     [{'field': 'hotel_allowances.amenity', 'message': 'Must be a valid boolean.'}])

        # validate hotel_allowances cannot be NULL
        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances='null'
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params).json()
        self._validate_error_message(resp, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.',
                                     [{'field': 'hotel_allowances', 'message': 'This field may not be null.'}])

        # validate hotel_allowances.meals and hotel_allowances.amenity cannot be NULL
        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances=json.dumps(dict(amenity=None, meals=None))
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.',
                                     [{'field': 'hotel_allowances.amenity', 'message': 'This field may not be null.'},
                                      {'field': 'hotel_allowances.meals', 'message': 'This field may not be null.'}])

    def test_validate_hotel_allowance_amenity_max_setting(self):
        """
        validate 400 errors are returned for hotel allowance amenity value exceeding the airline setting
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        currency_codes = ['USD', 'EUR', 'CAD', 'GBP']
        for currency_code in currency_codes:
            passengers_payload = self._generate_n_passenger_payload(1)

            # validate hotel_allowances cannot be NULL
            passengers_payload[0].update(dict(
                hotel_allowances=dict(amenity=dict(amount='100.00', currency_code=currency_code))
            ))

            resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
            self.assertEqual(resp.status_code, 400)
            resp_json = resp.json()

            self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                         'hotel_allowances.amenity.amount exceeds the current airline maximum setting value for ' + currency_code, [])

    def test_validate_hotel_allowance_amenity_max_setting_success(self):
        """
        validate successful amenity allowance imports with settings check
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        currency_codes = [
            # validate each setting for equaling max and less than max
            dict(code='GBP', amount='10.00'), dict(code='GBP', amount='8.00'),
            dict(code='EUR', amount='20.00'), dict(code='EUR', amount='12.00'),
            dict(code='USD', amount='20.00'), dict(code='USD', amount='15.00'),
            dict(code='CAD', amount='25.00'), dict(code='CAD', amount='20.00'),
        ]

        for currency_code in currency_codes:
            passengers_payload = self._generate_n_passenger_payload(1)

            # validate hotel_allowances cannot be NULL
            passengers_payload[0].update(dict(
                hotel_allowances=dict(amenity=dict(amount=currency_code['amount'], currency_code=currency_code['code']))
            ))

            resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
            self.assertEqual(resp.status_code, 201)
            resp_json = resp.json()
            self.assertGreater(len(resp_json['data']), 0)

            passenger = resp.json()['data'][0]
            self.assertEqual(passenger['context_id'], passengers_payload[0]['context_id'])
            self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
            self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
            self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
            self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

    def test_validate_hotel_allowance_breakfast_max(self):
        """
        validate max breakfast allowance settings
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=0, dinner=0))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # hotel_id with high allowance rate
        hotel_id_high_allowance = 'tvl-98734'
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98734, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate error returned
        self.assertEqual(booking_resp.status_code, 400)
        self._validate_error_message(booking_resp.json(), 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                     'Hotel breakfast allowance rate is higher than the allowed breakfast allowance rate by the airline for USD', [])

        # hotel_id with same allowance rate
        hotel_id_high_allowance = 'tvl-100511'
        self.add_hotel_availability(100511, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        UUID(booking_resp_json['data']['voucher_id'], version=4)
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNotNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['meals']['lunch'])
        self.assertIsNone(hotel_allowances['meals']['dinner'])
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '20.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '20.00')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(hotel_allowances['meals']['breakfast']['total']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

    def test_validate_hotel_allowance_lunch_max(self):
        """
        validate max lunch allowance settings
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=0, lunch=1, dinner=0))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # hotel_id with high allowance rate
        hotel_id_high_allowance = 'tvl-98734'
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98734, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate error returned
        self.assertEqual(booking_resp.status_code, 400)
        self._validate_error_message(booking_resp.json(), 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                     'Hotel lunch allowance rate is higher than the allowed lunch allowance rate by the airline for USD', [])

        # hotel_id with same allowance rate
        hotel_id_high_allowance = 'tvl-100511'
        self.add_hotel_availability(100511, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        UUID(booking_resp_json['data']['voucher_id'], version=4)
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNotNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['meals']['breakfast'])
        self.assertIsNone(hotel_allowances['meals']['dinner'])
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '20.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '20.00')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(hotel_allowances['meals']['lunch']['total']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

    def test_validate_hotel_allowance_dinner_max(self):
        """
        validate max dinner allowance settings
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=0, lunch=0, dinner=1))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # hotel_id with high allowance rate
        hotel_id_high_allowance = 'tvl-98734'
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98734, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate error returned
        self.assertEqual(booking_resp.status_code, 400)
        self._validate_error_message(booking_resp.json(), 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                     'Hotel dinner allowance rate is higher than the allowed dinner allowance rate by the airline for USD', [])

        # hotel_id with same allowance rate
        hotel_id_high_allowance = 'tvl-100511'
        self.add_hotel_availability(100511, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        UUID(booking_resp_json['data']['voucher_id'], version=4)
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNotNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['meals']['breakfast'])
        self.assertIsNone(hotel_allowances['meals']['lunch'])
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '20.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '20.00')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(hotel_allowances['meals']['dinner']['total']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

    def test_validate_hotel_allowance_amenity_max(self):
        """
        validate max amenity allowance settings
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount=20, currency_code='USD'))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        # hotel_id with high allowance rate
        hotel_id_high_allowance = 'tvl-98734'
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98734, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate error returned
        self.assertEqual(booking_resp.status_code, 400)
        self._validate_error_message(booking_resp.json(), 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                     'Hotel amenity allowance amount is higher than the allowed amenity allowance amount by the hotel', [])

        # hotel_id with same allowance rate
        hotel_id_high_allowance = 'tvl-100511'
        self.add_hotel_availability(100511, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        UUID(booking_resp_json['data']['voucher_id'], version=4)
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertIsNotNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])
        self.assertEqual(hotel_allowances['amenity']['amount'], '20.00')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'accepted')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['currency_code'], 'USD')
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(hotel_allowances['amenity']['amount']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

    def test_validate_hotel_allowance_hotel_amenity_max_converted(self):
        """
        validate max hotel amenity allowance settings for a converted allowance
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount=15, currency_code='EUR'))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        # hotel_id with high allowance rate
        hotel_id_high_allowance = 'tvl-98734'
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98734, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate error returned
        self.assertEqual(booking_resp.status_code, 400)
        self._validate_error_message(booking_resp.json(), 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                     'Hotel amenity allowance amount is higher than the allowed amenity allowance amount by the hotel', [])

        # hotel_id with same allowance rate
        hotel_id_high_allowance = 'tvl-100511'
        self.add_hotel_availability(100511, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        UUID(booking_resp_json['data']['voucher_id'], version=4)
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertIsNotNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])
        # NOTE: not correct currency conversion but current snap has this conversion rate by default
        self.assertEqual(hotel_allowances['amenity']['amount'], '16.89')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'accepted')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['currency_code'], 'USD')
        self.assertEqual(hotel_voucher['total_amount'], str(Decimal(hotel_allowances['amenity']['amount']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax'])))

    def test_validate_hotel_allowance_airline_amenity_max_converted(self):
        """
        validate max airline amenity allowance settings for a converted allowance
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount=20, currency_code='USD')),
            port_accommodation='YYZ'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        # hotel_id with high allowance rate
        hotel_id_high_allowance = 'tvl-88403'
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(88403, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        booking_payload = dict(hotel_id=hotel_id_high_allowance, context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate error returned
        self.assertEqual(booking_resp.status_code, 400)
        self._validate_error_message(booking_resp.json(), 400, 'Bad Request', 'INVALID_ACCOMMODATION',
                                     'hotel_allowances.amenity.amount exceeds the current airline maximum setting value for CAD', [])

    def test_validate_hotel_allowance_hotel_search(self):
        """
        validate hotel search for hotel allowances
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        # add inventory
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91157, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(91158, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(91159, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(91160, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(91161, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # validate hotels have meal accommodations
        validated_hotel_1 = False
        validated_hotel_2 = False
        validated_hotel_3 = False
        validated_hotel_4 = False

        query_params = dict(
            port='MAD',
            room_count=1,
            hotel_allowances=json.dumps(dict(meals=True))
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            if hotel['hotel_id'] == 'tvl-91158':
                self.assertIsNone(hotel['hotel_allowances']['amenity'])
                self.assertEqual(hotel['hotel_allowances']['meals']['breakfast']['rate'], '10.00')
                self.assertIsNone(hotel['hotel_allowances']['meals']['lunch'])
                self.assertIsNone(hotel['hotel_allowances']['meals']['dinner'])
                validated_hotel_1 = True
            if hotel['hotel_id'] == 'tvl-91159':
                self.assertIsNone(hotel['hotel_allowances']['amenity'])
                self.assertEqual(hotel['hotel_allowances']['meals']['lunch']['rate'], '10.00')
                self.assertIsNone(hotel['hotel_allowances']['meals']['breakfast'])
                self.assertIsNone(hotel['hotel_allowances']['meals']['dinner'])
                validated_hotel_2 = True
            if hotel['hotel_id'] == 'tvl-91160':
                self.assertIsNone(hotel['hotel_allowances']['amenity'])
                self.assertEqual(hotel['hotel_allowances']['meals']['dinner']['rate'], '10.00')
                self.assertIsNone(hotel['hotel_allowances']['meals']['breakfast'])
                self.assertIsNone(hotel['hotel_allowances']['meals']['lunch'])
                validated_hotel_3 = True
            if hotel['hotel_id'] == 'tvl-91161':
                self.assertEqual(hotel['hotel_allowances']['amenity']['amount'], '15.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['breakfast']['rate'], '12.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['lunch']['rate'], '20.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['dinner']['rate'], '10.00')
                validated_hotel_4 = True

        self.assertTrue(validated_hotel_1)
        self.assertTrue(validated_hotel_2)
        self.assertTrue(validated_hotel_3)
        self.assertTrue(validated_hotel_4)

        # validate hotels have amenity accommodations
        validated_hotel_1 = False
        validated_hotel_2 = False

        query_params = dict(
            port='MAD',
            room_count=1,
            hotel_allowances=json.dumps(dict(amenity=True))
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['amenity'])
            if hotel['hotel_id'] == 'tvl-91157':
                self.assertEqual(hotel['hotel_allowances']['amenity']['amount'], '10.00')
                self.assertIsNone(hotel['hotel_allowances']['meals'])
                validated_hotel_1 = True
            if hotel['hotel_id'] == 'tvl-91161':
                self.assertEqual(hotel['hotel_allowances']['amenity']['amount'], '15.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['breakfast']['rate'], '12.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['lunch']['rate'], '20.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['dinner']['rate'], '10.00')
                validated_hotel_2 = True
        self.assertTrue(validated_hotel_1)
        self.assertTrue(validated_hotel_2)

        # validate hotels have meal and amenity accommodations
        validated_hotel_1 = False

        query_params = dict(
            port='MAD',
            room_count=1,
            hotel_allowances=json.dumps(dict(meals=True, amenity=True))
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertIsNotNone(hotel['hotel_allowances']['amenity'])
            if hotel['hotel_id'] == 'tvl-91161':
                self.assertEqual(hotel['hotel_allowances']['amenity']['amount'], '15.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['breakfast']['rate'], '12.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['lunch']['rate'], '20.00')
                self.assertEqual(hotel['hotel_allowances']['meals']['dinner']['rate'], '10.00')
                validated_hotel_1 = True
        self.assertTrue(validated_hotel_1)

    def test_validate_hotel_allowance_expedia(self):
        """
        validate expedia hotels return nothing for hotel allowances
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances=json.dumps(dict(meals=True))
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)

        query_params = dict(
            port='LAX',
            room_count=1,
            hotel_allowances=json.dumps(dict(meals=True)),
            provider='ean'
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertEqual(len(hotels), 0)

    def test_validate_hotel_allowance_setting_disabled(self):
        """
        validate only allowance inventory is returned for passenger hotel allowances
        on the pax app when the setting is disabled
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=0, dinner=1)),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        query_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        resp = requests.get(url=hotel_url, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertEqual(len(hotels), 0)

        # add inventory with only dinner (ensure it does not return)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91160, 71, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        resp = requests.get(url=hotel_url, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertEqual(len(hotels), 0)

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91161, 71, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        resp = requests.get(url=hotel_url, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)

        # book hotel with allowance
        query_params = dict(ak1=passenger['ak1'], ak2=passenger['ak2'])
        booking_payload = dict(hotel_id='tvl-91161', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload, params=query_params)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals']['lunch'])
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '12.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '10.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '10.00')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

    def test_validate_hotel_allowance_setting_enabled(self):
        """
        validate non allowance inventory is returned for passenger hotel allowances
        on the pax app when the setting is disabled
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1), amenity=dict(amount=10, currency_code='USD')),
            port_accommodation='JFK'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        query_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        resp = requests.get(url=hotel_url, params=query_params)
        self.assertEqual(resp.status_code, 200)

        # tvl
        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertGreater(hotel['hard_block_count'], 0)
            self.assertIsNone(hotel['hotel_allowances']['meals'])
            self.assertIsNone(hotel['hotel_allowances']['amenity'])

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1), amenity=dict(amount=10, currency_code='USD')),
            port_accommodation='FAT'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        query_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        resp = requests.get(url=hotel_url, params=query_params)
        self.assertEqual(resp.status_code, 200)

        # ean
        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertEqual(hotel['hard_block_count'], 0)
            self.assertIsNone(hotel['hotel_allowances']['meals'])
            self.assertIsNone(hotel['hotel_allowances']['amenity'])

    def test_validate_hotel_allowance_pax_app_booking(self):
        """
        validate hotel allowances pax app booking
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1), amenity=dict(amount=5, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        query_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        resp = requests.get(url=hotel_url, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertIsNotNone(hotel['hotel_allowances']['amenity'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['lunch']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['amenity']['amount']), 0)

        # book hotel with allowance
        query_params = dict(ak1=passenger['ak1'], ak2=passenger['ak2'])
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, data=booking_payload, params=query_params)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '6.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '7.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '8.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '5.00')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'accepted')

    def test_validate_hotel_allowance_are_null_for_expedia(self):
        """
        validate expedia hotels return null for hotel allowances
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        query_params = dict(
            port=port,
            room_count=1,
            provider='ean'
        )

        resp = requests.get(url=hotel_url, headers=headers, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0, msg='no expedia inventory for ' + repr(port))
        for hotel in hotels:
            self.assertEqual(hotel['provider'], 'ean')
            self.assertIsNone(hotel['hotel_allowances']['amenity'])
            self.assertIsNone(hotel['hotel_allowances']['meals'])

    def test_validate_hotel_allowance_airline_booking(self):
        """
        validate hotel allowances airline api booking
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1), amenity=dict(amount=5, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        query_params = dict(
            room_count=1,
            port='MAD'
        )

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        resp = requests.get(url=hotel_url, params=query_params, headers=headers)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['lunch']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['amenity']['amount']), 0)

        # book hotel with allowance
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '6.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '7.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '8.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '5.00')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'accepted')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']

        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

        self.assertEqual(hotel_voucher['total_amount'],
                         str(Decimal(hotel_allowances['amenity']['amount']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax']) +
                             Decimal(hotel_allowances['meals']['breakfast']['total']) + Decimal(hotel_allowances['meals']['lunch']['total']) +
                             Decimal(hotel_allowances['meals']['dinner']['total'])))

    def test_validate_hotel_allowance_airline_booking_multiple_allowances(self):
        """
        validate hotel allowances airline api booking with multiple allowances
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=2, lunch=2, dinner=2), amenity=dict(amount=4.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        query_params = dict(
            room_count=1,
            port='MAD'
        )

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1,pay_type='0')

        resp = requests.get(url=hotel_url, params=query_params, headers=headers)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['lunch']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['amenity']['amount']), 0)

        # book hotel with allowance
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '14.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '4.50')

        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'accepted')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']

        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

        self.assertEqual(hotel_voucher['total_amount'],
                         str(Decimal(hotel_allowances['amenity']['amount']) + Decimal(
                             hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax']) +
                             Decimal(hotel_allowances['meals']['breakfast']['total']) + Decimal(
                             hotel_allowances['meals']['lunch']['total']) +
                             Decimal(hotel_allowances['meals']['dinner']['total'])))

    def test_validate_hotel_allowance_airline_booking_with_fees(self):
        """
        validate hotel allowances airline api booking with fees
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1), amenity=dict(amount=5, currency_code='EUR')),
            port_accommodation='MAD',
            service_pet=True
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        query_params = dict(
            room_count=1,
            port='MAD'
        )

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        resp = requests.get(url=hotel_url, params=query_params, headers=headers)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertTrue(hotel['service_pets_allowed'], True)
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['lunch']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['amenity']['amount']), 0)

        # book hotel with allowance
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '6.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '7.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '8.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '5.00')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']

        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

        self.assertEqual(hotel_voucher['fees'][0]['type'], 'service_pet')
        self.assertEqual(hotel_voucher['fees'][0]['rate'], '20.00')
        self.assertEqual(hotel_voucher['fees'][0]['count'], 1)
        self.assertEqual(hotel_voucher['fees'][0]['total'], '20.00')
        self.assertEqual(hotel_voucher['total_amount'],
                         str(Decimal(hotel_allowances['amenity']['amount']) + Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax']) +
                             Decimal(hotel_allowances['meals']['breakfast']['total']) + Decimal(hotel_allowances['meals']['lunch']['total']) +
                             Decimal(hotel_allowances['meals']['dinner']['total']) + Decimal(hotel_voucher['fees'][0]['total'])))

    def test_validate_hotel_allowance_pax_app_booking_with_fees(self):
        """
        validate hotel allowances pax app booking with fees
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1), amenity=dict(amount=5, currency_code='EUR')),
            port_accommodation='MAD',
            service_pet=True
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        query_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        resp = requests.get(url=hotel_url, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['lunch']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['amenity']['amount']), 0)

        # book hotel with allowance
        query_params = dict(ak1=passenger['ak1'], ak2=passenger['ak2'])
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, data=booking_payload, params=query_params)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '6.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '7.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '8.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '5.00')

    def test_validate_hotel_allowance_public_hotels_removed(self):
        """
        validate that pax with hotel allowances have their allowances checked
        during pax app hotel search and hotels are removed from the hotel list
        that do not meet the needs of the combined pax
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url_public = self._api_host + '/api/v1/offer/hotels'
        hotel_url_airline = self._api_host + '/api/v1/hotels'

        passengers_payload = self._generate_n_passenger_payload(5)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=0, dinner=0)),
            port_accommodation='DUB'
        ))
        passengers_payload[1].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=0, lunch=1, dinner=0), amenity=dict(amount=5, currency_code='EUR')),
            port_accommodation='DUB'
        ))
        passengers_payload[2].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=0, lunch=0, dinner=1)),
            port_accommodation='DUB'
        ))
        passengers_payload[3].update(dict(
            hotel_allowances=dict(amenity=dict(amount=3, currency_code='EUR')),
            port_accommodation='DUB'
        )),
        passengers_payload[4].update(dict(
            hotel_allowances=dict(amenity=dict(amount=8, currency_code='EUR')),
            port_accommodation='DUB'
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        query_params = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=3
        )

        event_date = self._get_event_date('Europe/Madrid')

        # add inventory with allowances (over settings max)
        self.add_hotel_availability(96063, 294, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')
        self.add_hotel_availability(91219, 294, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')
        self.add_hotel_availability(91220, 294, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')
        self.add_hotel_availability(91217, 294, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')

        # add inventory with allowances (under settings max)
        self.add_hotel_availability(91218, 294, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')

        resp = requests.get(url=hotel_url_public, params=query_params)
        self.assertEqual(resp.status_code, 200)

        hotel_ids = []
        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertIsNotNone(hotel['hotel_allowances']['amenity'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['lunch']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['amenity']['amount']), 0)
            hotel_ids.append(hotel['hotel_id'])

        # validate hotel_ids exist and do not exist
        hotel_ids_should_exist = ['tvl-91218']
        hotel_ids_should_not_exist = ['tvl-91217', 'tvl-96063', 'tvl-91219', 'tvl-91220']
        for hotel_id in hotel_ids_should_exist:
            self.assertIn(hotel_id, hotel_ids)
        for hotel_id in hotel_ids_should_not_exist:
            self.assertNotIn(hotel_id, hotel_ids)

        # airline api search
        query_params = dict(
            room_count=3,
            port='DUB',
            hotel_allowances=json.dumps(dict(meals=True, amenity=True))
        )

        resp = requests.get(url=hotel_url_airline, params=query_params, headers=headers)
        self.assertEqual(resp.status_code, 200)

        hotel_ids = []
        hotels = resp.json()['data']
        self.assertGreater(len(hotels), 0)
        for hotel in hotels:
            self.assertIsNotNone(hotel['hotel_allowances']['meals'])
            self.assertIsNotNone(hotel['hotel_allowances']['amenity'])
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['breakfast']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['lunch']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['meals']['dinner']['rate']), 0)
            self.assertGreater(Decimal(hotel['hotel_allowances']['amenity']['amount']), 0)
            hotel_ids.append(hotel['hotel_id'])

        # validate all hotel_ids are returned on airline api
        for hotel_id in hotel_ids_should_exist:
            self.assertIn(hotel_id, hotel_ids)
        for hotel_id in hotel_ids_should_not_exist:
            self.assertIn(hotel_id, hotel_ids)

    def test_validate_passenger_import_hotel_allowance_max_meal_allowance_quantity_and_amenity_amount(self):
        """
        validate 400 errors are returned for hotel allowance serializer on passenger import
        when quantity is greater than the max allowed (MAX_MEAL_ALLOWANCE_QUANTITY) and amenity amount
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer)

        # validate breakfast
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=20, lunch=0, dinner=0))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure this value is less than or equal to 14.', 'field': '[0].hotel_allowances.meals.breakfast'}])

        # validate lunch
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=0, lunch=15, dinner=0))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure this value is less than or equal to 14.', 'field': '[0].hotel_allowances.meals.lunch'}])

        # validate dinner
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=0, lunch=0, dinner=99))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure this value is less than or equal to 14.', 'field': '[0].hotel_allowances.meals.dinner'}])

        # validate max is allowed
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=14, lunch=14, dinner=14))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)

        # validate amenity amount max 8 digits
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount='999999999', currency_code='USD'))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure that there are no more than 8 digits in total.', 'field': '[0].hotel_allowances.amenity.amount'}])

        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount='99999999.99', currency_code='USD'))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure that there are no more than 8 digits in total.', 'field': '[0].hotel_allowances.amenity.amount'}])

        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount='999999.999', currency_code='USD'))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure that there are no more than 8 digits in total.', 'field': '[0].hotel_allowances.amenity.amount'}])

        # validate 8 digits is allowed
        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount='999999.99', currency_code='USD'))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(amenity=dict(amount='9999999', currency_code='USD'))
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        resp_json = resp.json()
        self.assertEqual(resp.status_code, 400)

        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': 'Ensure that there are no more than 6 digits before the decimal point.', 'field': '[0].hotel_allowances.amenity.amount'}])

    def test_validate_hotel_allowance_multiple_allowances_multiple_pax(self):
        """
        validate hotel allowances airline api booking with multiple allowances and multiple pax
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1), amenity=dict(amount=2.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))
        passengers_payload[1].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=2, lunch=2, dinner=2), amenity=dict(amount=4.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        if resp_json['data'][0]['context_id'] == passengers_payload[0]['context_id']:
            passenger = resp_json['data'][0]
            passenger2 = resp_json['data'][1]
        else:
            passenger = resp_json['data'][1]
            passenger2 = resp_json['data'][0]

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # book hotel with allowance
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id'], passenger2['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 2)
        if booking_resp_json['data']['passengers'][0]['context_id'] == passenger['context_id']:
            hotel_allowances1 = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
            hotel_allowances2 = booking_resp_json['data']['passengers'][1]['hotel_allowances_voucher']
        else:
            hotel_allowances1 = booking_resp_json['data']['passengers'][1]['hotel_allowances_voucher']
            hotel_allowances2 = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']

        self.assertEqual(hotel_allowances2['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances2['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances2['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances2['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances2['meals']['lunch']['count'], 2)
        self.assertEqual(hotel_allowances2['meals']['lunch']['total'], '14.00')
        self.assertEqual(hotel_allowances2['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances2['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances2['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances2['amenity']['amount'], '4.50')
        self.assertEqual(hotel_allowances1['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances1['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances1['meals']['breakfast']['total'], '6.00')
        self.assertEqual(hotel_allowances1['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances1['meals']['lunch']['count'], 1)
        self.assertEqual(hotel_allowances1['meals']['lunch']['total'], '7.00')
        self.assertEqual(hotel_allowances1['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances1['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances1['meals']['dinner']['total'], '8.00')
        self.assertEqual(hotel_allowances1['amenity']['amount'], '2.50')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['total_amount'],
                         str(Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax']) +
                             Decimal(hotel_allowances1['meals']['breakfast']['total']) +
                             Decimal(hotel_allowances1['meals']['lunch']['total']) +
                             Decimal(hotel_allowances1['meals']['dinner']['total']) +
                             Decimal(hotel_allowances1['amenity']['amount']) +
                             Decimal(hotel_allowances2['meals']['breakfast']['total']) +
                             Decimal(hotel_allowances2['meals']['lunch']['total']) +
                             Decimal(hotel_allowances2['meals']['dinner']['total']) +
                             Decimal(hotel_allowances2['amenity']['amount'])
                             )
                         )

        self.assertEqual(hotel_voucher['total_amount'],
                         str(Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax']) +
                             Decimal(hotel_voucher['hotel_allowances_voucher_total'])
                             )
                         )

        self.assertEqual(hotel_voucher['hotel_allowances_voucher_total'],
                         str(Decimal(hotel_allowances1['meals']['breakfast']['total']) +
                             Decimal(hotel_allowances1['meals']['lunch']['total']) +
                             Decimal(hotel_allowances1['meals']['dinner']['total']) +
                             Decimal(hotel_allowances1['amenity']['amount']) +
                             Decimal(hotel_allowances2['meals']['breakfast']['total']) +
                             Decimal(hotel_allowances2['meals']['lunch']['total']) +
                             Decimal(hotel_allowances2['meals']['dinner']['total']) +
                             Decimal(hotel_allowances2['amenity']['amount'])
                             )
                         )

        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        hotel_voucher_full_state = full_state_1['voucher']['hotel_voucher']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(hotel_voucher_full_state['hotel_allowances_voucher_total'], hotel_voucher['hotel_allowances_voucher_total'])
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '6.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '7.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '8.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '2.50')

        full_state_2 = requests.get(url=passenger_url + '/' + passenger2['context_id'] + '/state', headers=headers).json()['data']
        hotel_voucher_full_state = full_state_2['voucher']['hotel_voucher']
        hotel_allowances = full_state_2['voucher']['hotel_allowances_voucher']
        self.assertEqual(hotel_voucher_full_state['hotel_allowances_voucher_total'], hotel_voucher['hotel_allowances_voucher_total'])
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '14.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '4.50')

    def test_validate_hotel_allowance_single_allowances_multiple_pax(self):
        """
        validate hotel allowances airline api booking with single allowances and multiple pax
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[0].update(dict(
            port_accommodation='MAD'
        ))
        passengers_payload[1].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=2, lunch=2, dinner=2), amenity=dict(amount=4.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        if resp_json['data'][0]['context_id'] == passengers_payload[0]['context_id']:
            passenger = resp_json['data'][0]
            passenger2 = resp_json['data'][1]
        else:
            passenger = resp_json['data'][1]
            passenger2 = resp_json['data'][0]

        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')
        self.assertEqual(passenger2['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger2['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger2['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger2['hotel_allowance_status']['amenity'], 'offered')

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # full state checks
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        full_state_2 = requests.get(url=passenger_url + '/' + passenger2['context_id'] + '/state', headers=headers).json()['data']

        passenger = full_state_1['passenger']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        passenger2 = full_state_2['passenger']
        self.assertEqual(passenger2['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger2['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger2['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger2['hotel_allowance_status']['amenity'], 'offered')

        # book hotel with allowance
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id'], passenger2['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 2)
        if booking_resp_json['data']['passengers'][0]['context_id'] == passenger['context_id']:
            hotel_allowances1 = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
            hotel_allowances2 = booking_resp_json['data']['passengers'][1]['hotel_allowances_voucher']
            passenger = booking_resp_json['data']['passengers'][0]
            passenger2 = booking_resp_json['data']['passengers'][1]
        else:
            hotel_allowances1 = booking_resp_json['data']['passengers'][1]['hotel_allowances_voucher']
            hotel_allowances2 = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
            passenger = booking_resp_json['data']['passengers'][1]
            passenger2 = booking_resp_json['data']['passengers'][0]

        self.assertEqual(hotel_allowances2['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances2['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances2['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances2['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances2['meals']['lunch']['count'], 2)
        self.assertEqual(hotel_allowances2['meals']['lunch']['total'], '14.00')
        self.assertEqual(hotel_allowances2['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances2['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances2['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances2['amenity']['amount'], '4.50')
        self.assertIsNone(hotel_allowances1['meals'])
        self.assertIsNone(hotel_allowances1['amenity'])

        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')
        self.assertEqual(passenger2['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger2['hotel_allowance_status']['lunch'], 'accepted')
        self.assertEqual(passenger2['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger2['hotel_allowance_status']['amenity'], 'accepted')

        # validate all taxes, rates, and allowances add up to total
        hotel_voucher = booking_resp_json['data']['hotel_voucher']
        self.assertEqual(hotel_voucher['total_amount'],
                         str(Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax']) +
                             Decimal(hotel_allowances2['meals']['breakfast']['total']) +
                             Decimal(hotel_allowances2['meals']['lunch']['total']) +
                             Decimal(hotel_allowances2['meals']['dinner']['total']) +
                             Decimal(hotel_allowances2['amenity']['amount'])
                             )
                         )

        self.assertEqual(hotel_voucher['total_amount'],
                         str(Decimal(hotel_voucher['room_vouchers'][0]['rate']) + Decimal(hotel_voucher['tax']) +
                             Decimal(hotel_voucher['hotel_allowances_voucher_total'])
                             )
                         )

        self.assertEqual(hotel_voucher['hotel_allowances_voucher_total'],
                         str(Decimal(hotel_allowances2['meals']['breakfast']['total']) +
                             Decimal(hotel_allowances2['meals']['lunch']['total']) +
                             Decimal(hotel_allowances2['meals']['dinner']['total']) +
                             Decimal(hotel_allowances2['amenity']['amount'])
                             )
                         )

        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        hotel_voucher_full_state = full_state_1['voucher']['hotel_voucher']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(hotel_voucher_full_state['hotel_allowances_voucher_total'], hotel_voucher['hotel_allowances_voucher_total'])
        self.assertIsNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['amenity'])

        full_state_2 = requests.get(url=passenger_url + '/' + passenger2['context_id'] + '/state', headers=headers).json()['data']
        hotel_voucher_full_state = full_state_2['voucher']['hotel_voucher']
        hotel_allowances = full_state_2['voucher']['hotel_allowances_voucher']
        self.assertEqual(hotel_voucher_full_state['hotel_allowances_voucher_total'], hotel_voucher['hotel_allowances_voucher_total'])
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['rate'], '7.00')
        self.assertEqual(hotel_allowances['meals']['lunch']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['lunch']['total'], '14.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '4.50')

        passenger = full_state_1['passenger']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        passenger2 = full_state_2['passenger']
        self.assertEqual(passenger2['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger2['hotel_allowance_status']['lunch'], 'accepted')
        self.assertEqual(passenger2['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger2['hotel_allowance_status']['amenity'], 'accepted')

    def test_validate_hotel_allowance_decline(self):
        """
        validate hotel allowances status create as declined
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=2, lunch=0, dinner=2), amenity=dict(amount=4.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # full state checks
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        passenger = full_state_1['passenger']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])

        # decline hotel with allowance
        decline_resp = requests.put(url=passenger_url + '/' + passenger['context_id'] + '/decline', headers=headers)
        self.assertEqual(decline_resp.status_code, 200)
        passenger = decline_resp.json()['data']['passengers'][0]
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'declined')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'declined')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'declined')
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])

        # full state check
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        passenger = full_state_1['passenger']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'declined')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'declined')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'declined')
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])

    def test_validate_hotel_allowance_cancel(self):
        """
        validate hotel allowances status create as canceled
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=2, lunch=0, dinner=2), amenity=dict(amount=4.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # full state checks
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        passenger = full_state_1['passenger']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])

        # book hotel with allowance
        booking_payload = dict(hotel_id='tvl-91163', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'accepted')

        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '4.50')
        self.assertIsNone(hotel_allowances['meals']['lunch'])

        # full state check
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        passenger = full_state_1['passenger']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'accepted')
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '4.50')
        self.assertIsNone(hotel_allowances['meals']['lunch'])

        # cancel hotel with allowance
        cancel_resp = requests.put(url=passenger_url + '/' + passenger['context_id'] + '/cancel', headers=headers).json()
        self.assertEqual(len(cancel_resp['data']['passengers']), 1)
        hotel_allowances = cancel_resp['data']['passengers'][0]['hotel_allowances_voucher']
        passenger = cancel_resp['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'canceled_voucher')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'canceled_voucher')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'canceled_voucher')

        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '4.50')
        self.assertIsNone(hotel_allowances['meals']['lunch'])

        # full state check
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        passenger = full_state_1['passenger']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'canceled_voucher')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'canceled_voucher')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'canceled_voucher')
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '6.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '12.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['rate'], '8.00')
        self.assertEqual(hotel_allowances['meals']['dinner']['count'], 2)
        self.assertEqual(hotel_allowances['meals']['dinner']['total'], '16.00')
        self.assertEqual(hotel_allowances['amenity']['amount'], '4.50')
        self.assertIsNone(hotel_allowances['meals']['lunch'])

    def test_validate_hotel_allowance_cancel_offer(self):
        """
        validate hotel allowances status create as offered_unavailable
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=2, lunch=0, dinner=2), amenity=dict(amount=4.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # full state checks
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        passenger = full_state_1['passenger']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])

        # cancel hotel with no allowance
        cancel_resp = requests.put(url=passenger_url + '/' + passenger['context_id'] + '/cancel', headers=headers).json()
        self.assertEqual(len(cancel_resp['data']['passengers']), 1)
        hotel_allowances = cancel_resp['data']['passengers'][0]['hotel_allowances_voucher']
        passenger = cancel_resp['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'canceled_offer')
        self.assertIsNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['amenity'])

        # full state check
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        passenger = full_state_1['passenger']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'canceled_offer')
        self.assertIsNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['amenity'])

    def test_validate_hotel_allowance_cancel_offer_all_meals(self):
        """
        validate hotel allowances status create as canceled_offer
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=1)),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91163, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # full state checks
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        passenger = full_state_1['passenger']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])

        # cancel hotel with no allowance
        cancel_resp = requests.put(url=passenger_url + '/' + passenger['context_id'] + '/cancel', headers=headers).json()
        self.assertEqual(len(cancel_resp['data']['passengers']), 1)
        hotel_allowances = cancel_resp['data']['passengers'][0]['hotel_allowances_voucher']
        passenger = cancel_resp['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')
        self.assertIsNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['amenity'])

        # full state check
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        passenger = full_state_1['passenger']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'canceled_offer')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'not_offered')
        self.assertIsNone(hotel_allowances['meals'])
        self.assertIsNone(hotel_allowances['amenity'])

    def test_validate_hotel_allowance_offered_unavailable(self):
        """
        validate hotel allowances status create as offered_unavailable
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=1, lunch=1, dinner=0), amenity=dict(amount=4.50, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]

        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        # add inventory with all allowances (ensure it returns)
        event_date = self._get_event_date('Europe/Madrid')
        self.add_hotel_availability(91158, 294, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')

        # full state checks
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        passenger = full_state_1['passenger']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')
        self.assertIsNone(hotel_allowances['amenity'])
        self.assertIsNone(hotel_allowances['meals'])

        # book hotel with allowance
        booking_payload = dict(hotel_id='tvl-91158', context_ids=[passenger['context_id']], room_count=1)
        booking_resp = requests.post(url=hotel_url, headers=headers, data=booking_payload)

        # validate success
        self.assertEqual(booking_resp.status_code, 200)
        booking_resp_json = booking_resp.json()
        self.assertEqual(len(booking_resp_json['data']['passengers']), 1)
        hotel_allowances = booking_resp_json['data']['passengers'][0]['hotel_allowances_voucher']
        passenger = booking_resp_json['data']['passengers'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered_unavailable')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered_unavailable')

        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '10.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '10.00')
        self.assertIsNone(hotel_allowances['meals']['lunch'])
        self.assertIsNone(hotel_allowances['amenity'])

        # full state check
        full_state_1 = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        passenger = full_state_1['passenger']
        hotel_allowances = full_state_1['voucher']['hotel_allowances_voucher']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'accepted')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered_unavailable')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered_unavailable')
        self.assertEqual(hotel_allowances['meals']['breakfast']['rate'], '10.00')
        self.assertEqual(hotel_allowances['meals']['breakfast']['count'], 1)
        self.assertEqual(hotel_allowances['meals']['breakfast']['total'], '10.00')
        self.assertIsNone(hotel_allowances['meals']['lunch'])
        self.assertIsNone(hotel_allowances['amenity'])

    def test_validate_hotel_allowance_status_passenger_context(self):
        """
        validate hotel allowances status create as offered/not_offered on passenger/context endpoint
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            hotel_allowances=dict(meals=dict(breakfast=0, lunch=1, dinner=2), amenity=dict(amount=1, currency_code='EUR')),
            port_accommodation='MAD'
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')

        passenger = requests.get(url=passenger_url + '/' + passenger['context_id'], headers=headers).json()['data']
        self.assertEqual(passenger['hotel_allowance_status']['breakfast'], 'not_offered')
        self.assertEqual(passenger['hotel_allowance_status']['lunch'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['dinner'], 'offered')
        self.assertEqual(passenger['hotel_allowance_status']['amenity'], 'offered')
