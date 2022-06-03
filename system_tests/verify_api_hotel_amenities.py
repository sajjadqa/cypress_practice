from uuid import UUID

import requests


from stormx_verification_framework import (
    StormxSystemVerification,
    uses_expedia,
)


class TestApiHotelAmenities(StormxSystemVerification):
    """
    Verify hotel amenities are reported correctly in inventory, booking, and state check endpoints.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelAmenities, cls).setUpClass()

    def test_hotel_amenities(self):
        """
        validate system returns only available hotel_amenities for Travelliance inventory
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=LAX'

        hotel_id = 98700
        # hotel_amenity_id = 44865  # populated dynamically from amenity object
        amenity_name = 'Business Center'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id, 294, event_date, ap_block_type=1,
                                    block_price='150.00', blocks=5, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        # validate Business Center amenity in amenities list
        self.assertIn({'name': amenity_name}, hotel_object['amenities'])

        # get Business Center amenity object
        amenity_object = None
        hotel_amenities = self.get_available_amenities_for_a_hotel(hotel_id)
        for amenity in hotel_amenities['amenities']:
            if amenity['amenity_name'] == amenity_name:
                amenity_object = amenity

        self.assertIsNotNone(amenity_object, " Amenity (" + amenity_name + ") is not enabled for hotel")
        hotel_amenity_id = amenity_object['id']
        amenity_master_id = amenity_object['amenity_master_id']

        # remove amenity relationship to hotel
        self.add_edit_hotel_amenity(hotel_id=hotel_id, hotel_amenity_id=hotel_amenity_id, available=0,
                                    amenity_id=amenity_master_id)

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        # validate Business Center amenity NOT in amenities list
        self.assertNotIn({'name': amenity_name}, hotel_object['amenities'])

        # re establish the amenity relationship to hotel
        self.add_edit_hotel_amenity(hotel_id=hotel_id, hotel_amenity_id=hotel_amenity_id, available=1,
                                    amenity_id=amenity_master_id)

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        # validate Business Center amenity is back in amenities list
        self.assertIn({'name': amenity_name}, hotel_object['amenities'])

        # un-activate the parent amenity master
        self.add_edit_amenity(amenity_id=amenity_master_id, amenity_name=amenity_object['amenity_name'],
                              is_available=0)

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        # validate Business Center amenity NOT in amenities list
        self.assertNotIn({'name': amenity_name}, hotel_object['amenities'])

        # re-activate the parent amenity master
        self.add_edit_amenity(amenity_id=amenity_master_id, amenity_name=amenity_object['amenity_name'],
                              is_available=1)

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        # validate Business Center amenity is back in amenities list
        self.assertIn({'name': amenity_name}, hotel_object['amenities'])

    def test_hotel_restaurant_on_property_tvl(self):
        """
        validates hotel information with and with out restaurant_on_property
        on voucher responses and full state for tvl inventory
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        voucher_url = self._api_host + '/api/v1/voucher/'
        passenger_url = self._api_host + '/api/v1/passenger/'

        hotel_id_with_amenity = 'tvl-98711'
        hotel_id_without_amenity = 'tvl-103476'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id_with_amenity.split('-')[1], 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(hotel_id_without_amenity.split('-')[1], 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        hotel_resp = requests.get(url=hotel_url + '?room_count=1&port=LAX&provider=tvl', headers=headers)
        self.assertEqual(hotel_resp.status_code, 200)
        hotel_json = hotel_resp.json()['data']
        self.assertGreater(len(hotel_json), 0)

        validated_hotel_with_amenity = False
        validated_hotel_with_amenity_property = False
        validated_hotel_without_amenity = False
        for hotel in hotel_json:
            self.assertEqual(hotel['provider'], 'tvl')
            if hotel['hotel_id'] == hotel_id_with_amenity:
                for amenity in hotel['amenities']:
                    if amenity['name'] == 'Restaurant on Property':
                        validated_hotel_with_amenity_property = True
                self.assertEqual(hotel['restaurant_on_property'], True)
                validated_hotel_with_amenity = True
            if hotel['hotel_id'] == hotel_id_without_amenity:
                for amenity in hotel['amenities']:
                    if amenity['name'] == 'Restaurant on Property':
                        self.assertFalse(True, msg='hotel restaurant amenity unexpectedly found')
                self.assertEqual(hotel['restaurant_on_property'], False)
                validated_hotel_without_amenity = True
        self.assertEqual(validated_hotel_with_amenity, True)
        self.assertEqual(validated_hotel_with_amenity_property, True)
        self.assertEqual(validated_hotel_without_amenity, True)

        # validate hotel with restaurant
        passengers = self._create_2_passengers('Purple Rain Airlines', port_accommodation='LAX')

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=1,
            hotel_id=hotel_id_with_amenity
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()['data']
        UUID(book_resp_json['voucher_id'], version=4)
        self.assertEqual(book_resp_json['hotel_voucher']['restaurant_on_property'], True)

        voucher_resp = requests.get(url=voucher_url + book_resp_json['voucher_id'], headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()['data']
        UUID(voucher_resp_json['voucher_id'], version=4)
        self.assertEqual(voucher_resp_json['hotel_voucher']['restaurant_on_property'], True)

        full_state_resp = requests.get(url=passenger_url + passengers[0]['context_id'] +  '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()['data']
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['restaurant_on_property'], True)

        # validate hotel without restaurant
        passengers = self._create_2_passengers('Purple Rain Airlines', port_accommodation='LAX')

        payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=1,
            hotel_id=hotel_id_without_amenity
        )

        book_resp = requests.post(hotel_url, headers=headers, json=payload)
        self.assertEqual(book_resp.status_code, 200)
        book_resp_json = book_resp.json()['data']
        UUID(book_resp_json['voucher_id'], version=4)
        self.assertEqual(book_resp_json['hotel_voucher']['restaurant_on_property'], False)

        voucher_resp = requests.get(url=voucher_url + book_resp_json['voucher_id'], headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()['data']
        UUID(voucher_resp_json['voucher_id'], version=4)
        self.assertEqual(voucher_resp_json['hotel_voucher']['restaurant_on_property'], False)

        full_state_resp = requests.get(url=passenger_url + passengers[0]['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()['data']
        self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['restaurant_on_property'], False)
        self.assertNotIn('amenities', full_state_resp_json['voucher']['hotel_voucher'])

    @uses_expedia
    def test_hotel_restaurant_on_property_ean(self):
        """
        validates hotel information with and with out restaurant_on_property
        on voucher responses and full state for ean inventory
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'
        voucher_url = self._api_host + '/api/v1/voucher/'
        passenger_url = self._api_host + '/api/v1/passenger/'

        hotel_id_with_amenity = None
        hotel_id_without_amenity = None

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        hotel_resp = requests.get(url=hotel_url + '?room_count=1&port='+ port +'&provider=ean', headers=headers)
        self.assertEqual(hotel_resp.status_code, 200)
        hotel_json = hotel_resp.json()['data']
        self.assertGreater(len(hotel_json), 0, msg='no expedia inventory in port ' + repr(port))

        validated_hotel_with_amenity = False
        validated_hotel_with_amenity_property = False
        validated_hotel_without_amenity = False
        for hotel in hotel_json:
            self.assertEqual(hotel['provider'], 'ean')
            if hotel['restaurant_on_property']:
                for amenity in hotel['amenities']:
                    if amenity['name'] == 'Restaurant on Property':
                        hotel_id_with_amenity = hotel['hotel_id']
                        validated_hotel_with_amenity_property = True
                        validated_hotel_with_amenity = True
                self.assertEqual(hotel['restaurant_on_property'], True)
            else:
                for amenity in hotel['amenities']:
                    if amenity['name'] == 'Restaurant on Property':
                        self.assertFalse(True, msg='hotel restaurant amenity unexpectedly found')
                self.assertEqual(hotel['restaurant_on_property'], False)
                validated_hotel_without_amenity = True
                hotel_id_without_amenity = hotel['hotel_id']
        self.assertEqual(validated_hotel_with_amenity, True)
        self.assertEqual(validated_hotel_with_amenity_property, True)
        if hotel_id_without_amenity:
            self.assertEqual(validated_hotel_without_amenity, True)

        # validate hotel with restaurant

        if validated_hotel_with_amenity:
            self.assertEqual(validated_hotel_with_amenity, True)
            self.assertEqual(validated_hotel_with_amenity_property, True)

            passengers = self._create_2_passengers('Purple Rain Airlines', port_accommodation=port)

            payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=1,
            hotel_id=hotel_id_with_amenity
        )

            book_resp = requests.post(hotel_url, headers=headers, json=payload)
            self.assertEqual(book_resp.status_code, 200)
            book_resp_json = book_resp.json()['data']
            UUID(book_resp_json['voucher_id'], version=4)
            self.assertEqual(book_resp_json['hotel_voucher']['restaurant_on_property'], True)

            voucher_resp = requests.get(url=voucher_url + book_resp_json['voucher_id'], headers=headers)
            self.assertEqual(voucher_resp.status_code, 200)
            voucher_resp_json = voucher_resp.json()['data']
            UUID(voucher_resp_json['voucher_id'], version=4)
            self.assertEqual(voucher_resp_json['hotel_voucher']['restaurant_on_property'], True)

            full_state_resp = requests.get(url=passenger_url + passengers[0]['context_id'] + '/state', headers=headers)
            self.assertEqual(full_state_resp.status_code, 200)
            full_state_resp_json = full_state_resp.json()['data']
            self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['restaurant_on_property'], True)

        # validate hotel without restaurant
        if validated_hotel_without_amenity:
            self.assertEqual(validated_hotel_without_amenity, True)

            passengers = self._create_2_passengers('Purple Rain Airlines', port_accommodation=port)

            payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=1,
            hotel_id=hotel_id_without_amenity
        )

            book_resp = requests.post(hotel_url, headers=headers, json=payload)
            self.assertEqual(book_resp.status_code, 200)
            book_resp_json = book_resp.json()['data']
            UUID(book_resp_json['voucher_id'], version=4)
            self.assertEqual(book_resp_json['hotel_voucher']['restaurant_on_property'], False)

            voucher_resp = requests.get(url=voucher_url + book_resp_json['voucher_id'], headers=headers)
            self.assertEqual(voucher_resp.status_code, 200)
            voucher_resp_json = voucher_resp.json()['data']
            UUID(voucher_resp_json['voucher_id'], version=4)
            self.assertEqual(voucher_resp_json['hotel_voucher']['restaurant_on_property'], False)

            full_state_resp = requests.get(url=passenger_url + passengers[0]['context_id'] + '/state', headers=headers)
            self.assertEqual(full_state_resp.status_code, 200)
            full_state_resp_json = full_state_resp.json()['data']
            self.assertEqual(full_state_resp_json['voucher']['hotel_voucher']['restaurant_on_property'], False)
            self.assertNotIn('amenities', full_state_resp_json['voucher']['hotel_voucher'])

    def test_hotel_shuttle_time_24_hour_format(self):
        """
        validate system returns shuttle amenity
        and it is in correct format if shuttle is available for 24 hours
        """

        hotel_id = 83900# Hilton Pasadena
        hotel_port = 'LAX'
        airline = 'Purple Rain Airlines'
        shuttle_amenity = {
            'id': 0,
            'amenity_master_id': 1,
            'amenity_name': 'Hotel Shuttle',
            'allow_operating_hours': True,
            'hotel_amenity_operated_from': '00:00',
            'hotel_amenity_operated_to': '00:00',
            'amenity_fee': '12.05',
            'is_available': True,
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenities(hotel_id=hotel_id, hotel_amenities=[shuttle_amenity])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        headers = self._generate_airline_headers(customer=airline)
        hotel_url = self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=' + hotel_port

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id, 294, event_date, ap_block_type=1, block_price='150.00',
                                    blocks=5, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)

        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        self.assertIsNotNone(hotel_object)
        # validate hotel shuttle amenity
        self.assertIn({'name': shuttle_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(shuttle_amenity['is_available'], hotel_object['shuttle'])
        operating_hours = '0:00 23:59'
        self.assertEqual(operating_hours, hotel_object['shuttle_timing'])

    def test_hotel_shuttle_time_hour_format(self):
        """
        validate system returns shuttle amenity
        and it is in correct format if shuttle is available for hours like 09:00 to 03:00
        """

        hotel_id = 83900# Hilton Pasadena
        hotel_port = 'LAX'
        airline = 'Purple Rain Airlines'
        shuttle_amenity = {
            'id': 0,
            'amenity_master_id': 1,
            'amenity_name': 'Hotel Shuttle',
            'allow_operating_hours': True,
            'hotel_amenity_operated_from': '03:00',
            'hotel_amenity_operated_to': '09:00',
            'amenity_fee': '12.05',
            'is_available': True,
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenities(hotel_id=hotel_id, hotel_amenities=[shuttle_amenity])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        headers = self._generate_airline_headers(customer=airline)
        hotel_url = self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=' + hotel_port

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id, 294, event_date, ap_block_type=1, block_price='150.00',
                                    blocks=5, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)

        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        self.assertIsNotNone(hotel_object)
        # validate hotel shuttle amenity
        self.assertIn({'name': shuttle_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(shuttle_amenity['is_available'], hotel_object['shuttle'])
        operating_hours = '3:00 9:00'
        self.assertEqual(operating_hours, hotel_object['shuttle_timing'])

    def test_hotel_shuttle_not_serviced_case(self):
        """
        validate system does not returns shuttle amenity if it is not serviced
        and it has serviced timing of 0:00 to 0:00
        """

        hotel_id = 83900# Hilton Pasadena
        hotel_port = 'LAX'
        airline = 'Purple Rain Airlines'
        shuttle_amenity = {
                'id': 0,
                'amenity_master_id': 1,
                'amenity_name': 'Hotel Shuttle',
                'allow_operating_hours': True,
                'hotel_amenity_operated_from': '',
                'hotel_amenity_operated_to': '',
                'amenity_fee': '12.05',
                'is_available': False,
                'comment': 'testing via system test'
            }

        response = self.add_edit_hotel_amenities(hotel_id=hotel_id, hotel_amenities=[shuttle_amenity])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        headers = self._generate_airline_headers(customer=airline)
        hotel_url = self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=' + hotel_port

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id, 294, event_date, ap_block_type=1, block_price='150.00',
                                    blocks=5, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)

        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        self.assertIsNotNone(hotel_object)
        # validate hotel shuttle amenity not present
        self.assertNotIn({'name': shuttle_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(shuttle_amenity['is_available'], hotel_object['shuttle'])
        operating_hours = ''
        self.assertEqual(operating_hours, hotel_object['shuttle_timing'])
