from datetime import date, datetime, timedelta

import faker
import pytz
from stormx_verification_framework import StormxSystemVerification
from StormxApp.constants import StormxConstants


class TestHotelContracts(StormxSystemVerification):
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
        super(TestHotelContracts, cls).setUpClass()

        tz = pytz.timezone('America/Chicago')  # PHP box timezone
        cls.today = datetime.now(tz)
        cls.advance_block_date = cls.today + timedelta(
            days=StormxConstants.MAX_NUMBER_OF_NIGHTS)

    def get_contract_response_for_ports(self, port_id, type):
        fake = faker.Faker()
        date = self.advance_block_date
        contract_response = self.create_hotel_block(
            self.hotel, self.status, port_id, 1, self.airline,
            self.rate, fake.date_between(start_date="-20d", end_date=date),
            fake.date_between(start_date=date,
                              end_date="+20d"),
            self.room_count, self.room_count,
            self.room_count, self.room_count,
            self.room_count, self.room_count, self.room_count, 1, type
        )
        self.assertEqual(contract_response.status_code, 200)
        contract_json = contract_response.json()
        return contract_json

    def test_contracted_block_with_out_port(self):
        contract_json = self.get_contract_response_for_ports(0, self.hardblock_type)
        self.assertEqual(contract_json['success'], '')
        self.assertEqual(contract_json['msg'], 'Port must be selected.')

    def test_contracted_block_with_port(self):
        contract_json = self.get_contract_response_for_ports(self.port_serviced, self.hardblock_type)
        self.assertEqual(contract_json['success'], '1')

    def test_soft_blocked_with_out_port(self):
        contract_json = self.get_contract_response_for_ports(0, self.softblock_type)
        self.assertEqual(contract_json['success'], '1')

    def test_soft_block_with_port(self):
        contract_json = self.get_contract_response_for_ports(self.port_serviced, self.softblock_type)
        self.assertEqual(contract_json['success'], '1')
