import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import requests

from stormx_verification_framework import StormxSystemVerification


class TestApiHotelBookingBlocks(StormxSystemVerification):
    """
    Verify hotel bookings with a focus on correct block prioritization.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBookingBlocks, cls).setUpClass()

    def test_voucher_uses_correct_block(self):
        """
        validate voucher process uses correct block
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        port_id = 925  # FAT
        airline_id = 294  # PurpleRain
        hotel_id = 'tvl-98843'  # Motel6 FAT
        hotel_id_2 = 'tvl-98842'  # Holiday Inn FAT
        hotel_id_3 = 'tvl-98845'  # Comfort Suites FAT
        event_date = self._get_event_date('America/Los_Angeles')
        _event_date_time = self._calculate_event_datetime('America/Los_Angeles')
        event_date_time = self._get_event_date_time('America/Los_Angeles', _event_date_time)

        comment = 'first ' + str(uuid4())
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='90.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], 0, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='70.00', blocks=3, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='70.00', blocks=2, comment=comment, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=3, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')

        previous_hotel_availability = self.get_hotel_availability(hotel_id_2.split('-')[1], event_date)
        expected_block = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment)
        expected_block_id = expected_block['hotel_availability_id']

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
        self.assertIsNotNone(expected_block_obj)
        self.assertEqual(expected_block_obj['ap_block'], '2')

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1', headers=headers).json()['data']
        self.assertEqual(len(hotels), 3)

        # validate hotel sort order and values
        self.assertEqual(hotels[0]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[0]['available'], 7)
        self.assertEqual(hotels[0]['hard_block_count'], 6)
        self.assertEqual(hotels[0]['rate'], '70.00')

        self.assertEqual(hotels[1]['hotel_id'], hotel_id)
        self.assertEqual(hotels[1]['available'], 2)
        self.assertEqual(hotels[1]['hard_block_count'], 1)
        self.assertEqual(hotels[1]['rate'], '90.00')

        self.assertEqual(hotels[2]['hotel_id'], hotel_id_3)
        self.assertEqual(hotels[2]['available'], 4)
        self.assertEqual(hotels[2]['hard_block_count'], 0)
        self.assertEqual(hotels[2]['rate'], '100.00')

        # create passengers and proceed with booking
        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=1,
            hotel_id=hotel_id_2
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_2)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), 1)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            self.assertEqual(room_voucher['count'], 1)
            self.assertEqual(room_voucher['rate'], '70.00')
            self.assertEqual(room_voucher['hard_block'], True)
        voucher_uuid = voucher['voucher_id']
        UUID(voucher_uuid, version=4)
        expected_total_amount = str(Decimal(voucher['hotel_voucher']['room_vouchers'][0]['rate']) + Decimal(voucher['hotel_voucher']['tax']))
        self.assertEqual(voucher['hotel_voucher']['total_amount'], expected_total_amount)

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
        self.assertIsNotNone(expected_block_obj)
        self.assertEqual(expected_block_obj['ap_block'], '1')

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1', headers=headers).json()['data']
        self.assertEqual(len(hotels), 3)

        self.assertEqual(hotels[0]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[0]['available'], 6)
        self.assertEqual(hotels[0]['hard_block_count'], 5)
        self.assertEqual(hotels[0]['rate'], '70.00')

        voucher_ids = []
        room_blocks = []
        vouchers = self.get_hotel_usage_history(port_id, airline_id)
        for voucher in vouchers:
            if voucher['hotel_id'] == hotel_id_2.split('-')[1]:
                voucher_ids.append(voucher['voucher_id'])
        for voucher_id in voucher_ids:
            voucher_data = self.get_voucher_data(voucher_id)
            if str(UUID(voucher_data['voucher_uuid'], version=4)) == voucher_uuid:
                room_blocks = list(voucher_data['voucher_room_blocks'])
                break
        self.assertEqual(len(room_blocks), 1)
        self.assertEqual(room_blocks[0]['fk_block_id'], expected_block_id)
        self.assertEqual(room_blocks[0]['rate'], '70.00')
        self.assertEqual(room_blocks[0]['count'], '1')

        self.assertEqual(voucher_data['voucher_room_rate'], '70')
        self.assertEqual(voucher_data['voucher_hotel_nights'], '1')
        self.assertEqual(voucher_data['voucher_room_total'], '1')

        # create quick vouchers and use all FAT inventory
        response_json = self.create_quick_voucher(airline_id, hotel_id.split('-')[1], port_id,
                                                  number_of_rooms=2, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        response_json = self.create_quick_voucher(airline_id, hotel_id_2.split('-')[1], port_id,
                                                  number_of_rooms=6, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        response_json = self.create_quick_voucher(airline_id, hotel_id_3.split('-')[1], port_id,
                                                  number_of_rooms=4, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&provider=tvl', headers=headers)
        self.assertEqual(hotels.status_code, 200)
        self.assertEqual(len(hotels.json()['data']), 0)

    def test_multi_block_voucher_uses_correct_blocks(self):
        """
        validate multi block voucher process uses correct blocks
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        port_id = 925  # FAT
        airline_id = 294  # PurpleRain
        hotel_id = 'tvl-98843'  # Motel6 FAT
        hotel_id_2 = 'tvl-98842'  # Holiday Inn FAT
        hotel_id_3 = 'tvl-98845'  # Comfort Suites FAT
        event_date = self._get_event_date('America/Los_Angeles')
        _event_date_time = self._calculate_event_datetime('America/Los_Angeles')
        event_date_time = self._get_event_date_time('America/Los_Angeles', _event_date_time)

        comment = 'first ' + str(uuid4())
        comment2 = 'second ' + str(uuid4())
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='90.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], 0, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='100.00', blocks=2, comment=comment2, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='70.00', blocks=2, comment=comment, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=3, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')

        previous_hotel_availability = self.get_hotel_availability(hotel_id_2.split('-')[1], event_date)
        expected_block_id = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment)['hotel_availability_id']
        expected_block_id2 = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment2)['hotel_availability_id']

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        expected_block_obj2 = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
            if block['hotel_availability_id'] == expected_block_id2:
                expected_block_obj2 = dict(block)
        self.assertIsNotNone(expected_block_obj)
        self.assertEqual(expected_block_obj['ap_block'], '2')
        self.assertIsNotNone(expected_block_obj2)
        self.assertEqual(expected_block_obj2['ap_block'], '2')

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=3', headers=headers).json()['data']
        self.assertEqual(len(hotels), 2)

        # validate hotel sort order and values
        self.assertEqual(hotels[0]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[0]['available'], 6)
        self.assertEqual(hotels[0]['hard_block_count'], 5)
        self.assertEqual(hotels[0]['rate'], '80.00')

        self.assertEqual(hotels[1]['hotel_id'], hotel_id_3)
        self.assertEqual(hotels[1]['available'], 4)
        self.assertEqual(hotels[1]['hard_block_count'], 0)
        self.assertEqual(hotels[1]['rate'], '100.00')

        # create passengers and proceed with booking
        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=3,
            hotel_id=hotel_id_2
        )

        validated_block1 = False
        validated_block2 = False
        expected_total_amount = Decimal('0.00')
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_2)
        self.assertEqual(voucher['hotel_voucher']['rooms_booked'], 3)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            if room_voucher['count'] == 2:
                self.assertEqual(room_voucher['rate'], '70.00')
                self.assertEqual(room_voucher['hard_block'], True)
                expected_total_amount += Decimal(room_voucher['rate']) * room_voucher['count']
                validated_block1 = True
            else:
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['rate'], '100.00')
                self.assertEqual(room_voucher['hard_block'], True)
                expected_total_amount += Decimal(room_voucher['rate'])
                validated_block2 = True
        voucher_uuid = voucher['voucher_id']
        UUID(voucher_uuid, version=4)
        self.assertTrue(validated_block1)
        self.assertTrue(validated_block2)

        expected_total_amount = str(expected_total_amount + Decimal(voucher['hotel_voucher']['tax']))
        self.assertEqual(voucher['hotel_voucher']['total_amount'], expected_total_amount)

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        expected_block_obj2 = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
            if block['hotel_availability_id'] == expected_block_id2:
                expected_block_obj2 = dict(block)
        self.assertIsNone(expected_block_obj)
        self.assertIsNotNone(expected_block_obj2)
        self.assertEqual(expected_block_obj2['ap_block'], '1')

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1', headers=headers).json()['data']
        self.assertEqual(len(hotels), 3)

        self.assertEqual(hotels[0]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[0]['available'], 3)
        self.assertEqual(hotels[0]['hard_block_count'], 2)
        self.assertEqual(hotels[0]['rate'], '100.00')

        voucher_ids = []
        room_blocks = []
        vouchers = self.get_hotel_usage_history(port_id, airline_id)
        for voucher in vouchers:
            if voucher['hotel_id'] == hotel_id_2.split('-')[1]:
                voucher_ids.append(voucher['voucher_id'])
        for voucher_id in voucher_ids:
            voucher_data = self.get_voucher_data(voucher_id)
            if str(UUID(voucher_data['voucher_uuid'], version=4)) == voucher_uuid:
                room_blocks = list(voucher_data['voucher_room_blocks'])
                break
        self.assertEqual(len(room_blocks), 2)
        validated_block1 = False
        validated_block2 = False
        for room_block in room_blocks:
            if room_block['count'] == '2':
                self.assertEqual(room_block['fk_block_id'], expected_block_id)
                self.assertEqual(room_block['rate'], '70.00')
                validated_block1 = True
            else:
                self.assertEqual(room_block['fk_block_id'], expected_block_id2)
                self.assertEqual(room_block['count'], '1')
                self.assertEqual(room_block['rate'], '100.00')
                validated_block2 = True
        self.assertTrue(validated_block1)
        self.assertTrue(validated_block2)

        self.assertEqual(voucher_data['voucher_room_rate'], '240')
        self.assertEqual(voucher_data['voucher_hotel_nights'], '1')
        self.assertEqual(voucher_data['voucher_room_total'], '3')

        # create quick vouchers and use all FAT inventory
        response_json = self.create_quick_voucher(airline_id, hotel_id.split('-')[1], port_id,
                                                  number_of_rooms=2, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        response_json = self.create_quick_voucher(airline_id, hotel_id_2.split('-')[1], port_id,
                                                  number_of_rooms=3, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        response_json = self.create_quick_voucher(airline_id, hotel_id_3.split('-')[1], port_id,
                                                  number_of_rooms=4, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&provider=tvl', headers=headers)
        self.assertEqual(hotels.status_code, 200)
        self.assertEqual(len(hotels.json()['data']), 0)

    def test_multi_night_voucher_uses_correct_blocks(self):
        """
        validates multi night voucher uses correct blocks
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        port_id = 925  # FAT
        airline_id = 294  # PurpleRain
        hotel_id = 'tvl-98843'  # Motel6 FAT
        hotel_id_2 = 'tvl-98842'  # Holiday Inn FAT
        hotel_id_3 = 'tvl-98845'  # Comfort Suites FAT
        hotel_id_4 = 'tvl-98849'  # Park Inn FAT
        event_date = self._get_event_date('America/Los_Angeles')
        event_date2 = event_date + datetime.timedelta(days=1)
        check_in_date = event_date.strftime('%Y-%m-%d')
        check_out_date = (event_date2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        _event_date_time = self._calculate_event_datetime('America/Los_Angeles')
        event_date_time = self._get_event_date_time('America/Los_Angeles', _event_date_time)

        comment = 'first ' + str(uuid4())
        comment2 = 'second ' + str(uuid4())
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='150.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='90.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date2, ap_block_type=0, block_price='150.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date2, ap_block_type=1, block_price='110.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], 0, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='70.00', blocks=2, comment=comment, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], 0, event_date2, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date2, ap_block_type=1, block_price='110.00', blocks=2, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date2, ap_block_type=2, block_price='130.00', blocks=1, comment=comment2, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=3, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date2, ap_block_type=1, block_price='60.00', blocks=4, pay_type='0')
        self.add_hotel_availability(hotel_id_4.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='150.00', blocks=1, pay_type='0')

        previous_hotel_availability = self.get_hotel_availability(hotel_id_2.split('-')[1], event_date)
        expected_block_id = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment)['hotel_availability_id']
        previous_hotel_availability = self.get_hotel_availability(hotel_id_2.split('-')[1], event_date2)
        expected_block_id2 = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment2)['hotel_availability_id']
        self.assertGreater(int(expected_block_id), 0)
        self.assertGreater(int(expected_block_id2), 0)

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        expected_block_obj2 = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
            if block['hotel_availability_id'] == expected_block_id2:
                expected_block_obj2 = dict(block)
        self.assertIsNotNone(expected_block_obj)
        self.assertEqual(expected_block_obj['ap_block'], '2')
        self.assertIsNone(expected_block_obj2)  # TODO: need service to grab next day inventory blocks

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1', headers=headers).json()['data']
        self.assertEqual(len(hotels), 4)

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&number_of_nights=2', headers=headers).json()['data']
        self.assertEqual(len(hotels), 3)

        # validate hotel sort order and values
        self.assertEqual(hotels[0]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[0]['available'], 4)
        self.assertEqual(hotels[0]['hard_block_count'], 4)
        self.assertEqual(hotels[0]['rate'], '100.00')
        self.assertEqual(hotels[0]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[0]['proposed_check_out_date'], check_out_date)

        self.assertEqual(hotels[1]['hotel_id'], hotel_id_3)
        self.assertEqual(hotels[1]['available'], 4)
        self.assertEqual(hotels[1]['hard_block_count'], 2)
        self.assertEqual(hotels[1]['rate'], '80.00')
        self.assertEqual(hotels[1]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[1]['proposed_check_out_date'], check_out_date)

        self.assertEqual(hotels[2]['hotel_id'], hotel_id)
        self.assertEqual(hotels[2]['available'], 2)
        self.assertEqual(hotels[2]['hard_block_count'], 1)
        self.assertEqual(hotels[2]['rate'], '100.00')
        self.assertEqual(hotels[2]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[2]['proposed_check_out_date'], check_out_date)

        # create passengers and proceed with booking
        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=1,
            hotel_id=hotel_id_2,
            number_of_nights=2
        )

        validated_block1 = False
        validated_block2 = False
        expected_total_amount = Decimal('0.00')
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_2)
        self.assertEqual(voucher['hotel_voucher']['rooms_booked'], 1)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), 2)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            if room_voucher['rate'] == '70.00':
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['hard_block'], True)
                expected_total_amount += Decimal(room_voucher['rate'])
                validated_block1 = True
            else:
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['rate'], '130.00')
                self.assertEqual(room_voucher['hard_block'], True)
                expected_total_amount += Decimal(room_voucher['rate'])
                validated_block2 = True
        voucher_uuid = voucher['voucher_id']
        UUID(voucher_uuid, version=4)
        self.assertTrue(validated_block1)
        self.assertTrue(validated_block2)

        expected_total_amount = str(expected_total_amount + Decimal(voucher['hotel_voucher']['tax']))
        self.assertEqual(voucher['hotel_voucher']['total_amount'], expected_total_amount)

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        expected_block_obj2 = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
            if block['hotel_availability_id'] == expected_block_id2:
                expected_block_obj2 = dict(block)
        self.assertIsNotNone(expected_block_obj)
        self.assertIsNone(expected_block_obj2)
        self.assertEqual(expected_block_obj['ap_block'], '1')

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&number_of_nights=2', headers=headers).json()['data']
        self.assertEqual(len(hotels), 3)

        self.assertEqual(hotels[0]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[0]['available'], 3)
        self.assertEqual(hotels[0]['hard_block_count'], 3)
        self.assertEqual(hotels[0]['rate'], '90.00')
        self.assertEqual(hotels[0]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[0]['proposed_check_out_date'], check_out_date)

        voucher_ids = []
        room_blocks = []
        vouchers = self.get_hotel_usage_history(port_id, airline_id)
        for voucher in vouchers:
            if voucher['hotel_id'] == hotel_id_2.split('-')[1]:
                voucher_ids.append(voucher['voucher_id'])
        for voucher_id in voucher_ids:
            voucher_data = self.get_voucher_data(voucher_id)
            if str(UUID(voucher_data['voucher_uuid'], version=4)) == voucher_uuid:
                room_blocks = list(voucher_data['voucher_room_blocks'])
                break
        self.assertEqual(len(room_blocks), 2)
        validated_block1 = False
        validated_block2 = False
        for room_block in room_blocks:
            if room_block['rate'] == '70.00':
                self.assertEqual(room_block['fk_block_id'], expected_block_id)
                self.assertEqual(room_block['count'], '1')
                validated_block1 = True
            else:
                self.assertEqual(room_block['fk_block_id'], expected_block_id2)
                self.assertEqual(room_block['count'], '1')
                self.assertEqual(room_block['rate'], '130.00')
                validated_block2 = True
        self.assertTrue(validated_block1)
        self.assertTrue(validated_block2)

        self.assertEqual(voucher_data['voucher_room_rate'], '200')
        self.assertEqual(voucher_data['voucher_hotel_nights'], '2')
        self.assertEqual(voucher_data['voucher_room_total'], '1')

        # create quick vouchers and use all FAT inventory
        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=2,
            hotel_id=hotel_id,
            number_of_nights=2
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        response_json = self.create_quick_voucher(airline_id, hotel_id_2.split('-')[1], port_id,
                                                  number_of_rooms=2, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=3,
            hotel_id=hotel_id_2,
            number_of_nights=2
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=4,
            hotel_id=hotel_id_3,
            number_of_nights=2
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        response_json = self.create_quick_voucher(airline_id, hotel_id_4.split('-')[1], port_id,
                                                  number_of_rooms=1, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&provider=tvl', headers=headers)
        self.assertEqual(hotels.status_code, 200)
        self.assertEqual(len(hotels.json()['data']), 0)

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&provider=tvl&number_of_nights=2', headers=headers)
        self.assertEqual(hotels.status_code, 200)
        self.assertEqual(len(hotels.json()['data']), 0)

    def test_multi_night_multi_room_voucher_uses_correct_blocks(self):
        """
        validates multi night multi room voucher uses correct blocks
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'
        passenger_url = self._api_host + '/api/v1/passenger'

        port_id = 925  # FAT
        airline_id = 294  # PurpleRain
        hotel_id = 'tvl-98843'  # Motel6 FAT
        hotel_id_2 = 'tvl-98842'  # Holiday Inn FAT
        hotel_id_3 = 'tvl-98845'  # Comfort Suites FAT
        hotel_id_4 = 'tvl-98849'  # Park Inn FAT
        event_date = self._get_event_date('America/Los_Angeles')
        event_date2 = event_date + datetime.timedelta(days=1)
        check_in_date = event_date.strftime('%Y-%m-%d')
        check_out_date = (event_date2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        _event_date_time = self._calculate_event_datetime('America/Los_Angeles')
        event_date_time = self._get_event_date_time('America/Los_Angeles', _event_date_time)

        comment = 'first ' + str(uuid4())
        comment2 = 'second ' + str(uuid4())
        comment3 = 'three ' + str(uuid4())
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='150.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='90.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date2, ap_block_type=0, block_price='150.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id.split('-')[1], airline_id, event_date2, ap_block_type=1, block_price='110.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], 0, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=1, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date, ap_block_type=2, block_price='70.00', blocks=2, comment=comment, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], 0, event_date2, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date2, ap_block_type=1, block_price='110.00', blocks=2, comment=comment3, pay_type='0')
        self.add_hotel_availability(hotel_id_2.split('-')[1], airline_id, event_date2, ap_block_type=2, block_price='130.00', blocks=1, comment=comment2, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=3, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='100.00', blocks=1, pay_type='0')
        self.add_hotel_availability(hotel_id_3.split('-')[1], airline_id, event_date2, ap_block_type=1, block_price='60.00', blocks=4, pay_type='0')
        self.add_hotel_availability(hotel_id_4.split('-')[1], airline_id, event_date, ap_block_type=0, block_price='150.00', blocks=2, pay_type='0')

        previous_hotel_availability = self.get_hotel_availability(hotel_id_2.split('-')[1], event_date)
        expected_block_id = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment)['hotel_availability_id']
        previous_hotel_availability = self.get_hotel_availability(hotel_id_2.split('-')[1], event_date2)
        expected_block_id2 = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment2)['hotel_availability_id']
        expected_block_id3 = self.find_hotel_availability_block_by_comment(previous_hotel_availability, comment3)['hotel_availability_id']
        self.assertGreater(int(expected_block_id), 0)
        self.assertGreater(int(expected_block_id2), 0)
        self.assertGreater(int(expected_block_id3), 0)

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        expected_block_obj2 = None
        expected_block_obj3 = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
            if block['hotel_availability_id'] == expected_block_id2:
                expected_block_obj2 = dict(block)
            if block['hotel_availability_id'] == expected_block_id3:
                expected_block_obj3 = dict(block)
        self.assertIsNotNone(expected_block_obj)
        self.assertEqual(expected_block_obj['ap_block'], '2')
        self.assertIsNone(expected_block_obj2)  # TODO: need service to grab next day inventory blocks
        self.assertIsNone(expected_block_obj3)  # TODO: need service to grab next day inventory blocks

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=2', headers=headers).json()['data']
        self.assertEqual(len(hotels), 4)

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=2&number_of_nights=2', headers=headers).json()['data']
        self.assertEqual(len(hotels), 3)

        # validate hotel sort order and values
        self.assertEqual(hotels[0]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[0]['available'], 4)
        self.assertEqual(hotels[0]['hard_block_count'], 4)
        self.assertEqual(hotels[0]['rate'], '95.00')
        self.assertEqual(hotels[0]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[0]['proposed_check_out_date'], check_out_date)

        self.assertEqual(hotels[1]['hotel_id'], hotel_id_3)
        self.assertEqual(hotels[1]['available'], 4)
        self.assertEqual(hotels[1]['hard_block_count'], 2)
        self.assertEqual(hotels[1]['rate'], '80.00')
        self.assertEqual(hotels[1]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[1]['proposed_check_out_date'], check_out_date)

        self.assertEqual(hotels[2]['hotel_id'], hotel_id)
        self.assertEqual(hotels[2]['available'], 2)
        self.assertEqual(hotels[2]['hard_block_count'], 1)
        self.assertEqual(hotels[2]['rate'], '125.00')
        self.assertEqual(hotels[2]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[2]['proposed_check_out_date'], check_out_date)

        # create passengers and proceed with booking
        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=2,
            hotel_id=hotel_id_2,
            number_of_nights=2
        )

        passenger = passengers[0]

        validated_block1 = False
        validated_block2 = False
        validated_block3 = False
        expected_total_amount = Decimal('0.00')
        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)
        voucher = hotel_booking_resp.json()['data']
        self.assertEqual(voucher['hotel_voucher']['hotel_id'], hotel_id_2)
        self.assertEqual(len(voucher['hotel_voucher']['room_vouchers']), 3)
        for room_voucher in voucher['hotel_voucher']['room_vouchers']:
            if room_voucher['rate'] == '70.00':
                self.assertEqual(room_voucher['count'], 2)
                self.assertEqual(room_voucher['hard_block'], True)
                self.assertEqual(room_voucher['block_type'], 'contract_block')
                expected_total_amount += Decimal(room_voucher['rate']) * room_voucher['count']
                validated_block1 = True
            elif room_voucher['rate'] == '110.00':
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['hard_block'], True)
                self.assertEqual(room_voucher['block_type'], 'hard_block')
                expected_total_amount += Decimal(room_voucher['rate']) * room_voucher['count']
                validated_block3 = True
            else:
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['rate'], '130.00')
                self.assertEqual(room_voucher['hard_block'], True)
                self.assertEqual(room_voucher['block_type'], 'contract_block')
                expected_total_amount += Decimal(room_voucher['rate']) * room_voucher['count']
                validated_block2 = True
        voucher_uuid = voucher['voucher_id']
        UUID(voucher_uuid, version=4)
        self.assertTrue(validated_block1)
        self.assertTrue(validated_block2)
        self.assertTrue(validated_block3)

        expected_total_amount = str(expected_total_amount + Decimal(voucher['hotel_voucher']['tax']))
        self.assertEqual(voucher['hotel_voucher']['total_amount'], expected_total_amount)

        hotel_voucher = voucher['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)

        # validate correct block was used and inventory has been decremented
        blocks = []
        expected_block_obj = None
        expected_block_obj2 = None
        expected_block_obj3 = None
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()
        for hotel in blocks_by_hotel:
            if hotel['id'] == hotel_id_2.split('-')[1]:
                blocks = list(hotel['hotel_price_list'])
        for block in blocks:
            if block['hotel_availability_id'] == expected_block_id:
                expected_block_obj = dict(block)
            if block['hotel_availability_id'] == expected_block_id2:
                expected_block_obj2 = dict(block)
            if block['hotel_availability_id'] == expected_block_id3:
                expected_block_obj3 = dict(block)
        self.assertIsNone(expected_block_obj)  # should be null all block inventory is consumed
        self.assertIsNone(expected_block_obj2)  # TODO: need service to grab next day inventory blocks
        self.assertIsNone(expected_block_obj3)  # TODO: need service to grab next day inventory blocks

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=2&number_of_nights=2', headers=headers).json()['data']
        self.assertEqual(len(hotels), 3)

        self.assertEqual(hotels[0]['hotel_id'], hotel_id_3)
        self.assertEqual(hotels[0]['available'], 4)
        self.assertEqual(hotels[0]['hard_block_count'], 2)
        self.assertEqual(hotels[0]['rate'], '80.00')
        self.assertEqual(hotels[0]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[0]['proposed_check_out_date'], check_out_date)

        self.assertEqual(hotels[1]['hotel_id'], hotel_id_2)
        self.assertEqual(hotels[1]['available'], 2)
        self.assertEqual(hotels[1]['hard_block_count'], 2)
        self.assertEqual(hotels[1]['rate'], '102.50')
        self.assertEqual(hotels[1]['proposed_check_in_date'], check_in_date)
        self.assertEqual(hotels[1]['proposed_check_out_date'], check_out_date)

        voucher_ids = []
        room_blocks = []
        vouchers = self.get_hotel_usage_history(port_id, airline_id)
        for voucher in vouchers:
            if voucher['hotel_id'] == hotel_id_2.split('-')[1]:
                voucher_ids.append(voucher['voucher_id'])
        for voucher_id in voucher_ids:
            voucher_data = self.get_voucher_data(voucher_id)
            if str(UUID(voucher_data['voucher_uuid'], version=4)) == voucher_uuid:
                room_blocks = list(voucher_data['voucher_room_blocks'])
                break
        self.assertEqual(len(room_blocks), 3)
        validated_block1 = False
        validated_block2 = False
        validated_block3 = False
        for room_block in room_blocks:
            if room_block['rate'] == '70.00':
                self.assertEqual(room_block['fk_block_id'], expected_block_id)
                self.assertEqual(room_block['count'], '2')
                validated_block1 = True
            elif room_block['rate'] == '110.00':
                self.assertEqual(room_block['fk_block_id'], expected_block_id3)
                self.assertEqual(room_block['count'], '1')
                validated_block3 = True
            else:
                self.assertEqual(room_block['fk_block_id'], expected_block_id2)
                self.assertEqual(room_block['count'], '1')
                self.assertEqual(room_block['rate'], '130.00')
                validated_block2 = True
        self.assertTrue(validated_block1)
        self.assertTrue(validated_block2)
        self.assertTrue(validated_block3)

        self.assertEqual(voucher_data['voucher_room_rate'], '380')
        self.assertEqual(voucher_data['voucher_hotel_nights'], '2')
        self.assertEqual(voucher_data['voucher_room_total'], '2')

        # create quick vouchers and use all FAT inventory
        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=2,
            hotel_id=hotel_id,
            number_of_nights=2
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        response_json = self.create_quick_voucher(airline_id, hotel_id_2.split('-')[1], port_id,
                                                  number_of_rooms=2, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=2,
            hotel_id=hotel_id_2,
            number_of_nights=2
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        passengers = self._create_2_passengers(customer, port_accommodation='FAT')

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            room_count=4,
            hotel_id=hotel_id_3,
            number_of_nights=2
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 200)

        response_json = self.create_quick_voucher(airline_id, hotel_id_4.split('-')[1], port_id,
                                                  number_of_rooms=2, passenger_names=[], number_of_nights=1,
                                                  flight_number='', voucher_date=event_date_time)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&provider=tvl', headers=headers)
        self.assertEqual(hotels.status_code, 200)
        self.assertEqual(len(hotels.json()['data']), 0)

        hotels = requests.get(url=hotels_url + '?port=FAT&room_count=1&provider=tvl&number_of_nights=2', headers=headers)
        self.assertEqual(hotels.status_code, 200)
        self.assertEqual(len(hotels.json()['data']), 0)

        validated_block1 = False
        validated_block2 = False
        validated_block3 = False
        full_state = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers).json()['data']
        room_vouchers = full_state['voucher']['hotel_voucher']['room_vouchers']
        for room_voucher in room_vouchers:
            if room_voucher['rate'] == '70.00':
                self.assertEqual(room_voucher['count'], 2)
                self.assertEqual(room_voucher['hard_block'], True)
                self.assertEqual(room_voucher['block_type'], 'contract_block')
                validated_block1 = True
            elif room_voucher['rate'] == '110.00':
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['hard_block'], True)
                self.assertEqual(room_voucher['block_type'], 'hard_block')
                validated_block3 = True
            else:
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['rate'], '130.00')
                self.assertEqual(room_voucher['hard_block'], True)
                self.assertEqual(room_voucher['block_type'], 'contract_block')
                validated_block2 = True
        self.assertTrue(validated_block1)
        self.assertTrue(validated_block2)
        self.assertTrue(validated_block3)

        hotel_voucher = full_state['voucher']['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)
