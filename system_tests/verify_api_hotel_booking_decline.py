
import copy
import json
import unittest

import requests

from StormxApp.tests.data_utilities import (
    generate_context_id,
    generate_pax_record_locator,
    generate_pax_record_locator_group,
    generate_flight_number,
    MOST_PASSENGERS_IN_LARGEST_AIRCRAFT
)

import pytz
import datetime
from uuid import UUID
from decimal import Decimal
from StormxApp.constants import StormxConstants


from stormx_verification_framework import (
    StormxSystemVerification,
    log_error_system_tests_output,
    passenger_sanitized_fields,
    pretty_print_json,
)


class TestApiHotelBookingDecline(StormxSystemVerification):
    """
    Verify functionality related to declining hotel offers.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelBookingDecline, cls).setUpClass()

    def test_passenger_decline_offer(self):
        """
        verify that passenger can decline to take the offered accommodations.
        """
        url_template = self._api_host + '/api/v1/passenger/{context_id}/decline'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer)
        passenger = passengers[0]
        context_id = passenger['context_id']
        context_id2 = passengers[1]['context_id']
        self.assertTrue(context_id)
        self.assertTrue(context_id2)
        self.assertNotEqual(context_id, context_id2)
        url = url_template.format(context_id=context_id)
        response = requests.put(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['meta']['message'], 'UPDATED')

        voucher_id = response_json['data']['voucher_id']
        UUID(voucher_id, version=4)
        expected_declined_date = response_json['data']['passengers'][0]['declined_date']
        self.assertIsNotNone(expected_declined_date)
        for passenger in response_json['data']['passengers']:
            self.assertEqual(len(response_json['data']['passengers']), 1)
            self.assertEqual(passenger['context_id'], context_id)
            self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertEqual(passenger['declined_date'], expected_declined_date)
            self.assertIsNone(passenger['canceled_date'])

        voucher_resp = requests.get(url=self._api_host + '/api/v1/voucher/' + voucher_id, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)
        voucher_resp_json = voucher_resp.json()
        for passenger in voucher_resp_json['data']['passengers']:
            self.assertEqual(len(voucher_resp_json['data']['passengers']), 1)
            self.assertEqual(passenger['context_id'], context_id)
            self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertIn('offer_opened_date', passenger)
            self.assertIn('declined_date', passenger)
            self.assertIn('canceled_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])
            self.assertEqual(passenger['declined_date'], expected_declined_date)
            self.assertIsNone(passenger['canceled_date'])

        passenger1_url = self._api_host + '/api/v1/passenger/' + context_id
        pax1_resp = requests.get(passenger1_url, headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        pax1_resp_json = pax1_resp.json()
        self.assertEqual(pax1_resp_json['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(pax1_resp_json['data']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(pax1_resp_json['data']['transport_accommodation_status'])
        self.assertEqual(pax1_resp_json['data']['declined_date'], expected_declined_date)

        passenger2_url = self._api_host + '/api/v1/passenger/' + context_id2
        pax2_resp = requests.get(passenger2_url, headers=headers)
        self.assertEqual(pax2_resp.status_code, 200)
        pax2_resp_json = pax2_resp.json()
        self.assertEqual(pax2_resp_json['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(pax2_resp_json['data']['meal_accommodation_status'], 'offered')
        self.assertIsNone(pax2_resp_json['data']['transport_accommodation_status'])
        self.assertIsNone(pax2_resp_json['data']['declined_date'])

        full_state_1 = self._api_host + '/api/v1/passenger/{context_id}/state'.format(context_id=context_id)
        full_state_2 = self._api_host + '/api/v1/passenger/{context_id}/state'.format(context_id=context_id2)
        full_state_1_response = requests.get(full_state_1, headers=headers)
        full_state_1_response_json = full_state_1_response.json()
        full_state_2_response = requests.get(full_state_2, headers=headers)
        full_state_2_response_json = full_state_2_response.json()

        self.assertEqual(full_state_1_response.status_code, 200)
        self.assertIs(full_state_1_response_json['error'], False)
        self.assertEqual(full_state_1_response_json['meta']['message'], 'OK')
        self.assertIsNone(full_state_1_response_json['data']['voucher']['hotel_voucher'])

        self.assertEqual(full_state_2_response.status_code, 200)
        self.assertIs(full_state_2_response_json['error'], False)
        self.assertEqual(full_state_2_response_json['meta']['message'], 'OK')
        self.assertIsNone(full_state_2_response_json['data']['voucher']['hotel_voucher'])

    def test_offer_decline(self):
        """
        tests the happy path for the offer/decline endpoint
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        decline_url = self._api_host + '/api/v1/offer/decline'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)

        import_response_json = requests.post(passenger_url, headers=headers, json=passenger_payload).json()

        self.assertEqual(import_response_json['data'][0]['hotel_accommodation_status'], 'offered')
        self.assertEqual(import_response_json['data'][0]['meal_accommodation_status'], 'offered')
        self.assertIsNone(import_response_json['data'][0]['transport_accommodation_status'])

        ak1 = import_response_json['data'][0]['ak1']
        ak2 = import_response_json['data'][0]['ak2']

        passenger_headers = self._generate_passenger_headers()
        response = requests.put(decline_url + '?ak1=' + ak1 + '&ak2=' + ak2, headers=passenger_headers)
        self.assertEqual(response.status_code, 200)
        decline_response_json = response.json()
        self.assertEqual(decline_response_json['data']['passengers'][0]['hotel_accommodation_status'], 'declined')
        self.assertEqual(decline_response_json['data']['passengers'][0]['meal_accommodation_status'], 'accepted')
        self.assertIsNone(decline_response_json['data']['passengers'][0]['transport_accommodation_status'])

    def test_valid_offer_decline(self):
        """
        verifies the system is checking that all passengers
        for the offer/decline endpoint are in a state of offered
        """
        expected_error_message = 'Passenger offer has already been accepted, declined or canceled.'

        passenger_url = self._api_host + '/api/v1/passenger'
        decline_url = self._api_host + '/api/v1/offer/decline'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update({
            'hotel_accommodation': False
        })
        import_response_json = requests.post(passenger_url, headers=headers, json=passenger_payload).json()

        ak1 = import_response_json['data'][0]['ak1']
        ak2 = import_response_json['data'][0]['ak2']

        passenger_headers = self._generate_passenger_headers()
        response = requests.put(decline_url + '?ak1=' + ak1 + '&ak2=' + ak2, headers=passenger_headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_CANNOT_DECLINE', expected_error_message, [])

    def test_valid_passenger_decline(self):
        """
        verifies the system is checking that all passengers
        for the passenger/decline endpoint are in a state of offered
        """
        expected_error_message = 'Passenger offer has already been accepted, declined or canceled.'

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update({
            'hotel_accommodation': False
        })

        import_response_json = requests.post(passenger_url, headers=headers, json=passenger_payload).json()
        self.assertEqual(import_response_json['meta']['status'], 201)
        context_id = import_response_json['data'][0]['context_id']

        decline_url = passenger_url + '/' + context_id + '/decline'
        response = requests.put(decline_url, headers=headers)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'PASSENGER_CANNOT_DECLINE', expected_error_message, [])


    def test_offer_decline_multiple_passengers(self):
        """
        tests the happy path for the offer/decline endpoint for multiple passengers on pnr
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        decline_url = self._api_host + '/api/v1/offer/decline'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)

        import_response_json = requests.post(passenger_url, headers=headers, json=passenger_payload).json()

        ak1 = import_response_json['data'][0]['ak1']
        ak2 = import_response_json['data'][0]['ak2']

        passenger_headers = self._generate_passenger_headers()
        response = requests.put(decline_url + '?ak1=' + ak1 + '&ak2=' + ak2, headers=passenger_headers)
        self.assertEqual(response.status_code, 200)

        for passenger in response.json()['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertEqual(passenger['transport_accommodation_status'], None)

        passenger_1 = import_response_json['data'][0]
        passenger_2 = import_response_json['data'][1]

        passenger_1_resp = requests.get(passenger_url + '/' + passenger_1['context_id'], headers=headers).json()
        passenger_2_resp = requests.get(passenger_url + '/' + passenger_2['context_id'], headers=headers).json()
        self.assertEqual(passenger_1_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_1_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_1_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_2_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_2_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_2_resp['data']['transport_accommodation_status'], None)

        voucher_id = passenger_1_resp['data']['voucher_id']
        voucher_url = self._api_host + '/api/v1/voucher/' + str(voucher_id)
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        passengers = voucher_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertEqual(len(passenger['meal_vouchers']), 2)

    def test_passenger_decline_multiple_passengers(self):
        """
        tests the happy path for the passenger/decline endpoint for multiple passengers on pnr
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)

        import_response_json = requests.post(passenger_url, headers=headers, json=passenger_payload).json()

        passenger_1 = import_response_json['data'][0]
        passenger_2 = import_response_json['data'][1]

        response = requests.put(passenger_url + '/' + passenger_1['context_id'] + '/decline?include_pnr=True', headers=headers)
        self.assertEqual(response.status_code, 200)

        voucher_json_data = response.json()['data']
        self.assertIn('modified_date', voucher_json_data)
        self.assertEqual(voucher_json_data['status'], 'finalized')

        for passenger in response.json()['data']['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertEqual(passenger['transport_accommodation_status'], None)
            for meal in passenger['meal_vouchers']:
                UUID(meal['id'], version=4)

        passenger_1_resp = requests.get(passenger_url + '/' + passenger_1['context_id'], headers=headers).json()
        passenger_2_resp = requests.get(passenger_url + '/' + passenger_2['context_id'], headers=headers).json()
        self.assertEqual(passenger_1_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_1_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_1_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_2_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_2_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_2_resp['data']['transport_accommodation_status'], None)

        voucher_id = passenger_1_resp['data']['voucher_id']
        voucher_url = self._api_host + '/api/v1/voucher/' + str(voucher_id)
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        passengers = voucher_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])
            self.assertEqual(len(passenger['meal_vouchers']), 2)
            for meal in passenger['meal_vouchers']:
                UUID(meal['id'], version=4)

        voucher_json_data = voucher_resp.json()['data']
        self.assertIn('modified_date', voucher_json_data)
        self.assertEqual(voucher_json_data['status'], 'finalized')

    def test_passenger_decline_include_pnr(self):
        """
        tests include_pnr query_string for the passenger/decline endpoint for multiple passengers on pnr
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(4)

        import_response_json = requests.post(passenger_url, headers=headers, json=passenger_payload).json()

        passenger_1 = import_response_json['data'][0]
        passenger_2 = import_response_json['data'][1]
        passenger_3 = import_response_json['data'][2]
        passenger_4 = import_response_json['data'][3]

        response = requests.put(passenger_url + '/' + passenger_1['context_id'] + '/decline', headers=headers)
        self.assertEqual(response.status_code, 200)
        passengers = response.json()['data']['passengers']
        self.assertEqual(len(passengers), 1)
        self.assertEqual(passengers[0]['context_id'], passenger_1['context_id'])

        passenger_1_resp = requests.get(passenger_url + '/' + passenger_1['context_id'], headers=headers).json()
        passenger_2_resp = requests.get(passenger_url + '/' + passenger_2['context_id'], headers=headers).json()
        passenger_3_resp = requests.get(passenger_url + '/' + passenger_3['context_id'], headers=headers).json()
        passenger_4_resp = requests.get(passenger_url + '/' + passenger_4['context_id'], headers=headers).json()
        self.assertEqual(passenger_1_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_1_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_1_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_2_resp['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_2_resp['data']['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger_2_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_3_resp['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_3_resp['data']['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger_3_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_4_resp['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_4_resp['data']['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger_4_resp['data']['transport_accommodation_status'], None)

        response2 = requests.put(passenger_url + '/' + passenger_2['context_id'] + '/decline?include_pnr=False', headers=headers)
        self.assertEqual(response2.status_code, 200)
        passengers2 = response2.json()['data']['passengers']
        self.assertEqual(len(passengers2), 1)
        self.assertEqual(passengers2[0]['context_id'], passenger_2['context_id'])

        passenger_2_resp = requests.get(passenger_url + '/' + passenger_2['context_id'], headers=headers).json()
        passenger_3_resp = requests.get(passenger_url + '/' + passenger_3['context_id'], headers=headers).json()
        passenger_4_resp = requests.get(passenger_url + '/' + passenger_4['context_id'], headers=headers).json()
        self.assertEqual(passenger_2_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_2_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_2_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_3_resp['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_3_resp['data']['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger_3_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_4_resp['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_4_resp['data']['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger_4_resp['data']['transport_accommodation_status'], None)

        response3 = requests.put(passenger_url + '/' + passenger_3['context_id'] + '/decline?include_pnr=True', headers=headers)
        self.assertEqual(response3.status_code, 200)
        passengers3 = response3.json()['data']['passengers']
        self.assertEqual(len(passengers3), 2)
        self.assertIn(passengers3[0]['context_id'], [passenger_3['context_id'], passenger_4['context_id']])
        self.assertIn(passengers3[1]['context_id'], [passenger_3['context_id'], passenger_4['context_id']])

        passenger_3_resp = requests.get(passenger_url + '/' + passenger_3['context_id'], headers=headers).json()
        passenger_4_resp = requests.get(passenger_url + '/' + passenger_4['context_id'], headers=headers).json()
        self.assertEqual(passenger_3_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_3_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_3_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_4_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_4_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_4_resp['data']['transport_accommodation_status'], None)

    def test_passenger_decline_multiple_passengers_diff_group(self):
        """
        verify passengers with different pnr_group for the passenger/decline endpoint do not all get declined together.
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(3)
        passenger_payload[2].update(dict(
            pax_record_locator_group=generate_pax_record_locator_group()
        ))

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)

        passenger_1 = passenger_payload[0]
        passenger_2 = passenger_payload[1]
        passenger_3 = passenger_payload[2]

        response = requests.put(passenger_url + '/' + passenger_1['context_id'] + '/decline?include_pnr=True', headers=headers)
        self.assertEqual(response.status_code, 200)

        passenger_1_resp = requests.get(passenger_url + '/' + passenger_1['context_id'], headers=headers).json()
        passenger_2_resp = requests.get(passenger_url + '/' + passenger_2['context_id'], headers=headers).json()
        passenger_3_resp = requests.get(passenger_url + '/' + passenger_3['context_id'], headers=headers).json()
        self.assertEqual(passenger_1_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_1_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_1_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_2_resp['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(passenger_2_resp['data']['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger_2_resp['data']['transport_accommodation_status'], None)
        self.assertEqual(passenger_3_resp['data']['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger_3_resp['data']['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger_3_resp['data']['transport_accommodation_status'], None)

    def test_airline_decline_hotel_only(self):
        """
        ensures system has correct accommodation level statuses for declining a hotel with no meals
        via airline api
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)

        passenger = import_resp.json()['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        decline_resp = requests.put(passenger_url + '/' + passenger['context_id'] + '/decline', headers=headers)
        self.assertEqual(decline_resp.status_code, 200)

        decline_resp_json_data = decline_resp.json()['data']['passengers'][0]
        self.assertEqual(decline_resp_json_data['hotel_accommodation_status'], 'declined')
        self.assertEqual(decline_resp_json_data['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(decline_resp_json_data['transport_accommodation_status'])

    def test_offer_decline_hotel_only(self):
        """
        ensures system has correct accommodation level statuses for declining a hotel with no meals
        via pax api
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)

        passenger = import_resp.json()['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        decline_offer_url = self._api_host + '/api/v1/offer/decline?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        decline_resp = requests.put(decline_offer_url)
        self.assertEqual(decline_resp.status_code, 200)

        decline_resp_json_data = decline_resp.json()['data']['passengers'][0]
        self.assertEqual(decline_resp_json_data['hotel_accommodation_status'], 'declined')
        self.assertEqual(decline_resp_json_data['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(decline_resp_json_data['transport_accommodation_status'])

    def test_valid_airline_decline_meals_single_pax(self):
        """
        ensures system is declining meals for valid use cases for single pax
        """
        expected_error_message = 'Passenger cannot decline meals. No meals were offered to Passenger.'

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)

        passenger = import_resp.json()['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        decline_resp = requests.put(passenger_url + '/' + passenger['context_id'] + '/decline?meals=true', headers=headers)
        self.assertEqual(decline_resp.status_code, 400)
        decline_resp_json = decline_resp.json()
        log_error_system_tests_output(pretty_print_json(decline_resp_json))
        self._validate_error_message(decline_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_DECLINE', expected_error_message, [])

    def test_airline_decline_meals_single_pax(self):
        """
        ensures system can decline meals via airline api for a single pax
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)

        passenger = import_resp.json()['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        decline_resp = requests.put(passenger_url + '/' + passenger['context_id'] + '/decline?meals=true', headers=headers)
        self.assertEqual(decline_resp.status_code, 200)

        decline_resp_json_data = decline_resp.json()['data']['passengers'][0]
        self.assertEqual(decline_resp_json_data['hotel_accommodation_status'], 'declined')
        self.assertEqual(decline_resp_json_data['meal_accommodation_status'], 'declined')
        self.assertIsNone(decline_resp_json_data['transport_accommodation_status'])

    def test_passenger_api_cannot_decline_meals(self):
        """
        verifies passenger api cannot decline meals
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(1)

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)

        passenger = import_resp.json()['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        decline_offer_url = self._api_host + '/api/v1/offer/decline?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2'] + '&meals=true'
        decline_resp = requests.put(decline_offer_url)
        self.assertEqual(decline_resp.status_code, 200)

        decline_resp_json_data = decline_resp.json()['data']['passengers'][0]
        self.assertEqual(decline_resp_json_data['hotel_accommodation_status'], 'declined')
        self.assertEqual(decline_resp_json_data['meal_accommodation_status'], 'accepted')
        self.assertIsNone(decline_resp_json_data['transport_accommodation_status'])

    def test_airline_decline_meals_include_pnr(self):
        """
        ensures system can decline meals via airline api for a 2 person pnr
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)
        passengers = import_resp.json()['data']
        self.assertEqual(len(passengers), 2)

        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

        decline_resp = requests.put(passenger_url + '/' + passengers[0]['context_id'] + '/decline?include_pnr=true&meals=true', headers=headers)
        self.assertEqual(decline_resp.status_code, 200)

        passengers = decline_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
            self.assertEqual(passenger['meal_accommodation_status'], 'declined')
            self.assertIsNone(passenger['transport_accommodation_status'])

    def test_valid_airline_decline_meals_multiple_pax(self):
        """
        ensures system is declining meals for valid use cases for multiple pax
        """
        expected_error_message = 'Passenger cannot decline meals. No meals were offered to Passenger.'

        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))
        passenger_payload[1].update(dict(
            meal_accommodation=False
        ))

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)

        passengers = import_resp.json()['data']
        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

        decline_resp = requests.put(passenger_url + '/' + passengers[0]['context_id'] + '/decline?meals=true', headers=headers)
        self.assertEqual(decline_resp.status_code, 400)
        decline_resp_json = decline_resp.json()
        log_error_system_tests_output(pretty_print_json(decline_resp_json))
        self._validate_error_message(decline_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_DECLINE', expected_error_message, [])

    def test_airline_decline_include_pnr_one_pax_meal_create(self):
        """
        ensures system can decline hotels and create meal vouchers for one pax only
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[1].update(dict(
            meal_accommodation=False,
            pax_record_locator=passenger_payload[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload[0]['pax_record_locator_group']
        ))

        context_id_meals = passenger_payload[0]['context_id']
        context_id_no_meals = passenger_payload[1]['context_id']

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)
        passengers = import_resp.json()['data']
        self.assertEqual(len(passengers), 2)

        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            else:
                self.assertTrue(False)

        decline_resp = requests.put(passenger_url + '/' + passengers[0]['context_id'] + '/decline?include_pnr=true&meals=false', headers=headers)
        self.assertEqual(decline_resp.status_code, 200)

        passengers = decline_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 2)
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            else:
                self.assertTrue(False)

        voucher_id = decline_resp.json()['data']['voucher_id']
        voucher_url = self._api_host + '/api/v1/voucher/' + str(voucher_id)
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        passengers = voucher_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 2)
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            else:
                self.assertTrue(False)

    def test_offer_decline_one_pax_meal_create(self):
        """
        ensures system can decline hotels and create meal vouchers for one pax only via pax app
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[1].update(dict(
            meal_accommodation=False,
            pax_record_locator=passenger_payload[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload[0]['pax_record_locator_group']
        ))

        context_id_meals = passenger_payload[0]['context_id']
        context_id_no_meals = passenger_payload[1]['context_id']

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)
        passengers = import_resp.json()['data']
        self.assertEqual(len(passengers), 2)

        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            else:
                self.assertTrue(False)

        decline_url = self._api_host + '/api/v1/offer/decline?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']
        decline_resp = requests.put(decline_url)
        self.assertEqual(decline_resp.status_code, 200)

        passengers = decline_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 2)
                for meal in passenger['meal_vouchers']:
                    self.assertEqual(meal['provider'], 'tvl')
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            else:
                self.assertTrue(False)

        pax_meals_url = self._api_host + '/api/v1/passenger/' + context_id_meals
        pax_meals_resp = requests.get(url=pax_meals_url, headers=headers)
        self.assertEqual(pax_meals_resp.status_code, 200)
        voucher_id = pax_meals_resp.json()['data']['voucher_id']

        voucher_url = self._api_host + '/api/v1/voucher/' + str(voucher_id)
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        passengers = voucher_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 2)
                for meal in passenger['meal_vouchers']:
                    self.assertEqual(meal['provider'], 'tvl')
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            else:
                self.assertTrue(False)

        full_state_url = self._api_host + '/api/v1/passenger/' + context_id_meals + '/state'
        full_state_resp = requests.get(url=full_state_url, headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        meal_vouchers = full_state_resp_json['data']['voucher']['meal_vouchers']
        self.assertGreater(len(meal_vouchers), 0)
        for meal in meal_vouchers:
            self.assertEqual(meal['provider'], 'tvl')

    def test_offer_decline_one_pax_meal_create_no_meal_provider(self):
        """
        ensures system can decline hotels and create meal vouchers for one pax only via pax app
        and ensures meal provider is not returned
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[1].update(dict(
            meal_accommodation=False,
            pax_record_locator=passenger_payload[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload[0]['pax_record_locator_group']
        ))

        context_id_meals = passenger_payload[0]['context_id']
        context_id_no_meals = passenger_payload[1]['context_id']

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)
        passengers = import_resp.json()['data']
        self.assertEqual(len(passengers), 2)

        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            else:
                self.assertTrue(False)

        decline_url = self._api_host + '/api/v1/offer/decline?ak1=' + passengers[0]['ak1'] + '&ak2=' + passengers[0]['ak2']
        decline_resp = requests.put(decline_url)
        self.assertEqual(decline_resp.status_code, 200)

        passengers = decline_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 2)
                for meal in passenger['meal_vouchers']:
                    self.assertEqual(meal['provider'], 'tvl')
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            else:
                self.assertTrue(False)

        pax_meals_url = self._api_host + '/api/v1/passenger/' + context_id_meals
        pax_meals_resp = requests.get(url=pax_meals_url, headers=headers)
        self.assertEqual(pax_meals_resp.status_code, 200)
        voucher_id = pax_meals_resp.json()['data']['voucher_id']

        voucher_url = self._api_host + '/api/v1/voucher/' + str(voucher_id)
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        passengers = voucher_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 2)
                for meal in passenger['meal_vouchers']:
                    self.assertEqual(meal['provider'], 'tvl')
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            else:
                self.assertTrue(False)

        full_state_url = self._api_host + '/api/v1/passenger/' + context_id_meals + '/state'
        full_state_resp = requests.get(url=full_state_url, headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        meal_vouchers = full_state_resp_json['data']['voucher']['meal_vouchers']
        self.assertGreater(len(meal_vouchers), 0)
        for meal in meal_vouchers:
            self.assertEqual(meal['provider'], 'tvl')

    def test_airline_decline_include_pnr_one_pax_meal_decline(self):
        """
        ensures system can decline hotels and decline meals for one pax only
        """
        passenger_url = self._api_host + '/api/v1/passenger'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)
        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[1].update(dict(
            meal_accommodation=False,
            pax_record_locator=passenger_payload[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload[0]['pax_record_locator_group']
        ))

        context_id_meals = passenger_payload[0]['context_id']
        context_id_no_meals = passenger_payload[1]['context_id']

        import_resp = requests.post(passenger_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_resp.status_code, 201)
        passengers = import_resp.json()['data']
        self.assertEqual(len(passengers), 2)

        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
            else:
                self.assertTrue(False)

        decline_resp = requests.put(passenger_url + '/' + passengers[0]['context_id'] + '/decline?include_pnr=true&meals=true', headers=headers)
        self.assertEqual(decline_resp.status_code, 200)

        passengers = decline_resp.json()['data']['passengers']
        self.assertEqual(len(passengers), 2)
        for passenger in passengers:
            if passenger['context_id'] == context_id_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'declined')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            elif passenger['context_id'] == context_id_no_meals:
                self.assertEqual(passenger['hotel_accommodation_status'], 'declined')
                self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
                self.assertIsNone(passenger['transport_accommodation_status'])
                self.assertEqual(len(passenger['meal_vouchers']), 0)
            else:
                self.assertTrue(False)

    def test_passenger_offer__hotel_only_decline(self):
        """
        verify passenger landing page has correct information embedded in it for the scenario:
          * airline offers hotel only. Passenger declines the hotel. Passenger revisits the offer link again after that.

        This test focuses mostly on confirmation payloads in their various places.
        """

        customer = 'Delta Air Lines'
        headers = self._generate_passenger_headers()

        # airline generates offer ----
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=True, meal_accommodation=False, meals=[])
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']

        # passenger visits offer link ----
        response = requests.get(passenger_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNone(embedded_json['confirmation'])
        context_ids = [p['context_id'] for p in embedded_json['other_passengers']]
        context_ids.insert(0, embedded_json['passenger']['context_id'])

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)

        # passenger declines hotel offer ----
        declining_response_data = self._passenger_decline_offer(passenger)
        self.assertIsNone(declining_response_data['hotel_voucher'])
        for p in declining_response_data['passengers']:
            self.assertEqual(p['meal_vouchers'], [])

        # passenger visits offer link again ----
        response = requests.get(passenger_offer_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNone(embedded_json['confirmation'])

        for field in passenger_sanitized_fields:
            self.assertNotIn(field, embedded_json['passenger'])

            for other_passenger in embedded_json['other_passengers']:
                self.assertNotIn(field, other_passenger)
