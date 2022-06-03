import json
from decimal import Decimal

import requests

from stormx_verification_framework import (
    StormxSystemVerification,
    display_response,
)


class TestHMTRecon(StormxSystemVerification):
    def setup(self):
        super(TestHMTRecon, self).setUp()

    def test_authorization(self):

        airline_id = 294  # Purple Rain
        hotel_id = 95378  # Hilton - Phoenix Airport
        port = 217  # port id for phx
        user_types = ["hotel"]

        # run for support user  ITSupport
        response = self.reconcilliation_access_authorization(endpoint='getReconData')
        self.assertNotEqual(response, {'ErrorMessage': 'Access denied'})

        # run for TVA operator user
        operator_user = self.create_new_tva_user(role="Operator", group_id=3, is_active=True)
        response = self.reconcilliation_access_authorization(endpoint='getReconData', test_user=operator_user)
        self.assertEqual(response, {'ErrorMessage': 'Access denied'})

        # run for TVA senior manager user
        operator_user = self.create_new_tva_user(role="Senior Management", group_id=2, is_active=True)
        response = self.reconcilliation_access_authorization(endpoint='getReconData', test_user=operator_user)
        self.assertEqual(response, {'ErrorMessage': 'Access denied'})

        # run for TVA readonly user
        operator_user = self.create_new_tva_user(role="Read Only User", group_id=2, is_active=True)
        response = self.reconcilliation_access_authorization(endpoint='getReconData', test_user=operator_user)
        self.assertEqual(response, {'ErrorMessage': 'Access denied'})

        # run for TVA supervisor user
        operator_user = self.create_new_tva_user(role="Supervisor", group_id=2, is_active=True)
        response = self.reconcilliation_access_authorization(endpoint='getReconData', test_user=operator_user)
        self.assertEqual(response, {'ErrorMessage': 'Access denied'})

        # run for TVA Finance user
        finance_user = self.create_new_tva_user(role="Finance", group_id=2, is_active=True)
        response = self.reconcilliation_access_authorization(endpoint='getReconData', test_user=finance_user)
        self.assertNotEqual(response, {'ErrorMessage': 'Access denied'})

        # run for airline users
        user_list = self.create_airline_users_with_different_roles(port_id=port, airline_id=airline_id)
        for user in user_list:
            response = self.reconcilliation_access_authorization(endpoint='getReconData', test_user=None,
                                                                 user_cookie=user.get('cookies'))
            self.assertEqual(response, {'ErrorMessage': 'Access denied'})

            # # run for hotel users
            # hotel_users = self.get_login_users_list(self,port_id=port, airline_id=airline_id, hotel_id=hotel_id,types=user_types,transport_id=0 )
            # for user in hotel_users:
            #     response = self.reconcilliation_access_authorization(endpoint='getReconData', test_user=None,
            #                                                          user_cookie=user.get('cookies'))
            #     self.assertEqual(response, {'ErrorMessage': 'Access denied'})

    def test_required_form_data(self):
        # if we don't provide any filter, airline is a mandatory filter
        response = self.get_reconcilliation_data()
        self.assertEqual(response, {'ErrorMessage': 'Airline Required'})

    def test_validating_form_data(self):
        """
        add a new transaction.
        provide all filters as new transaction and see if it is getting records

        :return:
        """

        # add a transaction here
        airline_id = 294  # Purple Rain
        hotel_id = 95378  # Hilton - Phoenix Airport
        port = 217  # port id for phx
        status = 0
        pax_name = 'Jane Doe'
        start_date = self._get_event_date('America/Phoenix')
        end_date = self._get_event_date('America/Phoenix')

        self.adding_a_test_hotel_transaction()
        recon_data = self.get_reconcilliation_data(airline_id=airline_id, hotel_id=hotel_id, status=status,
                                                   port_id=port,
                                                   name=pax_name, date_from=start_date, date_to=end_date)

        self.assertGreater(len(recon_data['transactions_data']), 0)

    def test_updating_hotel_data_with_wrong_status(self):
        """
        try updating status of a transaction to "invoiced". should get error
        :return:
        """

        airline = 294  # purple rain airline
        recon_for = 'H'

        self.adding_a_test_hotel_transaction()
        recon_data = self.get_reconcilliation_data(airline_id=airline, recon_for=recon_for, status=0)
        transaction_id = recon_data['transactions_data'][0]['single_card_transaction_id']
        status = 6  # invoiced status TODO: use status enum
        response = self.update_reconcilliation_transaction_status(transaction_id=transaction_id, status=status)

        self.assertEqual(response, {'loginError': 'Not Allowed'})

    def test_updating_status_for_hotel_data(self):
        """    Note: This Test require a transaction with "not processed" status.
               Used reconcilliation utility to get new transactions

               flow:
               Get  transactions with "not processed" status for an airline.
               update first transaction with "Reconciled" status.

               Get  transactions with "Reconciled" status for that airline.
               find old transaction id in "reconciled" transactions.

               """
        airline = 294  # purple rain airline
        recon_for = 'H'
        recon_date = self._get_event_date('America/Phoenix')

        self.adding_a_test_hotel_transaction()
        recon_data = self.get_reconcilliation_data(airline_id=airline, recon_for=recon_for,
                                                   status=0)  # get 'Not Processed' Transactions
        transaction_id = recon_data['transactions_data'][0]['single_card_transaction_id']
        status = 3  # reconcile status TODO: use status enum
        self.update_reconcilliation_transaction_status(transaction_id=transaction_id, status=status)
        recon_data = self.get_reconcilliation_data(airline_id=airline, recon_for=recon_for, status=status,
                                                   date_from=recon_date,
                                                   date_to=recon_date)  # get 'reconciled' transactions

        expected_status = 'Reconciled, Reconciled, Reconciled'  # test transactions function is adding 3 transactions at a time
        current_status = ''
        for recon in recon_data['transactions_data']:
            if recon['single_card_transaction_id'] == transaction_id:
                current_status = recon['Status']

        self.assertEqual(expected_status, current_status)

    def test_hotel_data_recon_totals(self):
        """
        Note: This Test require a transaction with "not processed" status.
        Used reconcilliation utility to get new transactions

        flow:
        Get reconciled Total for an airline.
        update another transaction with "Reconciled" status.
        Get reconciled Total for airline again.
        Match totals with expected totals
        :return:
        """

        airline = 294  # purple rain airline
        recon_for = 'H'
        status = 3  # reconcile status TODO: use status enum
        recon_totals = self.get_reconcilliation_Totals(airline_id=airline)  # get totals for purple rain

        self.adding_a_test_hotel_transaction()
        recon_data = self.get_reconcilliation_data(airline_id=airline, recon_for=recon_for,
                                                   status=0)  # get 'Not Processed' Transactions

        transaction_id = recon_data['transactions_data'][0]['single_card_transaction_id']
        transaction_items = int(recon_data['transactions_data'][0]['item'])
        transaction_nights = int(recon_data['transactions_data'][0]['nights'])
        transaction_amount = Decimal(recon_data['transactions_data'][0]['Transaction'])
        self.update_reconcilliation_transaction_status(transaction_id=transaction_id, status=status)

        expected_rooms = int(recon_totals['HotelTotal']) + (transaction_items * transaction_nights)
        expected_amount = Decimal(recon_totals['HotelAmount']) + transaction_amount

        recon_totals = self.get_reconcilliation_Totals(airline_id=airline)  # get totals for purple rain

        self.assertEqual(int(recon_totals['HotelTotal']), expected_rooms)
        self.assertAlmostEqual(Decimal(recon_totals['HotelAmount']), expected_amount)

    def test_history_of_transaction(self):
        """
        test if audit of transactions coming right
        :return:
        """
        airline = 294  # purple rain airline
        recon_for = 'H'

        trans = self.adding_a_test_hotel_transaction()
        recon_data = self.get_reconcilliation_data(airline_id=airline, recon_for=recon_for,
                                                   status=0)  # get 'Not Processed' Transactions
        transaction_id = recon_data['transactions_data'][0]['single_card_transaction_id']
        single_card_id = recon_data['transactions_data'][0]['single_card_id']
        self.update_reconcilliation_transaction_status(transaction_id=transaction_id, status=3)

        transaction_history = self.get_transaction_history(single_card_id)
        self.assertEqual(len(transaction_history['history']), 6)

    def test_invoice_creation_filters(self):
        """
        do not provide any filters for invoice creation and see if get validation error

        :return:
        """

        invoice_response = self.create_hmt_invoice()
        self.assertEqual(invoice_response, {'errorMessage': 'Please provide required information.'})

    def test_invoice_creation(self):
        """
        add some transactions
        update there status to reconcile
        apply same filters for invoice creation and see if invoice is being created

        :return:
        """
        airline_id = 294  # Purple Rain
        port = 217  # port id for phx
        currency = 'USD'
        airline_prefix = 'PRP'
        recon_for = 'H'
        start_date = self._get_event_date('America/Phoenix')
        end_date = self._get_event_date('America/Phoenix')

        # Add some new transactions
        self.adding_a_test_hotel_transaction()
        self.adding_a_test_hotel_transaction()

        recon_data = self.get_reconcilliation_data(airline_id=airline_id, recon_for=recon_for,
                                                   status=0, date_from=start_date,
                                                   date_to=end_date)  # get 'Not Processed' Transactions of today

        transactions_ids = []
        for recon in recon_data['transactions_data']:
            transactions_ids.append(recon['single_card_transaction_id'])

        self.update_reconcilliation_transaction_status(transactions_ids=transactions_ids, status=3)

        invoice_response = self.create_hmt_invoice(airline_id=airline_id, recon_for=recon_for, port_id=port,
                                                   currency=currency, date_from=start_date, date_to=end_date,
                                                   airline_prfix=airline_prefix)

        self.assertEqual(invoice_response, {'successMessage': 'saved'})

    def test_validate_invoice_search(self):
        # try getting invoices without any filter, airline is a mandatory filter
        response = self.get_hmt_recon_invoices()
        self.assertEqual(response, {'ErrorMessage': 'Airline Required'})

    def test_verify_meal_totals(self):
        airline = 294  # purple rain airline
        recon_for = 'M'

        status = 3  # reconcile status TODO: use status enum
        recon_totals = self.get_reconcilliation_Totals(airline_id=airline)  # get totals for purple rain

        self.adding_a_test_meal_transaction()
        recon_data = self.get_reconcilliation_data(airline_id=airline, recon_for=recon_for,
                                                   status=0)  # get 'Not Processed' Transactions

        transaction_id = recon_data['transactions_data'][0]['single_card_transaction_id']
        transaction_amount = Decimal(recon_data['transactions_data'][0]['Transaction'])
        self.update_reconcilliation_transaction_status(transaction_id=transaction_id, status=status)

        expected_meals = int(recon_totals['MealTotal']) + 1  # 1 meal per card
        expected_amount = Decimal(recon_totals['MealAmount']) + transaction_amount

        recon_totals = self.get_reconcilliation_Totals(airline_id=airline)  # get totals for purple rain

        self.assertEqual(int(recon_totals['MealTotal']), expected_meals)
        self.assertEqual(Decimal(recon_totals['MealAmount']), expected_amount)

    def adding_a_test_hotel_transaction(self):

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

    def adding_a_test_meal_transaction(self):
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
        transaction_json = self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('11.00'),
                                                       **merchant_info)
        self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('3.12'), **merchant_info)
        self.charge_single_use_card(card['card_number'], card['currency_code'], Decimal('-4.12'), **merchant_info)
