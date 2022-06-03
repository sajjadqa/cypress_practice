
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
    random_chunk,
    display_response,
    CUSTOMER_TOKENS,
    TEMPLATE_DATE,
    PASSENGER_TEMPLATE,
    StormxSystemVerification,
    pretty_print_json,
    log_error_system_tests_output
)


class TestApiNotifications(StormxSystemVerification):
    """
    Verify functionality related to notifications.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiNotifications, cls).setUpClass()

    def test_cancel_hotel_with_meals_notifications_single_pax(self):
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            notify=True
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        hotel_offerings = self._get_passenger_hotel_offerings(passenger)
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        booking_response_json = booking_response.json()['data']
        self.assertEqual(booking_response_json['passengers'][0]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(booking_response_json['passengers'][0]['meal_accommodation_status'], 'accepted')
        self.assertIsNone(booking_response_json['passengers'][0]['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNotNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 1)
        self.assertEqual(len(canceled_passengers[0]['notifications']), 6)
        self.assertEqual(len(canceled_passengers[0]['meal_vouchers']), 2)
        self.assertEqual(canceled_passengers[0]['meal_accommodation_status'], 'accepted')
        self.assertEqual(canceled_passengers[0]['hotel_accommodation_status'], 'canceled_voucher')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])

    def test_offer_cancel_hotel_with_meals_notifications_single_pax(self):
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            notify=True
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        hotel_offerings = self._get_passenger_hotel_offerings(passenger)
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        booking_response_json = booking_response.json()['data']
        self.assertEqual(booking_response_json['passengers'][0]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(booking_response_json['passengers'][0]['meal_accommodation_status'], 'accepted')
        self.assertIsNone(booking_response_json['passengers'][0]['transport_accommodation_status'])

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertNotIn('voucher_id', cancel_response_json['data'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 1)
        self.assertEqual(len(canceled_passengers[0]['notifications']), 6)
        self.assertEqual(len(canceled_passengers[0]['meal_vouchers']), 2)
        self.assertEqual(canceled_passengers[0]['meal_accommodation_status'], 'accepted')
        self.assertEqual(canceled_passengers[0]['hotel_accommodation_status'], 'canceled_voucher')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])

    def test_offer_cancel_with_notifications_single_pax(self):
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)
        email_list = ['test@blackhole.bigtester.tvlinc.com']
        phone_list = ['+11234567894']

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            notify=True,
            emails=email_list,
            phone_numbers=phone_list
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        self._test_passenger_notifications(passenger['notifications'], email_list, phone_list, 1, 1, 2, 0, False, True)

        cancel_url = self._api_host + '/api/v1/offer/cancel?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNone(cancel_response_json['data']['hotel_voucher'])
        self.assertNotIn('voucher_id', cancel_response_json['data'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 1)
        self.assertEqual(len(canceled_passengers[0]['notifications']), 2)
        self._test_passenger_notifications(canceled_passengers[0]['notifications'], email_list, phone_list, 1, 1, 2, 0, True, True)
        self.assertEqual(canceled_passengers[0]['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(canceled_passengers[0]['hotel_accommodation_status'], 'canceled_offer')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'canceled_offer')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])
        self.assertEqual(len(get_passenger_response['data']['notifications']), 2)
        self._test_passenger_notifications(get_passenger_response['data']['notifications'], email_list, phone_list, 1, 1, 2, 0)

    def test_passenger_cancel_with_notifications_single_pax(self):
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)
        email_list = ['test@blackhole.bigtester.tvlinc.com']
        phone_list = ['+11234567894']

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            notify=True,
            emails=email_list,
            phone_numbers=phone_list
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'offered')
        self.assertIsNone(passenger['transport_accommodation_status'])

        self._test_passenger_notifications(passenger['notifications'], email_list, phone_list, 1, 1, 2, 0, False, False)

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIn('voucher_id', cancel_response_json['data'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 1)
        self.assertEqual(len(canceled_passengers[0]['notifications']), 2)
        self._test_passenger_notifications(canceled_passengers[0]['notifications'], email_list, phone_list, 1, 1, 2, 0, True, False)
        self.assertEqual(canceled_passengers[0]['meal_accommodation_status'], 'canceled_offer')
        self.assertEqual(canceled_passengers[0]['hotel_accommodation_status'], 'canceled_offer')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_offer')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'canceled_offer')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])
        self.assertEqual(len(get_passenger_response['data']['notifications']), 2)
        self._test_passenger_notifications(get_passenger_response['data']['notifications'], email_list, phone_list, 1, 1, 2, 0)

    def test_cancel_hotel_with_meals_notifications_multiple_pax(self):
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        booking_url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(2)
        passenger_payload[0].update(dict(
            notify=True
        ))
        passenger_payload[1].update(dict(
            notify=True,
            pax_record_locator=passenger_payload[0]['pax_record_locator'],
            pax_record_locator_group=passenger_payload[0]['pax_record_locator_group'],
            emails=['email1@tvl.blackhole.com'],
            phone_numbers=['+12223334444']
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passengers = import_response_json['data']

        for passenger in passengers:
            self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
            self.assertEqual(passenger['meal_accommodation_status'], 'offered')
            self.assertIsNone(passenger['transport_accommodation_status'])

        hotel_offerings = self._get_passenger_hotel_offerings(passengers[0])
        self.assertGreater(len(hotel_offerings), 0)

        picked_hotel = hotel_offerings[0]
        booking_payload = dict(
            context_ids=[passengers[0]['context_id'], passengers[1]['context_id']],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )

        booking_response = requests.post(url=booking_url, headers=headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)

        booking_response_json = booking_response.json()['data']
        self.assertEqual(len(booking_response_json['passengers']), 2)
        for passenger in booking_response_json['passengers']:
            self.assertEqual(passenger['hotel_accommodation_status'], 'accepted')
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertIsNone(passenger['transport_accommodation_status'])

        passenger1 = booking_response_json['passengers'][0]
        passenger2 = booking_response_json['passengers'][1]

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger1['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        self.assertIsNotNone(cancel_response_json['data']['hotel_voucher'])
        self.assertIsNotNone(cancel_response_json['data']['voucher_id'])

        canceled_passengers = cancel_response_json['data']['passengers']
        self.assertEqual(len(canceled_passengers), 2)
        for passenger in canceled_passengers:
            self.assertEqual(len(passenger['notifications']), 6)
            self.assertEqual(len(passenger['meal_vouchers']), 2)
            self.assertEqual(passenger['meal_accommodation_status'], 'accepted')
            self.assertEqual(passenger['hotel_accommodation_status'], 'canceled_voucher')

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger1['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger2['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')
        self.assertIsNone(get_passenger_response['data']['transport_accommodation_status'])

    def test_voucher_passenger_notifications_airline_api(self):
        """
        verifies system is returning passenger_notifications for airline api
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        emails = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers = ['+11112222', '+12223333']
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=True, meal_accommodation=False,
                                               notify=True, emails=emails, phone_numbers=phone_numbers)
        passenger = passengers[0]
        context_ids = [passengers[0]['context_id'], passengers[1]['context_id']]

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        booking_response_data = self._airline_book_hotel(customer, picked_hotel, context_ids, room_count=desired_room_count)
        self.assertEqual(booking_response_data['hotel_voucher']['hotel_id'], picked_hotel['hotel_id'])
        confirmations = [notification for passenger in booking_response_data['passengers'] for notification in passenger['notifications']]
        self._test_passenger_notifications(confirmations, emails, phone_numbers, 6, 6, 8, 4)

        notification_url = self._api_host + '/api/v1/passenger/' + context_ids[0] + '/notifications'
        notification_payload_email = {'email': 'stormx.test3@tvlinc.com'}
        notification_payload_text = {'text': '+13334444'}
        notification_resp = requests.post(url=notification_url, headers=headers, data=notification_payload_email)
        self.assertEqual(notification_resp.status_code, 200)
        notification_resp = requests.post(url=notification_url, headers=headers, data=notification_payload_text)
        self.assertEqual(notification_resp.status_code, 200)

        emails.append('stormx.test3@tvlinc.com')
        phone_numbers.append('+13334444')

        voucher_id = booking_response_data['voucher_id']
        voucher_url = self._api_host + '/api/v1/voucher/' + str(voucher_id)
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        voucher_resp_json = voucher_resp.json()

        self.assertEqual(voucher_resp.status_code, 200)
        confirmations2 = [notification for passenger in voucher_resp_json['data']['passengers'] for notification in passenger['notifications']]
        self._test_passenger_notifications(confirmations2, emails, phone_numbers, 7, 7, 8, 6)

    def test_voucher_passenger_notifications_passenger_api(self):
        """
        verifies system is returning passenger_notifications for passenger api
        """
        customer = 'Purple Rain Airlines'
        emails = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers = ['+11112222', '+12223333']
        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=True,
                                               meal_accommodation=False,
                                               notify=True, emails=emails, phone_numbers=phone_numbers)
        passenger = passengers[0]
        context_ids = [passengers[0]['context_id'], passengers[1]['context_id']]

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        booking_response_data = self._passenger_book_hotel(passenger, picked_hotel, context_ids, room_count=desired_room_count)
        self.assertEqual(booking_response_data['hotel_voucher']['hotel_id'], picked_hotel['hotel_id'])
        confirmations = [notification for passenger in booking_response_data['passengers'] for notification in passenger['notifications']]
        self._test_passenger_notifications(confirmations, emails, phone_numbers, 6, 6, 8, 4, public_notification=True)

    def test_meal_only_notification(self):
        """
        verify confirmation notification is sent out on meal-only offer
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        context_id1 = passengers_payload[0]['context_id']

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            notify=True,
            hotel_accommodation=False
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        for passenger in import_resp_json['data']:
            self.assertEqual(len(passenger['notifications']), 4)
            for notification in passenger['notifications']:
                self.assertEqual(notification['notification_type'], 'confirmation')

        pax1_resp = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        pax1_resp_notifications = pax1_resp.json()['data']['notifications']

        self._test_passenger_notifications(pax1_resp_notifications, emails1, phone_numbers1, 2, 2, 0, 4)

        pax1_state_resp = requests.get(url=passenger_url + '/' + context_id1 + '/state', headers=headers)
        self.assertEqual(pax1_state_resp.status_code, 200)
        pax_1_state_notifications = pax1_state_resp.json()['data']['passenger']['notifications']

        self._test_passenger_notifications(pax_1_state_notifications, emails1, phone_numbers1, 2, 2, 0, 4)

    def test_confirmation_notifications_single_pax(self):
        """
        verifies system is returning confirmation passenger_notifications for single pax
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            notify=True
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        passenger = import_resp_json['data'][0]

        pax1_resp = requests.get(url=passenger_url + '/' + passenger['context_id'], headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        pax1_resp_json = pax1_resp.json()

        self._test_passenger_notifications(pax1_resp_json['data']['notifications'], emails1, phone_numbers1, 2, 2, 4, 0)

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        self._passenger_book_hotel(passenger, picked_hotel, [passenger['context_id']], room_count=desired_room_count)

        pax1_resp2 = requests.get(url=passenger_url + '/' + passenger['context_id'], headers=headers)
        self.assertEqual(pax1_resp2.status_code, 200)
        pax1_resp_json2 = pax1_resp2.json()

        self._test_passenger_notifications(pax1_resp_json2['data']['notifications'], emails1, phone_numbers1, 4, 4, 4, 4)

    def test_confirmation_notifications_multiple_pax(self):
        """
        verifies system is returning confirmation passenger_notifications for multiple pax
        test imports 3 passengers each with there own set of emails and phone_numbers and notify=True
        then the 3 passengers book a hotel room. next the test is verifying the system is returning
        the correct amount of offer and confirmation notifications for each passenger and
        verifying that the notifications returned belong to the correct emails and phone numbers per passenger
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(3)
        context_id1 = passengers_payload[0]['context_id']
        context_id2 = passengers_payload[1]['context_id']
        context_id3 = passengers_payload[2]['context_id']

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            notify=True
        ))

        emails2 = ['2stormx.test@tvlinc.com', '2stormx.test2@tvlinc.com']
        phone_numbers2 = ['+121112222', '+122223333']
        passengers_payload[1].update(dict(
            emails=emails2,
            phone_numbers=phone_numbers2,
            notify=True
        ))

        emails3 = ['3stormx.test@tvlinc.com', '3stormx.test2@tvlinc.com']
        phone_numbers3 = ['+131112222', '+132223333']
        passengers_payload[2].update(dict(
            emails=emails3,
            phone_numbers=phone_numbers3,
            notify=True
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        passenger = import_resp_json['data'][0]
        context_ids = [passenger['context_id'] for passenger in import_resp_json['data']]

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        self._passenger_book_hotel(passenger, picked_hotel, context_ids, room_count=desired_room_count)

        pax1_resp = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        notifications1 = pax1_resp.json()['data']['notifications']

        self._test_passenger_notifications(notifications1, emails1, phone_numbers1, 4, 4, 4, 4)

        pax2_resp = requests.get(url=passenger_url + '/' + context_id2, headers=headers)
        self.assertEqual(pax2_resp.status_code, 200)
        notifications2 = pax2_resp.json()['data']['notifications']

        self._test_passenger_notifications(notifications2, emails2, phone_numbers2, 4, 4, 4, 4)

        pax3_resp = requests.get(url=passenger_url + '/' + context_id3, headers=headers)
        self.assertEqual(pax3_resp.status_code, 200)
        notifications3 = pax3_resp.json()['data']['notifications']

        self._test_passenger_notifications(notifications3, emails3, phone_numbers3, 4, 4, 4, 4)

    def test_notifications(self):
        """
        test notification endpoints (passenger and airline) for the following:
        400 errors for bad inputs
        400 error for offer not in final state on public endpoint
        404 errors for multi tenant check
        200 errors for text, email, on both confirmation and offer states
        """
        import_url = self._api_host + '/api/v1/passenger'

        american_customer = 'American Airlines'
        american_headers = self._generate_airline_headers(american_customer)

        delta_customer = 'Delta Air Lines'
        delta_headers = self._generate_airline_headers(delta_customer)

        passenger1_payload = self._generate_n_passenger_payload(1)
        passenger1_payload[0].update(dict(
            hotel_accommodation=True
        ))

        passenger2_payload = self._generate_n_passenger_payload(1)
        passenger2_payload[0].update(dict(
            hotel_accommodation=False
        ))

        delta_import_response = requests.post(url=import_url, headers=delta_headers, json=passenger1_payload)
        self.assertEqual(delta_import_response.status_code, 201)
        import_response_json = delta_import_response.json()

        delta_import_response2 = requests.post(url=import_url, headers=delta_headers, json=passenger2_payload)
        self.assertEqual(delta_import_response2.status_code, 201)
        import_response2_json = delta_import_response2.json()

        passenger1 = import_response_json['data'][0]
        passenger2 = import_response2_json['data'][0]

        public_notify_url_1 = self._api_host + '/api/v1/offer/notifications?ak1=' + passenger1['ak1'] + '&ak2=' + passenger1['ak2']
        public_notify_url_2 = self._api_host + '/api/v1/offer/notifications?ak1=' + passenger2['ak1'] + '&ak2=' + passenger2['ak2']
        notify_url_1 = self._api_host + '/api/v1/passenger/' + passenger1['context_id'] + '/notifications'
        notify_url_2 = self._api_host + '/api/v1/passenger/' + passenger2['context_id'] + '/notifications'

        notification_data_bad = dict({
            'email': 'a@b.com',
            'text': '+15595595599'
        })

        notification_data_email = dict({
            'email': 'a@b.com'
        })

        notification_data_text = dict({
            'text': '+15595595599'
        })

        emails = ['a@b.com']
        phone_numbers = ['+15595595599']
        error_message_bad_input = 'Cannot send notification. Please provide a valid email address or phone_number, but not both.'
        error_message_bad_operation = 'Passenger cannot send notification. Offer is not in final state.'

        # multi tenant check
        security_1 = requests.post(url=notify_url_2, headers=american_headers, json=notification_data_email)
        self.assertEqual(security_1.status_code, 404)
        response_json = security_1.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 404, 'Not Found', 'PASSENGER_NOT_FOUND', 'Passenger not found for ' + passenger2['context_id'], [])

        # test bad data inputs
        public_bad_1 = requests.post(url=public_notify_url_1, headers=delta_headers, json=notification_data_bad)
        self.assertEqual(public_bad_1.status_code, 400)
        response_json = public_bad_1.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'CANNOT_NOTIFY', error_message_bad_operation, [])

        bad_1 = requests.post(url=notify_url_1, headers=delta_headers, json=notification_data_bad)
        self.assertEqual(bad_1.status_code, 400)
        response_json = bad_1.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'CANNOT_NOTIFY', error_message_bad_input, [])

        public_bad_2 = requests.post(url=public_notify_url_2, headers=delta_headers, json=dict())
        self.assertEqual(public_bad_2.status_code, 400)
        response_json = public_bad_2.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'CANNOT_NOTIFY', error_message_bad_input, [])

        bad_2 = requests.post(url=notify_url_2, headers=delta_headers, json=dict())
        self.assertEqual(bad_2.status_code, 400)
        response_json = bad_2.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'CANNOT_NOTIFY', error_message_bad_input, [])

        public_bad_1 = requests.post(url=public_notify_url_1, headers=delta_headers, json=notification_data_email)
        self.assertEqual(public_bad_1.status_code, 400)
        response_json = public_bad_1.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'CANNOT_NOTIFY', error_message_bad_operation, [])

        public_bad_2 = requests.post(url=public_notify_url_1, headers=delta_headers, json=notification_data_text)
        self.assertEqual(public_bad_2.status_code, 400)
        response_json = public_bad_2.json()
        log_error_system_tests_output(pretty_print_json(response_json))
        self._validate_error_message(response_json, 400, 'Bad Request', 'CANNOT_NOTIFY', error_message_bad_operation, [])

        # test good cases
        notify_1 = requests.post(url=notify_url_1, headers=delta_headers, json=notification_data_email)
        self.assertEqual(notify_1.status_code, 200)
        self._test_passenger_notifications([notify_1.json()['data']], emails, phone_numbers, 1, 0, 1, 0, False)

        notify_2 = requests.post(url=notify_url_1, headers=delta_headers, json=notification_data_text)
        self.assertEqual(notify_2.status_code, 200)
        self._test_passenger_notifications([notify_2.json()['data']], emails, phone_numbers, 0, 1, 1, 0, False)

        notify_3 = requests.post(url=notify_url_2, headers=delta_headers, json=notification_data_email)
        self.assertEqual(notify_3.status_code, 200)
        self._test_passenger_notifications([notify_3.json()['data']], emails, phone_numbers, 1, 0, 0, 1, False)

        notify_4 = requests.post(url=notify_url_2, headers=delta_headers, json=notification_data_text)
        self.assertEqual(notify_4.status_code, 200)
        self._test_passenger_notifications([notify_4.json()['data']], emails, phone_numbers, 0, 1, 0, 1, False)

        public_notify_1 = requests.post(url=public_notify_url_2, headers=delta_headers, json=notification_data_email)
        self.assertEqual(public_notify_1.status_code, 200)
        self._test_passenger_notifications([public_notify_1.json()['data']], emails, phone_numbers, 1, 0, 0, 1, False, True)

        public_notify_2 = requests.post(url=public_notify_url_2, headers=delta_headers, json=notification_data_text)
        self.assertEqual(public_notify_2.status_code, 200)
        self._test_passenger_notifications([public_notify_2.json()['data']], emails, phone_numbers, 0, 1, 0, 1, False, True)

    def test_notify_in_canceled_state_with_meals(self):
        """
        verifies system allows notifications for passengers in a canceled state and has meals
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=1)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        book_resp = self._passenger_book_hotel(passenger, picked_hotel, [passenger['context_id']], room_count=1)
        self.assertEqual(len(book_resp['passengers']), 1)
        self.assertEqual(book_resp['passengers'][0]['hotel_accommodation_status'], 'accepted')
        self.assertEqual(book_resp['passengers'][0]['meal_accommodation_status'], 'accepted')

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_voucher')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')

        notify_url_1 = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications'
        public_notify_url_1 = self._api_host + '/api/v1/offer/notifications?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']

        notification_data_email = dict({
            'email': 'a@b.com'
        })

        notification_data_text = dict({
            'text': '+15595595599'
        })

        emails = ['a@b.com']
        phone_numbers = ['+15595595599']

        notify_1 = requests.post(url=notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(notify_1.status_code, 200)
        self._test_passenger_notifications([notify_1.json()['data']], emails, phone_numbers, 1, 0, 0, 1, False)

        notify_2 = requests.post(url=notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(notify_2.status_code, 200)
        self._test_passenger_notifications([notify_2.json()['data']], emails, phone_numbers, 0, 1, 0, 1, False)

        public_notify_1 = requests.post(url=public_notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(public_notify_1.status_code, 200)
        self._test_passenger_notifications([public_notify_1.json()['data']], emails, phone_numbers, 1, 0, 0, 1, False, True)

        public_notify_2 = requests.post(url=public_notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(public_notify_2.status_code, 200)
        self._test_passenger_notifications([public_notify_2.json()['data']], emails, phone_numbers, 0, 1, 0, 1, False, True)

    def test_notify_in_canceled_state_with_no_meals(self):
        """
        verifies system does not allow notifications for passengers in a canceled state with no meals
        """
        expected_error_message = 'Passenger cannot send notification. Offer is in a canceled state.'

        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        cancel_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel'
        cancel_response = requests.put(url=cancel_url, headers=headers)
        self.assertEqual(cancel_response.status_code, 200)
        cancel_response_json = cancel_response.json()
        self.assertIs(cancel_response_json['error'], False)

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'canceled_offer')

        notify_url_1 = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications'
        public_notify_url_1 = self._api_host + '/api/v1/offer/notifications?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']

        notification_data_email = dict({
            'email': 'a@b.com'
        })

        notification_data_text = dict({
            'text': '+15595595599'
        })

        notify_1 = requests.post(url=notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(notify_1.status_code, 400)
        notify_resp_json = notify_1.json()
        log_error_system_tests_output(pretty_print_json(notify_resp_json))
        self._validate_error_message(notify_resp_json, 400, 'Bad Request', 'CANNOT_NOTIFY', expected_error_message, [])

        notify_2 = requests.post(url=notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(notify_2.status_code, 400)
        notify_resp_json2 = notify_2.json()
        log_error_system_tests_output(pretty_print_json(notify_resp_json2))
        self._validate_error_message(notify_resp_json2, 400, 'Bad Request', 'CANNOT_NOTIFY', expected_error_message, [])

        public_notify_1 = requests.post(url=public_notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(public_notify_1.status_code, 400)
        public_notify_json = public_notify_1.json()
        log_error_system_tests_output(pretty_print_json(public_notify_json))
        self._validate_error_message(public_notify_json, 400, 'Bad Request', 'CANNOT_NOTIFY', expected_error_message, [])

        public_notify_2 = requests.post(url=public_notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(public_notify_2.status_code, 400)
        public_notify_json2 = public_notify_2.json()
        log_error_system_tests_output(pretty_print_json(public_notify_json2))
        self._validate_error_message(public_notify_json2, 400, 'Bad Request', 'CANNOT_NOTIFY', expected_error_message, [])

    def test_notify_in_declined_state_with_meals(self):
        """
        verifies system allows notifications for passengers in a declined state and has meals
        """
        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        decline_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/decline'
        deny_response = requests.put(url=decline_url, headers=headers)
        self.assertEqual(deny_response.status_code, 200)
        deny_response_json = deny_response.json()
        self.assertIs(deny_response_json['error'], False)

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'accepted')

        notify_url_1 = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications'
        public_notify_url_1 = self._api_host + '/api/v1/offer/notifications?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']

        notification_data_email = dict({
            'email': 'a@b.com'
        })

        notification_data_text = dict({
            'text': '+15595595599'
        })

        emails = ['a@b.com']
        phone_numbers = ['+15595595599']

        notify_1 = requests.post(url=notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(notify_1.status_code, 200)
        self._test_passenger_notifications([notify_1.json()['data']], emails, phone_numbers, 1, 0, 0, 1, False)

        notify_2 = requests.post(url=notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(notify_2.status_code, 200)
        self._test_passenger_notifications([notify_2.json()['data']], emails, phone_numbers, 0, 1, 0, 1, False)

        public_notify_1 = requests.post(url=public_notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(public_notify_1.status_code, 200)
        self._test_passenger_notifications([public_notify_1.json()['data']], emails, phone_numbers, 1, 0, 0, 1, False, True)

        public_notify_2 = requests.post(url=public_notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(public_notify_2.status_code, 200)
        self._test_passenger_notifications([public_notify_2.json()['data']], emails, phone_numbers, 0, 1, 0, 1, False, True)

    def test_notify_in_declined_state_with_no_meals(self):
        """
        verifies system does not allow notifications for passengers in a declined state with no meals
        """
        expected_error_message = 'Passenger cannot send notification. Offer is in a declined state.'

        customer = 'Purple Rain Airlines'
        offer_url = self._api_host + '/api/v1/passenger'
        headers = self._generate_airline_headers(customer)

        passenger_payload = self._generate_n_passenger_payload(1)
        passenger_payload[0].update(dict(
            meal_accommodation=False
        ))

        import_response = requests.post(url=offer_url, headers=headers, json=passenger_payload)
        self.assertEqual(import_response.status_code, 201)
        import_response_json = import_response.json()
        passenger = import_response_json['data'][0]

        decline_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/decline'
        deny_response = requests.put(url=decline_url, headers=headers)
        self.assertEqual(deny_response.status_code, 200)
        deny_response_json = deny_response.json()
        self.assertIs(deny_response_json['error'], False)

        get_passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        get_passenger_response = requests.get(url=get_passenger_url, headers=headers).json()
        self.assertEqual(get_passenger_response['data']['hotel_accommodation_status'], 'declined')
        self.assertEqual(get_passenger_response['data']['meal_accommodation_status'], 'not_offered')

        notify_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications'
        public_notify_url = self._api_host + '/api/v1/offer/notifications?ak1=' + passenger['ak1'] + '&ak2=' + passenger['ak2']

        notification_data = dict({
            'email': 'a@b.com'
        })

        notify_resp = requests.post(url=notify_url, headers=headers, json=notification_data)
        self.assertEqual(notify_resp.status_code, 400)
        notify_resp_json = notify_resp.json()
        log_error_system_tests_output(pretty_print_json(notify_resp_json))
        self._validate_error_message(notify_resp_json, 400, 'Bad Request', 'CANNOT_NOTIFY', expected_error_message, [])

        public_notify_resp = requests.post(url=public_notify_url, headers=headers, json=notification_data)
        self.assertEqual(public_notify_resp.status_code, 400)
        public_notify_json = public_notify_resp.json()
        log_error_system_tests_output(pretty_print_json(public_notify_json))
        self._validate_error_message(public_notify_json, 400, 'Bad Request', 'CANNOT_NOTIFY', expected_error_message, [])

    def test_add_notification_before_and_after_booking_pax_api(self):
        """
        tests adding notifications before and after booking via pax api and ensures
        system is sending out offer and confirmation notifications accordingly
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        context_id1 = passengers_payload[0]['context_id']

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            notify=True
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        passenger = import_resp_json['data'][0]
        context_ids = [passenger['context_id'] for passenger in import_resp_json['data']]
        self._test_passenger_notifications(passenger['notifications'], emails1, phone_numbers1, 2, 2, 4, 0, False)

        pax1_resp = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        notifications1 = pax1_resp.json()['data']['notifications']
        self._test_passenger_notifications(notifications1, emails1, phone_numbers1, 2, 2, 4, 0)

        notify_url_1 = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications'

        notification_data_email = dict({
            'email': 'a@b.com'
        })

        notification_data_text = dict({
            'text': '+15595595599'
        })

        emails1.append('a@b.com')
        phone_numbers1.append('+15595595599')

        notify_1 = requests.post(url=notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(notify_1.status_code, 200)
        self._test_passenger_notifications([notify_1.json()['data']], emails1, phone_numbers1, 1, 0, 1, 0, False)

        pax1_resp2 = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp2.status_code, 200)
        notifications2 = pax1_resp2.json()['data']['notifications']
        self._test_passenger_notifications(notifications2, emails1, phone_numbers1, 3, 2, 5, 0)

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        book_resp = self._passenger_book_hotel(passenger, picked_hotel, context_ids, room_count=desired_room_count)
        confirmations = [notification for passenger in book_resp['passengers'] for notification in passenger['notifications']]
        self._test_passenger_notifications(confirmations, emails1, phone_numbers1, 6, 4, 5, 5, public_notification=True)

        pax1_resp3 = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp3.status_code, 200)
        notifications3 = pax1_resp3.json()['data']['notifications']
        self._test_passenger_notifications(notifications3, emails1, phone_numbers1, 6, 4, 5, 5)

        notify_2 = requests.post(url=notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(notify_2.status_code, 200)
        self._test_passenger_notifications([notify_2.json()['data']], emails1, phone_numbers1, 0, 1, 0, 1, False)

        pax1_resp4 = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp4.status_code, 200)
        notifications4 = pax1_resp4.json()['data']['notifications']
        self._test_passenger_notifications(notifications4, emails1, phone_numbers1, 6, 5, 5, 6)

    def test_notifications_notify_false(self):
        """
        tests system is not sending out notifications when notify=False
        for meal only and after hotel booking scenarios
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        context_id1 = passengers_payload[0]['context_id']

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            notify=False,
            hotel_accommodation=False
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        passenger = import_resp_json['data'][0]
        self.assertEqual(len(passenger['notifications']), 0)

        pax1_resp = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        notifications1 = pax1_resp.json()['data']['notifications']
        self._test_passenger_notifications(notifications1, emails1, phone_numbers1, 0, 0, 0, 0)

        passengers_payload2 = self._generate_n_passenger_payload(1)
        context_id2 = passengers_payload2[0]['context_id']

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload2[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            notify=False
        ))

        import_resp2 = requests.post(url=passenger_url, headers=headers, json=passengers_payload2)
        self.assertEqual(import_resp2.status_code, 201)
        import_resp_json2 = import_resp2.json()
        passenger2 = import_resp_json2['data'][0]
        context_ids2 = [passenger['context_id'] for passenger in import_resp_json2['data']]
        self.assertEqual(len(passenger2['notifications']), 0)

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger2, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        book_resp = self._passenger_book_hotel(passenger2, picked_hotel, context_ids2, room_count=desired_room_count)
        confirmations = [notification for passenger in book_resp['passengers'] for notification in passenger['notifications']]
        self._test_passenger_notifications(confirmations, emails1, phone_numbers1, 0, 0, 0, 0)

        pax1_resp2 = requests.get(url=passenger_url + '/' + context_id2, headers=headers)
        self.assertEqual(pax1_resp2.status_code, 200)
        notifications2 = pax1_resp2.json()['data']['notifications']
        self._test_passenger_notifications(notifications2, emails1, phone_numbers1, 0, 0, 0, 0)

    def test_notifications_notify_false_add_notification_before_booking(self):
        """
        tests system is not sending out notifications when notify=False
        and adding notification before booking
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        context_id1 = passengers_payload[0]['context_id']

        passengers_payload[0].update(dict(
            notify=False
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        passenger = import_resp_json['data'][0]
        context_ids = [passenger['context_id'] for passenger in import_resp_json['data']]
        self.assertEqual(len(passenger['notifications']), 0)

        notify_url_1 = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications'

        notification_data_text = dict({
            'text': '+15595595599'
        })

        phone_numbers = ['+15595595599']

        notify_1 = requests.post(url=notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(notify_1.status_code, 200)
        self._test_passenger_notifications([notify_1.json()['data']], [], phone_numbers, 0, 1, 1, 0, False)

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        book_resp = self._passenger_book_hotel(passenger, picked_hotel, context_ids, room_count=desired_room_count)
        confirmations = [notification for passenger in book_resp['passengers'] for notification in passenger['notifications']]
        self._test_passenger_notifications(confirmations, [], phone_numbers, 0, 1, 1, 0, public_notification=True)

        pax1_resp = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        notifications = pax1_resp.json()['data']['notifications']
        self._test_passenger_notifications(notifications, [], phone_numbers, 0, 1, 1, 0)

    def test_notifications_duplicate_emails_texts(self):
        """
        tests system is not sending out duplicate notifications after hotel booking
        scenario:
        two passengers are imported. passenger 1 has two emails and two phone_numbers with notify=True.
        passenger 2 has notify=False. notifications for passenger 1 are added with same phone_number and email.
        test verifies that only one confirmation per email/phone_number is sent out for passenger 1.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(2)

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            notify=True
        ))

        passengers_payload[1].update(dict(
            notify=False
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        self.assertEqual(len(import_resp_json['data']), 2)
        passenger = import_resp_json['data'][0]
        passenger2 = import_resp_json['data'][1]
        context_ids = [passenger['context_id'] for passenger in import_resp_json['data']]
        self.assertEqual(len(passenger['notifications']), 4)
        self.assertEqual(len(passenger2['notifications']), 0)

        notify_url_1 = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications'

        notification_data_text = dict({
            'text': phone_numbers1[0]
        })

        notification_data_email = dict({
            'email': emails1[0]
        })

        notify_1 = requests.post(url=notify_url_1, headers=headers, json=notification_data_text)
        self.assertEqual(notify_1.status_code, 200)
        self._test_passenger_notifications([notify_1.json()['data']], emails1, phone_numbers1, 0, 1, 1, 0, False)

        notify_2 = requests.post(url=notify_url_1, headers=headers, json=notification_data_email)
        self.assertEqual(notify_2.status_code, 200)
        self._test_passenger_notifications([notify_2.json()['data']], emails1, phone_numbers1, 1, 0, 1, 0, False)

        desired_room_count = 1
        hotel_offerings = self._get_passenger_hotel_offerings(passenger, room_count=desired_room_count)
        self.assertGreaterEqual(len(hotel_offerings), 1)

        picked_hotel = hotel_offerings[0]
        book_resp = self._passenger_book_hotel(passenger, picked_hotel, context_ids, room_count=desired_room_count)
        confirmations = [notification for passenger in book_resp['passengers'] for notification in passenger['notifications']]
        self._test_passenger_notifications(confirmations, emails1, phone_numbers1, 5, 5, 6, 4, public_notification=True)

        pax1_resp = requests.get(url=passenger_url + '/' + passenger['context_id'], headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        notifications = pax1_resp.json()['data']['notifications']
        self._test_passenger_notifications(notifications, emails1, phone_numbers1, 5, 5, 6, 4)

        pax2_resp = requests.get(url=passenger_url + '/' + passenger2['context_id'], headers=headers)
        self.assertEqual(pax2_resp.status_code, 200)
        notifications2 = pax2_resp.json()['data']['notifications']
        self._test_passenger_notifications(notifications2, emails1, phone_numbers1, 0, 0, 0, 0)

    def test_validate_email_notifications(self):
        """
        validate notifications endpoint forces correct email input
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passengers = self._create_2_passengers(customer=customer)

        notify_url = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/notifications'

        notification_data_text = {
            'email': 'testblackholetravellianceinc.com'
        }

        notify_resp = requests.post(url=notify_url, json=notification_data_text, headers=headers)
        self.assertEqual(notify_resp.status_code, 400)
        self._validate_error_message(notify_resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger notifications.',
                                     [{'field': 'email', 'message': 'Enter a valid email address.'}])

        notification_data_text = {
            'email': 'testareallylongnameyoukowwhatImeanonthenotificationsendpointyadadad@blackhole.travellianceinc.com'
        }

        notify_resp = requests.post(url=notify_url, json=notification_data_text, headers=headers)
        self.assertEqual(notify_resp.status_code, 400)
        self._validate_error_message(notify_resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger notifications.',
                                     [{'field': 'email', 'message': 'Ensure this field has no more than 45 characters.'}])

    def test_validate_text_notifications(self):
        """
        validate notifications endpoint forces correct phone_number input
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passengers = self._create_2_passengers(customer=customer)

        notify_url = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/notifications'

        notification_data_text = {
            'text': '15591234567'
        }

        notify_resp = requests.post(url=notify_url, json=notification_data_text, headers=headers)
        self.assertEqual(notify_resp.status_code, 400)
        self._validate_error_message(notify_resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger notifications.',
                                     [{'message': "phone number must be in the E.164 format and always start with a '+'. Expected format: '+{country_code}{subscriber_phone_number}', no spaces or symbols.", 'field': 'text'}])

        notification_data_text = {
            'text': '+155912345670178945642345961489641531987198513521981981'
        }

        notify_resp = requests.post(url=notify_url, json=notification_data_text, headers=headers)
        self.assertEqual(notify_resp.status_code, 400)
        self._validate_error_message(notify_resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'Invalid input criteria for passenger notifications.',
                                     [{'field': 'text', 'message': "phone number must be in the E.164 format and always start with a '+'. Expected format: '+{country_code}{subscriber_phone_number}', no spaces or symbols."}, {'field': 'text', 'message': 'Ensure this field has no more than 16 characters.'}])

    def _test_passenger_contact_info(self, emails, phone_numbers, passenger):
        """
        helper function for testing passenger_contact_info
        param emails: list(string)
        param phone_numbers: list(string)
        param passenger: Passenger JSON
        return: None
        """
        for email in passenger['emails']:
            self.assertIn(email, emails)

        for phone_number in passenger['phone_numbers']:
            self.assertIn(phone_number, phone_numbers)

        self.assertEqual(len(passenger['emails']), len(emails))
        self.assertEqual(len(passenger['emails']), len(emails))
        self.assertEqual(len(passenger['phone_numbers']), len(phone_numbers))


    def test_passenger_contact_info_notify_false(self):
        """
        test ensuring system is adding and not adding passenger_contact_info correctly when notify=False
        and calling the passenger notifications endpoint
        """
        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+13121112222', '+13122223333']
        existing_email_data = {'email': 'stormx.test@tvlinc.com'}
        existing_text_data = {'text': '+13121112222'}
        new_email_data = {'email': 'stormx.test3@tvlinc.com'}
        new_text_data = {'text': '+13123334444'}

        passenger = self._create_2_passengers(customer='Purple Rain Airlines', notify=False, emails=emails1, phone_numbers=phone_numbers1)[0]
        self.assertEqual(passenger['notify'], False)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger)

        headers = self._generate_airline_headers('Purple Rain Airlines')
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        notification_url = passenger_url + '/notifications'

        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=existing_email_data)
        self.assertEqual(notify_resp.status_code, 200)
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=existing_text_data)
        self.assertEqual(notify_resp.status_code, 200)
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=new_email_data)
        self.assertEqual(notify_resp.status_code, 200)
        emails1.append(new_email_data['email'])
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=new_text_data)
        self.assertEqual(notify_resp.status_code, 200)
        phone_numbers1.append(new_text_data['text'])
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        passenger_state_url = passenger_url + '/state'
        state_resp = requests.get(url=passenger_state_url, headers=headers)
        self.assertEqual(state_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, state_resp.json()['data']['passenger'])

    def test_passenger_contact_info_notify_true(self):
        """
        test ensuring system is adding and not adding passenger_contact_info correctly when notify=True
        and calling the passenger notifications endpoint
        """
        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+13121112222', '+13122223333']
        existing_email_data = {'email': 'stormx.test@tvlinc.com'}
        existing_text_data = {'text': '+13121112222'}
        new_email_data = {'email': 'stormx.test3@tvlinc.com'}
        new_text_data = {'text': '+13123334444'}

        passenger = self._create_2_passengers(customer='Purple Rain Airlines', notify=True, emails=emails1, phone_numbers=phone_numbers1)[0]
        self.assertEqual(passenger['notify'], True)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger)

        headers = self._generate_airline_headers('Purple Rain Airlines')
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        notification_url = passenger_url + '/notifications'

        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=existing_email_data)
        self.assertEqual(notify_resp.status_code, 200)
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=existing_text_data)
        self.assertEqual(notify_resp.status_code, 200)
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=new_email_data)
        self.assertEqual(notify_resp.status_code, 200)
        emails1.append(new_email_data['email'])
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        notify_resp = requests.post(url=notification_url, headers=headers, json=new_text_data)
        self.assertEqual(notify_resp.status_code, 200)
        phone_numbers1.append(new_text_data['text'])
        passenger_resp = requests.get(url=passenger_url, headers=headers)
        self.assertEqual(passenger_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, passenger_resp.json()['data'])

        passenger_state_url = passenger_url + '/state'
        state_resp = requests.get(url=passenger_state_url, headers=headers)
        self.assertEqual(state_resp.status_code, 200)
        self._test_passenger_contact_info(emails1, phone_numbers1, state_resp.json()['data']['passenger'])
