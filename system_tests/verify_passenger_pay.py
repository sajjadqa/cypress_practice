import requests
from time import sleep
from uuid import UUID
from stormx_verification_framework import StormxSystemVerification, should_skip_local_test


class TestPassengerPay(StormxSystemVerification):
    """
    validate passenger pay feature (StormX API / Roomstorm)
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestPassengerPay, cls).setUpClass()

    @should_skip_local_test
    def test_validate_multi_night_pax_pay(self):
        """
        validates multi night pax pay is not allowed (temporarily)
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            number_of_nights=2
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'FEATURE_NOT_SUPPORTED',
                                     'Passenger pay feature is currently not supported for multi night reservations.', [])

    @should_skip_local_test
    def test_validate_airline_pay_values_same_group(self):
        """
        validate all passengers on the same group must have the same airline pay value
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT', 'All passengers on PNR group must contain same airline_pay value.', [])

    @should_skip_local_test
    def test_validate_airline_pay_values_same_group_open(self):
        """
        validate all passengers on the same group must have the same airline pay value
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(3)
        passengers_payload[2].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=[passengers_payload[0]])
        self.assertEqual(resp.status_code, 201)
        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=[passengers_payload[1]])
        self.assertEqual(resp.status_code, 201)
        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=[passengers_payload[2]])
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT', 'All passengers on PNR group must contain same airline_pay value.', [])

    @should_skip_local_test
    def test_add_airline_pay_passengers_to_pnr(self):
        """
        validate a PNR can get additional airline pay passengers if airline pay PNR.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(3)
        for passenger_payload in passengers_payload:
            passenger_payload.update(dict(
                airline_pay=False,
                meal_accommodation=False,
                hotel_accommodation=True,
                phone_numbers=[],
                emails=['test@blackhole.tvlinc.com'],
                notify=True
            ))

        passengers = []

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=[passengers_payload[0]])
        self.assertEqual(resp.status_code, 201)
        passengers.append(resp.json()['data'][0])
        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=[passengers_payload[1]])
        self.assertEqual(resp.status_code, 201)
        passengers.append(resp.json()['data'][0])
        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=[passengers_payload[2]])
        self.assertEqual(resp.status_code, 201)
        passengers.append(resp.json()['data'][0])

        for passenger in passengers:
            self.assertFalse(passenger['airline_pay'])
            self.assertFalse(passenger['meal_accommodation'])
            self.assertTrue(passenger['hotel_accommodation'])
            self._test_passenger_notifications(passenger['notifications'], ['test@blackhole.tvlinc.com'], [], 1, 0, 0, 0, False, False, 1)

    @should_skip_local_test
    def test_validate_passenger_pay_hotel_accommodation(self):
        """
        test passenger pay passengers have hotel_accommodation=True
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            hotel_accommodation=False
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT', 'All passenger pay passengers must have hotel_accommodation=true.', [])

        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[0].update(dict(
            airline_pay=False,
            hotel_accommodation=False
        ))
        passengers_payload[1].update(dict(
            airline_pay=False
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT', 'All passenger pay passengers must have hotel_accommodation=true.', [])

    @should_skip_local_test
    def test_validate_passenger_pay_meal_accommodation(self):
        """
        test passenger pay passengers have meal_accommodation=False
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=True
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'All passenger pay passengers must have meal_accommodation, and transport_accommodation set to false.', [])

        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False
        ))
        passengers_payload[1].update(dict(
            airline_pay=False,
            meal_accommodation=True
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 400)
        self._validate_error_message(resp.json(), 400, 'Bad Request', 'INVALID_INPUT',
                                     'All passenger pay passengers must have meal_accommodation, and transport_accommodation set to false.', [])

    @should_skip_local_test
    def test_validate_passenger_pay_notify(self):
        """
        test passenger pay passengers do need need notify true
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=False
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)

        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=False
        ))
        passengers_payload[1].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=False
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)

    @should_skip_local_test
    def test_single_passenger_pay_passenger(self):
        """
        validate a single passenger can enter the system with airline_pay=False
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['airline_pay'], False)
        self._test_passenger_notifications(passenger['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)

    @should_skip_local_test
    def test_two_passenger_pay_passengers_single_notification(self):
        """
        validate a two passengers can enter the system with airline_pay=False and only one with notify=True
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(2)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=False,
            emails=[],
            phone_numbers=[]
        ))
        passengers_payload[1].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertEqual(len(resp_json['data']), 2)

        if resp_json['data'][0]['context_id'] == passengers_payload[0]['context_id']:
            passenger1 = resp_json['data'][0]
            passenger2 = resp_json['data'][1]
        else:
            passenger1 = resp_json['data'][1]
            passenger2 = resp_json['data'][0]

        self.assertEqual(passenger1['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger1['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger2['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger2['meal_accommodation_status'], 'not_offered')

        self.assertEqual(len(passenger1['notifications']), 0)
        self.assertEqual(len(passenger2['notifications']), 2)
        notifications = passenger1['notifications'] + passenger2['notifications']

        self.assertEqual(passenger1['airline_pay'], False)
        self.assertEqual(passenger2['airline_pay'], False)
        self._test_passenger_notifications(notifications, ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)

    @should_skip_local_test
    def test_two_passengers_different_pnr_group_different_airline_pay(self):
        """
        validate passengers can enter the system on separate pnr groups with different airline_pay values
        and one receives an offer to the pax app
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload_airline_pay = self._generate_n_passenger_payload(1)
        passengers_payload_pax_pay = self._generate_n_passenger_payload(1)

        passengers_payload_airline_pay[0].update(dict(
            airline_pay=True,
            meal_accommodation=True,
            hotel_accommodation=True,
            notify=True,
            emails=['test2@blackhole.tvlinc.com'],
            phone_numbers=['+12224444']
        ))
        passengers_payload_pax_pay[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333'],
            pnr_create_date=passengers_payload_airline_pay[0]['pnr_create_date'],
            pax_record_locator=passengers_payload_airline_pay[0]['pax_record_locator'],
            flight_number=passengers_payload_airline_pay[0]['flight_number'],
        ))
        passengers_payload = [passengers_payload_airline_pay[0], passengers_payload_pax_pay[0]]

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertEqual(len(resp_json['data']), 2)

        if resp_json['data'][0]['context_id'] == passengers_payload_airline_pay[0]['context_id']:
            passenger1 = resp_json['data'][0]
            passenger2 = resp_json['data'][1]
        else:
            passenger1 = resp_json['data'][1]
            passenger2 = resp_json['data'][0]

        self.assertEqual(passenger1['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger1['meal_accommodation_status'], 'offered')
        self.assertEqual(passenger2['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger2['meal_accommodation_status'], 'not_offered')

        self.assertTrue(passenger1['airline_pay'])
        self.assertIsNotNone(passenger1['offer_url'])
        self.assertIsNotNone(passenger1['ak1'])
        self.assertIsNotNone(passenger1['ak2'])
        self.assertFalse(passenger2['airline_pay'])
        self.assertIsNone(passenger2['offer_url'])
        self.assertIsNone(passenger2['ak1'])
        self.assertIsNone(passenger2['ak2'])

        notifications = passenger1['notifications'] + passenger2['notifications']
        self._test_passenger_notifications(passenger1['notifications'], ['test2@blackhole.tvlinc.com'], ['+12224444'], 1, 1, 2, 0, False, False, 0)
        self._test_passenger_notifications(passenger2['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)
        self._test_passenger_notifications(notifications, ['test@blackhole.tvlinc.com', 'test2@blackhole.tvlinc.com'], ['+12223333', '+12224444'], 2, 2, 2, 0, False, False, 2)

    @should_skip_local_test
    def test_two_passengers_different_pnr_group_different_airline_pay_one_meal_only(self):
        """
        validate passengers can enter the system on separate pnr groups with different airline_pay values
        and one receives a meal only voucher
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload_airline_pay = self._generate_n_passenger_payload(1)
        passengers_payload_pax_pay = self._generate_n_passenger_payload(1)

        passengers_payload_airline_pay[0].update(dict(
            airline_pay=True,
            meal_accommodation=True,
            hotel_accommodation=False,
            notify=True,
            emails=['test2@blackhole.tvlinc.com'],
            phone_numbers=['+12224444']
        ))
        passengers_payload_pax_pay[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333'],
            pnr_create_date=passengers_payload_airline_pay[0]['pnr_create_date'],
            pax_record_locator=passengers_payload_airline_pay[0]['pax_record_locator'],
            flight_number=passengers_payload_airline_pay[0]['flight_number'],
        ))
        passengers_payload = [passengers_payload_airline_pay[0], passengers_payload_pax_pay[0]]

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        self.assertEqual(len(resp_json['data']), 2)

        if resp_json['data'][0]['context_id'] == passengers_payload_airline_pay[0]['context_id']:
            passenger1 = resp_json['data'][0]
            passenger2 = resp_json['data'][1]
        else:
            passenger1 = resp_json['data'][1]
            passenger2 = resp_json['data'][0]

        self.assertEqual(passenger1['hotel_accommodation_status'], 'not_offered')
        self.assertEqual(passenger1['meal_accommodation_status'], 'accepted')
        self.assertEqual(passenger2['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger2['meal_accommodation_status'], 'not_offered')

        self.assertTrue(passenger1['airline_pay'])
        self.assertIsNotNone(passenger1['offer_url'])
        self.assertIsNotNone(passenger1['ak1'])
        self.assertIsNotNone(passenger1['ak2'])
        UUID(passenger1['voucher_id'], version=4)
        self.assertFalse(passenger2['airline_pay'])
        self.assertIsNone(passenger2['offer_url'])
        self.assertIsNone(passenger2['ak1'])
        self.assertIsNone(passenger2['ak2'])

        notifications = passenger1['notifications'] + passenger2['notifications']
        self._test_passenger_notifications(passenger1['notifications'], ['test2@blackhole.tvlinc.com'], ['+12224444'], 1, 1, 0, 2, False, False, 0)
        self._test_passenger_notifications(passenger2['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)
        self._test_passenger_notifications(notifications, ['test@blackhole.tvlinc.com', 'test2@blackhole.tvlinc.com'], ['+12223333', '+12224444'], 2, 2, 0, 2, False, False, 2)

    @should_skip_local_test
    def test_passenger_pay_notification_no_passenger_pay_url(self):
        """
        validate passenger pay passenger receives 400 error if no url has been given yet
        when requesting a notification.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['airline_pay'], False)
        self._test_passenger_notifications(passenger['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)

        payload = {
            'email': 'test@blackhole.tvlinc.com'
        }

        notify_resp = requests.post(url=self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications', headers=headers, json=payload)
        self.assertEqual(notify_resp.status_code, 400)
        notify_json = notify_resp.json()
        self._validate_error_message(notify_json, 400, 'Bad Request', 'CANNOT_NOTIFY', 'Passenger has no passenger pay url.', [])

    @should_skip_local_test
    def test_passenger_pay_cannot_book_hotel(self):
        """
        validate passenger pay passenger receives 400 error if passenger uses hotel endpoint.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['airline_pay'], False)
        self._test_passenger_notifications(passenger['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)

        payload = {
            'context_ids': [passenger['context_id']],
            'room_count': 1,
            'hotel_id': 'tvl-12345'
        }

        booking_resp = requests.post(url=self._api_host + '/api/v1/hotels', headers=headers, json=payload)
        self.assertEqual(booking_resp.status_code, 400)
        booking_resp_json = booking_resp.json()
        self._validate_error_message(booking_resp_json, 400, 'Bad Request', 'PASSENGER_INVALID_STATUS', 'Passenger pay passengers cannot use this endpoint.', [])

    @should_skip_local_test
    def test_passenger_pay_cannot_decline_hotel(self):
        """
        validate passenger pay passenger receives 400 error if passenger uses decline endpoint.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['airline_pay'], False)
        self._test_passenger_notifications(passenger['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)

        decline_resp = requests.put(url=self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/decline', headers=headers)
        self.assertEqual(decline_resp.status_code, 400)
        decline_resp_json = decline_resp.json()
        self._validate_error_message(decline_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_DECLINE', 'Passenger pay passengers cannot use this endpoint.', [])

    @should_skip_local_test
    def test_passenger_pay_cannot_cancel_hotel(self):
        """
        validate passenger pay passenger receives 400 error if passenger uses cancel endpoint.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['airline_pay'], False)
        self._test_passenger_notifications(passenger['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)

        decline_resp = requests.put(url=self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/cancel', headers=headers)
        self.assertEqual(decline_resp.status_code, 400)
        decline_resp_json = decline_resp.json()
        self._validate_error_message(decline_resp_json, 400, 'Bad Request', 'PASSENGER_CANNOT_CANCEL', 'Passenger pay passengers cannot use this endpoint.', [])

    @should_skip_local_test
    def test_passenger_pay_end_to_end(self):
        """
        validate passenger pay works end to end with notify True.
        NOTE: must have dev credentials and queue information in env variables.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['airline_pay'], False)
        self._test_passenger_notifications(passenger['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, False, False, 2)

        # send a pax pay notification manually and validate url is not available (graceful 400, waiting for async job)
        payload = {
            'email': 'test@blackhole.tvlinc.com'
        }

        notify_resp = requests.post(url=self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications', headers=headers, json=payload)
        self.assertEqual(notify_resp.status_code, 400)
        notify_json = notify_resp.json()
        self._validate_error_message(notify_json, 400, 'Bad Request', 'CANNOT_NOTIFY', 'Passenger has no passenger pay url.', [])

        # get full state and validate offer_url is None (waiting for async job)
        full_state_resp = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        self.assertEqual(full_state_resp_json['data']['passenger']['context_id'], passenger['context_id'])
        self.assertEqual(full_state_resp_json['data']['passenger']['hotel_accommodation_status'], 'offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['airline_pay'], False)
        self.assertIsNone(full_state_resp_json['data']['passenger']['offer_url'])

        # sleep for 2 minutes to wait for room storm to process our request and for our internal queue process to run
        sleep(120)

        # get full state and validate offer_url is not None (async job should be done)
        full_state_resp = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        self.assertEqual(full_state_resp_json['data']['passenger']['context_id'], passenger['context_id'])
        self.assertEqual(full_state_resp_json['data']['passenger']['hotel_accommodation_status'], 'offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['airline_pay'], False)
        self.assertIsNotNone(full_state_resp_json['data']['passenger']['offer_url'])

        # validate pax pay email is now sent/processed
        self._test_passenger_notifications(full_state_resp_json['data']['passenger']['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 1, 1, 0, 0, True, False, 2)

        # send a pax pay notification manually and validate url is available
        payload = {
            'email': 'test@blackhole.tvlinc.com'
        }

        notify_resp = requests.post(url=self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications', headers=headers, json=payload)
        self.assertEqual(notify_resp.status_code, 200)
        notify_json = notify_resp.json()['data']
        self._test_passenger_notifications([notify_json], ['test@blackhole.tvlinc.com'], [], 1, 0, 0, 0, False, False, 1)

        # validate notification is now on full state and all are sent
        full_state_resp = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        self.assertEqual(full_state_resp_json['data']['passenger']['context_id'], passenger['context_id'])
        self.assertEqual(full_state_resp_json['data']['passenger']['airline_pay'], False)
        self.assertEqual(len(full_state_resp_json['data']['passenger']['notifications']), 3)
        self._test_passenger_notifications(full_state_resp_json['data']['passenger']['notifications'], ['test@blackhole.tvlinc.com'], ['+12223333'], 2, 1, 0, 0, True, False, 3)

    @should_skip_local_test
    def test_passenger_pay_end_to_end_notify_false(self):
        """
        validate passenger pay works end to end with notify False.
        NOTE: must have dev credentials and queue information in env variables.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=False
        ))

        resp = requests.post(url=self._api_host + '/api/v1/passenger', headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        resp_json = resp.json()
        passenger = resp_json['data'][0]
        self.assertEqual(passenger['hotel_accommodation_status'], 'offered')
        self.assertEqual(passenger['meal_accommodation_status'], 'not_offered')
        self.assertEqual(passenger['airline_pay'], False)
        self.assertEqual(len(passenger['notifications']), 0)

        # send a pax pay notification manually and validate url is not available (graceful 400, waiting for async job)
        payload = {
            'email': 'test@blackhole.tvlinc.com'
        }

        notify_resp = requests.post(url=self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications', headers=headers, json=payload)
        self.assertEqual(notify_resp.status_code, 400)
        notify_json = notify_resp.json()
        self._validate_error_message(notify_json, 400, 'Bad Request', 'CANNOT_NOTIFY', 'Passenger has no passenger pay url.', [])

        # get full state and validate offer_url is None (waiting for async job)
        full_state_resp = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        self.assertEqual(full_state_resp_json['data']['passenger']['context_id'], passenger['context_id'])
        self.assertEqual(full_state_resp_json['data']['passenger']['hotel_accommodation_status'], 'offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['airline_pay'], False)
        self.assertIsNone(full_state_resp_json['data']['passenger']['offer_url'])
        self.assertEqual(len(full_state_resp_json['data']['passenger']['notifications']), 0)

        # sleep for 2 minutes to wait for room storm to process our request and for our internal queue process to run
        sleep(120)

        # get full state and validate offer_url is not None (async job should be done)
        full_state_resp = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        self.assertEqual(full_state_resp_json['data']['passenger']['context_id'], passenger['context_id'])
        self.assertEqual(full_state_resp_json['data']['passenger']['hotel_accommodation_status'], 'offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['meal_accommodation_status'], 'not_offered')
        self.assertEqual(full_state_resp_json['data']['passenger']['airline_pay'], False)
        self.assertIsNotNone(full_state_resp_json['data']['passenger']['offer_url'])
        self.assertEqual(len(full_state_resp_json['data']['passenger']['notifications']), 0)

        # send a pax pay notification manually and validate url is available
        payload = {
            'email': 'test@blackhole.tvlinc.com'
        }

        notify_resp = requests.post(url=self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/notifications', headers=headers, json=payload)
        self.assertEqual(notify_resp.status_code, 200)
        notify_json = notify_resp.json()['data']
        self._test_passenger_notifications([notify_json], ['test@blackhole.tvlinc.com'], [], 1, 0, 0, 0, False, False, 1)

        # validate notification is now on full state
        full_state_resp = requests.get(url=passenger_url + '/' + passenger['context_id'] + '/state', headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)
        full_state_resp_json = full_state_resp.json()
        self.assertEqual(full_state_resp_json['data']['passenger']['context_id'], passenger['context_id'])
        self.assertEqual(full_state_resp_json['data']['passenger']['airline_pay'], False)
        self.assertEqual(len(full_state_resp_json['data']['passenger']['notifications']), 1)
        self._test_passenger_notifications(full_state_resp_json['data']['passenger']['notifications'], ['test@blackhole.tvlinc.com'], [], 1, 0, 0, 0, True, False, 1)

    @should_skip_local_test
    def validate_recycled_pnr_mixed_airline_pay_type(self):
        """
        test inspired from hotfix/pnr-search-issue.
        error where recycled pnrs having mixed airline_pay types causes 500 error in production.
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        pnr_url = self._api_host + '/api/v1/pnr'

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=False,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333']
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        pax_pay_passenger = resp.json()['data'][0]
        self.assertIsNone(pax_pay_passenger['offer_url'])

        passengers_payload = self._generate_n_passenger_payload(1)
        passengers_payload[0].update(dict(
            airline_pay=True,
            meal_accommodation=False,
            notify=True,
            emails=['test@blackhole.tvlinc.com'],
            phone_numbers=['+12223333'],
            pax_record_locator=pax_pay_passenger['pax_record_locator']
        ))

        resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(resp.status_code, 201)
        airline_pay_passenger = resp.json()['data'][0]

        query_params = dict(
            pax_record_locator=pax_pay_passenger['pax_record_locator']
        )

        sleep(60)  # sleep for 60 seconds to ensure async pax pay process is complete
        pnr_search = requests.get(url=pnr_url, headers=headers, params=query_params)
        self.assertEqual(pnr_search.status_code, 200)
        pnr_search_json = pnr_search.json()
        self.assertEqual(len(pnr_search_json['data']), 2)

        pnr_pax_pay_pax = None
        pnr_airline_pay_pax = None
        for passenger in pnr_search_json['data']:
            if passenger['context_id'] == pax_pay_passenger['context_id']:
                pnr_pax_pay_pax = passenger
            if passenger['context_id'] == airline_pay_passenger['context_id']:
                pnr_airline_pay_pax = passenger

        self.assertIsNotNone(pnr_pax_pay_pax)
        self.assertIsNotNone(pnr_airline_pay_pax)
        self.assertIsNotNone(pnr_pax_pay_pax['offer_url'])
