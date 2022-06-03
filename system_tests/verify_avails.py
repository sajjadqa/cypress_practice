from datetime import date, datetime, timedelta

import faker
import pytz
from stormx_verification_framework import StormxSystemVerification
from StormxApp.constants import StormxConstants


class TestAvailability(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    airline = 71
    hotel = 93993
    port_serviced = 666
    port_not_serviced = 1

    today = ''
    advance_block_date = ''
    rate = 100
    room_count = 50
    status = 1
    soft_block = 0
    hard_block = 1
    contracted_block = 2

    room_type = 1
    pay_type = 0
    hardblock_type = 'hardblock'
    softblock_type = 'softblock'

    @classmethod
    def setUpClass(cls):
        super(TestAvailability, cls).setUpClass()

        tz = pytz.timezone('America/Chicago')  # PHP box timezone
        cls.today = datetime.now(tz)
        cls.advance_block_date = cls.today + timedelta(
            days=StormxConstants.MAX_NUMBER_OF_NIGHTS)

    def get_block_avail_respose_json(self, auto_consume=0, new_room_count=0, block_type=0, type='hardblock'):
        fake = faker.Faker()
        date = self.advance_block_date
        contract_response = self.create_hotel_block(
            self.hotel, self.status, self.port_serviced, 1, self.airline,
            self.rate, fake.date_between(start_date="-20d", end_date=date),
            fake.date_between(start_date=date,
                              end_date="+20d"),
            self.room_count, self.room_count,
            self.room_count, self.room_count,
            self.room_count, self.room_count, self.room_count, auto_consume, type
        )
        self.assertEqual(contract_response.status_code, 200)
        contract_json = contract_response.json()
        contract_id = contract_json['rate']['_id']
        availability_date = self._get_event_date('America/Chicago')

        avails_response = self.add_hotel_availability(self.hotel, self.airline,
                                                      availability_date, self.room_count, self.rate, block_type, '', '', self.room_type, self.pay_type, True, contract_id if block_type == 2 else 0, contract_id if block_type == 0 else 0)
        availability_id = avails_response['info']['inserted_id']
        avails_response = self.update_hotel_availability(
            self.hotel, availability_id, self.airline, availability_date, new_room_count, self.rate, block_type)
        avails_response_json = avails_response.json()
        return avails_response_json

    def test_auto_consume_edit(self):
        avails_response_json = self.get_block_avail_respose_json(1, 1, self.contracted_block, self.hardblock_type)
        self.assertEqual(avails_response_json['success'], '0')
        self.assertEqual(avails_response_json['msg'],
                         "This block can not be edited, it was created from auto-consume contract.")

    def test_increase_from_contracted(self):
        avails_response_json = self.get_block_avail_respose_json(
            0, self.room_count+50, self.contracted_block, self.hardblock_type)
        self.assertEqual(avails_response_json['success'], '0')
        self.assertEqual(avails_response_json['msg'],
                         "Can't exceed original Contract amount")

    def test_avails_zero_out_contracted(self):
        avails_response_json = self.get_block_avail_respose_json(0, 0, self.contracted_block, self.hardblock_type)
        self.assertEqual(avails_response_json['success'], '1')

    def test_soft_block_with_contract_editing(self):
        avails_response_json = self.get_block_avail_respose_json(0, 10, self.soft_block, self.softblock_type)
        self.assertEqual(avails_response_json['success'], '1')

    def get_avail_edit_response_without_contract(self, block_type):
        availability_date = self._get_event_date('America/Chicago')
        avails_response = self.add_hotel_availability(self.hotel, self.airline,
                                                      availability_date, self.room_count, self.rate, block_type, '', '', self.room_type, self.pay_type, True)
        availability_id = avails_response['info']['inserted_id']
        avails_response = self.update_hotel_availability(
            self.hotel, availability_id, self.airline, availability_date, self.room_count+1, self.rate, block_type)
        avails_response_json = avails_response.json()
        return avails_response_json

    def test_soft_block_without_contract_editing(self):
        avails_response_json = self.get_avail_edit_response_without_contract(self.soft_block)
        self.assertEqual(avails_response_json['success'], '1')

    def test_hard_block_without_contract_editing(self):
        avails_response_json = self.get_avail_edit_response_without_contract(self.hard_block)
        self.assertEqual(avails_response_json['success'], '1')
