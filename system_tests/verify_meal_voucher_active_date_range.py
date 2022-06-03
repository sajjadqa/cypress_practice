import datetime
from uuid import UUID

import pytz
import requests

from StormxApp.constants import StormxConstants
from stormx_verification_framework import (
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output,
)


class TestMealVoucherActiveDateRange(StormxSystemVerification):
    """
    Verify that meal voucher credit cards' active date ranges are correct on vouchers.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestMealVoucherActiveDateRange, cls).setUpClass()

    def _test_wex_active_date_range(self, customer, port, meal_number_of_days):
        """
        system_test used by test_wex_active_date_range
        """
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            port_accommodation=port,
            meals=[{'meal_amount': 12.00, 'currency_code': 'USD', 'number_of_days': meal_number_of_days}]
        ))

        import_url = self._api_host + '/api/v1/passenger'
        import_resp = requests.post(url=import_url, headers=headers, json=passenger_payload)
        self.assertGreaterEqual(import_resp.status_code, 201)
        passenger = import_resp.json()['data'][0]

        hotels = self._get_passenger_hotel_offerings(passenger, room_count=1)
        self.assertGreaterEqual(len(hotels), 1)

        picked_hotel = hotels[0]
        booking_response_data = self._airline_book_hotel(customer, picked_hotel, [passenger['context_id']], room_count=1)
        UUID(booking_response_data['voucher_id'], version=4)

        voucher_url = self._api_host + '/api/v1/voucher/' + str(booking_response_data['voucher_id'])
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        voucher_resp_json = voucher_resp.json()
        passenger = voucher_resp_json['data']['passengers'][0]
        time_zone = passenger['meal_vouchers'][0]['time_zone']

        port_tz = pytz.timezone(time_zone)
        port_time_now = datetime.datetime.now(port_tz)

        wex_tz = pytz.timezone(StormxConstants.WEX_TIMEZONE)
        wex_time_now = datetime.datetime.now(wex_tz)
        offset = abs((wex_time_now.utcoffset() - port_time_now.utcoffset())).seconds / 3600

        active_from = datetime.datetime.strptime(passenger['meal_vouchers'][0]['active_from'], '%Y-%m-%d %H:%M')
        _active_to = datetime.datetime.strptime(passenger['meal_vouchers'][0]['active_to'], '%Y-%m-%d %H:%M')
        active_to = _active_to.replace(tzinfo=port_tz)

        self.assertEqual(active_from.strftime('%Y-%m-%d'), port_time_now.strftime('%Y-%m-%d'))
        self.assertIn(active_to.hour, [23 - offset, 23 - offset - 1])
        self.assertEqual(active_to.minute, 59)
        self.assertEqual((active_to - port_time_now).days, meal_number_of_days)

    def test_wex_active_date_range(self):
        """
        system test that tests booking a single room for all supported ports in the sandbox env.
        this test ensures that the active_date_range sent up to wex is working correctly for 1 and 2 days.
        NOTE: I would like to add additional days in the meal_number_of_days array but the length of the system_test
        increases greatly when doing so.
        """
        customer = 'Delta Air Lines'
        meal_number_of_days = [1, 2]
        active_ports = ['PHX', 'DFW', 'LAX', 'ATL', 'SEA', 'MSP', 'JFK', 'ORD', 'DCA']
        for port in active_ports:
            for meal in meal_number_of_days:
                self._test_wex_active_date_range(customer, port, meal)

    def _test_wex_active_date_range_meal_only(self, customer, port, meal_number_of_days):
        """
        system_test used by test_wex_active_date_range
        """
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            port_accommodation=port,
            hotel_accommodation=False,
            meals=[{'meal_amount': 12.00, 'currency_code': 'USD', 'number_of_days': meal_number_of_days}]
        ))

        import_url = self._api_host + '/api/v1/passenger'
        import_resp = requests.post(url=import_url, headers=headers, json=passenger_payload)
        self.assertGreaterEqual(import_resp.status_code, 201)
        passenger = import_resp.json()['data'][0]

        voucher_url = self._api_host + '/api/v1/voucher/' + str(passenger['voucher_id'])
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        voucher_resp_json = voucher_resp.json()
        passenger = voucher_resp_json['data']['passengers'][0]
        time_zone = passenger['meal_vouchers'][0]['time_zone']

        port_tz = pytz.timezone(time_zone)
        port_time_now = datetime.datetime.now(port_tz)

        wex_tz = pytz.timezone(StormxConstants.WEX_TIMEZONE)
        wex_time_now = datetime.datetime.now(wex_tz)
        offset = abs((wex_time_now.utcoffset() - port_time_now.utcoffset())).seconds / 3600

        active_from = datetime.datetime.strptime(passenger['meal_vouchers'][0]['active_from'], '%Y-%m-%d %H:%M')
        _active_to = datetime.datetime.strptime(passenger['meal_vouchers'][0]['active_to'], '%Y-%m-%d %H:%M')
        active_to = _active_to.replace(tzinfo=port_tz)

        self.assertEqual(active_from.strftime('%Y-%m-%d'), port_time_now.strftime('%Y-%m-%d'))
        self.assertIn(active_to.hour, [23 - offset, 23 - offset - 1])
        self.assertEqual(active_to.minute, 59)
        self.assertEqual((active_to - port_time_now).days, meal_number_of_days)

    def test_wex_active_date_range_meal_only(self):
        """
        system test that tests meal only vouchers for some supported ports in the sandbox env.
        this test ensures that the active_date_range sent up to wex is working correctly for 1, 2, and 3 days.
        """
        customer = 'Purple Rain Airlines'
        meal_number_of_days = [1, 2, 3]
        active_ports = ['LAX', 'MSP', 'JFK']
        for port in active_ports:
            for meal in meal_number_of_days:
                self._test_wex_active_date_range_meal_only(customer, port, meal)
