import json
from decimal import Decimal

import requests

from stormx_verification_framework import (
    StormxSystemVerification,
    uses_expedia,
    pretty_print_json,
    log_error_system_tests_output
)

from stormx_api_client.exceptions import BadRequestException


class TestApiHotelBookingExpedia(StormxSystemVerification):
    """
    Verify hotel booking scenarios that test some of the details specific to Expedia inventory.

    This set of tests especially focuses on the the endpoint `POST /api/v1/hotels`.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBookingExpedia, cls).setUpClass()

    # TODO: maybe split up into a few different tests.
    # TODO: run the same tests on the agent booking side!
    @uses_expedia
    def test_passenger_book_hotel__ean_failure_scenarios(self):
        def do_booking(test_command):
            url = self._api_host + '/api/v1/offer/hotels'
            customer = 'Purple Rain Airlines'
            booking_headers = self._generate_passenger_headers()
            booking_headers['Test-Command'] = json.dumps(test_command)
            airport_iata_code = self.select_airport_for_expedia_testing([
                ('BWI', 'America/Phoenix'),
                ('LGW', 'Europe/London')
            ])

            passengers = self._create_2_passengers(customer=customer, port_accommodation=airport_iata_code)
            leader_of_passenger_group = passengers[1]
            follower_of_passenger_group = passengers[0]
            passenger_ids = [p['context_id'] for p in passengers]

            # both leader and follower check the offerings on their cell phones together----
            leader_hotel_offerings = self._get_passenger_hotel_offerings(leader_of_passenger_group)
            self.assertGreaterEqual(len(leader_hotel_offerings), 2)

            # leader books hotel ----
            leader_picked_hotel = leader_hotel_offerings[0]  # the first hotel in the list
            leader_query_parameters = dict(
                ak1=leader_of_passenger_group['ak1'],
                ak2=leader_of_passenger_group['ak2'],
            )
            leader_booking_payload = dict(
                context_ids=passenger_ids,
                hotel_id=leader_picked_hotel['hotel_id'],
                room_count=1,
            )
            booking_response = requests.post(url, headers=booking_headers, params=leader_query_parameters,
                                             json=leader_booking_payload)
            return booking_response.status_code, booking_response.json()

        # use the sandbox `test_command` feature to control the expedia failure case for each attempt to `call_book()`.
        # the enumeration values come from https://developer.expediapartnersolutions.com/reference/rapid-booking-test-request

        # TODO: this appears to be another bug in the expedia simulation: 'request_currency' key was not found for
        #       checked_price_occupancy_details['totals']['inclusive']['request_currency']
        # status_code, response_json = do_booking(test_command={'call_price_check': ['matched']})
        # self.assertEqual(status_code, 200)
        # self.assertEqual(response_json['meta']['error_code'], '')
        # self.assertEqual(response_json['meta']['message'], 'OK')
        # self.assertEqual(response_json['meta']['error_description'], '')

        status_code, response_json = do_booking(test_command={'call_price_check': ['price_changed']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'The downstream provider changed prices. '
                         'Please try the booking again in a minute or try selecting a different hotel.')

        status_code, response_json = do_booking(test_command={'call_price_check': ['sold_out']})
        self.assertEqual(status_code, 400)
        self.assertEqual(response_json['meta']['error_code'], 'INSUFFICIENT_INVENTORY')
        self.assertEqual(response_json['meta']['message'], 'Bad Request')
        self.assertIn('Not enough inventory found for ', response_json['meta']['error_description'])

        status_code, response_json = do_booking(test_command={'call_price_check': ['unknown_internal_error']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'The downstream provider reported an unknown error and the booking failed. '
                         'Please retry the booking again in a minute, or try selecting a different hotel.')

        status_code, response_json = do_booking(test_command={'call_price_check': ['service_unavailable']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'The downstream provider booking service is temporarily unavailable. '
                         'Please retry the booking again in a minute.')

        status_code, response_json = do_booking(test_command={'call_book': ['standard']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], '')
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertEqual(response_json['meta']['error_description'], '')

        status_code, response_json = do_booking(test_command={'call_book': ['cc_declined']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'The downstream hotel provider reported that the booking failed.')

        status_code, response_json = do_booking(test_command={'call_book': ['rooms_unavailable']})
        self.assertEqual(status_code, 400)
        self.assertEqual(response_json['meta']['error_code'], 'INSUFFICIENT_INVENTORY')
        self.assertEqual(response_json['meta']['message'], 'Bad Request')
        self.assertIn('Not enough inventory found for ', response_json['meta']['error_description'])

        status_code, response_json = do_booking(test_command={'call_book': ['price_match']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'The downstream hotel provider reported that the booking failed.')

        # # TODO: wait for expedia simulation bug fix!  price_unavailable is supposed to return 410, not 503, then rework this test case.
        # status_code, response_json = do_booking(test_command={'call_book': ['price_unavailable']})
        # self.assertEqual(status_code, 200)
        # self.assertEqual(response_json['meta']['error_code'], 'BOOKING_STATE_UNKNOWN')
        # self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        # self.assertEqual(response_json['meta']['error_description'],
        #                  'The downstream hotel provider reported that the booking failed.')

        # scenario: error first two booking attempts, success second booking attempt.
        status_code, response_json = do_booking(
            test_command={'call_book': ['internal_server_error', 'internal_server_error', 'standard']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], '')
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertEqual(response_json['meta']['error_description'], '')

        # scenario: error first 3 booking attempts.
        status_code, response_json = do_booking(
            test_command={'call_book': ['internal_server_error', 'internal_server_error', 'internal_server_error']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'The downstream provider reported an unknown error and the booking failed. '
                         'Please retry the booking again in a minute, or try selecting a different hotel.')

        status_code, response_json = do_booking(
            test_command={'call_book': ['service_unavailable', 'service_unavailable', 'service_unavailable']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'The downstream provider booking service is temporarily unavailable.Please retry the booking again in a minute.')

        # fail on first attempt to connect to expedia to complete the booking.
        status_code, response_json = do_booking(test_command={'call_book': ['requests.ConnectTimeout']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_FAILED')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'Unable to reach the downstream provider and submit the booking. Please try the booking again in a minute.')

        # recover from two network errors
        status_code, response_json = do_booking(
            test_command={'call_book': ['requests.ReadTimeout', 'requests.ReadTimeout', 'standard']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], '')
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertEqual(response_json['meta']['error_description'], '')

        # fail after three network errors
        status_code, response_json = do_booking(
            test_command={'call_book': ['requests.ReadTimeout', 'requests.ReadTimeout', 'requests.ReadTimeout']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'BOOKING_STATE_UNKNOWN')
        self.assertEqual(response_json['meta']['message'], 'Booking Problem')
        self.assertEqual(response_json['meta']['error_description'],
                         'There was a network communication issue issue with the downstream provider while booking. '
                         'Unfortunately, we do not yet know if the pending booking succeeded or failed. '
                         'Please refresh status in a minute to see if this transaction succeeded or failed.')

        # recover after a successful booking that we didn't know was successful
        status_code, response_json = do_booking(
            test_command={'call_book': ['requests.ReadTimeout-after_success', 'standard']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], '')
        self.assertEqual(response_json['meta']['message'], 'OK')
        self.assertEqual(response_json['meta']['error_description'], '')

        status_code, response_json = do_booking(test_command={'call_book': ['requests.bleh-bad-testing-command']})
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_JSON')
        self.assertEqual(response_json['meta']['message'], 'Invalid Test Command')
        self.assertEqual(response_json['meta']['error_description'],
                         "unknown test command: 'requests.bleh-bad-testing-command'")

    def _verify_hotel_voucher_totals_correctly(self, hotel_voucher):
        reported_total = hotel_voucher['total_amount']

        fees_sum = Decimal('0.00')
        for fee in hotel_voucher['fees']:
            self.assertGreater(fee['rate'], 0)
            self.assertEqual(fee['total'], fee['count'] * fee['rate'])
            fees_sum += fee['total']

        room_rate_total = Decimal('0.00')
        for room in hotel_voucher['room_vouchers']:
            self.assertGreater(room['rate'], 0)
            room_rate_total += room['count'] * room['rate']

        tax = hotel_voucher['tax']

        print('\t' + repr((room_rate_total, tax, hotel_voucher['fees'])))
        computed_total = room_rate_total + tax + fees_sum
        self.assertEqual(computed_total, reported_total, msg='total incorrect for ' + repr((hotel_voucher['hotel_id'], hotel_voucher['hotel_name'])))

    # # TODO: this is a really slow, exhasutive test! Maybe run once a week somewhere??
    # @uses_expedia
    # def test_ean_totalling_in_lots_of_bookings(self):
    #     customer = 'Purple Rain Airlines'
    #     airline_client = self.get_airline_api_client(customer)
    #
    #     port_objects = self.get_objects('PortMaster', fields=('port_prefix', 'port_timezone'), port_is_available=1, limit=1000)
    #     ports_and_timezones = [ (p['port_prefix'], p['port_timezone']) for p in port_objects]
    #     ports_for_testing = sorted(self.select_multiple_airports_for_expedia_testing(ports_and_timezones))
    #     print(ports_for_testing)
    #     print('len(ports_for_testing) = ', len(ports_for_testing))
    #     #ports_for_testing = [p for p in ports_for_testing if p >= 'AAA']  # if test breaks and you want to restart.
    #     for port in ports_for_testing:
    #
    #         passenger_count = 4
    #         print('-'*80)
    #         print('port:' + repr(port) + '...')
    #         hotels = airline_client.get_hotels(port=port, room_count=1, provider='ean')
    #
    #         for picked_hotel in hotels:
    #             print(repr((picked_hotel['hotel_id'], picked_hotel['hotel_name'])))
    #             ean_offer = picked_hotel['hotel_id']
    #             passengers = airline_client.import_passengers(self._generate_n_passenger_payload(passenger_count, port_accommodation=port))
    #             context_ids = [passenger['context_id'] for passenger in passengers]
    #             try:
    #                 ean_voucher = airline_client.book_hotel(context_ids=context_ids, hotel_id=ean_offer, room_count=1)
    #             except BadRequestException as e:
    #                 print('\t****booking failed ' + repr(e.response.json()['meta']['error_code'] + '. moving on...'))
    #                 continue
    #             self._verify_hotel_voucher_totals_correctly(ean_voucher['hotel_voucher'])
    #             full_state = airline_client.get_passenger_full_state(passengers[0]['context_id'])
    #             self._verify_hotel_voucher_totals_correctly(full_state['voucher']['hotel_voucher'])

    @uses_expedia
    def test_ean_booking_2_pax_1_room(self):
        """
        validate an expedia booking with 2 pax in 1 room
        """
        customer = 'Purple Rain Airlines'
        airline_client = self.get_airline_api_client(customer)

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        passengers_payload = self._generate_n_passenger_payload(2, port_accommodation=port)
        passengers = airline_client.import_passengers(passengers_payload)

        hotels = airline_client.get_hotels(port=port, room_count=1, provider='ean')

        picked_hotel = hotels[0]
        ean_offer = picked_hotel['hotel_id']
        context_ids=[passenger['context_id'] for passenger in passengers]

        ean_voucher = airline_client.book_hotel(context_ids=context_ids, hotel_id=ean_offer, room_count=1)

        hotel_voucher = ean_voucher['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
            self.assertEqual(tax['amount'], hotel_voucher['tax'])
            self.assertEqual(tax['name'], 'OTA_TAXES')
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)
        self.assertEqual(len(hotel_voucher['taxes']), 1)

        self.assertEqual(ean_voucher['hotel_voucher']['provider'], 'ean')
        self.assertEqual(ean_voucher['hotel_voucher']['hotel_id'], ean_offer)

        fees_sum = Decimal('0.00')
        for fee in ean_voucher['hotel_voucher']['fees']:
            self.assertGreater(fee['rate'], 0)
            self.assertEqual(fee['total'], fee['count'] * fee['rate'])
            fees_sum += fee['total']

        if picked_hotel['rate'] == ean_voucher['hotel_voucher']['room_vouchers'][0]['rate']:
            self.assertEqual(ean_voucher['hotel_voucher']['tax'], picked_hotel['tax'])

        expected_total = ean_voucher['hotel_voucher']['room_vouchers'][0]['rate'] + ean_voucher['hotel_voucher']['tax'] + fees_sum
        self.assertEqual(ean_voucher['hotel_voucher']['total_amount'], expected_total)
        self.assertEqual(len(ean_voucher['hotel_voucher']['room_vouchers']), 1)
        self.assertEqual(ean_voucher['hotel_voucher']['room_vouchers'][0]['count'], 1)
        self.assertEqual(ean_voucher['hotel_voucher']['hotel_name'], picked_hotel['hotel_name'])

        self.assertTrue(ean_voucher['hotel_voucher']['confirmation_id'].isdigit())
        self.assertEqual(len(ean_voucher['hotel_voucher']['confirmation_id']), 13)
        # should not be present when we have a confirmation number
        self.assertIsNone(ean_voucher['hotel_voucher']['hotel_key'])

        self.assertEqual({passenger['context_id'] for passenger in passengers},
                         {passenger['context_id'] for passenger in ean_voucher['passengers']})

        full_state = airline_client.get_passenger_full_state(passengers[0]['context_id'])
        self.assertEqual(full_state['voucher']['hotel_voucher']['total_amount'], expected_total)
        self.assertEqual(full_state['voucher']['hotel_voucher']['room_vouchers'][0]['rate'],
                         ean_voucher['hotel_voucher']['room_vouchers'][0]['rate'])
        self.assertEqual(full_state['voucher']['hotel_voucher']['tax'], ean_voucher['hotel_voucher']['tax'])
        self.assertEqual(full_state['voucher']['hotel_voucher']['hotel_id'], ean_offer)
        self.assertEqual(full_state['voucher']['hotel_voucher']['hotel_name'],
                         ean_voucher['hotel_voucher']['hotel_name'])

        fees_sum_full_state = Decimal('0.00')
        for fee in full_state['voucher']['hotel_voucher']['fees']:
            self.assertGreater(fee['rate'], 0)
            self.assertEqual(fee['total'], fee['count'] * fee['rate'])
            fees_sum_full_state += fee['total']

        self.assertEqual(fees_sum, fees_sum_full_state)

        hotel_voucher = full_state['voucher']['hotel_voucher']
        tax_total = Decimal('0.00')
        for tax in hotel_voucher['taxes']:
            tax_total += Decimal(tax['amount'])
            self.assertEqual(tax['amount'], hotel_voucher['tax'])
            self.assertEqual(tax['name'], 'OTA_TAXES')
        self.assertEqual(Decimal(hotel_voucher['tax']), tax_total)
        self.assertEqual(len(hotel_voucher['taxes']), 1)

    @uses_expedia
    def test_ean_booking_7_pax_3_rooms(self):
        """
        validate an expedia booking with 7 pax in 3 rooms

        validate some of the AA hacks / workarounds too.
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer)
        airline_client = self.get_airline_api_client(customer)

        port = self.select_airport_for_expedia_testing([
            ('TUS', 'America/Phoenix'),
            ('LGW', 'Europe/London')
        ])

        passengers = self._generate_n_passenger_payload(7, port_accommodation=port)
        passengers = airline_client.import_passengers(passengers)

        hotels = airline_client.get_hotels(port=port, room_count=3, provider='ean')
        self.assertGreater(len(hotels), 0, msg='no inventory in ' + repr(port))

        ean_offer = hotels[0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=3
        )

        passenger = passengers[0]

        booking_response = airline_client.book_hotel(raw_response=True, **booking_payload)
        ean_voucher = airline_client.get_data_or_raise(booking_response)

        self.assertEqual(ean_voucher['hotel_voucher']['provider'], 'ean')
        self.assertEqual(ean_voucher['hotel_voucher']['hotel_id'], ean_offer)

        for room in ean_voucher['hotel_voucher']['room_vouchers']:
            self.assertIs(room['hard_block'], False)
            self.assertEqual(room['block_type'], 'soft_block')
            self.assertGreater(Decimal(room['rate']), Decimal('20.00'))  # ensure reasonable rate.
            self.assertLess(Decimal(room['rate']), Decimal('300.00'))  # ensure reasonable rate.
            # right now the $300.00
            # self.assertLess(Decimal(room['rate']) + Decimal(room['rate']), Decimal('300.00'))

        # ensure total number of rooms is right in the blocks.
        total_rooms = 0
        for room in ean_voucher['hotel_voucher']['room_vouchers']:
            total_rooms += room['count']
        self.assertEqual(total_rooms, 3)

        self.assertGreater(Decimal(ean_voucher['hotel_voucher']['total_amount']),
                           Decimal('60.00'))  # ensure reasonable rate.
        self.assertLess(Decimal(ean_voucher['hotel_voucher']['total_amount']),
                        Decimal('1200.00'))  # ensure reasonable rate.

        tax_percentage = 100 * Decimal(ean_voucher['hotel_voucher']['tax']) / (
                    Decimal(ean_voucher['hotel_voucher']['total_amount']) - Decimal(
                ean_voucher['hotel_voucher']['tax']))
        # print('tax_percentage=', tax_percentage)
        self.assertGreaterEqual(tax_percentage, 4)  # ensure reasonable percentage.
        self.assertLessEqual(tax_percentage, 30)  # ensure reasonable percentage.

        self.assertTrue(ean_voucher['hotel_voucher']['confirmation_id'].isdigit())
        self.assertEqual(len(ean_voucher['hotel_voucher']['confirmation_id']), 13)

        expected_aa_hacked_value = 'ITN:' + ean_voucher['hotel_voucher']['confirmation_id']
        self.assertEqual(ean_voucher['hotel_voucher']['hotel_key'], expected_aa_hacked_value)

        self.assertEqual({passenger['context_id'] for passenger in passengers},
                         {passenger['context_id'] for passenger in ean_voucher['passengers']})

        full_state = airline_client.get_passenger_full_state(passenger['context_id'])
        self.assertEqual(full_state['voucher']['hotel_voucher']['provider'], 'ean')
        room_vouchers = full_state['voucher']['hotel_voucher']['room_vouchers']
        for room_voucher in room_vouchers:
            self.assertEqual(room_voucher['hard_block'], False)
            self.assertEqual(room_voucher['block_type'], 'soft_block')

    @uses_expedia
    def test_ean_booking_1_adult_2_rooms(self):
        """
        validate an expedia booking with 7 pax in 3 rooms

        validate some of the AA hacks / workarounds too.
        """
        customer = 'American Airlines'
        airline_client = self.get_airline_api_client(customer)

        port = self.select_airport_for_expedia_testing([
            ('TUS', 'America/Phoenix'),
            ('LGW', 'Europe/London')
        ])

        passengers = self._generate_n_passenger_payload(1, port_accommodation=port, life_stage='adult')
        passengers = airline_client.import_passengers(passengers)

        hotels = airline_client.get_hotels(port=port, room_count=2, provider='ean')
        self.assertGreater(len(hotels), 0, msg='no inventory in ' + repr(port))

        ean_offer = hotels[0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=2
        )

        booking_response = airline_client.book_hotel(raw_response=True, **booking_payload)
        booking_response_json_data = airline_client.get_data_or_raise(booking_response)
        self.assertEqual(booking_response.status_code, 200)
        self.assertEqual(booking_response_json_data['hotel_voucher']['rooms_booked'], 2)
        self.assertIsNone(booking_response_json_data['hotel_voucher']['hotel_message'])

    @uses_expedia
    def test_ean_booking_1_child_1_room(self):
        """
        validate an expedia booking with 7 pax in 3 rooms

        validate some of the AA hacks / workarounds too.
        """
        customer = 'American Airlines'
        airline_client = self.get_airline_api_client(customer)

        port = self.select_airport_for_expedia_testing([
            ('TUS', 'America/Phoenix'),
            ('LGW', 'Europe/London')
        ])

        passengers = self._generate_n_passenger_payload(1, port_accommodation=port, life_stage='child')
        passengers = airline_client.import_passengers(passengers)

        hotels = airline_client.get_hotels(port=port, room_count=1, provider='ean')
        self.assertGreater(len(hotels), 0, msg='no inventory in ' + repr(port))

        ean_offer = hotels[0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=1
        )

        # just assure booking doesn't fail. It will raise an exception if something
        # goes wrong.
        airline_client.book_hotel(**booking_payload)


    @uses_expedia
    def test_ean_booking_1_young_adult_1_room(self):
        """
        validate an expedia booking with 7 pax in 3 rooms

        validate some of the AA hacks / workarounds too.
        """
        customer = 'American Airlines'
        airline_client = self.get_airline_api_client(customer)

        port = self.select_airport_for_expedia_testing([
            ('PHX', 'America/Phoenix'),
            ('LGW', 'Europe/London')
        ])

        passengers = self._generate_n_passenger_payload(1, port_accommodation=port, life_stage='young_adult')
        passengers = airline_client.import_passengers(passengers)

        hotels = airline_client.get_hotels(port=port, room_count=1, provider='ean')
        self.assertGreater(len(hotels), 0, msg='no inventory in ' + repr(port))

        ean_offer = hotels[0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=1
        )

        # just assure booking doesn't fail. It will raise an exception if something
        # goes wrong.
        airline_client.book_hotel(**booking_payload)

    @uses_expedia
    def test_ean_booking_max_rooms(self):
        """
        validate an expedia booking with 7 pax in 3 rooms

        validate some of the AA hacks / workarounds too.
        """
        customer = 'American Airlines'
        airline_client = self.get_airline_api_client(customer)

        port = self.select_airport_for_expedia_testing([
            ('PHX', 'America/Phoenix'),
            ('LGW', 'Europe/London')
        ])
        number_of_rooms_to_book = 9

        passengers = self._generate_n_passenger_payload(number_of_rooms_to_book, port_accommodation=port,
                                                        life_stage='adult')
        passengers = airline_client.import_passengers(passengers)

        hotels = airline_client.get_hotels(port=port, room_count=3, provider='ean')
        self.assertGreater(len(hotels), 0, msg='no inventory in ' + repr(port))

        ean_offer = hotels[0]['hotel_id']

        booking_payload = dict(
            context_ids=[passenger['context_id'] for passenger in passengers],
            hotel_id=ean_offer,
            room_count=number_of_rooms_to_book
        )

        booking_response = airline_client.book_hotel(raw_response=True, **booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertTrue(booking_response_json['error'])
        self.assertTrue(booking_response_json['meta']['error_code'], 'MAX_ROOMS_EXCEEDED')
        self.assertTrue(booking_response_json['meta']['error_description'],
                        'The hotel provider only allows a maximum of 8 rooms per booking.')

    @uses_expedia
    def test_ean_booking_disabled_for_british(self):
        customer = 'British Airways'
        airline_client = self.get_airline_api_client(customer)

        # import passengers and set up booking parameters
        passengers = self._create_2_passengers(customer=customer, port_accommodation='LAX')
        booking_payload = dict(
            # the key here is that this is an expedia hotel id, and that
            # we will not even consider decoding it if expedia inventory
            # is disabled.
            hotel_id='ean-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            room_count=1,
            context_ids=[passenger['context_id'] for passenger in passengers]
        )

        # book hotel validate response, and validate full state for booking
        response = airline_client.book_hotel(raw_response=True, **booking_payload)
        self._validate_error_message(response.json(), 200, 'Booking Problem', 'BOOKING_FAILED',
                                     'The downstream hotel provider reported that the booking failed.', [])
