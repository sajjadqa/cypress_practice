import datetime
import unittest
from decimal import Decimal

import pytz
import requests

from StormxApp.constants import StormxConstants
from stormx_verification_framework import (
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output,
    uses_expedia,
)

hotel_sanitized_fields = ['rate', 'tax', 'provider']


class TestApiHotelSearch(StormxSystemVerification):
    """
    Verify general hotel search behavior.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelSearch, cls).setUpClass()

    def test_passenger_get_hotel_offers(self):
        """
        verify that the passenger can look at their hotel offers.
        """
        url = self._api_host + '/api/v1/offer/hotels'
        customer = 'Delta Air Lines'
        headers = self._generate_passenger_headers()

        passengers = self._create_2_passengers(customer=customer)

        for passenger in passengers:
            query_parameters = dict(
                ak1=passenger['ak1'],
                ak2=passenger['ak2'],
                room_count='1',
            )
            response = requests.get(url, headers=headers, params=query_parameters)
            self.assertEqual(response.status_code, 200)
            response_json = response.json()
            self.assertIs(response_json['error'], False)
            returned_hotels = response_json['data']
            self.assertGreaterEqual(len(returned_hotels), 1)

            for hotel in returned_hotels:
                self.assertNotIn('tax', hotel)
                self.assertNotIn('rate', hotel)

    def test_airline_get_hotel_offers(self):
        """
        verify that the airline can look at their hotel offers.
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer=customer)

        for passenger in passengers:
            query_parameters = dict(
                port=passenger['port_accommodation'],
                room_count='1'
            )
            response = requests.get(url, headers=headers, params=query_parameters)
            self.assertEqual(response.status_code, 200)
            response_json = response.json()
            self.assertIs(response_json['error'], False)
            returned_hotels = response_json['data']
            self.assertGreaterEqual(len(returned_hotels), 1)

            for hotel in returned_hotels:
                self.assertIn('tax', hotel)
                self.assertIn('rate', hotel)

    def test_get_hotels_by_group_and_date(self):
        """
        verify that an airline can look up hotels a list of possible hotels for a passenger.
        """
        url = self._api_host + '/api/v1/hotels'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer)
        passenger = passengers[0]

        query_parameters = dict(
            port=passenger['port_accommodation'],
            room_count='1',
        )

        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        hotels = response_json['data']
        self.assertGreaterEqual(len(hotels), 1)

    def test_hotel_sanitized_fields(self):
        """
        validate public hotel objects do not contain various fields
        """
        customer = 'Purple Rain Airlines'
        passengers = self._create_2_passengers(customer=customer)

        hotels = self._get_passenger_hotel_offerings(passengers[0])
        for hotel in hotels:
            self.assertEqual('tvl', hotel['hotel_id'].split('-', 1)[0])
            for field in hotel_sanitized_fields:
                self.assertNotIn(field, hotel)

    def test_handicap_can_search_through_pax_app_roh_temp(self):
        """
        verify handicap can search through pax app using ROH temporarily
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            handicap=True,
            notify=False
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'
        pax_headers = self._generate_passenger_headers()

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertGreater(len(response_json['data']), 0)
        self.assertIn('hotel_id', response_json['data'][0])

    def test_hotel_search_port(self):
        """
        verifies system returns hotels for port searched
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        active_ports = ['PHX', 'DFW', 'LAX', 'ATL', 'SEA', 'MSP', 'JFK', 'ORD', 'DCA']
        for port in active_ports:
            hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=' + port

            hotel_response = requests.get(hotel_url, headers=headers)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)
            self.assertGreater(len(hotel_response_json['data']), 0)

            for hotel in hotel_response_json['data']:
                self.assertEqual(hotel['airport_code'], port)

    """
    Hotel Search Tests below assumes sufficient inventory has already been loaded in system.
    """

    def test_pax_app_hotel_search_port(self):
        """
        verifies system returns hotels for port searched on pax app
        """
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        active_ports = ['PHX', 'DFW', 'LAX', 'ATL', 'SEA', 'MSP', 'JFK', 'ORD', 'DCA']
        for port in active_ports:
            passenger_payload = self._generate_n_passenger_payload(1)

            passenger_payload[0].update(dict(
                port_accommodation=port
            ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)

            passenger = response_json['data'][0]
            hotel_url = self._api_host + '/api/v1/offer/hotels'

            search_query_parameters = dict(
                ak1=passenger['ak1'],
                ak2=passenger['ak2'],
                room_count=1
            )

            hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)
            self.assertGreater(len(hotel_response_json['data']), 0)

            for hotel in hotel_response_json['data']:
                self.assertEqual(hotel['airport_code'], port)

    def test_hotel_search_room_count(self):
        """
        verifies system returns hotels for room_count searched
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        providers = ['', 'tvl', 'ean']
        for provider in providers:
            room_counts = [1, 5, 8]
            for room_count in room_counts:
                hotel_url = self._api_host + '/api/v1/hotels?room_count=' + str(room_count) + '&port=' + port
                if len(provider) > 0:
                    hotel_url += '&provider=' + provider

                hotel_response = requests.get(hotel_url, headers=headers)
                failure_message = 'provider=' + repr(provider) + ' failed in port ' + repr(port) + 'with room count room_count ' + repr(room_count) + '.'
                self.assertEqual(hotel_response.status_code, 200, msg=failure_message)
                hotel_response_json = hotel_response.json()
                self.assertIs(hotel_response_json['error'], False, msg=failure_message)
                self.assertGreater(len(hotel_response_json['data']), 0, msg=failure_message)

                for hotel in hotel_response_json['data']:
                    self.assertGreaterEqual(hotel['available'], room_count, msg=failure_message)

    def test_hotel_search_premium(self):
        """
        verifies system returns hotels for premium searched
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # add premium inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98730, 294, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')

        providers = ['', 'tvl', 'ean']
        for provider in providers:
            hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=LAX&is_premium=true'
            if len(provider) > 0:
                hotel_url += '&provider=' + provider

            hotel_response = requests.get(hotel_url, headers=headers)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)

            try:
                self.assertGreater(len(hotel_response_json['data']), 0)
                for hotel in hotel_response_json['data']:
                    self.assertGreaterEqual(hotel['star_rating'], 4)
            except AssertionError:
                if provider == 'ean':
                    # TODO: let's make this the expectation with the next database snapshot.
                    print('WARN: no premium inventory for expedia.')
                else:
                    self.assertGreater(len(hotel_response_json['data']), 0)

    def test_hotel_search_handicap(self):
        """
        verifies system returns hotels for handicap searched
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # add handicap inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98730, 294, event_date, ap_block_type=1, block_price='150.00', blocks=5,
                                    room_type=2, pay_type='0')

        providers = ['', 'tvl', 'ean']
        for provider in providers:

            if provider == 'ean':
                port = self.select_airport_for_expedia_testing([
                    ('LAX', 'America/Los_Angeles'),
                    ('LGW', 'Europe/London')
                ])
            else:
                port = 'LAX'

            hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=' + port + '&handicap=true'
            if len(provider) > 0:
                hotel_url += '&provider=' + provider

            failure_message = 'provider=' + repr(provider) + ' failed.'
            hotel_response = requests.get(hotel_url, headers=headers)
            self.assertEqual(hotel_response.status_code, 200, msg=failure_message)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False, msg=failure_message)
            self.assertGreater(len(hotel_response_json['data']), 0, msg=failure_message)

    def test_pax_app_hotel_search_pax_status_aa(self):
        """
        verifies system returns premium hotels for certain pax statuses for AA
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        pax_statuses = ['EP', 'CK']
        for pax_status in pax_statuses:
            passenger_payload = self._generate_n_passenger_payload(1)
            passenger_payload[0].update(dict(
                port_accommodation='LAX',
                ticket_level='economy',
                pax_status=pax_status
            ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)

            passenger = response_json['data'][0]
            hotel_url = self._api_host + '/api/v1/offer/hotels'

            search_query_parameters = dict(
                ak1=passenger['ak1'],
                ak2=passenger['ak2'],
                room_count=1
            )

            hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)
            self.assertGreater(len(hotel_response_json['data']), 0)
            self.assertLessEqual(len(hotel_response_json['data']), 3)

            premium_count = 0
            for index, hotel in enumerate(hotel_response_json['data']):
                if index == 0:
                    self.assertGreaterEqual(hotel['star_rating'], 4)
                    premium_count += 1
                else:
                    if hotel['star_rating'] >= 4:
                        premium_count += 1
            self.assertGreater(premium_count, 0)

    def test_pax_app_hotel_search_ticket_level_aa(self):
        """
        verifies system returns premium hotels for first class ticket_level for AA
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        ticket_levels = ['first', 'business']
        for ticket_level in ticket_levels:
            passenger_payload = self._generate_n_passenger_payload(1)
            passenger_payload[0].update(dict(
                port_accommodation='LAX',
                ticket_level=ticket_level,
                pax_status='nonPremium'
            ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)

            passenger = response_json['data'][0]
            hotel_url = self._api_host + '/api/v1/offer/hotels'

            search_query_parameters = dict(
                ak1=passenger['ak1'],
                ak2=passenger['ak2'],
                room_count=1
            )

            hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)
            self.assertGreater(len(hotel_response_json['data']), 0)
            self.assertLessEqual(len(hotel_response_json['data']), 3)

            premium_count = 0
            for index, hotel in enumerate(hotel_response_json['data']):
                if index == 0:
                    self.assertGreaterEqual(hotel['star_rating'], 4)
                    premium_count += 1
                else:
                    if hotel['star_rating'] >= 4:
                        premium_count += 1
            self.assertGreater(premium_count, 0)

    def test_pax_app_hotel_search_pax_status_ba(self):
        """
        verifies system returns premium hotels for certain pax statuses for BA
        """
        customer = 'British Airways'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        event_date = self._get_event_date('Europe/London')
        self.add_hotel_availability(86342, 69, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')
        self.add_hotel_availability(86329, 69, event_date, ap_block_type=1, block_price='75.00', blocks=5, pay_type='0')
        self.add_hotel_availability(83632, 69, event_date, ap_block_type=1, block_price='120.00',blocks=5, pay_type='0')
        self.add_hotel_availability(89300, 69, event_date, ap_block_type=1, block_price='150.00',blocks=5, pay_type='0')

        pax_statuses = ['GOLD']
        for pax_status in pax_statuses:
            passenger_payload = self._generate_n_passenger_payload(1)
            passenger_payload[0].update(dict(
                port_accommodation='LHR',
                ticket_level='economy',
                pax_status=pax_status
            ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)

            passenger = response_json['data'][0]
            hotel_url = self._api_host + '/api/v1/offer/hotels'

            search_query_parameters = dict(
                ak1=passenger['ak1'],
                ak2=passenger['ak2'],
                room_count=1
            )

            hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)
            self.assertGreater(len(hotel_response_json['data']), 0)
            self.assertLessEqual(len(hotel_response_json['data']), 3)

            premium_count = 0
            for index, hotel in enumerate(hotel_response_json['data']):
                if index == 0:
                    self.assertGreaterEqual(hotel['star_rating'], 4)
                    premium_count += 1
                else:
                    if hotel['star_rating'] >= 4:
                        premium_count += 1
            self.assertGreater(premium_count, 0)

    def test_pax_app_hotel_search_ticket_level_ba(self):
        """
        verifies system returns premium hotels for first class ticket_level for BA
        """
        customer = 'British Airways'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        event_date = self._get_event_date('Europe/London')
        self.add_hotel_availability(86342, 69, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')
        self.add_hotel_availability(86329, 69, event_date, ap_block_type=1, block_price='75.00', blocks=5, pay_type='0')
        self.add_hotel_availability(83632, 69, event_date, ap_block_type=1, block_price='120.00', blocks=5, pay_type='0')
        self.add_hotel_availability(89300, 69, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')

        ticket_levels = ['first']
        for ticket_level in ticket_levels:
            passenger_payload = self._generate_n_passenger_payload(1)
            passenger_payload[0].update(dict(
                port_accommodation='LHR',
                ticket_level=ticket_level,
                pax_status='nonPremium'
            ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)

            passenger = response_json['data'][0]
            hotel_url = self._api_host + '/api/v1/offer/hotels'

            search_query_parameters = dict(
                ak1=passenger['ak1'],
                ak2=passenger['ak2'],
                room_count=1
            )

            hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)
            self.assertGreater(len(hotel_response_json['data']), 0)
            self.assertLessEqual(len(hotel_response_json['data']), 3)

            premium_count = 0
            for index, hotel in enumerate(hotel_response_json['data']):
                if index == 0:
                    self.assertGreaterEqual(hotel['star_rating'], 4)
                    premium_count += 1
                else:
                    if hotel['star_rating'] >= 4:
                        premium_count += 1
            self.assertGreater(premium_count, 0)

    def test_pax_app_hotel_search_non_premium(self):
        """
        test non premium inventory is returned for pax app for ba and aa
        """
        passenger_url = self._api_host + '/api/v1/passenger'

        event_date = self._get_event_date('Europe/London')
        self.add_hotel_availability(86342, 69, event_date, ap_block_type=1, block_price='100.00', blocks=5, pay_type='0')
        self.add_hotel_availability(86329, 69, event_date, ap_block_type=1, block_price='75.00', blocks=5, pay_type='0')
        self.add_hotel_availability(83632, 69, event_date, ap_block_type=1, block_price='120.00', blocks=5, pay_type='0')
        self.add_hotel_availability(89300, 69, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')

        customers = ['British Airways', 'American Airlines']
        for customer in customers:
            headers = self._generate_airline_headers(customer=customer)
            pax_headers = self._generate_passenger_headers()
            passenger_payload = self._generate_n_passenger_payload(1)
            passenger_payload[0].update(dict(
                port_accommodation='LAX',
                ticket_level='economy',
                pax_status='nonPremium'
            ))

            if customer == 'British Airways':
                passenger_payload[0].update(dict(
                    port_accommodation='LHR'
                ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_json['error'], False)

            passenger = response_json['data'][0]
            hotel_url = self._api_host + '/api/v1/offer/hotels'

            search_query_parameters = dict(
                ak1=passenger['ak1'],
                ak2=passenger['ak2'],
                room_count=1
            )

            hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
            self.assertEqual(hotel_response.status_code, 200)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False)
            self.assertGreater(len(hotel_response_json['data']), 0)
            self.assertLessEqual(len(hotel_response_json['data']), 3)

            non_premium_count = 0
            for index, hotel in enumerate(hotel_response_json['data']):
                if hotel['star_rating'] < 4:
                    non_premium_count += 1
            self.assertGreater(non_premium_count, 0)

    def test_hotel_search_service_pet(self):
        """
        verifies system returns hotels for service_pet searched
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # add service pet inventory
        event_date = self._get_event_date('America/Chicago')
        self.add_hotel_availability(85725, 72, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')

        providers = ['', 'tvl', 'ean']
        for provider in providers:
            hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=ORD&service_pet=true'
            if len(provider) > 0:
                hotel_url += '&provider=' + provider

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['service_pets_allowed'], True)

    def test_pax_app_hotel_search_service_pet(self):
        """
        verifies system returns hotels for service_pet for pax app
        """
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add service pet inventory
        event_date = self._get_event_date('America/Chicago')
        self.add_hotel_availability(85725, 72, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='ORD',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=False
        ))

        passenger_payload[1].update(dict(
            port_accommodation='ORD',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertGreaterEqual(hotel['service_pets_allowed'], True)

    def test_hotel_search_service_pet_and_premium(self):
        """
        verifies system returns hotels for service_pet and premium searched
        """
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=ORD'

        # add premium and service_pet inventory
        event_date = self._get_event_date('America/Chicago')
        self.add_hotel_availability(85725, 72, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')
        self.add_hotel_availability(85765, 72, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        non_premium_count = 0
        premium_count = 0
        non_service_pet_count = 0
        service_pet_count = 0
        for hotel in hotel_response_json['data']:

            if hotel['star_rating'] < 4:
                non_premium_count += 1
            else:
                premium_count += 1

            if hotel['service_pets_allowed']:
                service_pet_count += 1
            else:
                non_service_pet_count += 1

        self.assertGreaterEqual(non_premium_count, 1)
        self.assertGreaterEqual(premium_count, 1)
        self.assertGreaterEqual(service_pet_count, 1)
        self.assertGreaterEqual(non_service_pet_count, 0)

        hotel_url2 = self._api_host + '/api/v1/hotels?room_count=1&port=ORD&is_premium=true&service_pet=true'

        hotel_response2 = requests.get(hotel_url2, headers=headers)
        self.assertEqual(hotel_response2.status_code, 200)
        hotel_response_json2 = hotel_response2.json()
        self.assertIs(hotel_response_json2['error'], False)
        self.assertGreater(len(hotel_response_json2['data']), 0)

        for hotel in hotel_response_json2['data']:
            self.assertGreaterEqual(hotel['star_rating'], 4)
            self.assertEqual(hotel['service_pets_allowed'], True)
            self.assertGreaterEqual(hotel['available'], 1)
            self.assertEqual(hotel['airport_code'], 'ORD')

    def test_pax_app_hotel_search_service_pet_and_premium(self):
        """
        verifies system returns hotels for service_pet and premium for pax app for AA
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add premium inventory and service_pet inventory
        event_date = self._get_event_date('America/Chicago')
        self.add_hotel_availability(97051, 71, event_date, ap_block_type=1, block_price='150.00', blocks=5, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='ORD',
            ticket_level='first',
            pax_status='nonPremium',
            service_pet=False
        ))

        passenger_payload[1].update(dict(
            port_accommodation='ORD',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=2
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        index = 0
        previous_rating = 0
        for hotel in hotel_response_json['data']:
            if index == 0:
                self.assertGreaterEqual(hotel['star_rating'], 4)
            else:
                self.assertLessEqual(hotel['star_rating'], previous_rating)
            previous_rating = hotel['star_rating']
            self.assertEqual(hotel['service_pets_allowed'], True)
            self.assertGreaterEqual(hotel['available'], 2)
            self.assertEqual(hotel['airport_code'], 'ORD')
            index += 1

    def test_validate_hotel_search_number_of_nights(self):
        """
        ensures system is validating number_of_nights for hotel_search
        """
        expected_min_value_error_detail = [{'field': 'number_of_nights', 'message': 'Ensure this value is greater than or equal to 1.'}]
        expected_max_value_error_detail = [{'field': 'number_of_nights', 'message': 'Ensure this value is less than or equal to 7.'}]
        expected_nights_is_int_error_detail = [{'field': 'number_of_nights', 'message': 'A valid integer is required.'}]

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=LAX&number_of_nights='

        hotel_response = requests.get(hotel_url + str(0), headers=headers)  # validates min requirement
        self.assertEqual(hotel_response.status_code, 400)
        hotel_response_json = hotel_response.json()
        log_error_system_tests_output(pretty_print_json(hotel_response_json))
        self._validate_error_message(hotel_response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.', expected_min_value_error_detail)

        hotel_response = requests.get(hotel_url + str(101), headers=headers)  # validates max requirement
        self.assertEqual(hotel_response.status_code, 400)
        hotel_response_json = hotel_response.json()
        log_error_system_tests_output(pretty_print_json(hotel_response_json))
        self._validate_error_message(hotel_response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.', expected_max_value_error_detail)

        hotel_response = requests.get(hotel_url + 'aString', headers=headers)  # validates int requirement
        self.assertEqual(hotel_response.status_code, 400)
        hotel_response_json = hotel_response.json()
        log_error_system_tests_output(pretty_print_json(hotel_response_json))
        self._validate_error_message(hotel_response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.', expected_nights_is_int_error_detail)

    def test_hotel_search_number_of_nights_default_is_1(self):
        """
        verifies system is providing default value of 1
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=LAX'

        time_zone = pytz.timezone('America/Los_Angeles')
        today = datetime.datetime.now(time_zone)

        if today.hour < StormxConstants.BOOKING_PREVIOUS_DAY_INVENTORY_HOUR:
            initial_night_of_stay = today - datetime.timedelta(days=1)
        else:
            initial_night_of_stay = today

        proposed_check_in_date = initial_night_of_stay.strftime('%Y-%m-%d')
        proposed_check_out_date = (initial_night_of_stay + datetime.timedelta(1)).strftime('%Y-%m-%d')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['proposed_check_in_date'], proposed_check_in_date)
            self.assertEqual(hotel['proposed_check_out_date'], proposed_check_out_date)

    def test_multi_night_search_day1_10_rooms_day2_1_room(self):
        """
        validates an issue in the system where the following:
        day 1: airline_soft_block 10 rooms
        day 2: airline_soft_block 1 room
        search number of nights 2 for HNL and the BW hotel would not show up
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        # set up multi night inventory
        hotel_id_hnl = 'tvl-82180'  # Best Western HNL
        event_date_hnl = self._get_event_date('Pacific/Honolulu')
        event_date_hnl_day2 = event_date_hnl + datetime.timedelta(days=1)
        self.add_hotel_availability(hotel_id_hnl.split('-')[1], 294, event_date_hnl, ap_block_type=0,
                                    block_price='100.00', blocks=10, pay_type='0')
        self.add_hotel_availability(hotel_id_hnl.split('-')[1], 294, event_date_hnl_day2, ap_block_type=0,
                                    block_price='200.00', blocks=1, pay_type='0')

        # setup some variables
        room_count = 1
        number_of_nights = 2
        expected_check_in_date = event_date_hnl.strftime('%Y-%m-%d')
        expected_check_out_date = (event_date_hnl_day2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # validate hotel is in multi night search results
        hotel_search_resp = requests.get(url=hotels_url + '?port=HNL&room_count=' + str(room_count) + '&number_of_nights=' + str(number_of_nights), headers=headers).json()
        self.assertGreater(len(hotel_search_resp['data']), 0)
        hotel_ids = [hotel['hotel_id'] for hotel in hotel_search_resp['data']]
        self.assertIn(hotel_id_hnl, hotel_ids)

        for hotel in hotel_search_resp['data']:
            self.assertEqual(hotel['proposed_check_in_date'], expected_check_in_date)
            self.assertEqual(hotel['proposed_check_out_date'], expected_check_out_date)

    def _test_hotel_search_number_of_nights(self, port, number_of_nights):
        """
        verifies system is returning hotels for number_of_nights query string param
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=' + port + '&number_of_nights=' + str(number_of_nights)

        if port == 'LAX':
            region = 'America/Los_Angeles'
        elif port == 'JFK':
            region = 'America/New_York'
        else:
            self.assertTrue(False)

        time_zone = pytz.timezone(region)
        today = datetime.datetime.now(time_zone)

        if today.hour < StormxConstants.BOOKING_PREVIOUS_DAY_INVENTORY_HOUR:
            initial_night_of_stay = today - datetime.timedelta(days=1)
        else:
            initial_night_of_stay = today

        proposed_check_in_date = initial_night_of_stay.strftime('%Y-%m-%d')
        proposed_check_out_date = (initial_night_of_stay + datetime.timedelta(number_of_nights)).strftime('%Y-%m-%d')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['proposed_check_in_date'], proposed_check_in_date)
            self.assertEqual(hotel['proposed_check_out_date'], proposed_check_out_date)

    def test_hotel_search_number_of_nights(self):
        """
        tests hotel search number_of_nights for various number_of_nights and ports
        """
        hotel_id_lax = '98702'
        hotel_id_jfk = '85376'

        event_date_lax = self._get_event_date('America/Los_Angeles')
        event_date_jfk = self._get_event_date('America/New_York')
        event_date_lax_day2 = event_date_lax + datetime.timedelta(days=1)
        event_date_jfk_day2 = event_date_jfk + datetime.timedelta(days=1)

        self.add_hotel_availability(hotel_id_lax, 294, event_date_lax, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_lax, 294, event_date_lax_day2, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk, 294, event_date_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_jfk, 294, event_date_jfk_day2, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        nights = [1, 2]
        ports = ['LAX', 'JFK']
        for number_of_nights in nights:
            for port in ports:
                self._test_hotel_search_number_of_nights(port, number_of_nights)


    def test_hotel_search_pet(self):
        """
        verifies system returns hotels for pet searched
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # add inventory
        event_date = self._get_event_date('Pacific/Honolulu')
        self.add_hotel_availability(100303, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100304, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100306, 294, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')

        providers = ['', 'tvl', 'ean']
        for provider in providers:
            port = 'KOA'
            hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=' + port + '&pet=true'
            if len(provider) > 0:
                hotel_url += '&provider=' + provider

            hotel_response = requests.get(hotel_url, headers=headers)
            failure_message = 'provider=' + repr(provider) + ' failed for port ' + repr(port) + '.'
            self.assertEqual(hotel_response.status_code, 200, msg=failure_message)
            hotel_response_json = hotel_response.json()
            self.assertIs(hotel_response_json['error'], False, msg=failure_message)
            if provider == 'ean':
                self.assertEqual(len(hotel_response_json['data']), 0, msg=failure_message)  # TODO: remove when expedia pets is implemented.
            else:
                self.assertGreater(len(hotel_response_json['data']), 0, msg=failure_message)

            for hotel in hotel_response_json['data']:
                self.assertEqual(hotel['pets_allowed'], True, msg=failure_message)

    def test_pax_app_hotel_search_pet(self):
        """
        verifies system returns hotels for service_pet for pax app
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add inventory
        event_date = self._get_event_date('Pacific/Honolulu')
        self.add_hotel_availability(100303, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100304, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100306, 294, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            pet=False
        ))

        passenger_payload[1].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)

    def test_hotel_search_pet_and_service_pet(self):
        """
        verifies system returns hotels for pet searched and service_pet
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=LAX&pet=true&service_pet=true'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(98719, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)
            self.assertEqual(hotel['service_pets_allowed'], True)

    def test_pax_app_hotel_search_pet_and_service_pet(self):
        """
        verifies system returns hotels for service_pet for pax app
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(98719, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=False,
            service_pet=True
        ))

        passenger_payload[1].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True,
            service_pet=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=2
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)
            self.assertEqual(hotel['service_pets_allowed'], True)

    def test_hotel_search_pet_and_service_pet_and_premium(self):
        """
        verifies system returns hotels for pet searched and service_pet and premium
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=LAX&pet=true&service_pet=true&is_premium=true'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(98719, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)
            self.assertEqual(hotel['service_pets_allowed'], True)
            self.assertEqual(hotel['premium'], True)


    @unittest.skip('skipping until AA pet hack is removed')
    def test_pax_app_hotel_search_pet_and_service_pet_and_premium(self):
        """
        verifies system returns hotels for service_pet for pax app
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(80657, 71, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(98719, 71, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(3)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=False,
            service_pet=True
        ))

        passenger_payload[1].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True,
            service_pet=False
        ))

        passenger_payload[2].update(dict(
            port_accommodation='LAX',
            ticket_level='first',
            pax_status='premium',
            pet=False,
            service_pet=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=2
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel = hotel_response_json['data'][0]
        self.assertEqual(hotel['pets_allowed'], True)
        self.assertEqual(hotel['service_pets_allowed'], True)
        self.assertEqual(hotel['premium'], True)

    def test_hotel_search_variety(self):
        """
        verifies system returns hotels for variety searched
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=KOA'

        # add inventory
        event_date = self._get_event_date('Pacific/Honolulu')
        self.add_hotel_availability(100303, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100304, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100306, 294, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        pet_count = 0
        service_pet_count = 0
        neither_count = 0
        for hotel in hotel_response_json['data']:
            if hotel['pets_allowed']:
                pet_count += 1
            if hotel['service_pets_allowed']:
                service_pet_count += 1
            if not hotel['pets_allowed'] and not hotel['service_pets_allowed']:
                neither_count += 1
        self.assertEqual(pet_count, 1)
        self.assertGreaterEqual(service_pet_count, 1)
        self.assertEqual(neither_count, 0)

    def test_hotel_search_variety_pet_false(self):
        """
        verifies system returns hotels for variety searched with pet false
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=KOA&pet=false'

        # add inventory
        event_date = self._get_event_date('Pacific/Honolulu')
        self.add_hotel_availability(100303, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100304, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100306, 294, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        pet_count = 0
        service_pet_count = 0
        neither_count = 0
        for hotel in hotel_response_json['data']:
            if hotel['pets_allowed']:
                pet_count += 1
            if hotel['service_pets_allowed']:
                service_pet_count += 1
            if not hotel['pets_allowed'] and not hotel['service_pets_allowed']:
                neither_count += 1
        self.assertEqual(pet_count, 1)
        self.assertGreaterEqual(service_pet_count, 1)
        self.assertEqual(neither_count, 0)

    def test_pax_app_hotel_search_variety(self):
        """
        verifies system returns hotels for variety for pax app
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add inventory
        event_date = self._get_event_date('Pacific/Honolulu')
        self.add_hotel_availability(100303, 294, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100304, 294, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100306, 294, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium'
        ))

        passenger_payload[1].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium'
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        pet_count = 0
        service_pet_count = 0
        neither_count = 0
        for hotel in hotel_response_json['data']:
            if hotel['pets_allowed']:
                pet_count += 1
            if hotel['service_pets_allowed']:
                service_pet_count += 1
            if not hotel['pets_allowed'] and not hotel['service_pets_allowed']:
                neither_count += 1
        self.assertEqual(pet_count, 1)
        self.assertGreaterEqual(service_pet_count, 1)
        self.assertEqual(neither_count, 0)

    def test_pax_app_remove_premium_inventory(self):
        """
        validates REMOVE_PREMIUM_INVENTORY_FOR_NON_PREMIUM_PAX feature
        """
        port = 'PHL'
        premium_hotel = 'tvl-87544'
        non_premium_hotel = 'tvl-97092'
        hotel_url = self._api_host + '/api/v1/hotels'
        offer_hotel_url = self._api_host + '/api/v1/offer/hotels'
        event_date = self._get_event_date('America/Los_Angeles')

        # non premium passengers
        aa_customer = 'American Airlines'
        aa_headers = self._generate_airline_headers(aa_customer)
        aa_passengers = self._create_2_passengers(aa_customer, port_accommodation=port, pax_status='non-premium', ticket_level='economy')

        # premium passengers
        ba_customer = 'British Airways'
        ba_headers = self._generate_airline_headers(ba_customer)
        ba_passengers = self._create_2_passengers(ba_customer, port_accommodation=port, pax_status='GOLD')

        # query string parameters
        aa_query_parameters = dict(
            ak1=aa_passengers[0]['ak1'],
            ak2=aa_passengers[0]['ak2'],
            room_count=1
        )

        ba_query_parameters = dict(
            ak1=ba_passengers[0]['ak1'],
            ak2=ba_passengers[0]['ak2'],
            room_count=1
        )

        # validate no StormX inventory exists for LAS
        resp_json = requests.get(url=hotel_url + '?provider=tvl&room_count=1&port=' + port, headers=aa_headers).json()
        self.assertEqual(len(resp_json['data']), 0)

        # premium inventory
        self.add_hotel_availability(premium_hotel.split('-')[1], 0, event_date, ap_block_type=0, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(premium_hotel.split('-')[1], 0, event_date, ap_block_type=0, block_price='150.00', blocks=2, pay_type='0')

        # public non premium hotel query
        # only premium inventory exists so premium hotel should display
        resp_json = requests.get(url=offer_hotel_url, params=aa_query_parameters).json()
        self.assertGreater(len(resp_json['data']), 0)
        hotel_ids = [hotel['hotel_id'] for hotel in resp_json['data']]
        self.assertIn(premium_hotel, hotel_ids)
        self.assertNotIn(non_premium_hotel, hotel_ids)

        # public premium hotel query
        # only premium inventory exists so premium hotel should display
        resp_json = requests.get(url=offer_hotel_url, params=ba_query_parameters).json()
        self.assertGreater(len(resp_json['data']), 0)
        hotel_ids = [hotel['hotel_id'] for hotel in resp_json['data']]
        self.assertIn(premium_hotel, hotel_ids)
        self.assertNotIn(non_premium_hotel, hotel_ids)

        # non premium inventory
        self.add_hotel_availability(non_premium_hotel.split('-')[1], 0, event_date, ap_block_type=0, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(non_premium_hotel.split('-')[1], 0, event_date, ap_block_type=0, block_price='150.00', blocks=2, pay_type='0')

        # public non premium hotel query
        # premium and non premium inventory exists so non premium hotel should display only
        resp_json = requests.get(url=offer_hotel_url, params=aa_query_parameters).json()
        self.assertGreater(len(resp_json['data']), 0)
        hotel_ids = [hotel['hotel_id'] for hotel in resp_json['data']]
        self.assertNotIn(premium_hotel, hotel_ids)
        self.assertIn(non_premium_hotel, hotel_ids)

        # public premium hotel query
        # premium and non premium inventory exists so premium and non premium hotel should display
        resp_json = requests.get(url=offer_hotel_url, params=ba_query_parameters).json()
        self.assertGreater(len(resp_json['data']), 0)
        hotel_ids = [hotel['hotel_id'] for hotel in resp_json['data']]
        self.assertIn(premium_hotel, hotel_ids)
        self.assertIn(non_premium_hotel, hotel_ids)

        # use non premium hotel inventory
        payload = dict(
            context_ids=[passenger['context_id'] for passenger in aa_passengers],
            hotel_id=non_premium_hotel,
            room_count=4
        )
        resp = requests.post(url=hotel_url, headers=aa_headers, data=payload)
        self.assertEqual(resp.status_code, 200)

        # use premium hotel inventory
        payload = dict(
            context_ids=[passenger['context_id'] for passenger in ba_passengers],
            hotel_id=premium_hotel,
            room_count=4
        )
        resp = requests.post(url=hotel_url, headers=ba_headers, data=payload)
        self.assertEqual(resp.status_code, 200)



    def test_invalid_port_on_hotel_search(self):
        """
        verifies system can handle invalid ports during hotel search and provide error message
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url1 = self._api_host + '/api/v1/hotels?room_count=1&port=XXX'
        hotel_url2 = self._api_host + '/api/v1/hotels?room_count=1&port=011'
        hotel_url3 = self._api_host + '/api/v1/hotels?room_count=1&port=0YU'
        hotel_url4 = self._api_host + '/api/v1/hotels?room_count=1&port=0YUa'
        hotel_url5 = self._api_host + '/api/v1/hotels?room_count=1&port=0Y'

        response = requests.get(hotel_url1, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PORT', 'XXX is not a valid choice for port', [])

        response = requests.get(hotel_url2, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PORT', '011 is not a valid choice for port', [])

        response = requests.get(hotel_url3, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PORT', '0YU is not a valid choice for port', [])

        response = requests.get(hotel_url4, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel search.',
                                     [{'field': 'port', 'message': 'Ensure this field has no more than 3 characters.'}])

        response = requests.get(hotel_url5, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for hotel search.',
                                     [{'field': 'port', 'message': 'Ensure this field has at least 3 characters.'}])

    def _test_hotel_availability_sorted(self, hotel_availability, number_of_hotels, is_premium=False, all_premium=False):
        """
        hotel_availability: hotel JSON
        number_of_rooms: int
        is_premium: bool default False
        all_premium: bool default False
        utility for testing hotel availability sorting
        """
        index = 0
        for hotel in hotel_availability:
            if all_premium:
                self.assertTrue(hotel['premium'])

            if index == 0:
                previous_is_premium = hotel['premium']
                previous_hard_block_count = hotel['hard_block_count']
                previous_has_shuttle = hotel['shuttle']
                previous_rate = Decimal(hotel['rate'])
                previous_distance = hotel['distance']
            else:
                if is_premium:
                    if hotel['premium'] == previous_is_premium:
                        if hotel['hard_block_count'] == previous_hard_block_count:
                            if hotel['shuttle'] == previous_has_shuttle:
                                if Decimal(hotel['rate']) == previous_rate:
                                    if hotel['distance'] == previous_distance:
                                        pass
                                    else:
                                        self.assertGreater(hotel['distance'], previous_distance)
                                else:
                                    self.assertGreater(Decimal(hotel['rate']), previous_rate)
                            else:
                                if previous_has_shuttle:
                                    self.assertFalse(hotel['shuttle'])
                                else:
                                    self.assertTrue(hotel['shuttle'])
                        else:
                            self.assertLess(hotel['hard_block_count'], previous_hard_block_count)
                    else:
                        if previous_is_premium:
                            self.assertFalse(hotel['premium'])
                        else:
                            self.assertTrue(hotel['premium'])
                else:
                    if hotel['hard_block_count'] == previous_hard_block_count:
                        if hotel['shuttle'] == previous_has_shuttle:
                            if Decimal(hotel['rate']) == previous_rate:
                                if hotel['distance'] == previous_distance:
                                    pass
                                else:
                                    self.assertGreater(hotel['distance'], previous_distance)
                            else:
                                self.assertGreater(Decimal(hotel['rate']), previous_rate)
                        else:
                            if previous_has_shuttle:
                                self.assertFalse(hotel['shuttle'])
                            else:
                                self.assertTrue(hotel['shuttle'])
                    else:
                        self.assertLess(hotel['hard_block_count'], previous_hard_block_count)

                previous_is_premium = hotel['premium']
                previous_hard_block_count = hotel['hard_block_count']
                previous_has_shuttle = hotel['shuttle']
                previous_rate = Decimal(hotel['rate'])
                previous_distance = hotel['distance']

            index += 1

        if number_of_hotels:
            self.assertLessEqual(len(hotel_availability), number_of_hotels)

    def _get_hotel_range(self, hotel_distance, hotel_rate):
        """
        :param hotel_distance: Decimal
        :param hotel_rate: Decimal
        :return: int
        """
        DECIMAL_3 = Decimal('3.00')
        DECIMAL_6 = Decimal('6.00')
        DECIMAL_10 = Decimal('10.00')
        DECIMAL_99 = Decimal('99.00')
        DECIMAL_125 = Decimal('125.00')
        DECIMAL_150 = Decimal('150.00')

        if hotel_distance <= DECIMAL_3 and hotel_rate < DECIMAL_99:
            hotel_range = 0
        elif hotel_distance > DECIMAL_3 and hotel_distance <= DECIMAL_6 and hotel_rate < DECIMAL_99:
            hotel_range = 1
        elif hotel_distance > DECIMAL_6 and hotel_distance <= DECIMAL_10 and hotel_rate < DECIMAL_99:
            hotel_range = 2
        elif hotel_distance <= DECIMAL_3 and hotel_rate >= DECIMAL_99 and hotel_rate < DECIMAL_125:
            hotel_range = 3
        elif hotel_distance > DECIMAL_3 and hotel_distance <= DECIMAL_6 and hotel_rate >= DECIMAL_99 and hotel_rate < DECIMAL_125:
            hotel_range = 4
        elif hotel_distance > DECIMAL_6 and hotel_distance <= DECIMAL_10 and hotel_rate >= DECIMAL_99 and hotel_rate < DECIMAL_125:
            hotel_range = 5
        elif hotel_distance <= DECIMAL_3 and hotel_rate >= DECIMAL_125 and hotel_rate <= DECIMAL_150:
            hotel_range = 6
        elif hotel_distance > DECIMAL_3 and hotel_distance <= DECIMAL_6 and hotel_rate >= DECIMAL_125 and hotel_rate <= DECIMAL_150:
            hotel_range = 7
        elif hotel_distance > DECIMAL_6 and hotel_distance <= DECIMAL_10 and hotel_rate >= DECIMAL_125 and hotel_rate <= DECIMAL_150:
            hotel_range = 8
        else:
            hotel_range = 9

        return hotel_range

    def _test_expedia_hotel_availability_sorted(self, hotel_availability, number_of_hotels, airline_id,
                                                is_premium=False, all_premium=False):
        """
        hotel_availability: hotel JSON
        number_of_rooms: int
        airline: int
        is_premium: bool default False
        all_premium: bool default False
        utility for testing hotel availability sorting for expedia
        """
        index = 0
        for hotel in hotel_availability:
            if airline_id == 347:
                self.assertGreaterEqual(hotel['star_rating'], 4)
                if index == 0:
                    previous_distance = Decimal(hotel['distance'])
                else:
                    distance = Decimal(hotel['distance'])
                    self.assertGreaterEqual(distance, previous_distance)
                    previous_distance = Decimal(hotel['distance'])
                index += 1
            else:
                self.assertGreaterEqual(hotel['star_rating'], 3)

                if all_premium:
                    self.assertTrue(hotel['premium'])

                if index == 0:
                    previous_is_premium = hotel['premium']
                    previous_distance = Decimal(hotel['distance'])
                    previous_hotel_range = self._get_hotel_range(previous_distance, Decimal(hotel['rate']))
                else:
                    distance = Decimal(hotel['distance'])
                    rate = Decimal(hotel['rate'])
                    hotel_range = self._get_hotel_range(distance, rate)

                    # premium sort order logic validation
                    if is_premium:
                        if hotel['premium'] == previous_is_premium:
                            # hotel_range should always be greater or equal
                            self.assertGreaterEqual(hotel_range, previous_hotel_range)
                        else:
                            if previous_is_premium:
                                self.assertFalse(hotel['premium'])
                            else:
                                self.assertTrue(hotel['premium'])

                        # if in last range should always be sorted by distance
                        if previous_hotel_range == 9 and hotel_range == 9:
                            self.assertGreaterEqual(distance, previous_distance)

                    else:
                        # hotel_range should always be greater or equal
                        self.assertGreaterEqual(hotel_range, previous_hotel_range)

                        # if in last range should always be sorted by distance
                        if previous_hotel_range == 9:
                            self.assertGreaterEqual(distance, previous_distance)

                    previous_is_premium = hotel['premium']
                    previous_distance = Decimal(hotel['distance'])
                    previous_hotel_range = self._get_hotel_range(Decimal(hotel['distance']), Decimal(hotel['rate']))

                index += 1

        self.assertLessEqual(len(hotel_availability), number_of_hotels)

    def test_public_hotels_sorted_random(self):
        """
        test public hotel availability sorting with random inventory
        """
        purple_rain_customer = 'Purple Rain Airlines'
        american_customer = 'American Airlines'
        aa_num_of_hotels = 3
        default_num_of_hotels = 10

        ports = ['PHX', 'DFW', 'DCA']
        for port in ports:
            aa_pax = self._create_2_passengers(customer=american_customer, port_accommodation=port, ticket_level='economy', pax_status='custom')
            pr_pax = self._create_2_passengers(customer=purple_rain_customer, port_accommodation=port, ticket_level='economy', pax_status='custom')

            aa_pax_availability = self._get_passenger_hotel_offerings(aa_pax[0])
            aa_availability = self._airline_get_passenger_hotel_offerings(american_customer, port, 1)
            for pax_hotel in aa_pax_availability:
                for hotel in aa_availability:
                    if pax_hotel['hotel_id'] == hotel['hotel_id']:
                        if 'rate' not in pax_hotel:
                            pax_hotel['rate'] = hotel['rate']

            pr_pax_availability = self._get_passenger_hotel_offerings(pr_pax[0])
            pr_availability = self._airline_get_passenger_hotel_offerings(purple_rain_customer, port, 1)
            for pax_hotel in pr_pax_availability:
                for hotel in pr_availability:
                    if pax_hotel['hotel_id'] == hotel['hotel_id']:
                        if 'rate' not in pax_hotel:
                            pax_hotel['rate'] = hotel['rate']

            self._test_hotel_availability_sorted(aa_pax_availability, aa_num_of_hotels)
            self._test_hotel_availability_sorted(pr_pax_availability, default_num_of_hotels)
            self._test_hotel_availability_sorted(aa_availability, None)
            self._test_hotel_availability_sorted(pr_availability, None)

    def _add_premium_inventory(self, airline_id):
        """
        adds premium inventory for system tests needing it
        param airline_id: int
        """
        today_phx = self._get_event_date('America/Phoenix')
        today_dfw = self._get_event_date('America/Chicago')
        today_dca = self._get_event_date('America/New_York')
        today_lax = self._get_event_date('America/Los_Angeles')
        today_jfk = self._get_event_date('America/New_York')

        # PHX
        self.add_hotel_availability(87532, airline_id, today_phx, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(95417, airline_id, today_phx, ap_block_type=1, block_price='105.99', blocks=3, pay_type='0')

        # DFW
        self.add_hotel_availability(81527, airline_id, today_dfw, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(96533, airline_id, today_dfw, ap_block_type=1, block_price='105.99', blocks=3, pay_type='0')

        # DCA
        self.add_hotel_availability(96121, airline_id, today_dca, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(96118, airline_id, today_dca, ap_block_type=1, block_price='105.99', blocks=3, pay_type='0')

        # LAX
        self.add_hotel_availability(98695, airline_id, today_lax, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(98689, airline_id, today_lax, ap_block_type=1, block_price='105.99', blocks=3, pay_type='0')

        # JFK
        self.add_hotel_availability(98964, airline_id, today_jfk, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(85431, airline_id, today_jfk, ap_block_type=1, block_price='105.99', blocks=3, pay_type='0')

    def test_aa_hotels_sorted_premium__tvl_inventory(self):
        """
        test public hotel availability sorting with random inventory for premium pax
        """
        american_customer = 'American Airlines'
        aa_num_of_hotels = 3
        headers = self._generate_airline_headers(american_customer)
        self._add_premium_inventory(71)

        ports = ['PHX', 'DFW', 'DCA', 'LAX', 'JFK']
        for port in ports:
            aa_pax = self._create_2_passengers(customer=american_customer, port_accommodation=port, ticket_level='first')

            aa_pax_availability = self._get_passenger_hotel_offerings(aa_pax[0])
            aa_availability = self._airline_get_passenger_hotel_offerings(american_customer, port, 1)
            for pax_hotel in aa_pax_availability:
                for hotel in aa_availability:
                    if pax_hotel['hotel_id'] == hotel['hotel_id']:
                        if 'rate' not in pax_hotel:
                            pax_hotel['rate'] = hotel['rate']

            premium_hotels = requests.get(url=self._api_host + '/api/v1/hotels?provider=tvl&port=' + port + '&room_count=1&is_premium=true', headers=headers).json()['data']
            self.assertGreater(len(premium_hotels), 0)
            self.assertTrue(premium_hotels[0]['premium'])

            self._test_hotel_availability_sorted(aa_pax_availability, aa_num_of_hotels, is_premium=True)
            self._test_hotel_availability_sorted(aa_availability, None)
            self._test_hotel_availability_sorted(premium_hotels, None, is_premium=True)

    def test_purple_rain_hotels_sorted_premium(self):
        """
        test public hotel availability sorting with random inventory for premium pax
        """
        customer = 'Purple Rain Airlines'
        num_of_hotels = 10
        headers = self._generate_airline_headers(customer)
        self._add_premium_inventory(294)

        ports = ['PHX', 'DFW', 'DCA', 'LAX', 'JFK']
        for port in ports:
            pax = self._create_2_passengers(customer=customer, port_accommodation=port, ticket_level='first')

            pax_availability = self._get_passenger_hotel_offerings(pax[0])
            availability = self._airline_get_passenger_hotel_offerings(customer, port, 1)
            for pax_hotel in pax_availability:
                for hotel in availability:
                    if pax_hotel['hotel_id'] == hotel['hotel_id']:
                        if 'rate' not in pax_hotel:
                            pax_hotel['rate'] = hotel['rate']

            premium_hotels = requests.get(url=self._api_host + '/api/v1/hotels?port=' + port + '&room_count=1&is_premium=true', headers=headers).json()['data']
            self.assertGreater(len(premium_hotels), 0)

            self._test_hotel_availability_sorted(pax_availability, num_of_hotels)
            self._test_hotel_availability_sorted(availability, None)
            self._test_hotel_availability_sorted(premium_hotels, None, is_premium=True, all_premium=True)

    def _setup_public_hotels_sorted_controlled_inventory(self):
        """
        add inventory for the public_hotels_sorted_controlled test
        """
        today = self._get_event_date('America/New_York')

        # AA ACY
        self.add_hotel_availability(99589, 71, today, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(99590, 71, today, ap_block_type=2, block_price='160.00', blocks=15, pay_type='0')
        self.add_hotel_availability(99591, 71, today, ap_block_type=1, block_price='161.99', blocks=25, pay_type='0')
        self.add_hotel_availability(99592, 71, today, ap_block_type=1, block_price='121.99', blocks=56, pay_type='0')
        self.add_hotel_availability(99593, 71, today, ap_block_type=2, block_price='160.00', blocks=15, pay_type='0')
        self.add_hotel_availability(101089, 71, today, ap_block_type=1, block_price='161.99', blocks=5, pay_type='0')
        self.add_hotel_availability(101090, 71, today, ap_block_type=2, block_price='121.99', blocks=50, pay_type='0')

        # PR ACY
        self.add_hotel_availability(99589, 294, today, ap_block_type=1, block_price='149.99', blocks=5, pay_type='0')
        self.add_hotel_availability(99590, 294, today, ap_block_type=1, block_price='130.00', blocks=5, pay_type='0')
        self.add_hotel_availability(99591, 294, today, ap_block_type=1, block_price='121.99', blocks=6, pay_type='0')
        self.add_hotel_availability(99592, 294, today, ap_block_type=1, block_price='150.99', blocks=7, pay_type='0')
        self.add_hotel_availability(99593, 294, today, ap_block_type=1, block_price='122.00', blocks=8, pay_type='0')
        self.add_hotel_availability(101089, 294, today, ap_block_type=1, block_price='121.99', blocks=5, pay_type='0')
        self.add_hotel_availability(101090, 294, today, ap_block_type=2, block_price='121.99', blocks=1, pay_type='0')

        # AA EWR
        self.add_hotel_availability(85441, 71, today, ap_block_type=2, block_price='100.99', blocks=1, pay_type='0')
        self.add_hotel_availability(97325, 71, today, ap_block_type=2, block_price='160.00', blocks=5, pay_type='0')
        self.add_hotel_availability(97223, 71, today, ap_block_type=2, block_price='161.99', blocks=2, pay_type='0')
        self.add_hotel_availability(97228, 71, today, ap_block_type=1, block_price='121.99', blocks=5, pay_type='0')
        self.add_hotel_availability(85440, 71, today, ap_block_type=1, block_price='160.00', blocks=51, pay_type='0')
        self.add_hotel_availability(85460, 71, today, ap_block_type=1, block_price='100.99', blocks=15, pay_type='0')
        self.add_hotel_availability(97236, 71, today, ap_block_type=1, block_price='160.00', blocks=56, pay_type='0')
        self.add_hotel_availability(97237, 71, today, ap_block_type=1, block_price='161.99', blocks=45, pay_type='0')
        self.add_hotel_availability(103221, 71, today, ap_block_type=1, block_price='121.99', blocks=54, pay_type='0')
        self.add_hotel_availability(97242, 71, today, ap_block_type=1, block_price='160.00', blocks=45, pay_type='0')
        self.add_hotel_availability(85471, 71, today, ap_block_type=1, block_price='121.99', blocks=5, pay_type='0')
        self.add_hotel_availability(85473, 71, today, ap_block_type=0, block_price='160.00', blocks=5, pay_type='0')

        # PR EWR
        self.add_hotel_availability(85441, 294, today, ap_block_type=2, block_price='100.99', blocks=55, pay_type='0')
        self.add_hotel_availability(97325, 294, today, ap_block_type=2, block_price='160.00', blocks=54, pay_type='0')
        self.add_hotel_availability(97223, 294, today, ap_block_type=2, block_price='161.99', blocks=54, pay_type='0')
        self.add_hotel_availability(97228, 294, today, ap_block_type=1, block_price='121.99', blocks=53, pay_type='0')
        self.add_hotel_availability(85440, 294, today, ap_block_type=1, block_price='160.00', blocks=35, pay_type='0')
        self.add_hotel_availability(85460, 294, today, ap_block_type=1, block_price='100.99', blocks=35, pay_type='0')
        self.add_hotel_availability(97236, 294, today, ap_block_type=2, block_price='160.00', blocks=5, pay_type='0')
        self.add_hotel_availability(97237, 294, today, ap_block_type=1, block_price='161.99', blocks=5, pay_type='0')
        self.add_hotel_availability(103221, 294, today, ap_block_type=1, block_price='121.99', blocks=57, pay_type='0')
        self.add_hotel_availability(97242, 294, today, ap_block_type=1, block_price='160.00', blocks=75, pay_type='0')
        self.add_hotel_availability(85471, 294, today, ap_block_type=1, block_price='121.99', blocks=5, pay_type='0')
        self.add_hotel_availability(85473, 294, today, ap_block_type=2, block_price='160.00', blocks=51, pay_type='0')

    def test_public_hotels_sorted_controlled(self):
        """
        test public hotel availability sorting with controlled inventory
        """
        purple_rain_customer = 'Purple Rain Airlines'
        american_customer = 'American Airlines'
        aa_num_of_hotels = 3
        default_num_of_hotels = 10

        self._setup_public_hotels_sorted_controlled_inventory()

        ports = ['ACY', 'EWR']
        for port in ports:
            aa_pax = self._create_2_passengers(customer=american_customer, port_accommodation=port, ticket_level='economy', pax_status='custom')
            pr_pax = self._create_2_passengers(customer=purple_rain_customer, port_accommodation=port, ticket_level='economy', pax_status='custom')

            aa_pax_availability = self._get_passenger_hotel_offerings(aa_pax[0])
            aa_availability = self._airline_get_passenger_hotel_offerings(american_customer, port, 1)
            for pax_hotel in aa_pax_availability:
                for hotel in aa_availability:
                    if pax_hotel['hotel_id'] == hotel['hotel_id']:
                        if 'rate' not in pax_hotel:
                            pax_hotel['rate'] = hotel['rate']

            pr_pax_availability = self._get_passenger_hotel_offerings(pr_pax[0])
            pr_availability = self._airline_get_passenger_hotel_offerings(purple_rain_customer, port, 1)
            for pax_hotel in pr_pax_availability:
                for hotel in pr_availability:
                    if pax_hotel['hotel_id'] == hotel['hotel_id']:
                        if 'rate' not in pax_hotel:
                            pax_hotel['rate'] = hotel['rate']

            self._test_hotel_availability_sorted(aa_pax_availability, aa_num_of_hotels)
            self._test_hotel_availability_sorted(pr_pax_availability, default_num_of_hotels)
            self._test_hotel_availability_sorted(aa_availability, None)
            self._test_hotel_availability_sorted(pr_availability, None)

    def test_validate_non_airline_specific_inventory_different_hotels(self):
        """
        system test validating that inventory only gets returned
        if its assigned to the airline that is making the request
        or if its assigned to no airline at all for different hotels
        """
        hotel_url = self._api_host + '/api/v1/hotels'
        event_date = self._get_event_date('America/Los_Angeles')
        purple_rain_headers = self._generate_airline_headers('Purple Rain Airlines')
        aa_headers = self._generate_airline_headers('American Airlines')
        delta_headers = self._generate_airline_headers('Delta Air Lines')

        hotel_id_pr = 'tvl-96373'  # LAS rooms will be tied to Purple Rain
        hotel_id_aa = 'tvl-96399'  # LAS rooms will be tied to AA
        hotel_id_all = 'tvl-100508'  # LAS rooms will be tied to no airline

        self.add_hotel_availability(96373, 294, event_date, ap_block_type=1, block_price='149.99', blocks=1,
                                    pay_type='0')
        self.add_hotel_availability(96399, 71, event_date, ap_block_type=2, block_price='129.99', blocks=1,
                                    pay_type='0')
        self.add_hotel_availability(100508, 0, event_date, ap_block_type=0, block_price='109.99', blocks=1,
                                    pay_type='0')

        purple_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=1', headers=purple_rain_headers)
        self.assertEqual(purple_hotels_resp.status_code, 200)
        purple_hotels = purple_hotels_resp.json()['data']
        self.assertEqual(len(purple_hotels), 2)

        has_hotel_id_pr = False
        has_hotel_id_all = False
        for hotel in purple_hotels:
            if hotel['hotel_id'] == hotel_id_pr:
                pr_hotel = hotel
                self.assertEqual(hotel['rate'], '149.99')
                self.assertEqual(hotel['available'], 1)
                self.assertEqual(hotel['hard_block_count'], 1)
                has_hotel_id_pr = True
            if hotel['hotel_id'] == hotel_id_all:
                self.assertEqual(hotel['rate'], '109.99')
                self.assertEqual(hotel['available'], 1)
                self.assertEqual(hotel['hard_block_count'], 0)
                has_hotel_id_all = True
        self.assertTrue(has_hotel_id_pr)
        self.assertTrue(has_hotel_id_all)

        aa_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=1', headers=aa_headers)
        self.assertEqual(aa_hotels_resp.status_code, 200)
        aa_hotels = aa_hotels_resp.json()['data']
        self.assertEqual(len(aa_hotels), 2)

        has_hotel_id_aa = False
        has_hotel_id_all = False
        for hotel in aa_hotels:
            if hotel['hotel_id'] == hotel_id_aa:
                aa_hotel = hotel
                self.assertEqual(hotel['rate'], '129.99')
                self.assertEqual(hotel['available'], 1)
                self.assertEqual(hotel['hard_block_count'], 1)
                has_hotel_id_aa = True
            if hotel['hotel_id'] == hotel_id_all:
                self.assertEqual(hotel['rate'], '109.99')
                self.assertEqual(hotel['available'], 1)
                self.assertEqual(hotel['hard_block_count'], 0)
                has_hotel_id_all = True
        self.assertTrue(has_hotel_id_aa)
        self.assertTrue(has_hotel_id_all)

        delta_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=1', headers=delta_headers)
        self.assertEqual(delta_hotels_resp.status_code, 200)
        delta_hotels = delta_hotels_resp.json()['data']
        self.assertEqual(len(delta_hotels), 1)
        self.assertEqual(delta_hotels[0]['hotel_id'], hotel_id_all)
        self.assertEqual(delta_hotels[0]['rate'], '109.99')
        self.assertEqual(delta_hotels[0]['available'], 1)
        self.assertEqual(delta_hotels[0]['hard_block_count'], 0)
        delta_hotel = delta_hotels[0]

        pr_pax = self._create_2_passengers(customer='Purple Rain Airlines', port_accommodation='LAS')[0]
        aa_pax = self._create_2_passengers(customer='American Airlines', port_accommodation='LAS')[0]
        delta_pax = self._create_2_passengers(customer='Delta Air Lines', port_accommodation='LAS')[0]

        pr_booking_payload = {
            'hotel_id': hotel_id_aa,
            'room_count': 1,
            'context_ids': [pr_pax['context_id']]
        }

        pr_bad_book = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(pr_bad_book.status_code, 400)
        pr_bad_book_json = pr_bad_book.json()
        self._validate_error_message(pr_bad_book_json, 400, 'Bad Request', 'INSUFFICIENT_INVENTORY',
                                     'Not enough inventory found for La Quinta Inn & Suites - LAS Airport South', [])

        aa_booking_payload = {
            'hotel_id': hotel_id_pr,
            'room_count': 1,
            'context_ids': [aa_pax['context_id']]
        }

        aa_bad_book = requests.post(url=hotel_url, json=aa_booking_payload, headers=aa_headers)
        self.assertEqual(aa_bad_book.status_code, 400)
        aa_bad_book_json = aa_bad_book.json()
        self._validate_error_message(aa_bad_book_json, 400, 'Bad Request', 'INSUFFICIENT_INVENTORY',
                                     'Not enough inventory found for Doubletree Club - LAS Airport', [])

        delta_booking_payload = {
            'hotel_id': hotel_id_aa,
            'room_count': 1,
            'context_ids': [delta_pax['context_id']]
        }

        delta_bad_book = requests.post(url=hotel_url, json=delta_booking_payload, headers=delta_headers)
        self.assertEqual(delta_bad_book.status_code, 400)
        delta_bad_book_json = delta_bad_book.json()
        self._validate_error_message(delta_bad_book_json, 400, 'Bad Request', 'INSUFFICIENT_INVENTORY',
                                     'Not enough inventory found for La Quinta Inn & Suites - LAS Airport South', [])

        self._airline_book_hotel('Purple Rain Airlines', pr_hotel, [pr_pax['context_id']],
                                 1)  # helper method does success validation
        self._airline_book_hotel('American Airlines', aa_hotel, [aa_pax['context_id']],
                                 1)  # helper method does success validation
        self._airline_book_hotel('Delta Air Lines', delta_hotel, [delta_pax['context_id']],
                                 1)  # helper method does success validation

    def test_validate_non_airline_specific_inventory_same_hotel(self):
        """
        system test validating that inventory only gets returned
        if its assigned to the airline that is making the request
        or if its assigned to no airline at all for same hotels
        """
        hotel_url = self._api_host + '/api/v1/hotels'
        event_date = self._get_event_date('America/Los_Angeles')
        purple_rain_headers = self._generate_airline_headers('Purple Rain Airlines')
        aa_headers = self._generate_airline_headers('American Airlines')
        delta_headers = self._generate_airline_headers('Delta Air Lines')

        hotel_id_all = 'tvl-96373'  # LAS rooms will be tied to PR, AA, and no airline

        self.add_hotel_availability(96373, 294, event_date, ap_block_type=1, block_price='150.00', blocks=1,
                                    pay_type='0')
        self.add_hotel_availability(96373, 71, event_date, ap_block_type=2, block_price='100.00', blocks=2,
                                    pay_type='0')
        self.add_hotel_availability(96373, 0, event_date, ap_block_type=0, block_price='50.00', blocks=3, pay_type='0')

        # ensure hard block rate returned
        purple_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=1', headers=purple_rain_headers)
        self.assertEqual(purple_hotels_resp.status_code, 200)
        purple_hotels = purple_hotels_resp.json()['data']
        self.assertEqual(len(purple_hotels), 1)
        self.assertEqual(purple_hotels[0]['hotel_id'], hotel_id_all)
        self.assertEqual(purple_hotels[0]['rate'], '150.00')
        self.assertEqual(purple_hotels[0]['available'], 4)
        self.assertEqual(purple_hotels[0]['hard_block_count'], 1)

        # ensure avg rate is returned
        purple_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=2', headers=purple_rain_headers)
        self.assertEqual(purple_hotels_resp.status_code, 200)
        purple_hotels = purple_hotels_resp.json()['data']
        self.assertEqual(len(purple_hotels), 1)
        self.assertEqual(purple_hotels[0]['hotel_id'], hotel_id_all)
        self.assertEqual(purple_hotels[0]['rate'], '100.00')
        self.assertEqual(purple_hotels[0]['available'], 4)
        self.assertEqual(purple_hotels[0]['hard_block_count'], 1)
        pr_hotel = purple_hotels[0]

        # ensure hard block rate is returned
        aa_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=2', headers=aa_headers)
        self.assertEqual(aa_hotels_resp.status_code, 200)
        aa_hotels = aa_hotels_resp.json()['data']
        self.assertEqual(len(aa_hotels), 1)
        self.assertEqual(aa_hotels[0]['hotel_id'], hotel_id_all)
        self.assertEqual(aa_hotels[0]['rate'], '100.00')
        self.assertEqual(aa_hotels[0]['available'], 5)
        self.assertEqual(aa_hotels[0]['hard_block_count'], 2)

        # ensure avg rate is returned
        aa_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=3', headers=aa_headers)
        self.assertEqual(aa_hotels_resp.status_code, 200)
        aa_hotels = aa_hotels_resp.json()['data']
        self.assertEqual(len(aa_hotels), 1)
        self.assertEqual(aa_hotels[0]['hotel_id'], hotel_id_all)
        self.assertEqual(aa_hotels[0]['rate'], '83.33')
        self.assertEqual(aa_hotels[0]['available'], 5)
        self.assertEqual(aa_hotels[0]['hard_block_count'], 2)
        aa_hotel = aa_hotels[0]

        # ensure soft block rate is returned
        delta_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=1', headers=delta_headers)
        self.assertEqual(delta_hotels_resp.status_code, 200)
        delta_hotels = delta_hotels_resp.json()['data']
        self.assertEqual(len(delta_hotels), 1)
        self.assertEqual(delta_hotels[0]['hotel_id'], hotel_id_all)
        self.assertEqual(delta_hotels[0]['rate'], '50.00')
        self.assertEqual(delta_hotels[0]['available'], 3)
        self.assertEqual(delta_hotels[0]['hard_block_count'], 0)
        delta_hotel = delta_hotels[0]

        pr_pax = self._create_2_passengers(customer='Purple Rain Airlines', port_accommodation='LAS')[0]
        aa_pax = self._create_2_passengers(customer='American Airlines', port_accommodation='LAS')[0]
        delta_pax = self._create_2_passengers(customer='Delta Air Lines', port_accommodation='LAS')[0]

        pr_booking_payload = {
            'hotel_id': hotel_id_all,
            'room_count': 5,
            'context_ids': [pr_pax['context_id']]
        }

        pr_bad_book = requests.post(url=hotel_url, json=pr_booking_payload, headers=purple_rain_headers)
        self.assertEqual(pr_bad_book.status_code, 400)
        pr_bad_book_json = pr_bad_book.json()
        self._validate_error_message(pr_bad_book_json, 400, 'Bad Request', 'INSUFFICIENT_INVENTORY',
                                     'No inventory found for Doubletree Club - LAS Airport', [])

        aa_booking_payload = {
            'hotel_id': hotel_id_all,
            'room_count': 6,
            'context_ids': [aa_pax['context_id']]
        }

        aa_bad_book = requests.post(url=hotel_url, json=aa_booking_payload, headers=aa_headers)
        self.assertEqual(aa_bad_book.status_code, 400)
        aa_bad_book_json = aa_bad_book.json()
        self._validate_error_message(aa_bad_book_json, 400, 'Bad Request', 'INSUFFICIENT_INVENTORY',
                                     'No inventory found for Doubletree Club - LAS Airport', [])

        delta_booking_payload = {
            'hotel_id': hotel_id_all,
            'room_count': 4,
            'context_ids': [delta_pax['context_id']]
        }

        delta_bad_book = requests.post(url=hotel_url, json=delta_booking_payload, headers=delta_headers)
        self.assertEqual(delta_bad_book.status_code, 400)
        delta_bad_book_json = delta_bad_book.json()
        self._validate_error_message(delta_bad_book_json, 400, 'Bad Request', 'INSUFFICIENT_INVENTORY',
                                     'No inventory found for Doubletree Club - LAS Airport', [])

        total_counter = Decimal('0.00')
        pr_hard_block_booked = False
        pr_soft_block_booked = False
        pr_booking = self._airline_book_hotel('Purple Rain Airlines', pr_hotel, [pr_pax['context_id']], 2)
        room_vouchers = pr_booking['hotel_voucher']['room_vouchers']
        self.assertEqual(len(room_vouchers), 2)
        for room_voucher in room_vouchers:
            if room_voucher['hard_block']:
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['rate'], Decimal('150.00'))
                pr_hard_block_booked = True
                total_counter += room_voucher['rate']
            else:
                self.assertEqual(room_voucher['hard_block'], False)
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['rate'], Decimal('50.00'))
                pr_soft_block_booked = True
                total_counter += Decimal(room_voucher['rate'])
        self.assertTrue(pr_hard_block_booked)
        self.assertTrue(pr_soft_block_booked)
        self.assertEqual(pr_booking['hotel_voucher']['hotel_id'], hotel_id_all)
        self.assertEqual(pr_booking['hotel_voucher']['rooms_booked'], 2)
        self.assertEqual(pr_booking['hotel_voucher']['total_amount'],
                         total_counter + pr_booking['hotel_voucher']['tax'])

        total_counter = Decimal('0.00')
        aa_hard_block_booked = False
        aa_soft_block_booked = False
        aa_booking = self._airline_book_hotel('American Airlines', aa_hotel, [aa_pax['context_id']], 3)
        room_vouchers = aa_booking['hotel_voucher']['room_vouchers']
        self.assertEqual(len(room_vouchers), 2)
        for room_voucher in room_vouchers:
            if room_voucher['hard_block']:
                self.assertEqual(room_voucher['count'], 2)
                self.assertEqual(room_voucher['rate'], Decimal('100.00'))
                aa_hard_block_booked = True
                total_counter += (Decimal(room_voucher['rate']) * room_voucher['count'])
            else:
                self.assertEqual(room_voucher['hard_block'], False)
                self.assertEqual(room_voucher['count'], 1)
                self.assertEqual(room_voucher['rate'], Decimal('50.00'))
                aa_soft_block_booked = True
                total_counter += Decimal(room_voucher['rate'])
        self.assertTrue(aa_hard_block_booked)
        self.assertTrue(aa_soft_block_booked)
        self.assertEqual(aa_booking['hotel_voucher']['hotel_id'], hotel_id_all)
        self.assertEqual(aa_booking['hotel_voucher']['rooms_booked'], 3)
        self.assertEqual(aa_booking['hotel_voucher']['total_amount'],
                         total_counter + Decimal(aa_booking['hotel_voucher']['tax']))

        # ensure soft block rate is returned and inventory has decremented
        delta_hotels_resp = requests.get(url=hotel_url + '?port=LAS&room_count=1', headers=delta_headers)
        self.assertEqual(delta_hotels_resp.status_code, 200)
        delta_hotels = delta_hotels_resp.json()['data']
        self.assertEqual(len(delta_hotels), 1)
        self.assertEqual(delta_hotels[0]['hotel_id'], hotel_id_all)
        self.assertEqual(delta_hotels[0]['rate'], '50.00')
        self.assertEqual(delta_hotels[0]['available'], 1)  # was 3 but should be 1 now
        self.assertEqual(delta_hotels[0]['hard_block_count'], 0)

        total_counter = Decimal('0.00')
        delta_booking = self._airline_book_hotel('Delta Air Lines', delta_hotel, [delta_pax['context_id']], 1)
        room_vouchers = delta_booking['hotel_voucher']['room_vouchers']
        self.assertEqual(len(room_vouchers), 1)
        self.assertEqual(room_vouchers[0]['hard_block'], False)
        self.assertEqual(room_vouchers[0]['count'], 1)
        self.assertEqual(room_vouchers[0]['rate'], Decimal('50.00'))
        total_counter += Decimal(room_vouchers[0]['rate'])
        self.assertEqual(delta_booking['hotel_voucher']['hotel_id'], hotel_id_all)
        self.assertEqual(delta_booking['hotel_voucher']['rooms_booked'], 1)
        self.assertEqual(delta_booking['hotel_voucher']['total_amount'],
                         total_counter + Decimal(delta_booking['hotel_voucher']['tax']))

    def test_validate_port_geg_saves_searches__tvl_inventory(self):
        """
        test validating that the port 'GEG' will allow a passenger save and a hotel search.
        this port was used by Dave to realize this was needed to be done in production.
        """
        passenger = self._create_2_passengers('Purple Rain Airlines', port_accommodation='GEG', port_origin='GEG')  # validation done on method call
        hotel_search = requests.get(url=self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=' + passenger[0]['port_accommodation'], headers=self._generate_airline_headers('Purple Rain Airlines'))
        self.assertEqual(hotel_search.status_code, 200)
        self.assertEqual(hotel_search.json()['data'], [])

    def test_airline_hotels_sorted(self):
        """
        test hotel availability sorting
        """
        purple_rain_customer = 'Purple Rain Airlines'
        today = self._get_event_date('America/New_York')

        # PR ACY
        self.add_hotel_availability(99589, 294, today, ap_block_type=1, block_price='149.99', blocks=15, pay_type='0')
        self.add_hotel_availability(99590, 0, today, ap_block_type=0, block_price='120.00', blocks=50, pay_type='0')
        self.add_hotel_availability(99591, 294, today, ap_block_type=1, block_price='121.99', blocks=54, pay_type='0')
        self.add_hotel_availability(99592, 0, today, ap_block_type=0, block_price='150.99', blocks=45, pay_type='0')
        self.add_hotel_availability(99593, 294, today, ap_block_type=0, block_price='120.00', blocks=5, pay_type='0')
        self.add_hotel_availability(101089, 294, today, ap_block_type=0, block_price='121.99', blocks=54, pay_type='0')
        self.add_hotel_availability(101090, 294, today, ap_block_type=2, block_price='121.99', blocks=15, pay_type='0')

        # PR EWR
        self.add_hotel_availability(85441, 0, today, ap_block_type=0, block_price='100.99', blocks=6, pay_type='0')
        self.add_hotel_availability(97325, 0, today, ap_block_type=0, block_price='160.00', blocks=75, pay_type='0')
        self.add_hotel_availability(97223, 294, today, ap_block_type=0, block_price='161.99', blocks=55, pay_type='0')
        self.add_hotel_availability(97228, 294, today, ap_block_type=1, block_price='121.99', blocks=15, pay_type='0')
        self.add_hotel_availability(85440, 294, today, ap_block_type=0, block_price='160.00', blocks=58, pay_type='0')
        self.add_hotel_availability(85460, 294, today, ap_block_type=2, block_price='100.99', blocks=52, pay_type='0')

        ports = ['ACY', 'EWR']
        for port in ports:
            pr_availability = self._airline_get_passenger_hotel_offerings(purple_rain_customer, port, 1)
            self.assertGreater(len(pr_availability), 4)

            index = 0
            previous_count = 0
            for hotel in pr_availability:
                if index == 0:
                    previous_count = hotel['hard_block_count']
                else:
                    self.assertLessEqual(hotel['hard_block_count'], previous_count)
                    previous_count = hotel['hard_block_count']
                index += 1

    def test_validate_pax_search_number_of_nights(self):
        """
        validate number_of_nights can be greater than 1 on pax app
        """
        hotel_id_lax = '98702'
        event_date_lax = self._get_event_date('America/Los_Angeles')
        event_date_lax_day2 = event_date_lax + datetime.timedelta(days=1)
        event_date_lax_day3 = event_date_lax + datetime.timedelta(days=2)

        self.add_hotel_availability(hotel_id_lax, 294, event_date_lax, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_lax, 294, event_date_lax_day2, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')
        self.add_hotel_availability(hotel_id_lax, 294, event_date_lax_day3, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        passengers = self._create_2_passengers('Purple Rain Airlines', number_of_nights=2)
        pax_hotel_url = self._api_host + '/api/v1/offer/hotels?room_count=1&ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']
        resp = requests.get(url=pax_hotel_url)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)

        passengers = self._create_2_passengers('Purple Rain Airlines', number_of_nights=3)
        pax_hotel_url = self._api_host + '/api/v1/offer/hotels?room_count=1&ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']
        resp = requests.get(url=pax_hotel_url)
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertGreater(len(resp_json['data']), 0)

    def test_hotel_search_pet_and_service_pet_aa(self):
        """
        system test validating aa pet hack is removed
        and aa logic has returned to normal pet search behavior
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=KOA'

        # add inventory
        event_date = self._get_event_date('Pacific/Honolulu')
        self.add_hotel_availability(100303, 71, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100304, 71, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100306, 71, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')

        hotel_response = requests.get(hotel_url + '&service_pet=true', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['service_pets_allowed'], True)

        hotel_response = requests.get(hotel_url + '&pet=true', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)

        hotel_response = requests.get(hotel_url + '&pet=true&service_pet=true', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)
            self.assertEqual(hotel['service_pets_allowed'], True)

    def test_pax_app_hotel_search_pet_and_service_pet_aa(self):
        """
        system test validating aa pet hack is removed
        and pax app pet/service_pet search logic is reverted
        to normal behavior
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add inventory
        event_date = self._get_event_date('Pacific/Honolulu')
        self.add_hotel_availability(100303, 71, event_date, ap_block_type=1, block_price='150.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100304, 71, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100306, 71, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')

        # service_pet
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[0].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=False
        ))
        passenger_payload[1].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['service_pets_allowed'], True)

        # pet
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[0].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=False,
            pet=True
        ))
        passenger_payload[1].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=False,
            pet=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)

        # service_pet and pet
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[0].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=False
        ))
        passenger_payload[1].update(dict(
            port_accommodation='KOA',
            ticket_level='business',
            pax_status='nonPremium',
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)
            self.assertEqual(hotel['service_pets_allowed'], True)

    def test_hotel_search_pet_and_premium_aa(self):
        """
        verifies system returns hotels for pet searched and premium
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=LAX&pet=true&pet=true&is_premium=true'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98695, 71, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')
        self.add_hotel_availability(98734, 71, event_date, ap_block_type=1, block_price='75.00', blocks=2, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        count = 0
        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)
            if count == 0:
                self.assertEqual(hotel['premium'], True)
            count += 1

    def test_pax_app_hotel_search_pet_and_premium_aa(self):
        """
        verifies system returns hotels for pet and premium for pax app
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(98695, 71, event_date, ap_block_type=1, block_price='50.00', blocks=2, pay_type='0')
        self.add_hotel_availability(98734, 71, event_date, ap_block_type=1, block_price='75.00', blocks=2, pay_type='0')

        passenger_payload = self._generate_n_passenger_payload(3)

        passenger_payload[0].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=False
        ))

        passenger_payload[1].update(dict(
            port_accommodation='LAX',
            ticket_level='business',
            pax_status='nonPremium',
            service_pet=False
        ))

        passenger_payload[2].update(dict(
            port_accommodation='LAX',
            ticket_level='first',
            pax_status='premium',
            service_pet=False,
            pet=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]
        hotel_url = self._api_host + '/api/v1/offer/hotels'

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=2
        )

        hotel_response = requests.get(hotel_url, headers=pax_headers, params=search_query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        count = 0
        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['pets_allowed'], True)
            if count == 0:
                self.assertEqual(hotel['premium'], True)
            count += 1

    def test_validate_filter_blacklisted_hotels(self):
        """
        validate that StormX API filters out blacklisted hotels
        """
        port = 'ORD'

        aa_customer = 'American Airlines'
        aa_passengers = self._create_2_passengers(aa_customer, port_accommodation=port, pet=False, service_pet=False)

        pr_customer = 'Purple Rain Airlines'
        pr_passengers = self._create_2_passengers(pr_customer, port_accommodation=port, pet=False, service_pet=False)

        whitelist_hotel = 'tvl-97052'  # Hyatt Regency - O'Hare International Airport
        aa_blacklist_hotel_1 = 'tvl-97054'  # Wyndham ORD
        aa_blacklist_hotel_2 = 'tvl-85690'  # Hilton ORD

        event_date = self._get_event_date('America/Chicago')  # BNA timezone region is America/Chicago

        # add soft block availability
        self.add_hotel_availability(whitelist_hotel.split('-')[1], 0, event_date, ap_block_type=0, block_price='50.00', blocks=5, pay_type='0')
        self.add_hotel_availability(aa_blacklist_hotel_1.split('-')[1], 0, event_date, ap_block_type=0, block_price='60.00', blocks=5, pay_type='0')
        self.add_hotel_availability(aa_blacklist_hotel_2.split('-')[1], 0, event_date, ap_block_type=0, block_price='70.00', blocks=5, pay_type='0')

        # add hard block availability
        self.add_hotel_availability(whitelist_hotel.split('-')[1], 71, event_date, ap_block_type=1, block_price='50.00', blocks=5, pay_type='0')
        self.add_hotel_availability(whitelist_hotel.split('-')[1], 294, event_date, ap_block_type=1, block_price='50.00', blocks=5, pay_type='0')
        self.add_hotel_availability(aa_blacklist_hotel_1.split('-')[1], 71, event_date, ap_block_type=1, block_price='60.00', blocks=5, pay_type='0')
        self.add_hotel_availability(aa_blacklist_hotel_1.split('-')[1], 294, event_date, ap_block_type=1, block_price='60.00', blocks=5, pay_type='0')
        self.add_hotel_availability(aa_blacklist_hotel_2.split('-')[1], 71, event_date, ap_block_type=1, block_price='70.00', blocks=5, pay_type='0')
        self.add_hotel_availability(aa_blacklist_hotel_2.split('-')[1], 294, event_date, ap_block_type=1, block_price='70.00', blocks=5, pay_type='0')

        # get AA hotel availability (airline and passenger API)
        aa_airline_hotels = self._airline_get_passenger_hotel_offerings(customer=aa_customer, port=port, room_count=1)
        aa_passenger_hotels = self._get_passenger_hotel_offerings(passenger_dictionary=aa_passengers[0], room_count=1)

        # get PR hotel availability (airline and passenger API)
        pr_airline_hotels = self._airline_get_passenger_hotel_offerings(customer=pr_customer, port=port, room_count=1)
        pr_passenger_hotels = self._get_passenger_hotel_offerings(passenger_dictionary=pr_passengers[0], room_count=1)

        # get list of hotel availability hotel_ids
        aa_airline_hotel_ids = [hotel['hotel_id'] for hotel in aa_airline_hotels]
        aa_passenger_hotel_ids = [hotel['hotel_id'] for hotel in aa_passenger_hotels]
        pr_airline_hotel_ids = [hotel['hotel_id'] for hotel in pr_airline_hotels]
        pr_passenger_hotel_ids = [hotel['hotel_id'] for hotel in pr_passenger_hotels]

        # validate white list_hotel is in hotel availability
        self.assertIn(whitelist_hotel, aa_airline_hotel_ids)
        self.assertIn(whitelist_hotel, aa_passenger_hotel_ids)
        self.assertIn(whitelist_hotel, pr_airline_hotel_ids)
        self.assertIn(whitelist_hotel, pr_passenger_hotel_ids)

        # validate black_list_hotel_1 is not in hotel availability for AA and in hotel availability for PR
        self.assertNotIn(aa_blacklist_hotel_1, aa_airline_hotel_ids)
        self.assertNotIn(aa_blacklist_hotel_1, aa_passenger_hotel_ids)
        self.assertIn(aa_blacklist_hotel_1, pr_airline_hotel_ids)
        self.assertIn(aa_blacklist_hotel_1, pr_passenger_hotel_ids)

        # validate black_list_hotel_2 is not in hotel availability for AA and in hotel availability for PR
        self.assertNotIn(aa_blacklist_hotel_2, aa_airline_hotel_ids)
        self.assertNotIn(aa_blacklist_hotel_2, aa_passenger_hotel_ids)
        self.assertIn(aa_blacklist_hotel_2, pr_airline_hotel_ids)
        self.assertIn(aa_blacklist_hotel_2, pr_passenger_hotel_ids)

    def test_validate_hotel_provider(self):
        """
        validate hotel search provider field
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=LAX'

        # validate tvl provider is used with provider query string parameter not provided
        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0)
        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['provider'], 'tvl')

        # validate tvl provider is used with provider query string parameter empty
        hotel_response = requests.get(hotel_url + '&provider=', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0)
        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['provider'], 'tvl')

        # validate tvl provider is used with provider query string parameter empty
        hotel_response = requests.get(hotel_url + '&provider=tvl', headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0)
        for hotel in hotel_response_json['data']:
            self.assertEqual(hotel['provider'], 'tvl')

        # validate provider query string parameter must be from accepted providers list
        hotel_response = requests.get(hotel_url + '&provider=XYZ', headers=headers)
        self.assertEqual(hotel_response.status_code, 400)
        hotel_response_json = hotel_response.json()
        self._validate_error_message(hotel_response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.',
                                     [{'field': 'provider', 'message': '"XYZ" is not a valid choice.'}])

        # validate provider query string parameter must be from accepted providers list
        hotel_response = requests.get(hotel_url + '&provider=123', headers=headers)
        self.assertEqual(hotel_response.status_code, 400)
        hotel_response_json = hotel_response.json()
        self._validate_error_message(hotel_response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for hotel search.',
                                     [{'field': 'provider', 'message': '"123" is not a valid choice.'}])

    @uses_expedia
    def test_ean_hotel_provider(self):
        """
        validate that ean provider is accepted on hotel search
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        hotel_url = self._api_host + '/api/v1/hotels?room_count=1&port=' + port + '&provider=ean'

        hotel_response = requests.get(hotel_url, headers=headers)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertGreater(len(hotel_response_json['data']), 0, 'missing expedia inventory in ' + repr(port))
        for hotel in hotel_response_json['data']:
            self.assertIsNotNone(hotel['star_rating'])  # AA has requested 2-star and above hotels. don't want nulls.
            self.assertGreaterEqual(hotel['star_rating'], 2)  # AA has requested 2-star and above hotels.

    @uses_expedia
    def test_ean_search_max_rooms(self):
        """
        validate an expedia booking with 7 pax in 3 rooms

        validate some of the AA hacks / workarounds too.
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        port = self.select_airport_for_expedia_testing([
            ('PHX', 'America/Phoenix'),
            ('LGW', 'Europe/London')
        ])
        number_of_rooms = 9

        passengers = self._generate_n_passenger_payload(number_of_rooms, port_accommodation=port, life_stage='adult')
        import_response = requests.post(self._api_host + '/api/v1/passenger', headers=headers, json=passengers)
        self.assertEqual(import_response.status_code, 201)

        query_parameters = {
            'room_count': str(number_of_rooms),
            'port': port,
            'provider': 'ean'
        }

        hotel_response = requests.get(hotel_url, headers=headers, params=query_parameters)
        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertTrue(hotel_response_json['error'])
        self.assertEqual(hotel_response_json['meta']['error_code'], 'MAX_ROOMS_EXCEEDED')
        self.assertEqual(hotel_response_json['meta']['error_description'],
                         'The hotel provider only allows a maximum of 8 rooms per booking. '
                         'Hotel searches are restricted in the same way.')

    @uses_expedia
    def test_inventory_sorting(self):
        """
        test hotel sorting on tvl and expedia inventory
        """
        today_dca = self._get_event_date('America/New_York')
        today_phx = self._get_event_date('America/Phoenix')
        today_lax = self._get_event_date('America/Los_Angeles')
        today_dfw = self._get_event_date('America/Chicago')
        self.add_hotel_availability(96121, 294, today_dca, ap_block_type=1, block_price='99.99', blocks=3, pay_type='0')
        self.add_hotel_availability(85376, 294, today_dca, ap_block_type=1, block_price='99.99', blocks=3, pay_type='0')
        self.add_hotel_availability(87532, 294, today_phx, ap_block_type=1, block_price='99.99', blocks=3, pay_type='0')
        self.add_hotel_availability(98734, 294, today_lax, ap_block_type=1, block_price='99.99', blocks=3, pay_type='0')
        self.add_hotel_availability(96533, 294, today_dfw, ap_block_type=1, block_price='99.99', blocks=3, pay_type='0')

        aa_headers = self._generate_airline_headers('American Airlines')
        pr_headers = self._generate_airline_headers('Purple Rain Airlines')
        hotel_url = self._api_host + '/api/v1/hotels?room_count=1'

        providers = ['tvl', 'ean']
        ports_map = {
            'tvl': ['PHX', 'DFW', 'DCA', 'LAX', 'JFK']
        }

        ports_map['ean'] = self.select_multiple_airports_for_expedia_testing(
            [('FLL', 'America/New_York'), ('DFW', 'America/Chicago'),
             ('MIA', 'America/New_York'), ('MCO', 'America/New_York'),
             ('LAX', 'America/Los_Angeles')])

        # this will fail if LGW runs while temp code is in place
        if len(ports_map['ean']) == 0:
            ports_map['ean'] = ['LGW']

        for provider in providers:
            for port in ports_map[provider]:
                aa_hotels = requests.get(url=hotel_url + '&provider=' + provider + '&port=' + port,
                                         headers=aa_headers).json()
                self.assertGreater(len(aa_hotels['data']), 0)
                if provider == 'tvl':
                    self._test_hotel_availability_sorted(aa_hotels['data'], None, False, False)
                else:
                    self._test_expedia_hotel_availability_sorted(aa_hotels['data'], 10, 71, False, False)

                aa_hotels = requests.get(url=hotel_url + '&provider=' + provider + '&port=' + port + '&is_premium=true',
                                         headers=aa_headers).json()
                self.assertGreater(len(aa_hotels['data']), 0)
                if provider == 'tvl':
                    self._test_hotel_availability_sorted(aa_hotels['data'], None, True, False)
                else:
                    self._test_expedia_hotel_availability_sorted(aa_hotels['data'], 10, 71, True, False)

                pr_hotels = requests.get(url=hotel_url + '&provider=' + provider + '&port=' + port,
                                         headers=pr_headers).json()
                self.assertGreater(len(pr_hotels['data']), 0)
                if provider == 'tvl':
                    self._test_hotel_availability_sorted(pr_hotels['data'], None, False, False)
                else:
                    self._test_expedia_hotel_availability_sorted(pr_hotels['data'], 10, 294, False, False)

                pr_hotels = requests.get(url=hotel_url + '&provider=' + provider + '&port=' + port + '&is_premium=true',
                                         headers=pr_headers).json()
                self.assertGreater(len(pr_hotels['data']), 0, msg='no premium inventory for port ' + repr(port) + ' from provider ' + repr(provider))
                if provider == 'tvl':
                    self._test_hotel_availability_sorted(pr_hotels['data'], None, True, True)
                else:
                    self._test_expedia_hotel_availability_sorted(pr_hotels['data'], 10, 294, True, True)

    # actually doesn't require expedia for this particular test.
    def test_ean_inventory_disabled_for_british(self):
        customer = 'British Airways'
        headers = self._generate_airline_headers(customer=customer)
        hotel_url = self._api_host + '/api/v1/hotels'

        # get an inventory and validate passenger noteis empty string
        response = requests.get(hotel_url + '?room_count=1&port=LAX&provider=ean', headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['meta']['error_code'], '')
        self.assertEqual(len(response_json['data']), 0)  # ensure no Expedia inventory is presented to the customer.

    def test_hotel_sorting_united_crew(self):
        """"
        test custom sorting for united crew
        """
        customer = 'United Airlines - Crew Rooms'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'
        hotels_url = self._api_host + '/api/v1/hotels'
        hotel_offer_url = self._api_host + '/api/v1/offer/hotels'

        # ensure no inventory in port to start test
        resp = requests.get(url=hotels_url + '?room_count=1&port=YYC&provider=tvl', headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertEqual(len(resp['data']), 0)

        # validate pax app expedia inventory solutions before adding inventory
        # non premium
        passenger_payload = self._generate_n_passenger_payload(1, port_accommodation='YYC', ticket_level='economy')
        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertGreater(len(hotel_response_json['data']), 0)
        for hotel in hotel_response_json['data']:
            hotel_id_prefix = hotel['hotel_id'].split('-')
            self.assertEqual(hotel_id_prefix[0], 'ean')
            self.assertEqual(hotel['premium'], True)

        # premium
        # TODO: need to update ticket_level or pax_status once configuration verified
        passenger_payload = self._generate_n_passenger_payload(1, port_accommodation='YYC', ticket_level='business')
        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertGreater(len(hotel_response_json['data']), 0)
        hotel_id_prefix = hotel_response_json['data'][0]['hotel_id'].split('-')
        self.assertEqual(hotel_id_prefix[0], 'ean')
        self.assertEqual(hotel_response_json['data'][0]['premium'], True)

        # add inventory
        event_date = self._get_event_date('America/Edmonton')

        # premium
        self.add_hotel_availability(100824, 347, event_date, ap_block_type=2, block_price='150.00', blocks=3, pay_type='0')
        self.add_hotel_availability(107112, 347, event_date, ap_block_type=1, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(107112, 347, event_date, ap_block_type=0, block_price='100.00', blocks=2, pay_type='0')
        self.add_hotel_availability(100917, 0, event_date, ap_block_type=0, block_price='80.00', blocks=5, pay_type='0')

        # import passenger
        # TODO: need to update ticket_level or pax_status once configuration verified
        passenger_payload = self._generate_n_passenger_payload(5, port_accommodation='YYC', ticket_level='business')

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        # validate both hard block hotels appear only
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 2)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-100824')
        self.assertEqual(hotel_response_json['data'][1]['hotel_id'], 'tvl-107112')

        # validate only one hard block hotel appears
        search_query_parameters.update(dict(room_count=3))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 1)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-100824')

        # validate only hard block and airline soft block hotel appears only
        search_query_parameters.update(dict(room_count=4))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 1)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-107112')

        # validate nothing appears (soft block non premium is omitted)
        search_query_parameters.update(dict(room_count=5))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 0)

        # validate only soft block hotel appears
        self.add_hotel_availability(96510, 0, event_date, ap_block_type=0, block_price='80.00', blocks=5, pay_type='0')
        search_query_parameters.update(dict(room_count=5))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 1)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-96510')

        # add some non premium inventory
        self.add_hotel_availability(96483, 347, event_date, ap_block_type=2, block_price='50.00', blocks=5, pay_type='0')

        # validate only non premium hard block now appears
        search_query_parameters.update(dict(room_count=5))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 1)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-96483')

        # validate only non premium hard block now appears
        search_query_parameters.update(dict(room_count=4))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 1)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-96483')

        # validate premium hard blocks appear before non premium hard blocks
        search_query_parameters.update(dict(room_count=1))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 3)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-100824')
        self.assertEqual(hotel_response_json['data'][1]['hotel_id'], 'tvl-107112')
        self.assertEqual(hotel_response_json['data'][2]['hotel_id'], 'tvl-96483')

        # validate premium hard blocks appear before non premium hard blocks
        search_query_parameters.update(dict(room_count=3))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 2)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-100824')
        self.assertEqual(hotel_response_json['data'][1]['hotel_id'], 'tvl-96483')

        # validate non premium public search
        passenger_payload = self._generate_n_passenger_payload(1, port_accommodation='YYC', ticket_level='economy')

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        search_query_parameters.update(dict(room_count=1))
        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertEqual(len(hotel_response_json['data']), 3)
        self.assertEqual(hotel_response_json['data'][0]['hotel_id'], 'tvl-96483')
        self.assertEqual(hotel_response_json['data'][1]['hotel_id'], 'tvl-100824')
        self.assertEqual(hotel_response_json['data'][2]['hotel_id'], 'tvl-107112')

        # validate general non public sorting for united crew
        resp = requests.get(url=hotels_url + '?room_count=1&port=YYC&provider=tvl', headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertEqual(len(resp['data']), 5)
        self._test_hotel_availability_sorted(resp['data'], 5, False, False)

        # validate premium tvl non public
        resp = requests.get(url=hotels_url + '?room_count=1&port=YYC&provider=tvl&is_premium=true', headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertEqual(len(resp['data']), 3)
        self._test_hotel_availability_sorted(resp['data'], 3, True, True)

        # validate general expedia inventory
        resp = requests.get(url=hotels_url + '?room_count=1&port=LAX&provider=ean', headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertGreater(len(resp['data']), 0)
        self._test_expedia_hotel_availability_sorted(resp['data'], 10, 343, False, False)

        # validate premium expedia inventory
        resp = requests.get(url=hotels_url + '?room_count=1&port=LAX&provider=ean&is_premium=true', headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertGreater(len(resp['data']), 0)
        self._test_expedia_hotel_availability_sorted(resp['data'], 10, 343, True, True)

        # consume inventory
        hotel_data = [
            dict(id='tvl-96483', room_count=5),
            dict(id='tvl-100824', room_count=3),
            dict(id='tvl-107112', room_count=4),
            dict(id='tvl-96510', room_count=5)
        ]

        for hotel in hotel_data:
            passenger_payload = self._generate_n_passenger_payload(1)
            passenger_payload[0].update(dict(port_accommodation='YYC'))
            passenger = requests.post(passenger_url, headers=headers, json=passenger_payload).json()['data'][0]

            booking_payload = {
                'context_ids': [passenger['context_id']],
                'hotel_id': hotel['id'],
                'room_count': hotel['room_count']
            }

            resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
            self.assertEqual(resp.status_code, 200)

    def test_aa_public_premium_expedia(self):
        """"
        validate public premium expedia hotel search for AA
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        pax_headers = self._generate_passenger_headers()
        passenger_url = self._api_host + '/api/v1/passenger'
        hotels_url = self._api_host + '/api/v1/hotels'
        hotel_offer_url = self._api_host + '/api/v1/offer/hotels'

        # ensure no inventory in port to start test
        resp = requests.get(url=hotels_url + '?room_count=1&port=YYC&provider=tvl', headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertEqual(len(resp['data']), 0)

        # non premium
        passenger_payload = self._generate_n_passenger_payload(1, port_accommodation='YYC', pax_status='non-premium', ticket_level='economy')
        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertGreater(len(hotel_response_json['data']), 0)
        hotel_id_prefix = hotel_response_json['data'][0]['hotel_id'].split('-')
        self.assertEqual(hotel_id_prefix[0], 'ean')
        self.assertEqual(hotel_response_json['data'][0]['premium'], False)

        # premium
        passenger_payload = self._generate_n_passenger_payload(1, port_accommodation='YYC', ticket_level='business')
        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger = response_json['data'][0]

        search_query_parameters = dict(
            ak1=passenger['ak1'],
            ak2=passenger['ak2'],
            room_count=1
        )

        hotel_response_json = requests.get(hotel_offer_url, headers=pax_headers, params=search_query_parameters).json()
        self.assertGreater(len(hotel_response_json['data']), 0)
        hotel_id_prefix = hotel_response_json['data'][0]['hotel_id'].split('-')
        self.assertEqual(hotel_id_prefix[0], 'ean')
        self.assertEqual(hotel_response_json['data'][0]['premium'], True)
