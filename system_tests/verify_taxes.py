import datetime

import requests

from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestTaxes(StormxSystemVerification):
    """
    Verify that tax-related features of the API are functioning properly.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestTaxes, cls).setUpClass()

    def test_validate_taxes_percentage_single_room(self):
        """
        system test validating basic taxes, one percentage tax type only with one room booked.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-94925'  # MEM
        event_date = self._get_event_date('America/Chicago')  # MEM timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='89.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='MEM')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 1,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '14.35'
        expected_total_amount = '104.34'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_percentage_two_rooms(self):
        """
        system test validating basic taxes, one percentage tax type with two rooms booked.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-94925'  # MEM
        event_date = self._get_event_date('America/Chicago')  # MEM timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='89.99', blocks=2, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='MEM')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '28.71'
        expected_total_amount = '208.69'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_percentage_two_rooms_multi_block(self):
        """
        system test validating basic taxes, one percentage tax type with two rooms booked with multi blocks.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-94925'  # MEM
        event_date = self._get_event_date('America/Chicago')  # MEM timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='89.99', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='89.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='MEM')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '28.71'
        expected_total_amount = '208.69'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_single_room(self):
        """
        system test validating taxes, compound percentage tax types with a single room.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-83564'  # YYZ
        event_date = self._get_event_date('America/Toronto')  # YYZ timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='69.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='YYZ')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 1,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '15.43'
        expected_total_amount = '85.42'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_two_rooms(self):
        """
        system test validating taxes, compound percentage tax types with a two rooms.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-83564'  # YYZ
        event_date = self._get_event_date('America/Toronto')  # YYZ timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='69.99', blocks=2, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='YYZ')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '30.85'
        expected_total_amount = '170.83'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_two_rooms_multi_block(self):
        """
        system test validating taxes, compound percentage tax types with a two rooms multi block.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-83564'  # YYZ
        event_date = self._get_event_date('America/Toronto')  # YYZ timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='69.99', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='69.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='YYZ')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '30.85'
        expected_total_amount = '170.83'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_two_rooms_multi_block_diff_rate(self):
        """
        system test validating taxes, compound percentage tax types with a two rooms multi block with diff rates.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-83564'  # YYZ
        event_date = self._get_event_date('America/Toronto')  # YYZ timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='69.99', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='89.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='YYZ')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '35.26'
        expected_total_amount = '195.24'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_fixed_single_room(self):
        """
        system test validating taxes, compound percentage and fixed tax types with a single room.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-102083'  # CSG
        event_date = self._get_event_date('America/New_York')  # CSG timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='109.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='CSG')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 1,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '22.60'
        expected_total_amount = '132.59'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_fixed_two_rooms(self):
        """
        system test validating taxes, compound percentage and fixed tax types with two rooms.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-102083'  # CSG
        event_date = self._get_event_date('America/New_York')  # CSG timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='109.99', blocks=2, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='CSG')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '45.20'
        expected_total_amount = '265.18'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_fixed_two_rooms_multi_block(self):
        """
        system test validating taxes, compound percentage and fixed tax types with two rooms multi block.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-102083'  # CSG
        event_date = self._get_event_date('America/New_York')  # CSG timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='109.99', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='109.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='CSG')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '45.20'
        expected_total_amount = '265.18'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_compound_percentage_fixed_two_rooms_multi_block_diff_rate(self):
        """
        system test validating taxes, compound percentage and fixed tax types with two rooms multi block diff rate.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-102083'  # CSG
        event_date = self._get_event_date('America/New_York')  # CSG timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='70.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=1, block_price='109.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='CSG')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '38.80'
        expected_total_amount = '218.79'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_percentage_fixed_single_room(self):
        """
        system test validating taxes, percentage and fixed tax types with single room.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-92682'  # SEA
        event_date = self._get_event_date('America/Los_Angeles')  # SEA timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=2, block_price='49.00', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='SEA')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 1,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '8.08'
        expected_total_amount = '57.08'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_percentage_fixed_two_rooms(self):
        """
        system test validating taxes, percentage and fixed tax types with two rooms.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-92682'  # SEA
        event_date = self._get_event_date('America/Los_Angeles')  # SEA timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=2, block_price='109.99', blocks=2, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='SEA')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '31.28'
        expected_total_amount = '251.26'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_percentage_fixed_two_rooms_multi_block(self):
        """
        system test validating taxes, percentage and fixed tax types with two rooms multi block.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-92682'  # SEA
        event_date = self._get_event_date('America/Los_Angeles')  # SEA timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=2, block_price='109.99', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=2, block_price='109.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='SEA')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '31.28'
        expected_total_amount = '251.26'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_validate_taxes_percentage_fixed_two_rooms_multi_block_diff_rate(self):
        """
        system test validating taxes, percentage and fixed tax types with two rooms multi block and diff rates.
        NOTE: test could break if taxes change in DB (need to validate taxes against StormX UI voucher creation)
        """
        customer = 'Purple Rain Airlines'
        hotel_url = self._api_host + '/api/v1/hotels'
        purple_rain_headers = self._generate_airline_headers(customer)

        hotel_id = 'tvl-92682'  # SEA
        event_date = self._get_event_date('America/Los_Angeles')  # SEA timezone port
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=2, block_price='49.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], 294, event_date, ap_block_type=2, block_price='109.99', blocks=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='SEA')

        pr_booking_payload = {
            'hotel_id': hotel_id,
            'room_count': 2,
            'context_ids': [passengers[0]['context_id'], passengers[1]['context_id']]
        }

        expected_tax = '23.71'
        expected_total_amount = '182.70'
        resp = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data']['hotel_voucher']['tax'], expected_tax)
        self.assertEqual(resp_json['data']['hotel_voucher']['total_amount'], expected_total_amount)

    def test_multi_night_booking_fixed_taxes(self):
        """
        validate multi night booking taxes for a 2 night stay
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_sea = 'tvl-92682'
        event_date_sea = self._get_event_date('America/New_York')
        event_date_sea_day2 = event_date_sea + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_sea.split('-')[1], 294, event_date_sea, ap_block_type=1, block_price='50.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_sea.split('-')[1], 294, event_date_sea_day2, ap_block_type=1, block_price='49.99', blocks=1, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 2
        check_in_date = event_date_sea.strftime('%Y-%m-%d')
        check_out_date = (event_date_sea_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=SEA&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_sea, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='SEA', number_of_nights=2)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_sea,
            number_of_nights=number_of_nights
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        used_rate_1 = False
        used_rate_2 = False

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_sea)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
            if room_voucher['rate'] != '50.00':
                self.assertEqual(room_voucher['rate'], '49.99')
                used_rate_2 = True
            else:
                used_rate_1 = True
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

        # validate multi night taxes
        self.assertTrue(used_rate_1)
        self.assertTrue(used_rate_2)
        self.assertEqual(voucher['hotel_voucher']['tax'], '16.40')

    def test_single_night_booking_fixed_taxes(self):
        """
        validate single night booking for fixed taxes
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_sea = 'tvl-92682'
        event_date_sea = self._get_event_date('America/New_York')
        self.add_hotel_availability(hotel_id_sea.split('-')[1], 294, event_date_sea, ap_block_type=1, block_price='49.99', blocks=1, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 1
        check_in_date = event_date_sea.strftime('%Y-%m-%d')
        check_out_date = (event_date_sea + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=SEA&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_sea, hotel_ids)

        # create passengers with 2 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='SEA', number_of_nights=2)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=room_count,
            hotel_id=hotel_id_sea,
            number_of_nights=number_of_nights
        )

        # book multi night stay
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        # validate multi night voucher
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_sea)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), number_of_nights)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], room_count)
            self.assertEqual(room_voucher['rate'], '49.99')
        self.assertEqual(voucher['hotel_voucher']['check_in_date'], check_in_date)
        self.assertEqual(voucher['hotel_voucher']['check_out_date'], check_out_date)

        # validate multi night taxes
        self.assertEqual(voucher['hotel_voucher']['tax'], '8.20')
