import requests

from uuid import UUID

from stormx_verification_framework import StormxSystemVerification


class TestApiHotelBookingDirectBilling(StormxSystemVerification):
    """
    Verify that direct billing bookings work correctly.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBookingDirectBilling, cls).setUpClass()

    def test_direct_billing_hotel_booking(self):
        """
        verify that a direct billing booking can complete successfully.
        """
        customer = 'Purple Rain Airlines'
        airline_id = 294
        port = 'BSB'  # International Airport of Brasilia. set up with Direct Billing hotels.

        airline_client = self.get_airline_api_client(customer)

        # import passengers ----
        passengers = airline_client.import_passengers(self._generate_n_passenger_payload(2, port_accommodation=port))

        # verify hotel image in hotel listings ----
        hotels = airline_client.get_hotels(port=port, room_count=1, provider='tvl')
        self.assertGreater(len(hotels), 0, msg='no hotel inventory in port ' + repr(port))
        picked_hotel = hotels[0]
        hotel_id_string = picked_hotel['hotel_id']
        hotel_id_int = hotel_id_string.split('-')[1]

        # book hotel ----
        tvl_voucher = airline_client.book_hotel(
            context_ids=[p['context_id'] for p in passengers],
            hotel_id=hotel_id_string,
            room_count=1
        )
        hotel_voucher = tvl_voucher['hotel_voucher']
        check_in_key = hotel_voucher['hotel_key']

        # passenger full state ----
        full_state = airline_client.get_passenger_full_state(passengers[0]['context_id'])

        # passenger's voucher ----
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']
        response = requests.get(passenger_offer_url, headers=self._generate_passenger_headers())
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)

        # unlock ----
        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        voucher_hotel_details_url = self._api_host + '/api/v1/tvl/hotel_voucher_details'
        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id='1')  # support
        unlock_payload = dict(
            hotel_id=hotel_id_int,
            check_in_key=check_in_key
        )
        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=unlock_payload)
        self.assertEqual(resp.status_code, 200)
        cc_data = resp.json()['data']

        # validate unlocked voucher details
        fields = ['nights', 'expiration', 'flight', 'amount', 'rooms', 'tax', 'card_number', 'cvc2', 'port',
                  'passengers', 'currency_code', 'check_in_date', 'rates', 'fees', 'airline_name']

        for field in fields:
            self.assertIn(field, cc_data)

        self.assertIsNone(cc_data['card_number'])
        self.assertIsNone(cc_data['cvc2'])
        self.assertIsNone(cc_data['expiration'])
        self.assertGreaterEqual(len(cc_data['rates']), 1)

        for rate in cc_data['rates']:
            self.assertIn('rate', rate)
            self.assertIn('count', rate)

        self.assertIn('-', cc_data['voucher_id'])
        UUID(cc_data['voucher_id'], version=4)
        voucher_uuid = cc_data['voucher_id']

        self.assertEqual(cc_data['hotel_payment_type'], 'direct_bill')

        detail_payload = dict(
            voucher_uuid=voucher_uuid
        )
        resp = requests.post(url=voucher_hotel_details_url, headers=stormx_user_headers_good, json=detail_payload)

        cc_data_2 = resp.json()['data']

        self.assertEqual(cc_data_2, cc_data)
