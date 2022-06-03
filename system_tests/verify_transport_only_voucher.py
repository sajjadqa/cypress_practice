from datetime import date, datetime
from stormx_verification_framework import StormxSystemVerification


class TestTransportOnlyVoucher(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    transport = [103224, 103225]
    airline_id = 294 
    tz = 'America/Los_Angeles'
    airport_id = 16
    passenger_names = ['Johnny Appleseed', 'Elizabeth Chapman']
    flight_number = 'PR-4321'
    voucher_id=None
    @classmethod
    def setUpClass(cls):
        super(TestTransportOnlyVoucher, cls).setUpClass()
    
    def create_transport_only_voucher(self, mode=''):
        now = self._get_timezone_now(self.tz)
        voucher_creation_date_time = self._get_event_date_time(self.tz, now)
        response_json = self.save_transport_only_voucher('', self.airline_id, self.transport, self.airport_id, voucher_date=voucher_creation_date_time,
                             passenger_names=self.passenger_names,
                             flight_number=self.flight_number, mode=mode,
                             verify_response_success=True)
        self.assertEqual(response_json['success'], '1')
        self.voucher_id = response_json['voucher']['voucher_id']

    def test_transport_only_voucher_save(self):
        self.create_transport_only_voucher()
        self.assertIsNotNone(self.voucher_id)
    
    def test_transport_only_voucher_finalize(self):
        now = self._get_timezone_now(self.tz)
        voucher_creation_date_time = self._get_event_date_time(self.tz, now)
        response_json = self.save_transport_only_voucher(self.voucher_id, self.airline_id, self.transport, self.airport_id, voucher_date=voucher_creation_date_time,
                             passenger_names=self.passenger_names,
                             flight_number=self.flight_number, mode='finalised',
                             verify_response_success=True)
        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])
        self.assertEqual(response_json['voucher']['voucher_status'], '50')
    
    def test_transport_only_voucher_save_with_same_transport(self):
        self.transport = [103224, 103225]
        self.create_transport_only_voucher()
        self.assertIsNotNone(self.voucher_id)