from uuid import UUID

import requests

from StormxApp.tests.data_utilities import (
    generate_pax_record_locator,
    generate_pax_record_locator_group,
)
from stormx_verification_framework import (
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output
)


class TestApiPassengerImport(StormxSystemVerification):
    """
    Verify passenger import input validation and functionality.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiPassengerImport, cls).setUpClass()

    @staticmethod
    def generate_longest_pax_record_locator():
        """
        WARNING: do not provide to early-adopting
        """
        pax_record_locator = generate_pax_record_locator()
        pax_record_locator += 'FILLER' * 10
        return pax_record_locator[0:50]

    def test_create_2_passengers(self):
        """
        verify that the system can create two customers.
        """
        customer = 'Purple Rain Airlines'
        passengers = self._create_2_passengers(customer=customer)
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

    def test_pax_record_locator_max_length(self):
        """
        verifies that `pax_record_locator` and `pax_record_locator` are
        accepted when they are 50 characters long and rejected if longer than 50.

        IMPORTANT: do not test over length 25 on early adopters like AA,
        which only agreed to max length of 25!
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'United Airlines - Crew Rooms'
        headers = self._generate_airline_headers(customer=customer)

        pax_record_locator_50_chars = self.generate_longest_pax_record_locator()
        passengers_payload = self._generate_n_passenger_payload(
            1,
            pax_record_locator=pax_record_locator_50_chars,
            pax_record_locator_group=pax_record_locator_50_chars
        )
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['data'][0]['pax_record_locator'], pax_record_locator_50_chars)
        self.assertEqual(response_json['data'][0]['pax_record_locator_group'], pax_record_locator_50_chars)

        pax_record_locator_51_chars = self.generate_longest_pax_record_locator() + 'X'
        passengers_payload = self._generate_n_passenger_payload(
            1,
            pax_record_locator=pax_record_locator_51_chars,
            pax_record_locator_group=pax_record_locator_51_chars
        )
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['meta']['error_description'], 'Invalid input criteria for passenger import.')
        self.assertIn(
            {'message': 'Ensure this field has no more than 50 characters.', 'field': '[0].pax_record_locator'},
            response_json['meta']['error_detail'])
        self.assertIn(
            {'message': 'Ensure this field has no more than 50 characters.', 'field': '[0].pax_record_locator_group'},
            response_json['meta']['error_detail'])
        self.assertEqual(response_json['meta']['message'], 'Bad Request')
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

    def test_meal_only_voucher(self):
        """
        verify that passenger import response returns the same voucher_id for each passenger
        """
        customer = 'Purple Rain Airlines'
        passengers = self._create_2_passengers(customer, hotel_accommodation=False)
        voucher_id1 = passengers[0]['voucher_id']
        voucher_id2 = passengers[1]['voucher_id']
        UUID(voucher_id1, version=4)
        UUID(voucher_id2, version=4)
        self.assertEqual(voucher_id1, voucher_id2)

        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'not_offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])

        url1 = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        url2 = self._api_host + '/api/v1/passenger/' + passengers[1]['context_id'] + '/state'
        headers = self._generate_airline_headers(customer=customer)

        response1 = requests.get(url=url1, headers=headers).json()
        response2 = requests.get(url=url2, headers=headers).json()
        self.assertEqual(len(response1['data']['voucher']['meal_vouchers']), 2)
        self.assertEqual(len(response2['data']['voucher']['meal_vouchers']), 2)
        self.assertEqual(response1['data']['voucher']['hotel_voucher'], None)
        self.assertEqual(response2['data']['voucher']['hotel_voucher'], None)

        self.assertEqual(response1['data']['passenger']['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(response1['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response1['data']['passenger']['transport_accommodation_status'])
        self.assertEqual(response2['data']['passenger']['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(response2['data']['passenger']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(response2['data']['passenger']['transport_accommodation_status'])

    # def test_transport_accommodation_not_allowed_for_now(self):
    #     url = self._api_host + '/api/v1/passenger'
    #     customer = 'American Airlines'
    #     headers = self._generate_airline_headers(customer=customer)
    #
    #     passengers_payload = self._generate_2_passenger_payload(transport_accommodation=True)
    #     response = requests.post(url, headers=headers, json=passengers_payload)
    #     self.assertEqual(response.status_code, 400)
    #     response_json = response.json()
    #     self.assertIs(response_json['error'], True)
    #     # TODO: verify error message

    def test_max_passenger_upload_per_request(self):
        """
        verify that a maximum of 9 passengers can be uploaded.
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # verify 99 passengers are allowed.
        passengers_payload = self._generate_n_passenger_payload(99)
        response = requests.post(url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertIs(response_json['error'], False)

        # verify 100 passengers are not allowed.
        passengers_payload = self._generate_n_passenger_payload(100)
        response = requests.post(url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'MAX_PASSENGER_IMPORT_EXCEEDED',
                                     'Passenger import must not exceed 99 passengers.', [])

    # TODO: revisit business requirements.
    # def test_max_passengers_per_pax_record_locator__2_requests(self):
    #     """
    #     verify that a maximum of 9 passenger limit per pax_record_locator is enforced,
    #     even between requests.
    #
    #     Test design:
    #         First experiment:
    #             * request #1: 4 passengers.
    #             * request #2: 5 passengers, same pax_record_locator, different pax_record_locator_groups.
    #                 - should be allowed.
    #
    #         Second experiment:
    #             * request #3: 5 passengers.
    #             * request #4: 5 passengers, same pax_record_locator, different pax_record_locator_groups.
    #                 - should not be allowed, since this would make the pax_record_locator have 10 people.
    #     """
    #     url = self._api_host + '/api/v1/passenger'
    #     customer = 'American Airlines'
    #     headers = self._generate_airline_headers(customer=customer)
    #
    #     # verify 4 + 5 passengers are allowed under pax_record_locator, between two requests.
    #     # note that these two groups of passengers have different pax_record_locator_groups.
    #     pax_record_locator = generate_pax_record_locator()
    #     passengers_payload = self._generate_n_passenger_payload(4, pax_record_locator=pax_record_locator)
    #     response = requests.post(url, headers=headers, json=passengers_payload)
    #     self.assertEqual(response.status_code, 201)
    #     response_json = response.json()
    #     self.assertIs(response_json['error'], False)
    #     passengers_payload = self._generate_n_passenger_payload(5, pax_record_locator=pax_record_locator)
    #     response = requests.post(url, headers=headers, json=passengers_payload)
    #     self.assertEqual(response.status_code, 201)
    #     response_json = response.json()
    #     self.assertIs(response_json['error'], False)
    #
    #     # verify 5 + 5 passengers are allowed under pax_record_locator, between two requests.
    #     # note that these two groups of passengers have different pax_record_locator_groups.
    #     pax_record_locator = generate_pax_record_locator()
    #     passengers_payload = self._generate_n_passenger_payload(4, pax_record_locator=pax_record_locator)
    #     response = requests.post(url, headers=headers, json=passengers_payload)
    #     self.assertEqual(response.status_code, 201)
    #     response_json = response.json()
    #     self.assertIs(response_json['error'], False)
    #     passengers_payload = self._generate_n_passenger_payload(5, pax_record_locator=pax_record_locator)
    #     response = requests.post(url, headers=headers, json=passengers_payload)
    #     self.assertEqual(response.status_code, 400)
    #     response_json = response.json()
    #     self.assertIs(response_json['error'], True)
    #     # TODO: verify error message.

    def test_different_accommodations_same_record_locator__two_requests(self):
        """
        verify that you can assign different accommodations to passengers
        under the same `pax_record_locator` if you a request for each
        pax_record_locator_group you want to set up.

        test case design:
            * request #1: two passengers with hotel only.
            * request #2: two passengers with meal only, under a different `pax_record_locator_group` than request #1.
            * ...all four passengers above are under the same `pax_record_locator`.
        """
        customer = 'American Airlines'
        common_pax_record_locator = generate_pax_record_locator()

        passenger_group_1_info = dict(
            pax_record_locator=common_pax_record_locator,
            pax_record_locator_group=generate_pax_record_locator_group(),
        )
        passengers_1 = self._create_2_passengers(customer, hotel_accommodation=True, meal_accommodation=False,
                                                 meals=[], **passenger_group_1_info)
        self.assertEqual(len(passengers_1), 2)  # just verify successful creation.

        # passengers under same `pax_record_locator` but different `pax_record_locator_group`
        passenger_group_2_info = dict(
            pax_record_locator=common_pax_record_locator,
            pax_record_locator_group=generate_pax_record_locator_group(),
        )
        passengers_2 = self._create_2_passengers(customer, hotel_accommodation=False, meal_accommodation=True,
                                                 **passenger_group_2_info)
        self.assertEqual(len(passengers_2), 2)  # just verify successful creation.

    # TODO: revisit business requirements again later.
    # def test_two_requests_for_one_pax_record_locator_group(self):
    #     """
    #     verify that the system prevents the submission of more passengers to the same
    #     `pax_record_locator_group`.
    #
    #     test case design:
    #         * request #1: two passengers.
    #         * request #2: two passengers.
    #         * ...all four passengers above are under the same `pax_record_locator` AND `pax_record_locator_group`..
    #     """
    #     url = self._api_host + '/api/v1/passenger'
    #     customer = 'American Airlines'
    #     common_group_info = dict(
    #         pax_record_locator=generate_pax_record_locator(),
    #         pax_record_locator_group=generate_pax_record_locator_group(),
    #     )
    #     headers = self._generate_airline_headers(customer=customer)
    #
    #     # make request with certain `pax_record_locator` & `pax_record_locator_group`
    #     passengers_payload = self._generate_2_passenger_payload(**common_group_info)
    #     response = requests.post(url, headers=headers, json=passengers_payload)
    #
    #     passengers_payload = self._generate_2_passenger_payload(**common_group_info)
    #     response = requests.post(url, headers=headers, json=passengers_payload)
    #     self.assertEqual(response.status_code, 400)
    #     response_json = response.json()
    #     self.assertIs(response_json['error'], True)
    #     # TODO: verify that error message indicates that we have seen the pax_record_locator_group or something.

    def test_different_accommodations_same_pax_record_locator_group__one_request(self):
        """
        verify that in one HTTP request that you can assign different accommodations
        to passengers under the same `pax_record_locator` if you split them under
        different `pax_record_locator_group`s.

        test case design:
            * make only one request:
                * 1 passenger with hotel-only accommodations.
                * 1 passenger with meal-only accommodations. This passenger has a different `pax_record_locator_group.`
                * ...both passengers above are under the same `pax_record_locator`.
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        # first passenger: hotel-only.
        passengers_payload[0].update(dict(
            hotel_accommodation=True,
            meal_accommodation=False,
            meals=[],
        ))

        # second passenger: meal-only, under different `pax_record_locator_group`
        passengers_payload[1].update(dict(
            hotel_accommodation=False,
            meal_accommodation=True,
            pax_record_locator_group=generate_pax_record_locator_group(),
        ))
        response = requests.post(url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        passengers = response_json['data']

        self.assertEqual(len(passengers), 2)  # verify both passengers were created.

    # def test_visit_passenger_landing_page(self):
    #     pass # TODO: get URL then visit URL.

    def test_different_record_locator(self):
        """
        verifies the system is checking that all passengers
        upon import have the same pax_record_locator
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[1].update(dict(
            pax_record_locator=generate_pax_record_locator(),
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PNR_PASSENGER',
                                     "Request contains passengers on different PNRs.", [])

    def test_different_number_of_nights_on_import(self):
        """
        verifies the system is checking that all passengers
        upon import have the same number_of_nights per PNR group
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[1].update(dict(
            number_of_nights=2,
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH',
                                     'All passengers on the PNR must have the same number_of_nights', [])

    def test_different_number_of_nights_open_group(self):
        """
        verifies the system is checking that all passengers
        upon import have the same number_of_nights per PNR group
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=1)

        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            pax_record_locator=passengers[0]['pax_record_locator'],
            pax_record_locator_group=passengers[0]['pax_record_locator_group'],
            pnr_create_date=passengers[0]['pnr_create_date'],
            port_accommodation='JFK',
            number_of_nights=2,
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH',
                                     'All passengers on the PNR must have the same number_of_nights', [])

        passengers_payload[0].update(dict(
            number_of_nights=1,
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)

    def test_validate_booking_different_number_of_nights(self):
        """
        verifies the system is checking that all passengers
        upon booking have the same number_of_nights per passed in context_ids
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[1].update(dict(
            number_of_nights=2,
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH',
                                     'All passengers on the PNR must have the same number_of_nights', [])

    def test_validate_booking_same_number_of_nights(self):
        """
        validate number of nights must be same if not provided during booking
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        hotels_url = self._api_host + '/api/v1/hotels'

        hotel_id_jfk = 'tvl-85376'
        room_count = 1

        # create passengers with 2 nights and 1 nights
        passengers = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=2)
        passengers2 = self._create_2_passengers(customer=customer, port_accommodation='JFK', number_of_nights=1)

        # setup booking payload
        booking_payload = dict(
            context_ids=[passengers[0]['context_id'], passengers2[0]['context_id']],
            room_count=room_count,
            hotel_id=hotel_id_jfk
        )

        hotel_booking_resp = requests.post(url=hotels_url, headers=headers, json=booking_payload)
        self.assertEqual(hotel_booking_resp.status_code, 400)
        hotel_booking_json = hotel_booking_resp.json()

        self._validate_error_message(hotel_booking_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH',
                                     'Not all passengers have the same number_of_nights value.', [])

    def test_no_accommodations(self):
        """
        verifies the system is checking that all passengers
        upon import have valid accommodations of at least meal or hotel
        """
        # TODO change to reflect transport accommodations when supported
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[0].update(dict(
            hotel_accommodation=False,
            meal_accommodation=False
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_ACCOMMODATION', 'Passenger import contains passengers without accommodations.', [])

    def test_no_email_and_phone_number_with_notify_true(self):
        """
        verifies the system is checking that all passengers
        upon import provide a valid email address if notify=True
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[0].update(dict(
            notify=True,
        ))
        del passengers_payload[0]['emails']
        del passengers_payload[0]['phone_numbers']

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Passenger import has missing email and phone_number for passengers with notify = true.', [])

    def test_passenger_import_phone_number_validation(self):
        """
        verifies the system is checking that all passengers
        upon import provide a valid phone_numbers if notify=True
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # bad phone number ----
        phone_numbers = ['My cell: 555 1234']
        passengers_payload = self._generate_n_passenger_payload(1, emails=[], phone_numbers=phone_numbers, notify=True)
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(
            response_json, 400, 'Bad Request', 'INVALID_INPUT',
            'Invalid input criteria for passenger import.',
            [
                {
                    'field': '[0].phone_numbers[0]',
                    'message': "phone number must be in the E.164 format and always start with a '+'. Expected format: '+{country_code}{subscriber_phone_number}', no spaces or symbols."
                },
                {
                    'field': '[0].phone_numbers[0]',
                    'message': 'Ensure this field has no more than 16 characters.'
                }
            ]
        )

        # bad phone number ----
        phone_numbers = ['+1']
        passengers_payload = self._generate_n_passenger_payload(1, emails=[], phone_numbers=phone_numbers, notify=True)
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self._validate_error_message(
            response_json, 400, 'Bad Request', 'INVALID_INPUT',
            'Invalid input criteria for passenger import.',
            [
                {
                    'field': '[0].phone_numbers[0]',
                    'message': "phone number must be in the E.164 format and always start with a '+'. Expected format: '+{country_code}{subscriber_phone_number}', no spaces or symbols."
                }
            ]
        )

        # good phone number ----
        phone_numbers = ['+14805551234']
        passengers_payload = self._generate_n_passenger_payload(1, emails=[], phone_numbers=phone_numbers, notify=True)
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertIs(response_json['error'], False)

    def test_valid_meal_accommodations(self):
        """
        verifies the system is checking that all passengers
        upon import provide valid meal accommodations
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # leave meals out, meal=True, hotel=False
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False
        ))
        del passengers_payload[0]['meals']

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_ACCOMMODATION', 'Passenger import contains invalid meal accommodations.', [])

        # empty meal object, meal=True, hotel=False
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            meals=[dict()]
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{"field": "[0].meals[0].currency_code", "message": "This field is required."},
                                      {"field": "[0].meals[0].number_of_days", "message": "This field is required."},
                                      {"field": "[0].meals[0].meal_amount", "message": "This field is required."}])

        # empty meal object, meal=True, hotel=False (second pax)
        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[1].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            meals=[dict()]
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{"field": "[1].meals[0].currency_code", "message": "This field is required."},
                                      {"field": "[1].meals[0].number_of_days", "message": "This field is required."},
                                      {"field": "[1].meals[0].meal_amount", "message": "This field is required."}])

        # empty meal object, meal=True, hotel=False (1st pax)
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            meals=[{'currency_code': 'bad_input', 'meal_amount': 12, 'number_of_days': 1}]
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{"field": "[0].meals[0].currency_code", "message": '"bad_input" is not a valid choice.'}])

        # empty meal object, meal=True, hotel=False (1st pax, second meal)
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            meals=[{'currency_code': 'USD', 'meal_amount': 12, 'number_of_days': 1}, {'currency_code': 'USD', 'meal_amount': 12, 'number_of_days': 'bad input'}]
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{"field": "[0].meals[1].number_of_days", "message": 'A valid integer is required.'}])

        # empty meal object, meal=True, hotel=False (2nd pax, second meal)
        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[1].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            meals=[
                {'currency_code': 'USD', 'meal_amount': 12, 'number_of_days': 1},
                {'currency_code': 'USD', 'meal_amount': 12, 'number_of_days': 'bad input'},
                {'currency_code': 'USD', 'meal_amount': 12, 'number_of_days': 1}
            ]
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{"field": "[1].meals[1].number_of_days", "message": 'A valid integer is required.'}])

        # empty meals list, meal=True, hotel=False
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=True,
            hotel_accommodation=False,
            meals=list()
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_ACCOMMODATION', 'Passenger import contains invalid meal accommodations.', [])

    def test_validate_passenger_import_pet_required(self):
        """
        validates that pet field is required during passenger import
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        del passengers_payload[0]['pet']

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{"field": "[0].pet", "message": "This field is required."}])

    def test_valid_hotel_accommodations(self):
        """
        verifies the system is checking that all passengers
        upon import provide valid hotel accommodations
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[0].update(dict(
            hotel_accommodation=True,
        ))
        passengers_payload[1].update(dict(
            hotel_accommodation=False,
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH',
                                     'PNR contains passengers with different hotel accommodations.', [])

        # leave meals out, meal=False, hotel=True
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=False,
            hotel_accommodation=True
        ))
        del passengers_payload[0]['meals']

        response = requests.post(url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)

        # empty meal object, meal=False, hotel=True
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=False,
            hotel_accommodation=True,
            meals=[dict()]
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], True)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'field': '[0].meals[0].currency_code', 'message': 'This field is required.'},
                                      {'field': '[0].meals[0].number_of_days', 'message': 'This field is required.'},
                                      {'field': '[0].meals[0].meal_amount', 'message': 'This field is required.'}])

        # empty meals list, meal=False, hotel=True
        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            meal_accommodation=False,
            hotel_accommodation=True,
            meals=list()
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        self.assertEqual(response.status_code, 201)


    def test_empty_passenger_list_handling(self):
        """
        system test verifying that passenger payload during import and mass meal job is not empty
        """
        expected_error_message = 'We did not receive a list of passengers. Please send up a valid list of passenger objects.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        import_url = self._api_host + '/api/v1/passenger'

        import_resp = requests.post(url=import_url, headers=headers, json=[])
        import_resp_json = import_resp.json()

        self.assertEqual(import_resp.status_code, 400)
        log_error_system_tests_output(pretty_print_json(import_resp_json))
        self._validate_error_message(import_resp_json, 400, 'Bad Request', 'INVALID_INPUT', expected_error_message, [])

    def test_handicap_can_receive_notifications(self):
        """
        verifies system can now have notify and handicap both set to true
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_n_passenger_payload(1)

        passengers_payload[0].update(dict(
            notify=True,
            handicap=True
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['data'][0]['context_id'], passengers_payload[0]['context_id'])
        self.assertEqual(response_json['data'][0]['handicap'], True)

    def test_children_cannot_receive_notifications(self):
        """
        verifies the system is checking for all passengers
        upon import that children cannot receive notifications
        """
        expected_error_message = 'Children cannot receive notifications. Children must interact with agent or be booked with an adult.'

        url = self._api_host + '/api/v1/passenger'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[1].update(dict(
            life_stage='child',
            notify=True
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'AGENT_INTERVENTION_REQUIRED', expected_error_message, [])

    def test_pnr_can_contain_all_children(self):
        """
        verifies system allows children to be on a PNR by them self.
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            life_stage='child',
            meal_accommodation=False,
            hotel_accommodation=True,
            transport_accommodation=False,
            notify=False
        ))

        response = requests.post(url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passengers_payload = self._generate_2_passenger_payload()
        passengers_payload[0].update(dict(
            life_stage='child',
            meal_accommodation=False,
            hotel_accommodation=True,
            transport_accommodation=False,
            notify=False
        ))

        passengers_payload[1].update(dict(
            life_stage='child',
            meal_accommodation=False,
            hotel_accommodation=True,
            transport_accommodation=False,
            notify=False
        ))

        response2 = requests.post(url, headers=headers, json=passengers_payload)
        response_json2 = response2.json()
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response_json2['error'], False)

        passengers_payload2 = self._generate_2_passenger_payload()
        passengers_payload2[0].update(dict(
            first_name='Adam',
            life_stage='adult',
            meal_accommodation=True,
            hotel_accommodation=True,
            transport_accommodation=False
        ))

        passengers_payload2[1].update(dict(
            first_name='Carrie',
            life_stage='child',
            meal_accommodation=False,
            hotel_accommodation=True,
            transport_accommodation=False,
            notify=False
        ))

        response3 = requests.post(url, headers=headers, json=passengers_payload2)
        response_json3 = response3.json()
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response_json3['error'], False)

        # verify that life_stage is set correctly for the adult and child passsengers.
        adam = [p for p in response_json3['data'] if p['first_name'] == 'Adam'][0]
        carrie = [p for p in response_json3['data'] if p['first_name'] == 'Carrie'][0]
        self.assertEqual(adam['life_stage'], 'adult')
        self.assertEqual(carrie['life_stage'], 'child')
        adam_full_state = requests.get(url=self._api_host + '/api/v1/passenger/{context_id}/state'.format(context_id=adam['context_id']), headers=headers)
        self.assertEqual(adam_full_state.json()['data']['passenger']['life_stage'], 'adult')
        carrie_full_state = requests.get(url=self._api_host + '/api/v1/passenger/{context_id}/state'.format(context_id=carrie['context_id']), headers=headers)
        self.assertEqual(carrie_full_state.json()['data']['passenger']['life_stage'], 'child')

    def test_children_cannot_get_auth_keys(self):
        """
        verifies the system is checking for all passengers
        upon import that children do not get auth keys generated
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[1].update(dict(
            life_stage='child',
            notify=False
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()

        if response_json['data'][0]['life_stage'] == 'child':
            child = response_json['data'][0]
            adult = response_json['data'][1]
        else:
            child = response_json['data'][1]
            adult = response_json['data'][0]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)
        self.assertIsNone(child['ak1'])
        self.assertIsNone(child['ak2'])

        # exception will raise if auth_keys are not valid UUID
        UUID(adult['ak1'], version=4)
        UUID(adult['ak2'], version=4)

    def test_different_port_accommodations(self):
        """
        verifies the system is ensuring all passengers have the same port_accommodation upon import
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[1].update(dict(
            port_accommodation='ORD'
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', 'All passengers on the PNR must have the same port_accommodation', [])

    def test_different_number_of_nights(self):
        """
        verifies the system is ensuring all passengers have the same number_of_nights upon import
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passengers_payload = self._generate_2_passenger_payload()

        passengers_payload[1].update(dict(
            number_of_nights=2
        ))

        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', 'All passengers on the PNR must have the same number_of_nights', [])

    def test_invalid_email_phone_number_with_notify_true(self):
        """
        verifies system is ensuring if notify=True that proper email or phone_number is set
        """
        error_message = 'Passenger import has missing email and phone_number for passengers with notify = true.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True
        ))

        del passenger_payload[0]['emails']
        del passenger_payload[0]['phone_numbers']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_numbers=[],
            emails=[]
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_numbers=None,
            emails=[]
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_numbers=[],
            emails=None
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_numbers=None,
            emails=None
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_numbers=[]
        ))

        del passenger_payload[0]['emails']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_numbers=None
        ))

        del passenger_payload[0]['emails']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            emails=[]
        ))

        del passenger_payload[0]['phone_numbers']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            emails=None
        ))

        del passenger_payload[0]['phone_numbers']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', error_message, [])

    def test_valid_email_phone_number_with_notify_true(self):
        """
        verifies system is ensuring if notify=True that different email/phone_number combinations are valid
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True
        ))

        del passenger_payload[0]['emails']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True
        ))

        del passenger_payload[0]['phone_numbers']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            emails=[]
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            emails=None
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_numbers=[]
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=True,
            phone_number=None
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

    def test_null_blank_optional_fields(self):
        """
        verifies system is allowing optional fields to be null and blank and that system is saving them as null in DB
        """
        optional_fields = ['pax_status', 'ticket_level']

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=False,
            pax_status="",
            ticket_level=""
        ))

        del passenger_payload[0]['scheduled_depart']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        for field in optional_fields:
            self.assertEqual(response_json['data'][0][field], '')

        self.assertIsNone(response_json['data'][0]['scheduled_depart'])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=False,
            phone_numbers=None,
            emails=None,
            scheduled_depart=None,
            pax_status=None,
            ticket_level=None
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        for field in optional_fields:
            self.assertEqual(response_json['data'][0][field], '')

        self.assertIsNone(response_json['data'][0]['scheduled_depart'])

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            notify=False
        ))

        for field in optional_fields:
            del passenger_payload[0][field]

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        for field in optional_fields:
            self.assertEqual(response_json['data'][0][field], '')

    def test_ensure_context_id_case_insensitive(self):
        """
        verifies system can handle context_id being case insensitive
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            context_id=passenger_payload[0]['context_id'] + '_aBc'
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        context_id = response_json['data'][0]['context_id']
        context_id_lower_case = context_id.lower()
        context_id_upper_case = context_id.upper()

        response2 = requests.get(passenger_url + '/' + context_id, headers=headers)
        response3 = requests.get(passenger_url + '/' + context_id_lower_case, headers=headers)
        response4 = requests.get(passenger_url + '/' + context_id_upper_case, headers=headers)

        response_json2 = response2.json()
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response_json2['error'], False)

        response_json3 = response3.json()
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response_json3['error'], False)

        response_json4 = response4.json()
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(response_json4['error'], False)

        self.assertEqual(response_json2['data'], response_json3['data'])
        self.assertEqual(response_json2['data'], response_json4['data'])
        self.assertEqual(response_json3['data'], response_json4['data'])

    def test_context_id_valid_characters(self):
        """
        verifies system can handle underscores and dashes for context_id
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)

        passenger_payload[0].update(dict(
            context_id=passenger_payload[0]['context_id'] + '_aBc__--_abc'
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

    def test_context_id_invalid_characters(self):
        """
        verifies system is validating context_id for invalid characters
        """
        error_message_invalid_characters_0 = [{'field': '[0].context_id', 'message': 'context_id must only contain letters, numbers, underscores, or dashes.'}]
        error_message_invalid_characters_1 = [{'field': '[1].context_id', 'message': 'context_id must only contain letters, numbers, underscores, or dashes.'}]

        invalid_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', ',',
                              '<', '.', '>', '?', '/', '|', '{', '[', '}', ']', ':', ';', "'", '"']

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        for invalid_character in invalid_characters:
            passenger_payload = self._generate_n_passenger_payload(2)

            passenger_payload[0].update(dict(
                context_id=passenger_payload[0]['context_id'] + invalid_character
            ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 400)
            log_error_system_tests_output(pretty_print_json(response_json))
            self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.', error_message_invalid_characters_0)

        passenger_payload = self._generate_n_passenger_payload(2)

        for invalid_character in invalid_characters:
            passenger_payload[1].update(dict(
                context_id=passenger_payload[0]['context_id'] + invalid_character
            ))

            response = requests.post(passenger_url, headers=headers, json=passenger_payload)
            response_json = response.json()
            self.assertEqual(response.status_code, 400)
            log_error_system_tests_output(pretty_print_json(response_json))
            self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.', error_message_invalid_characters_1)

    def test_invalid_port_origin_on_pax_import(self):
        """
        verifies system can handle invalid port_origin during import and provide error message
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[0].update(dict(
            port_origin='OYUa'
        ))
        passenger_payload[1].update(dict(
            port_origin='OY'
        ))

        response = requests.post(passenger_url, headers=headers, json=[passenger_payload[0]])
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'field': '[0].port_origin', 'message': 'Ensure this field has no more than 3 characters.'}])

        response = requests.post(passenger_url, headers=headers, json=[passenger_payload[1]])
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'field': '[0].port_origin', 'message': 'Ensure this field has at least 3 characters.'}])

    def test_invalid_port_accommodation_on_pax_import(self):
        """
        verifies system can handle invalid port_accommodation during import and provide error message
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(5)
        passenger_payload[0].update(dict(
            port_accommodation='XXX'
        ))
        passenger_payload[1].update(dict(
            port_accommodation='011'
        ))
        passenger_payload[2].update(dict(
            port_accommodation='0YU'
        ))
        passenger_payload[3].update(dict(
            port_accommodation='OYUa'
        ))
        passenger_payload[4].update(dict(
            port_accommodation='OY'
        ))

        response = requests.post(passenger_url, headers=headers, json=[passenger_payload[0]])
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PORT', 'XXX is not a valid choice for port_accommodation', [])

        response = requests.post(passenger_url, headers=headers, json=[passenger_payload[1]])
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PORT', '011 is not a valid choice for port_accommodation', [])

        response = requests.post(passenger_url, headers=headers, json=[passenger_payload[2]])
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PORT', '0YU is not a valid choice for port_accommodation', [])

        response = requests.post(passenger_url, headers=headers, json=[passenger_payload[3]])
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'field': '[0].port_accommodation', 'message': 'Ensure this field has no more than 3 characters.'}])

        response = requests.post(passenger_url, headers=headers, json=[passenger_payload[4]])
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'field': '[0].port_accommodation', 'message': 'Ensure this field has at least 3 characters.'}])

    def test_ticket_level_choices_on_import(self):
        """
        tests that all the ticket_level choices work on passenger import
        verifies that the passed up ticket level choice is also returned
        """
        ticket_levels = ['first', 'business', 'premium_economy', 'economy']
        for ticket_level in ticket_levels:
            passengers = self._create_2_passengers('Purple Rain Airlines', ticket_level=ticket_level)
            for passenger in passengers:
                self.assertEqual(passenger['ticket_level'], ticket_level)

    def test_meal_only_by_group(self):
        """
        verifies system gives separate voucher_ids by group for meal-only imports
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(6)

        group_a = passenger_payload[0]['pax_record_locator_group'] + 'a'
        group_b = passenger_payload[1]['pax_record_locator_group'] + 'b'
        group_c = passenger_payload[3]['pax_record_locator_group'] + 'c'

        passenger_payload[0].update(dict(
            hotel_accommodation=False,
            pax_record_locator_group=group_a
        ))
        passenger_payload[1].update(dict(
            hotel_accommodation=False,
            pax_record_locator_group=group_b
        ))
        passenger_payload[2].update(dict(
            hotel_accommodation=False,
            pax_record_locator_group=group_b
        ))
        passenger_payload[3].update(dict(
            hotel_accommodation=False,
            pax_record_locator_group=group_c
        ))
        passenger_payload[4].update(dict(
            hotel_accommodation=False,
            pax_record_locator_group=group_c
        ))
        passenger_payload[5].update(dict(
            hotel_accommodation=False,
            pax_record_locator_group=group_c
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)
        self.assertEqual(len(response_json['data']), 6)

        all_passengers = response_json['data']
        group_a_passengers = list(filter(lambda p: p['pax_record_locator_group'] == group_a, all_passengers))
        group_b_passengers = list(filter(lambda p: p['pax_record_locator_group'] == group_b, all_passengers))
        group_c_passengers = list(filter(lambda p: p['pax_record_locator_group'] == group_c, all_passengers))

        self.assertEqual(len(group_a_passengers), 1)
        self.assertEqual(len(group_b_passengers), 2)
        self.assertEqual(len(group_c_passengers), 3)

        # verify that all passengers in the group share the same voucher id
        group_a_voucher_id = group_a_passengers[0]['voucher_id']
        for passenger in group_a_passengers:
            self.assertEqual(passenger['voucher_id'], group_a_voucher_id)

        group_b_voucher_id = group_b_passengers[0]['voucher_id']
        for passenger in group_b_passengers:
            self.assertEqual(passenger['voucher_id'], group_b_voucher_id)

        group_c_voucher_id = group_c_passengers[0]['voucher_id']
        for passenger in group_c_passengers:
            self.assertEqual(passenger['voucher_id'], group_c_voucher_id)

        self.assertNotEqual(group_a_voucher_id, group_b_voucher_id)
        self.assertNotEqual(group_a_voucher_id, group_c_voucher_id)
        self.assertNotEqual(group_b_voucher_id, group_c_voucher_id)

        voucher_a_url = self._api_host + '/api/v1/voucher/' + str(group_a_voucher_id)
        voucher_b_url = self._api_host + '/api/v1/voucher/' + str(group_b_voucher_id)
        voucher_c_url = self._api_host + '/api/v1/voucher/' + str(group_c_voucher_id)

        voucher_a_resp = requests.get(url=voucher_a_url, headers=headers)
        voucher_b_resp = requests.get(url=voucher_b_url, headers=headers)
        voucher_c_resp = requests.get(url=voucher_c_url, headers=headers)

        self.assertEqual(voucher_a_resp.status_code, 200)
        self.assertEqual(voucher_b_resp.status_code, 200)
        self.assertEqual(voucher_c_resp.status_code, 200)

        voucher_a_resp_json = voucher_a_resp.json()
        voucher_b_resp_json = voucher_b_resp.json()
        voucher_c_resp_json = voucher_c_resp.json()

        self.assertEqual(len(voucher_a_resp_json['data']['passengers']), 1)
        self.assertEqual(voucher_a_resp_json['data']['passengers'][0]['context_id'], group_a_passengers[0]['context_id'])
        self.assertEqual(voucher_a_resp_json['data']['voucher_id'], group_a_voucher_id)

        self.assertEqual(len(voucher_b_resp_json['data']['passengers']), 2)
        self.assertIn(voucher_b_resp_json['data']['passengers'][0]['context_id'], [passenger['context_id'] for passenger in group_b_passengers])
        self.assertIn(voucher_b_resp_json['data']['passengers'][1]['context_id'], [passenger['context_id'] for passenger in group_b_passengers])
        self.assertEqual(voucher_b_resp_json['data']['voucher_id'], group_b_voucher_id)

        self.assertEqual(len(voucher_c_resp_json['data']['passengers']), 3)
        self.assertIn(voucher_c_resp_json['data']['passengers'][0]['context_id'], [passenger['context_id'] for passenger in group_c_passengers])
        self.assertIn(voucher_c_resp_json['data']['passengers'][1]['context_id'], [passenger['context_id'] for passenger in group_c_passengers])
        self.assertIn(voucher_c_resp_json['data']['passengers'][2]['context_id'], [passenger['context_id'] for passenger in group_c_passengers])
        self.assertEqual(voucher_c_resp_json['data']['voucher_id'], group_c_voucher_id)

    def test_same_context_id_different_airline_on_pax_app(self):
        """
        verify system can book separate airlines with the same context_id through pax app
        """
        american_headers = self._generate_airline_headers('American Airlines')
        delta_headers = self._generate_airline_headers('Delta Air Lines')

        import_url = self._api_host + '/api/v1/passenger'
        passenger_payload = self._generate_n_passenger_payload(1)

        american_import_resp = requests.post(url=import_url, headers=american_headers, json=passenger_payload)
        delta_import_resp = requests.post(url=import_url, headers=delta_headers, json=passenger_payload)

        self.assertEqual(american_import_resp.status_code, 201)
        self.assertEqual(delta_import_resp.status_code, 201)

        passenger_aa = american_import_resp.json()['data'][0]
        passenger_delta = delta_import_resp.json()['data'][0]

        aa_hotel_offerings = self._get_passenger_hotel_offerings(passenger_aa)
        self.assertGreaterEqual(len(aa_hotel_offerings), 0)

        self._passenger_book_hotel(passenger_aa, aa_hotel_offerings[0], [passenger_aa['context_id']])
        aa_get_pax_resp = requests.get(url=import_url + '/' + passenger_aa['context_id'], headers=american_headers)
        self.assertEqual(aa_get_pax_resp.status_code, 200)
        aa_voucher_id = aa_get_pax_resp.json()['data']['voucher_id']
        self.assertIsNotNone(aa_voucher_id)

        delta_get_pax_resp = requests.get(url=import_url + '/' + passenger_delta['context_id'], headers=delta_headers)
        self.assertEqual(delta_get_pax_resp.status_code, 200)
        self.assertIsNone(delta_get_pax_resp.json()['data']['voucher_id'])

        delta_hotel_offerings = self._get_passenger_hotel_offerings(passenger_delta)
        self.assertGreaterEqual(len(delta_hotel_offerings), 0)

        self._passenger_book_hotel(passenger_delta, delta_hotel_offerings[0], [passenger_delta['context_id']])
        delta_get_pax_resp2 = requests.get(url=import_url + '/' + passenger_delta['context_id'], headers=delta_headers)
        self.assertEqual(delta_get_pax_resp2.status_code, 200)

        delta_pax_json = delta_get_pax_resp2.json()
        delta_voucher_id = delta_pax_json['data']['voucher_id']
        self.assertIsNotNone(delta_voucher_id)

        aa_get_pax_resp2 = requests.get(url=import_url + '/' + passenger_aa['context_id'], headers=american_headers)
        self.assertEqual(aa_get_pax_resp2.status_code, 200)
        self.assertEqual(aa_get_pax_resp2.json()['data']['voucher_id'], aa_voucher_id)
        self.assertNotEqual(aa_voucher_id, delta_voucher_id)

        voucher_url = self._api_host + '/api/v1/voucher/'

        aa_get_voucher_resp = requests.get(url=voucher_url + str(aa_voucher_id), headers=american_headers)
        self.assertEqual(aa_get_voucher_resp.status_code, 200)
        aa_get_delta_voucher_resp = requests.get(url=voucher_url + str(delta_voucher_id), headers=american_headers)
        self.assertEqual(aa_get_delta_voucher_resp.status_code, 404)

        delta_get_voucher_resp = requests.get(url=voucher_url + str(delta_voucher_id), headers=delta_headers)
        self.assertEqual(delta_get_voucher_resp.status_code, 200)
        delta_get_aa_voucher_resp = requests.get(url=voucher_url + str(aa_voucher_id), headers=delta_headers)
        self.assertEqual(delta_get_aa_voucher_resp.status_code, 404)

    def test_same_context_id_different_airline_on_airline_api(self):
        """
        verify system can book separate airlines with the same context_id through airline api
        """
        american_headers = self._generate_airline_headers('American Airlines')
        delta_headers = self._generate_airline_headers('Delta Air Lines')

        import_url = self._api_host + '/api/v1/passenger'
        passenger_payload = self._generate_n_passenger_payload(1)

        american_import_resp = requests.post(url=import_url, headers=american_headers, json=passenger_payload)
        delta_import_resp = requests.post(url=import_url, headers=delta_headers, json=passenger_payload)

        self.assertEqual(american_import_resp.status_code, 201)
        self.assertEqual(delta_import_resp.status_code, 201)

        passenger_aa = american_import_resp.json()['data'][0]
        passenger_delta = delta_import_resp.json()['data'][0]

        aa_hotel_offerings = self._get_passenger_hotel_offerings(passenger_aa)
        self.assertGreaterEqual(len(aa_hotel_offerings), 0)

        self._airline_book_hotel('American Airlines', aa_hotel_offerings[0], [passenger_aa['context_id']])
        aa_get_pax_resp = requests.get(url=import_url + '/' + passenger_aa['context_id'], headers=american_headers)
        self.assertEqual(aa_get_pax_resp.status_code, 200)
        aa_voucher_id = aa_get_pax_resp.json()['data']['voucher_id']
        self.assertIsNotNone(aa_voucher_id)

        delta_get_pax_resp = requests.get(url=import_url + '/' + passenger_delta['context_id'], headers=delta_headers)
        self.assertEqual(delta_get_pax_resp.status_code, 200)
        self.assertIsNone(delta_get_pax_resp.json()['data']['voucher_id'])

        delta_hotel_offerings = self._get_passenger_hotel_offerings(passenger_delta)
        self.assertGreaterEqual(len(delta_hotel_offerings), 0)

        self._airline_book_hotel('Delta Air Lines', delta_hotel_offerings[0], [passenger_delta['context_id']])
        delta_get_pax_resp2 = requests.get(url=import_url + '/' + passenger_delta['context_id'], headers=delta_headers)
        self.assertEqual(delta_get_pax_resp2.status_code, 200)

        delta_pax_json = delta_get_pax_resp2.json()
        delta_voucher_id = delta_pax_json['data']['voucher_id']
        self.assertIsNotNone(delta_voucher_id)

        aa_get_pax_resp2 = requests.get(url=import_url + '/' + passenger_aa['context_id'], headers=american_headers)
        self.assertEqual(aa_get_pax_resp2.status_code, 200)
        self.assertEqual(aa_get_pax_resp2.json()['data']['voucher_id'], aa_voucher_id)
        self.assertNotEqual(aa_voucher_id, delta_voucher_id)

        voucher_url = self._api_host + '/api/v1/voucher/'

        aa_get_voucher_resp = requests.get(url=voucher_url + str(aa_voucher_id), headers=american_headers)
        self.assertEqual(aa_get_voucher_resp.status_code, 200)
        aa_get_delta_voucher_resp = requests.get(url=voucher_url + str(delta_voucher_id), headers=american_headers)
        self.assertEqual(aa_get_delta_voucher_resp.status_code, 404)

        delta_get_voucher_resp = requests.get(url=voucher_url + str(delta_voucher_id), headers=delta_headers)
        self.assertEqual(delta_get_voucher_resp.status_code, 200)
        delta_get_aa_voucher_resp = requests.get(url=voucher_url + str(aa_voucher_id), headers=delta_headers)
        self.assertEqual(delta_get_aa_voucher_resp.status_code, 404)

    def test_import_passengers__bad_phone_number(self):
        """
        verify passenger notifications of type offered are returned for various passenger endpoints
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        bad_phone_number = '+1234567'  # minimum phone number i 8.
        passengers_payload = self._generate_n_passenger_payload(1, phone_numbers=[bad_phone_number],
                                                                notify=True, emails=[])
        response = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        expected_errors = [{
            'field': '[0].phone_numbers[0]',
            'message': "phone number must be in the E.164 format and always start with a '+'. "
                       "Expected format: '+{country_code}{subscriber_phone_number}', no spaces or symbols."
        }]
        self._validate_error_message(response.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.', expected_errors)

    def _test_passenger_import_emails_phone_numbers(self, customer, emails, phone_numbers, delete_emails, delete_phone_numbers):
        """
        verifies system is handling passenger_contact_info correctly when emails,
        and phone_numbers are null, and empty lists.
        """
        headers = self._generate_airline_headers(customer=customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            emails=emails,
            phone_numbers=phone_numbers,
        ))

        if delete_emails:
            del passenger_payload[0]['emails']

        if delete_phone_numbers:
            del passenger_payload[0]['phone_numbers']

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        passenger_json = response.json()['data'][0]
        self.assertEqual(response.status_code, 201)
        self.assertIn('emails', passenger_json)
        self.assertIn('phone_numbers', passenger_json)
        self.assertEqual(len(passenger_json['emails']), 0)
        self.assertEqual(len(passenger_json['phone_numbers']), 0)

        get_passenger_url = passenger_url + '/' + passenger_json['context_id']
        response = requests.get(get_passenger_url, headers=headers)
        passenger_json = response.json()['data']
        self.assertEqual(response.status_code, 200)
        self.assertIn('emails', passenger_json)
        self.assertIn('phone_numbers', passenger_json)
        self.assertEqual(len(passenger_json['emails']), 0)
        self.assertEqual(len(passenger_json['phone_numbers']), 0)

        state_passenger_url = get_passenger_url + '/state'
        response = requests.get(state_passenger_url, headers=headers)
        passenger_json = response.json()['data']['passenger']
        self.assertEqual(response.status_code, 200)
        self.assertIn('emails', passenger_json)
        self.assertIn('phone_numbers', passenger_json)
        self.assertEqual(len(passenger_json['emails']), 0)
        self.assertEqual(len(passenger_json['phone_numbers']), 0)

    def test_passenger_import_emails_phone_numbers(self):
        """
        verifies system is handling passenger_contact_info correctly when emails,
        and phone_numbers are null, and empty lists by calling test helper method
        """
        customer = 'Purple Rain Airlines'
        self._test_passenger_import_emails_phone_numbers(customer, [], [], False, False)
        self._test_passenger_import_emails_phone_numbers(customer, None, None, False, False)
        self._test_passenger_import_emails_phone_numbers(customer, [], None, False, False)
        self._test_passenger_import_emails_phone_numbers(customer, None, [], False, False)
        self._test_passenger_import_emails_phone_numbers(customer, [], [], True, True)
        self._test_passenger_import_emails_phone_numbers(customer, [], [], True, False)
        self._test_passenger_import_emails_phone_numbers(customer, [], [], False, True)
        self._test_passenger_import_emails_phone_numbers(customer, None, None, True, False)
        self._test_passenger_import_emails_phone_numbers(customer, None, None, False, True)

    def test_validate_pnr_create_date(self):
        """
        verifies system validates pnr_create_date is same for all passengers on a PNR
        """
        expected_error_message = 'All passengers on the PNR must have the same pnr_create_date'

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passenger_payload = self._generate_n_passenger_payload(2)

        passenger_payload[0].update(dict(
            pnr_create_date='2018-05-13'
        ))

        passenger_payload[1].update(dict(
            pnr_create_date='2018-05-14'
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', expected_error_message, [])

    def test_validate_existing_open_pnr(self):
        """
        verifies system validates imports for a open pnr that exist in the system.
        Test Outline:
        import a passenger.
        import a passenger in a separate import with the same pnr_create_date and pax_record_locator_group
        and then with the following different fields all in separate imports and verifies the correct
        error message is coming back: port_accommodation, pax_record_locator, hotel_accommodation, number_of_nights.
        Next successfully import the passenger into the PNR group. Then try to book just the first passenger via
        the passenger api and verify this does not succeed and validate the error message.
        Last book both passengers via the pax api and validate the response.
        """
        expected_port_error_message = 'All passengers on the PNR must have the same port_accommodation'
        expected_nights_error_message = 'All passengers on the PNR must have the same number_of_nights'
        expected_hotel_error_message = 'PNR contains passengers with different hotel accommodations.'
        expected_pnr_error_message = 'Request contains passengers on different PNRs.'
        expected_booking_error_message = 'Not all passengers in the PNR are being booked together.'

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passenger_payload_1 = self._generate_n_passenger_payload(1)
        passenger_payload_2 = self._generate_n_passenger_payload(1)

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_1)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)
        passenger_1 = response_json['data'][0]

        pnr_create_date = passenger_payload_1[0]['pnr_create_date']
        pnr_group = passenger_payload_1[0]['pax_record_locator_group']
        pnr_url = self._api_host + '/api/v1/pnr?pnr_create_date=' + pnr_create_date + '&pax_record_locator_group=' + pnr_group

        response = requests.get(pnr_url, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['error'], False)
        self.assertEqual(len(response_json['data']), 1)
        self.assertEqual(response_json['data'][0]['context_id'], passenger_payload_1[0]['context_id'])

        previous_port = str(passenger_payload_2[0]['port_accommodation'])
        previous_record_locator = str(passenger_payload_2[0]['pax_record_locator'])

        passenger_payload_2[0].update(dict(
            pax_record_locator=passenger_payload_1[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload_1[0]['pax_record_locator_group'],
            pnr_create_date=passenger_payload_1[0]['pnr_create_date'],
            port_accommodation='JFK'
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', expected_port_error_message, [])

        passenger_payload_2[0].update(dict(
            port_accommodation=previous_port,
            number_of_nights=2
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        # TODO: change to expected_nights_error_message once interface allows multi-night-booking (test will brake :D)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', expected_nights_error_message, [])

        passenger_payload_2[0].update(dict(
            number_of_nights=1,
            hotel_accommodation=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', expected_hotel_error_message, [])

        passenger_payload_2[0].update(dict(
            hotel_accommodation=True,
            pax_record_locator=previous_record_locator
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'INVALID_PNR_PASSENGER', expected_pnr_error_message, [])

        passenger_payload_2[0].update(dict(
            pax_record_locator=passenger_payload_1[0]['pax_record_locator']
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)

        response = requests.get(pnr_url, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['error'], False)
        self.assertEqual(len(response_json['data']), 2)

        has_context1 = False
        has_context2 = False

        if response_json['data'][0]['context_id'] == passenger_payload_1[0]['context_id']:
            has_context1 = True
        else:
            self.assertEqual(response_json['data'][0]['context_id'], passenger_payload_2[0]['context_id'])
            has_context2 = True

        if response_json['data'][1]['context_id'] == passenger_payload_1[0]['context_id']:
            has_context1 = True
        else:
            self.assertEqual(response_json['data'][1]['context_id'], passenger_payload_2[0]['context_id'])
            has_context2 = True

        self.assertTrue(has_context1)
        self.assertTrue(has_context2)

        hotel_offerings = self._get_passenger_hotel_offerings(passenger_1)
        self.assertGreaterEqual(len(hotel_offerings), 1)
        picked_hotel = hotel_offerings[0]

        booking_payload = dict(
            context_ids=[passenger_1['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1,
        )

        public_hotel_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passenger_1['ak1'] + '&ak2=' + passenger_1['ak2']
        hotel_resp = requests.post(public_hotel_url, json=booking_payload)
        self.assertEqual(hotel_resp.status_code, 400)
        hotel_resp_json = hotel_resp.json()
        log_error_system_tests_output(pretty_print_json(hotel_resp_json))
        self._validate_error_message(hotel_resp_json, 400, 'Bad Request', 'INVALID_BOOKING_REQUEST', expected_booking_error_message, [])

        booking_payload = dict(
            context_ids=[passenger_1['context_id'], passenger_payload_2[0]['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1,
        )

        public_hotel_url = self._api_host + '/api/v1/offer/hotels?ak1=' + passenger_1['ak1'] + '&ak2=' + passenger_1['ak2']
        hotel_resp = requests.post(public_hotel_url, json=booking_payload)
        self.assertEqual(hotel_resp.status_code, 200)
        hotel_resp_json = hotel_resp.json()
        self.assertEqual(len(hotel_resp_json['data']['passengers']), 2)

        has_context1 = False
        has_context2 = False

        for passenger in hotel_resp_json['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            if passenger['context_id'] == passenger_1['context_id']:
                has_context1 = True
            else:
                self.assertEqual(passenger['context_id'], passenger_payload_2[0]['context_id'])
                has_context2 = True

        self.assertTrue(has_context1)
        self.assertTrue(has_context2)

    def test_validate_existing_closed_pnr(self):
        """
        verifies system validate imports for a closed pnr that exist in the system
        """
        expected_mismatch_error_message = 'All passengers on the PNR must have the same port_accommodation'
        expected_pnr_closed_error_message = 'PNR already in a finalized state. Passengers cannot be added to the PNR group.'

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passenger_payload_1 = self._generate_n_passenger_payload(1)
        passenger_payload_2 = self._generate_n_passenger_payload(1)

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_1)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)
        passenger_1 = response_json['data'][0]

        passenger_payload_2[0].update(dict(
            pax_record_locator=passenger_payload_1[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload_1[0]['pax_record_locator_group'],
            pnr_create_date=passenger_payload_1[0]['pnr_create_date'],
            port_accommodation='JFK',
            number_of_nights=2
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', expected_mismatch_error_message, [])

        hotel_offerings = self._get_passenger_hotel_offerings(passenger_1)
        self.assertGreaterEqual(len(hotel_offerings), 1)
        picked_hotel = hotel_offerings[0]
        self._passenger_book_hotel(passenger_1, picked_hotel, [passenger_1['context_id']])

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PNR_ALREADY_FINALIZED', expected_pnr_closed_error_message, [])

    def test_validate_existing_closed_pnr_meal_only(self):
        """
        verifies system validates imports for a closed pnr that exist in the system
        """
        expected_mismatch_error_message = 'All passengers on the PNR must have the same port_accommodation'
        expected_pnr_closed_error_message = 'PNR already in a finalized state. Passengers cannot be added to the PNR group.'

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passenger_payload_1 = self._generate_n_passenger_payload(1)
        passenger_payload_2 = self._generate_n_passenger_payload(1)

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_1)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['error'], False)
        passenger_1 = response_json['data'][0]

        passenger_payload_2[0].update(dict(
            pax_record_locator=passenger_payload_1[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload_1[0]['pax_record_locator_group'],
            pnr_create_date=passenger_payload_1[0]['pnr_create_date'],
            port_accommodation='JFK',
            hotel=False
        ))

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_INFO_MISMATCH', expected_mismatch_error_message, [])

        hotel_offerings = self._get_passenger_hotel_offerings(passenger_1)
        self.assertGreaterEqual(len(hotel_offerings), 1)
        picked_hotel = hotel_offerings[0]
        self._passenger_book_hotel(passenger_1, picked_hotel, [passenger_1['context_id']])

        response = requests.post(passenger_url, headers=headers, json=passenger_payload_2)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PNR_ALREADY_FINALIZED', expected_pnr_closed_error_message, [])

    def test_send_dict_only_on_import(self):
        """
        validates system is not crashing and not returning unknown 500 error when import receives and object
        instead of a list of objects and returns a 400 error.
        """
        expected_error_message = 'We did not receive a list of passengers. Please send up a valid list of passenger objects.'

        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        import_url = self._api_host + '/api/v1/passenger'
        passengers = self._generate_n_passenger_payload(1)

        resp = requests.post(url=import_url, headers=headers, json={})  # send empty dict instead of list(dict)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        log_error_system_tests_output(pretty_print_json(resp_json))
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', expected_error_message, [])

        resp = requests.post(url=import_url, headers=headers, json=passengers[0])  # send dict instead of list(dict)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        log_error_system_tests_output(pretty_print_json(resp_json))
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', expected_error_message, [])

    def test_supported_meal_currencies(self):
        """
        system test to validate meal vouchers can be crated for GDP, EUR, and CAD
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        voucher_url = self._api_host + '/api/v1/voucher/'

        supported_meal_currencies = ['USD', 'CAD', 'EUR', 'GBP']
        for currency in supported_meal_currencies:
            voucher_id = self._create_2_passengers(customer,
                                                   meals=[{'meal_amount': 12, 'currency_code': currency, 'number_of_days': 1}],
                                                   hotel_accommodation=False)[0]['voucher_id']

            resp = requests.get(headers=headers, url=voucher_url + voucher_id).json()
            self.assertEqual(resp['data']['voucher_id'], voucher_id)

            for passenger in resp['data']['passengers']:
                for meal in passenger['meal_vouchers']:
                    self.assertEqual(meal['currency_code'], currency)

    def test_validate_first_name_last_name_length(self):
        """
        test validating length restriction of first and last name on passenger
        """
        name_length_51 = 'agoodnamethatisdefinitelyaboutfifty1charactersmannn'
        name_length_50 = 'agoodnamethatisdefinitelyaboutfiftycharactersmannn'

        customer = 'Purple Rain Airlines'
        url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer=customer)
        passengers = self._generate_2_passenger_payload()

        passengers[0].update(dict(
            first_name=name_length_51
        ))

        resp = requests.post(url, headers=headers, json=passengers)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[0].first_name', 'message': 'Ensure this field has no more than 50 characters.'}])

        passengers[0].update(dict(
            first_name=name_length_50
        ))

        passengers[1].update(dict(
            last_name=name_length_51
        ))

        resp = requests.post(url, headers=headers, json=passengers)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.',
                                     [{'field': '[1].last_name', 'message': 'Ensure this field has no more than 50 characters.'}])

        passengers[1].update(dict(
            last_name=name_length_50
        ))

        resp = requests.post(url, headers=headers, json=passengers)
        self.assertEqual(resp.status_code, 201)
        pax_data = resp.json()['data']
        self.assertEqual(len(pax_data), 2)
        for passenger in pax_data:
            if passenger['context_id'] == passengers[0]['context_id']:
                self.assertEqual(passenger['first_name'], name_length_50)
                self.assertEqual(len(passenger['first_name']), 50)
                self.assertNotEqual(passenger['last_name'], name_length_50)
            else:
                self.assertEqual(passenger['last_name'], name_length_50)
                self.assertEqual(len(passenger['last_name']), 50)
                self.assertNotEqual(passenger['first_name'], name_length_50)

    def test_validate_port_origin_can_be_port_not_in_system(self):
        """
        test validating that Passenger.port_origin can be a port not in our system
        """
        self._create_2_passengers('Purple Rain Airlines', port_origin='012')  # validation done on method call

    def test_validate_number_of_nights(self):
        """
        test number_of_nights can be from range 0 to 7
        """
        headers = self._generate_airline_headers('Purple Rain Airlines')
        url = self._api_host + '/api/v1/passenger'

        pax1 = self._create_2_passengers(customer='Purple Rain Airlines', hotel_accommodation=False, number_of_nights=0)
        pax2 = self._create_2_passengers(customer='Purple Rain Airlines', hotel_accommodation=False, number_of_nights=1)
        pax3 = self._create_2_passengers(customer='Purple Rain Airlines', hotel_accommodation=False, number_of_nights=7)

        for pax in pax1:
            UUID(pax['voucher_id'], version=4)
            self.assertEqual(pax['number_of_nights'], 0)

        for pax in pax2:
            UUID(pax['voucher_id'], version=4)
            self.assertEqual(pax['number_of_nights'], 1)

        for pax in pax3:
            UUID(pax['voucher_id'], version=4)
            self.assertEqual(pax['number_of_nights'], 7)

        payload = self._generate_n_passenger_payload(1)
        payload[0].update(dict(
            number_of_nights=-1
        ))
        resp = requests.post(url=url, headers=headers, json=payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.', [{'message': 'Ensure this value is greater than or equal to 0.', 'field': '[0].number_of_nights'}])

        payload = self._generate_n_passenger_payload(1)
        payload[0].update(dict(
            number_of_nights=0
        ))
        resp = requests.post(url=url, headers=headers, json=payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_ACCOMMODATION', 'number_of_nights must be greater than 0 for passengers with hotel_accommodations.', [])

        payload = self._generate_n_passenger_payload(1)
        payload[0].update(dict(
            number_of_nights=8
        ))
        resp = requests.post(url=url, headers=headers, json=payload)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_INPUT', 'Invalid input criteria for passenger import.', [{'message': 'Ensure this value is less than or equal to 7.', 'field': '[0].number_of_nights'}])

    def test_validate_passenger_import_phone_numbers(self):
        """
        validate passenger import endpoint forces correct phone_number input
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            phone_numbers=['15591234567']
        ))

        resp = requests.post(url=passenger_url, json=passenger_payload, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': "phone number must be in the E.164 format and always start with a '+'. Expected format: '+{country_code}{subscriber_phone_number}', no spaces or symbols.", 'field': '[0].phone_numbers[0]'}])

        passenger_payload[0].update(dict(
            phone_numbers=['+155912345679819851651654165373546816581650651']
        ))

        resp = requests.post(url=passenger_url, json=passenger_payload, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'message': "phone number must be in the E.164 format and always start with a '+'. Expected format: '+{country_code}{subscriber_phone_number}', no spaces or symbols.", 'field': '[0].phone_numbers[0]'}, {'field': '[0].phone_numbers[0]', 'message': 'Ensure this field has no more than 16 characters.'}])

    def test_validate_passenger_import_emails(self):
        """
        validate passenger import endpoint forces correct email input
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            emails=['testblackholetravellianceinc.com']
        ))

        resp = requests.post(url=passenger_url, json=passenger_payload, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'field': '[0].emails[0]', 'message': 'Enter a valid email address.'}])

        passenger_payload[0].update(dict(
            emails=['testareallylongnameyoukowwhatImeanonthenotificationsendpointyadadad@blackhole.travellianceinc.com']
        ))

        resp = requests.post(url=passenger_url, json=passenger_payload, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger import.',
                                     [{'field': '[0].emails[0]', 'message': 'Ensure this field has no more than 45 characters.'}])
