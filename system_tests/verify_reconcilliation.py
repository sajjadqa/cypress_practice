
import json
from decimal import Decimal

import requests


from stormx_verification_framework import StormxSystemVerification, display_response


class TestReconcilliation(StormxSystemVerification):
    """
    Verify StormX reconciliation functionality.
    """

    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestReconcilliation, cls).setUpClass()

    def test_charge_for_hotel_demo(self):
        customer = 'Purple Rain Airlines'
        airline_id = 294  # Purple Rain
        hotel_id = 95378  # Hilton - Phoenix Airport
        hotel_user_id = 10060  # active user at Hilton - Phoenix Airport
        merchant_info = dict(
            merchant_acceptor_id='483200924999',
            merchant_description='HILTON PHOENIX AIRPORT',
            merchant_city='PHOENIX',
            merchant_state='AZ',
            merchant_zip='85034',
            merchant_country_code='USA',
            sic_mcc_code='7011'
        )
        room_count = 1

        availability_date = self._get_event_date('America/Phoenix')

        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=25, block_price='100.00', ap_block_type=1,
                                    room_type=1, pay_type='0')

        passengers = self._create_2_passengers(customer=customer, port_accommodation='PHX')
        hotel_url = self._api_host + '/api/v1/hotels'
        booking_payload = dict(
            context_ids=[p['context_id'] for p in passengers],
            hotel_id='tvl-' + str(hotel_id),
            room_count=room_count,
            block_type='soft_block',
            hotel_rate=100
        )
        airline_headers = self._generate_airline_headers(customer)
        booking_response = requests.post(hotel_url, headers=airline_headers, json=booking_payload)
        check_in_key = booking_response.json()['data']['hotel_voucher']['hotel_key']


        stormx_user_headers_good = self._generate_tvl_stormx_user_headers(user_id=str(hotel_user_id))
        unlock_payload = dict(
            hotel_id=hotel_id,
            check_in_key=check_in_key
        )
        voucher_hotel_unlock_url = self._api_host + '/api/v1/tvl/hotel_voucher_unlock'
        resp = requests.post(url=voucher_hotel_unlock_url, headers=stormx_user_headers_good, json=unlock_payload)
        self.assertEqual(resp.status_code, 200)
        cc_json = resp.json()
        self.assertEqual(cc_json['meta']['error_code'], '')
        card_number = cc_json['data']['card_number']
        currency_code = cc_json['data']['currency_code']
        voucher_total_amount = Decimal(cc_json['data']['amount'])

        amount = voucher_total_amount
        self.charge_single_use_card(card_number, currency_code, amount, **merchant_info)
        self.charge_single_use_card(card_number, currency_code, Decimal('11.22'), **merchant_info)
        self.charge_single_use_card(card_number, currency_code, Decimal('-10.00'), **merchant_info)

    def test_charge_for_meal_demo(self):
        customer = 'Purple Rain Airlines'

        merchant_info = dict(
            merchant_acceptor_id='313756560881',
            merchant_description='PANDA EXPRESS #2301',
            merchant_city='PHOENIX',
            merchant_state='AZ',
            merchant_zip='85034',
            merchant_country_code='USA',
            sic_mcc_code='5814'
        )

        passengers = self._create_2_passengers(
            customer=customer, port_accommodation='PHX', hotel_accommodation=False,
            meals=[
                {'meal_amount': '12.00', 'currency_code': 'USD', 'number_of_days': 1},
            ]
        )
        # visit offer link and gather meal cards.
        resp = requests.get(url=passengers[0]['offer_url'])
        embedded_json = self._get_landing_page_embedded_json(resp)
        meal_cards = []
        for passenger in embedded_json['confirmation']['passengers']:
            for meal in passenger.get('meal_vouchers', []):
                meal_cards.append(meal)

        card = meal_cards[0]
        self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('10.00'), **merchant_info)

        card = meal_cards[1]
        transaction_json = self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('11.00'), **merchant_info)
        self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('3.12'), **merchant_info)
        self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('-4.12'), **merchant_info)
