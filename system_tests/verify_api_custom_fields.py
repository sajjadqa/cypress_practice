from uuid import UUID

import requests

from StormxApp.tests.data_utilities import (
    generate_flight_number,
    generate_pax_record_locator,
    generate_pax_record_locator_group,
)
from stormx_verification_framework import (
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output
)


class TestApiCustomFields(StormxSystemVerification):
    """
    Verify passenger import input validation and functionality for custom fields.
    """
    selected_environment_name = None
    ALWAYS_PRESENT_CUSTOM_FIELD_NAMES = [
        'disrupt_type',
    ]
    OPTIONAL_CUSTOM_FIELD_NAMES = [
        'system_id',
        'custom_field_1',
        'custom_field_2',
        'custom_field_3',
        'custom_field_4',
    ]
    CUSTOM_FIELD_NAMES = ALWAYS_PRESENT_CUSTOM_FIELD_NAMES + OPTIONAL_CUSTOM_FIELD_NAMES
    @classmethod
    def setUpClass(cls):
        super(TestApiCustomFields, cls).setUpClass()

    def test_passenger_import_custom_fields(self):
        """
        verifies that custom fields are handled properly on import.
        """
        for custom_field_name in self.ALWAYS_PRESENT_CUSTOM_FIELD_NAMES:
            self._test_passenger_import_custom_fields(custom_field_name, field_always_present=True)
        for custom_field_name in self.OPTIONAL_CUSTOM_FIELD_NAMES:
            self._test_passenger_import_custom_fields(custom_field_name, field_always_present=False)

    def _test_passenger_import_custom_fields(self, custom_field_name, field_always_present):
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers_payload = self._generate_n_passenger_payload(
            2,
            flight_number=generate_flight_number(),
            disrupt_type='',
        )
        passenger_with_custom_field = passengers_payload[0]
        context_id_custom = passenger_with_custom_field['context_id']
        passenger_without_custom_field = passengers_payload[1]
        context_id_not_custom = passenger_without_custom_field['context_id']
        pnr_create_date = passenger_with_custom_field['pnr_create_date']
        pax_record_locator_group = passenger_with_custom_field['pax_record_locator_group']
        flight_number = passenger_with_custom_field['flight_number']
        flight_search_params = {
            'flight_number': passenger_with_custom_field['flight_number'],
            'disrupt_depart': passenger_with_custom_field['disrupt_depart'],
            'port_accommodation': passenger_with_custom_field['port_accommodation'],
        }

        CUSTOM_VALUE = 'Lorem ipsum dolor sit amet, <BLAH BLAH 234 -)#%^cZ'
        passenger_with_custom_field[custom_field_name] = CUSTOM_VALUE
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)

        # verify field is properly returned/hidden in the passenger import response ----
        first_passenger = [p for p in response_json['data']
                           if p['context_id'] == context_id_custom][0]
        second_passenger = [p for p in response_json['data']
                            if p['context_id'] == context_id_not_custom][0]
        self.assertEqual(first_passenger[custom_field_name], CUSTOM_VALUE)
        if field_always_present:
            self.assertEqual(second_passenger[custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, second_passenger)

        # verify field is properly returned/hidden in the passenger lookup response ----
        url_pattern = self._api_host + '/api/v1/passenger/{context_id}'
        response_json = requests.get(url_pattern.format(context_id=context_id_custom), headers=headers).json()
        self.assertEqual(response_json['data'][custom_field_name], CUSTOM_VALUE)
        response_json = requests.get(url_pattern.format(context_id=context_id_not_custom), headers=headers).json()
        if field_always_present:
            self.assertEqual(response_json['data'][custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, response_json['data'])

        # verify field is properly returned/hidden in the related passenger lookup response ----
        url_pattern = self._api_host + '/api/v1/passenger/{context_id}/related'
        response_json = requests.get(url_pattern.format(context_id=context_id_custom), headers=headers).json()
        if field_always_present:
            self.assertEqual(response_json['data'][0][custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, response_json['data'][0])
        response_json = requests.get(url_pattern.format(context_id=context_id_not_custom), headers=headers).json()
        self.assertEqual(response_json['data'][0][custom_field_name], CUSTOM_VALUE)


        # verify field is properly returned/hidden in the passenger full state ----
        url_pattern = self._api_host + '/api/v1/passenger/{context_id}/state'
        response_json = requests.get(url_pattern.format(context_id=context_id_custom), headers=headers).json()
        self.assertEqual(response_json['data']['passenger'][custom_field_name], CUSTOM_VALUE)
        response_json = requests.get(url_pattern.format(context_id=context_id_not_custom), headers=headers).json()
        if field_always_present:
            self.assertEqual(response_json['data']['passenger'][custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, response_json['data']['passenger'])


        # verify field is properly returned/hidden in the PNR search ----
        url = self._api_host + '/api/v1/pnr'
        params = {'pax_record_locator_group': pax_record_locator_group, 'pnr_create_date': pnr_create_date}
        response_json = requests.get(url, headers=headers, params=params).json()
        first_passenger = [p for p in response_json['data']
                           if p['context_id'] == context_id_custom][0]
        second_passenger = [p for p in response_json['data']
                            if p['context_id'] == context_id_not_custom][0]
        self.assertEqual(first_passenger[custom_field_name], CUSTOM_VALUE)
        if field_always_present:
            self.assertEqual(second_passenger[custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, second_passenger)

        # verify field is properly returned/hidden in the PNR search ----
        url = self._api_host + '/api/v1/passenger'

        response_json = requests.get(url, headers=headers, params=flight_search_params).json()
        first_passenger = [p for p in response_json['data']
                           if p['context_id'] == context_id_custom][0]
        second_passenger = [p for p in response_json['data']
                            if p['context_id'] == context_id_not_custom][0]
        self.assertEqual(first_passenger[custom_field_name], CUSTOM_VALUE)
        if field_always_present:
            self.assertEqual(second_passenger[custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, second_passenger)


        # verify that pax app is able to present/hide the custom field ----
        passenger_offer_url = first_passenger['offer_url']
        response = requests.get(passenger_offer_url, headers=headers)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertEqual(embedded_json['passenger'][custom_field_name], CUSTOM_VALUE)
        if field_always_present:
            self.assertEqual(embedded_json['other_passengers'][0][custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, embedded_json['other_passengers'][0])

        passenger_offer_url = second_passenger['offer_url']
        response = requests.get(passenger_offer_url, headers=headers)
        embedded_json = self._get_landing_page_embedded_json(response)
        if field_always_present:
            self.assertEqual(embedded_json['passenger'][custom_field_name], '')
        else:
            self.assertNotIn(custom_field_name, embedded_json['passenger'])
        self.assertEqual(embedded_json['other_passengers'][0][custom_field_name], CUSTOM_VALUE)

        # verify that booking response does NOT contain the custom field ----
        hotel_offerings = self._get_passenger_hotel_offerings(first_passenger)
        self.assertGreater(len(hotel_offerings), 0)
        booking_response_data = self._airline_book_hotel(customer, hotel_offerings[0],
                                                         [context_id_custom, context_id_not_custom])
        pax1_custom = [p for p in booking_response_data['passengers']
                           if p['context_id'] == context_id_custom][0]
        pax2_not_custom = [p for p in booking_response_data['passengers']
                            if p['context_id'] == context_id_not_custom][0]
        self.assertNotIn(custom_field_name, pax1_custom)
        self.assertNotIn(custom_field_name, pax2_not_custom)

    def test_passenger_import_custom_fields__too_long(self):
        """
        verifies that custom fields are validated correctly.
        """
        for custom_field_name in self.CUSTOM_FIELD_NAMES:
            self._test_import_custom_fields__too_long(custom_field_name)

    def _test_import_custom_fields__too_long(self, custom_field_name):
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # verify field length is properly validated in the passenger import response ----
        passengers_payload = self._generate_n_passenger_payload(1, **{custom_field_name: 'X' * 51})  # too long.
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['meta']['error_description'], 'Invalid input criteria for passenger import.')
        self.assertEqual(
            response_json['meta']['error_detail'],
            [{'field': '[0].' + custom_field_name, 'message': 'Ensure this field has no more than 50 characters.'}])
        self.assertEqual(response_json['meta']['message'], 'Bad Request')
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

    def test_passenger_import_custom_fields__null(self):
        """
        verifies that custom fields cannot be submitted as null.
        """
        for custom_field_name in self.CUSTOM_FIELD_NAMES:
            self._test_passenger_import_custom_fields__null(custom_field_name)

    def _test_passenger_import_custom_fields__null(self, custom_field_name):
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # verify field length is properly validated in the passenger import response ----
        passengers_payload = self._generate_n_passenger_payload(1, **{custom_field_name: None})
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['meta']['error_description'], 'Invalid input criteria for passenger import.')
        self.assertEqual(
            response_json['meta']['error_detail'],
            [{'field': '[0].' + custom_field_name, 'message': 'This field may not be null.'}])
        self.assertEqual(response_json['meta']['message'], 'Bad Request')
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

    def test_passenger_import_custom_fields__blank(self):
        """
        verifies that custom fields may contain an empty string.
        """
        for custom_field_name in self.CUSTOM_FIELD_NAMES:
            self._test_passenger_import_custom_fields__blank(custom_field_name)

    def _test_passenger_import_custom_fields__blank(self, custom_field_name):
        url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # verify field length is properly validated in the passenger import response ----
        passengers_payload = self._generate_n_passenger_payload(1, **{custom_field_name: ''})
        response = requests.post(url, headers=headers, json=passengers_payload)
        response_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['data'][0][custom_field_name], '')
