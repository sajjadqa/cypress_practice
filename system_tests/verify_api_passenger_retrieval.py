import datetime
from uuid import UUID

import requests

from StormxApp.tests.data_utilities import (
    generate_pax_record_locator,
    generate_pax_record_locator_group,
    generate_flight_number,
)
from stormx_verification_framework import (
    display_response,
    TEMPLATE_DATE,
    StormxSystemVerification,
)


class TestApiPassengerRetrieval(StormxSystemVerification):
    """
    Verify that endpoints that fetch information about passengers function properly.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiPassengerRetrieval, cls).setUpClass()

    def test_get_passenger_by_context_id(self):
        """
        verify that you can look up existing passengers by their context_id.
        """
        url_template = self._api_host + '/api/v1/passenger/{context_id}'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer)

        for passenger in passengers:
            context_id = passenger['context_id']
            self.assertTrue(context_id)
            url = url_template.format(context_id=context_id)
            response = requests.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_get_passenger_by_context_id__bad_context_id(self):
        """
        verify the system gracefully handles looking up context_ids that do not exist.
        """
        url_template = self._api_host + '/api/v1/passenger/{context_id}'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer)

        url = url_template.format(context_id='GARBAGE_CONTEXT_ID_THAT_DOES_NOT_EXIST')
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_get_passengers_by_flight_place_and_time(self):
        """
        verify that airlines can look up passengers
        """
        url = self._api_host + '/api/v1/passenger'
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer=customer)

        # record 3 groups of 2 passengers on the same flight
        passenger_flight_info = dict(
            flight_number=generate_flight_number(),
            disrupt_depart=TEMPLATE_DATE + ' 18:30',  # TODO: generate.
            port_accommodation='LAX'
        )
        passengers = self._create_2_passengers(customer=customer, **passenger_flight_info)
        passengers += self._create_2_passengers(customer=customer, **passenger_flight_info)
        passengers += self._create_2_passengers(customer=customer, **passenger_flight_info)

        query_parameters = passenger_flight_info
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        returned_passengers = response.json()['data']
        self.assertEqual(len(returned_passengers), 6)

    def test_get_passengers_related_to_context_id(self):
        """
        verify that an airline can look up passengers in the same group by their context_id.
        """
        url_template = self._api_host + '/api/v1/passenger/{context_id}/related'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)

        # create a group of 4 passengers
        common_passenger_info = dict(
            pax_record_locator=generate_pax_record_locator(),
            pax_record_locator_group=generate_pax_record_locator_group(),
        )
        passengers = self._create_2_passengers(customer=customer, **common_passenger_info)
        passengers += self._create_2_passengers(customer=customer, **common_passenger_info)

        for passenger in passengers:
            context_id = passenger['context_id']
            self.assertTrue(context_id)
            url = url_template.format(context_id=context_id)
            response = requests.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)
            response_json = response.json()

            # 4 passengers total, 3 other passengers related to the current passenger.
            other_passengers = response_json['data']
            self.assertEqual(len(other_passengers), 3)

            # ensure the passenger is not in the list of passengers he is related to.
            other_context_ids = [p['context_id'] for p in other_passengers]
            self.assertNotIn(context_id, other_context_ids)

    def test_get_pnr_by_group_and_date(self):
        """
        verify that airlines can look up PNRs by pax_record_locator_group and pnr_create_date.

        (2 passengers are put under the same pax_record_locator_group, and they must be retrieved together.)
        """
        url = self._api_host + '/api/v1/pnr'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer)
        passenger_context_ids = set(p['context_id'] for p in passengers)

        query_parameters = dict(
            pax_record_locator_group=passengers[0]['pax_record_locator_group'],
            pnr_create_date=passengers[0]['pnr_create_date'],
        )
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        returned_passengers = response_json['data']
        returned_passenger_context_ids = set(p['context_id'] for p in returned_passengers)
        self.assertEqual(returned_passenger_context_ids, passenger_context_ids)

    def test_validate_pnr_create_date_not_required_on_pnr_search(self):
        """
        validate that pnr_create_date is not required on PNR search endpoint
        """
        url = self._api_host + '/api/v1/pnr'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer)
        passenger_context_ids = set(p['context_id'] for p in passengers)

        query_parameters = dict(
            pax_record_locator_group=passengers[0]['pax_record_locator_group'],
        )
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        returned_passengers = response_json['data']
        returned_passenger_context_ids = {p['context_id'] for p in returned_passengers}
        self.assertEqual(returned_passenger_context_ids, passenger_context_ids)

        query_parameters = dict(
            pax_record_locator=passengers[0]['pax_record_locator'],
        )
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        returned_passengers = response_json['data']
        returned_passenger_context_ids = {p['context_id'] for p in returned_passengers}
        self.assertEqual(returned_passenger_context_ids, passenger_context_ids)

    def test_validate_pnr_search_different_pnr_create_date(self):
        """
        validate that recycled PNRs does not crash the API.
        """
        url = self._api_host + '/api/v1/pnr'
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer=customer)

        pnr_create_date = datetime.datetime.utcnow().date()
        pnr_create_date_old = pnr_create_date - datetime.timedelta(days=365)

        pnr_create_date_string = pnr_create_date.strftime('%Y-%m-%d')
        pnr_create_date_old_string = pnr_create_date_old.strftime('%Y-%m-%d')

        passengers = self._create_2_passengers(customer=customer, pnr_create_date=pnr_create_date_string)
        passenger_context_ids = {passenger['context_id'] for passenger in passengers}
        self.assertEqual(len(passenger_context_ids), 2)

        passengers_old = self._create_2_passengers(customer=customer, pax_record_locator=passengers[0]['pax_record_locator'], pnr_create_date=pnr_create_date_old_string)
        passenger_context_ids_old = {passenger['context_id'] for passenger in passengers_old}
        self.assertEqual(len(passenger_context_ids_old), 2)

        all_passenger_context_ids = passenger_context_ids.union(passenger_context_ids_old)
        self.assertEqual(len(all_passenger_context_ids), 4)

        query_parameters = dict(
            pax_record_locator=passengers[0]['pax_record_locator'],
        )
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        returned_passengers = response_json['data']
        returned_passenger_context_ids = {passenger['context_id'] for passenger in returned_passengers}
        self.assertEqual(returned_passenger_context_ids, all_passenger_context_ids)

        query_parameters = dict(
            pax_record_locator=passengers[0]['pax_record_locator'],
            pnr_create_date=pnr_create_date_string
        )
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        returned_passengers = response_json['data']
        returned_passenger_context_ids = {passenger['context_id'] for passenger in returned_passengers}
        self.assertEqual(returned_passenger_context_ids, passenger_context_ids)

        query_parameters = dict(
            pax_record_locator=passengers[0]['pax_record_locator'],
            pnr_create_date=pnr_create_date_old_string
        )
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        returned_passengers = response_json['data']
        returned_passenger_context_ids = {passenger['context_id'] for passenger in returned_passengers}
        self.assertEqual(returned_passenger_context_ids, passenger_context_ids_old)

    def test_passenger_notifications_offered(self):
        """
        verify passenger notifications of type offered are returned for various passenger endpoints
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'
        pnr_url = self._api_host + '/api/v1/pnr'

        passengers_payload = self._generate_n_passenger_payload(3)
        context_id1 = passengers_payload[0]['context_id']
        context_id2 = passengers_payload[1]['context_id']
        context_id3 = passengers_payload[2]['context_id']
        flight_date = TEMPLATE_DATE + ' 16:30'
        flight_number = generate_flight_number()
        port = passengers_payload[0]['port_accommodation']
        pnr_group = passengers_payload[0]['pax_record_locator_group']
        pnr_create_date = passengers_payload[0]['pnr_create_date']

        emails1 = ['stormx.test@tvlinc.com', 'stormx.test2@tvlinc.com']
        phone_numbers1 = ['+11112222', '+12223333']
        passengers_payload[0].update(dict(
            emails=emails1,
            phone_numbers=phone_numbers1,
            disrupt_depart=flight_date,
            flight_number=flight_number,
            notify=True
        ))

        emails2 = ['2stormx.test@tvlinc.com', '2stormx.test2@tvlinc.com']
        phone_numbers2 = ['+121112222', '+122223333']
        passengers_payload[1].update(dict(
            emails=emails2,
            phone_numbers=phone_numbers2,
            disrupt_depart=flight_date,
            flight_number=flight_number,
            notify=True
        ))

        emails3 = ['3stormx.test@tvlinc.com', '3stormx.test2@tvlinc.com']
        phone_numbers3 = ['+131112222', '+132223333']
        passengers_payload[2].update(dict(
            emails=emails3,
            phone_numbers=phone_numbers3,
            disrupt_depart=flight_date,
            flight_number=flight_number,
            notify=True
        ))

        import_resp = requests.post(url=passenger_url, headers=headers, json=passengers_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()
        for passenger in import_resp_json['data']:
            self.assertEqual(len(passenger['notifications']), 4)
            for notification in passenger['notifications']:
                self.assertEqual(notification['notification_type'], 'offer')

        pax1_resp = requests.get(url=passenger_url + '/' + context_id1, headers=headers)
        self.assertEqual(pax1_resp.status_code, 200)
        pax1_resp_notifications = pax1_resp.json()['data']['notifications']

        self._test_passenger_notifications(pax1_resp_notifications, emails1, phone_numbers1, 2, 2, 4, 0)

        pax1_state_resp = requests.get(url=passenger_url + '/' + context_id1 + '/state', headers=headers)
        self.assertEqual(pax1_state_resp.status_code, 200)
        pax1_state_notifications = pax1_state_resp.json()['data']['passenger']['notifications']

        self._test_passenger_notifications(pax1_state_notifications, emails1, phone_numbers1, 2, 2, 4, 0)

        pax2_resp = requests.get(url=passenger_url + '/' + context_id2, headers=headers)
        self.assertEqual(pax2_resp.status_code, 200)
        pax2_resp_notifications = pax2_resp.json()['data']['notifications']

        self._test_passenger_notifications(pax2_resp_notifications, emails2, phone_numbers2, 2, 2, 4, 0)

        pax2_state_resp = requests.get(url=passenger_url + '/' + context_id2 + '/state', headers=headers)
        self.assertEqual(pax2_state_resp.status_code, 200)
        pax2_state_notifications = pax2_state_resp.json()['data']['passenger']['notifications']

        self._test_passenger_notifications(pax2_state_notifications, emails2, phone_numbers2, 2, 2, 4, 0)

        pax3_resp = requests.get(url=passenger_url + '/' + context_id3, headers=headers)
        self.assertEqual(pax3_resp.status_code, 200)
        pax3_resp_notifications = pax3_resp.json()['data']['notifications']

        self._test_passenger_notifications(pax3_resp_notifications, emails3, phone_numbers3, 2, 2, 4, 0)

        pax3_state_resp = requests.get(url=passenger_url + '/' + context_id3 + '/state', headers=headers)
        self.assertEqual(pax3_state_resp.status_code, 200)
        pax3_state_notifications = pax3_state_resp.json()['data']['passenger']['notifications']

        self._test_passenger_notifications(pax3_state_notifications, emails3, phone_numbers3, 2, 2, 4, 0)

        related_resp = requests.get(url=passenger_url + '/' + context_id1 + '/related', headers=headers)
        self.assertEqual(related_resp.status_code, 200)
        related_resp_json = related_resp.json()
        self.assertEqual(len(related_resp_json['data']), 2)

        for passenger in related_resp_json['data']:
            self.assertIn(passenger['context_id'], [context_id2, context_id3])
            self._test_passenger_notifications(passenger['notifications'], emails2 + emails3,
                                               phone_numbers2 + phone_numbers3, 2, 2, 4, 0)

        flight_resp = requests.get(url=passenger_url + '?flight_number=' + flight_number + '&disrupt_depart=' + flight_date + '&port_accommodation=' + port, headers=headers)
        self.assertEqual(flight_resp.status_code, 200)
        flight_resp_json = flight_resp.json()
        self.assertEqual(len(flight_resp_json['data']), 3)

        for passenger in flight_resp_json['data']:
            self.assertIn(passenger['context_id'], [context_id1, context_id2, context_id3])
            self._test_passenger_notifications(passenger['notifications'], emails1 + emails2 + emails3,
                                               phone_numbers1 + phone_numbers2 + phone_numbers3, 2, 2, 4, 0)

        pnr_resp = requests.get(url=pnr_url + '?pax_record_locator_group=' + pnr_group + '&pnr_create_date=' + pnr_create_date, headers=headers)
        self.assertEqual(pnr_resp.status_code, 200)
        pnr_resp_json = pnr_resp.json()
        self.assertEqual(len(pnr_resp_json['data']), 3)

        for passenger in pnr_resp_json['data']:
            self.assertIn(passenger['context_id'], [context_id1, context_id2, context_id3])
            self._test_passenger_notifications(passenger['notifications'], emails1 + emails2 + emails3,
                                               phone_numbers1 + phone_numbers2 + phone_numbers3, 2, 2, 4, 0)

    def test_status_not_in_passenger_objects(self):
        """
        ensuring system is not returning status field for passenger objects
        """
        headers = self._generate_airline_headers('Purple Rain Airlines')

        passengers = self._create_2_passengers(customer='Purple Rain Airlines', hotel_accommodation=False)
        for passenger in passengers:
            self.assertNotIn('status', passenger)
            self.assertIn('hotel_accommodation_status', passenger)
            self.assertIn('meal_accommodation_status', passenger)
            self.assertIn('transport_accommodation_status', passenger)

        voucher_url = self._api_host + '/api/v1/voucher/' + str(passengers[0]['voucher_id'])
        voucher_resp = requests.get(url=voucher_url, headers=headers)
        self.assertEqual(voucher_resp.status_code, 200)

        for passenger in voucher_resp.json()['data']['passengers']:
            self.assertNotIn('status', passenger)
            self.assertIn('hotel_accommodation_status', passenger)
            self.assertIn('meal_accommodation_status', passenger)
            self.assertIn('transport_accommodation_status', passenger)

        full_state_url = self._api_host + '/api/v1/passenger/' + passengers[0]['context_id'] + '/state'
        full_state_resp = requests.get(url=full_state_url, headers=headers)
        self.assertEqual(full_state_resp.status_code, 200)

        passenger = full_state_resp.json()['data']['passenger']
        self.assertNotIn('status', passenger)
        self.assertIn('hotel_accommodation_status', passenger)
        self.assertIn('meal_accommodation_status', passenger)
        self.assertIn('transport_accommodation_status', passenger)

    def test_tvl_internal_passenger_context(self):
        """
        test tvl/airline/{airline_id}/passenger/{context_id}
        """
        airline_id_bad = '72'
        airline_id_good = '294'
        customer = 'Purple Rain Airlines'
        stormx_headers = self._generate_tvl_stormx_headers()
        airline_headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        pax_payload = self._generate_n_passenger_payload(1)
        import_resp = requests.post(url=passenger_url, headers=airline_headers, json=pax_payload)
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()

        context_id = import_resp_json['data'][0]['context_id']
        tvl_passenger_url_good = self._api_host + '/api/v1/tvl/airline/' + airline_id_good + '/passenger/' + context_id
        tvl_passenger_url_bad = self._api_host + '/api/v1/tvl/airline/' + airline_id_bad + '/passenger/' + context_id

        tvl_context_resp_bad = requests.get(url=tvl_passenger_url_bad, headers=stormx_headers)
        self.assertEqual(tvl_context_resp_bad.status_code, 404)

        tvl_context_resp_good = requests.get(url=tvl_passenger_url_good, headers=stormx_headers)
        self.assertEqual(tvl_context_resp_good.status_code, 200)
        tvl_context_json = tvl_context_resp_good.json()
        self.assertEqual(tvl_context_json['data']['context_id'], context_id)

    def test_tvl_internal_pnr(self):
        """
        test tvl/airline/{airline_id}/pnr
        """
        airline_id_bad = '72'
        airline_id_good = '294'
        customer = 'Purple Rain Airlines'
        stormx_headers = self._generate_tvl_stormx_headers()
        airline_headers = self._generate_airline_headers(customer)
        passenger_url = self._api_host + '/api/v1/passenger'

        pax_payload1 = self._generate_n_passenger_payload(1)
        pax_payload2 = self._generate_n_passenger_payload(1)
        pax_payload1[0].update(dict(
            pax_record_locator=pax_payload2[0]['pax_record_locator'],
            pnr_create_date=pax_payload2[0]['pnr_create_date']
        ))

        import_resp = requests.post(url=passenger_url, headers=airline_headers, json=[pax_payload1[0], pax_payload2[0]])
        self.assertEqual(import_resp.status_code, 201)
        import_resp_json = import_resp.json()

        passenger_1 = import_resp_json['data'][0]
        passenger_2 = import_resp_json['data'][1]
        self.assertEqual(passenger_1['pnr_create_date'], passenger_2['pnr_create_date'])
        self.assertEqual(passenger_1['pax_record_locator'], passenger_2['pax_record_locator'])
        self.assertNotEqual(passenger_1['pax_record_locator_group'], passenger_2['pax_record_locator_group'])

        tvl_pnr_url_bad = self._api_host + '/api/v1/tvl/airline/' + airline_id_bad + '/pnr?pnr_create_date=' + passenger_1['pnr_create_date'] + '&pax_record_locator=' + passenger_1['pax_record_locator']
        tvl_pnr_url_good = self._api_host + '/api/v1/tvl/airline/' + airline_id_good + '/pnr?pnr_create_date=' + passenger_1['pnr_create_date'] + '&pax_record_locator=' + passenger_1['pax_record_locator']
        tvl_pnr_url_group_1 = self._api_host + '/api/v1/tvl/airline/' + airline_id_good + '/pnr?pnr_create_date=' + passenger_1['pnr_create_date'] + '&pax_record_locator_group=' + passenger_1['pax_record_locator_group']
        tvl_pnr_url_group_2 = self._api_host + '/api/v1/tvl/airline/' + airline_id_good + '/pnr?pnr_create_date=' + passenger_1['pnr_create_date'] + '&pax_record_locator_group=' + passenger_2['pax_record_locator_group']
        tvl_pnr_url = self._api_host + '/api/v1/tvl/airline/' + airline_id_good + '/pnr?pnr_create_date=' + passenger_1['pnr_create_date'] + '&pax_record_locator_group=' + passenger_1['pax_record_locator_group'] + '&pax_record_locator=' + passenger_1['pax_record_locator']

        tvl_pnr_bad = requests.get(url=tvl_pnr_url_bad, headers=stormx_headers)
        self.assertEqual(tvl_pnr_bad.status_code, 404)

        tvl_pnr_good = requests.get(url=tvl_pnr_url_good, headers=stormx_headers)
        self.assertEqual(tvl_pnr_good.status_code, 200)
        tvl_context_json = tvl_pnr_good.json()
        self.assertEqual(len(tvl_context_json['data']), 2)
        for passenger in tvl_context_json['data']:
            self.assertEqual(passenger['pnr_create_date'], passenger_1['pnr_create_date'])
            self.assertEqual(passenger['pax_record_locator'], passenger_1['pax_record_locator'])
        self.assertNotEqual(tvl_context_json['data'][0]['pax_record_locator_group'], tvl_context_json['data'][1]['pax_record_locator_group'])

        tvl_pnr_1 = requests.get(url=tvl_pnr_url_group_1, headers=stormx_headers)
        self.assertEqual(tvl_pnr_1.status_code, 200)
        tvl_pnr_1_json = tvl_pnr_1.json()
        self.assertEqual(len(tvl_pnr_1_json['data']), 1)
        for passenger in tvl_pnr_1_json['data']:
            self.assertEqual(passenger['pnr_create_date'], passenger_1['pnr_create_date'])
            self.assertEqual(passenger['pax_record_locator'], passenger_1['pax_record_locator'])
            self.assertEqual(passenger['pax_record_locator_group'], passenger_1['pax_record_locator_group'])

        tvl_pnr_2 = requests.get(url=tvl_pnr_url_group_2, headers=stormx_headers)
        self.assertEqual(tvl_pnr_2.status_code, 200)
        tvl_pnr_2_json = tvl_pnr_2.json()
        self.assertEqual(len(tvl_pnr_2_json['data']), 1)
        for passenger in tvl_pnr_2_json['data']:
            self.assertEqual(passenger['pnr_create_date'], passenger_1['pnr_create_date'])
            self.assertEqual(passenger['pax_record_locator'], passenger_1['pax_record_locator'])
            self.assertEqual(passenger['pax_record_locator_group'], passenger_2['pax_record_locator_group'])

        tvl_pnr = requests.get(url=tvl_pnr_url, headers=stormx_headers)
        self.assertEqual(tvl_pnr.status_code, 200)
        tvl_pnr_json = tvl_pnr.json()
        self.assertEqual(len(tvl_pnr_json['data']), 1)
        for passenger in tvl_pnr_json['data']:
            self.assertEqual(passenger['pnr_create_date'], passenger_1['pnr_create_date'])
            self.assertEqual(passenger['pax_record_locator'], passenger_1['pax_record_locator'])
            self.assertEqual(passenger['pax_record_locator_group'], passenger_1['pax_record_locator_group'])

    def test_validate_pnr_locator_or_group(self):
        """
        validate pnr endpoint forces serializer pax_record_locator or pax_record_locator_group
        """
        error_description = 'Request must contain at least a valid pax_record_locator or pax_record_locator_group.'
        stormx_headers = self._generate_tvl_stormx_headers()
        airline_headers = self._generate_airline_headers('Purple Rain Airlines')
        api_pnr_url = self._api_host + '/api/v1/pnr?pnr_create_date=2018-07-18'
        tvl_pnr_url = self._api_host + '/api/v1/tvl/airline/294/pnr?pnr_create_date=2018-07-18'

        resp = requests.get(url=api_pnr_url, headers=airline_headers)
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self._validate_error_message(resp_json, 400, 'Bad Request', 'INVALID_PNR_SEARCH', error_description, [])

        resp2 = requests.get(url=tvl_pnr_url, headers=stormx_headers)
        self.assertEqual(resp2.status_code, 400)
        resp_json2 = resp2.json()
        self._validate_error_message(resp_json2, 400, 'Bad Request', 'INVALID_PNR_SEARCH', error_description, [])

    def test_get_passenger_state_by_context_id(self):
        """
        verify that you can look up existing passengers by their context_id.
        """
        url_template = self._api_host + '/api/v1/passenger/{context_id}/state'
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)

        passengers = self._create_2_passengers(customer=customer)

        for passenger in passengers:
            context_id = passenger['context_id']
            self.assertTrue(context_id)
            url = url_template.format(context_id=context_id)
            response = requests.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.reason, 'OK')
            response_json = response.json()
            self.assertIs(response_json['error'], False)
            self.assertEqual(response_json['meta']['message'], 'OK')
            # display_response(response)
            # TODO: verify fields. also, this method might make a nice utility.

    def test_passenger_offer_opened_date(self):
        """
        validates passenger.offer_opened_date is returned
        on Passenger and FullState
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        # create passenger
        passengers = self._create_2_passengers(customer=customer)
        for passenger in passengers:
            self.assertIn('offer_opened_date', passenger)
            self.assertIsNone(passenger['offer_opened_date'])

        passenger = passengers[0]
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        full_state_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/state'
        offer_url = passenger['offer_url']

        # validate passenger.offer_opened_date is null
        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('offer_opened_date', resp['data'])
        self.assertIsNone(resp['data']['offer_opened_date'])

        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('offer_opened_date', resp['data']['passenger'])
        self.assertIsNone(resp['data']['passenger']['offer_opened_date'])
        modified_date = resp['data']['passenger']['modified_date']

        # visit offer link
        resp = requests.get(url=offer_url)
        embedded_json = self._get_landing_page_embedded_json(resp)
        expected_offer_opened_date = embedded_json['passenger']['offer_opened_date']

        # validate passenger.offer_opened_date is now populated and modified_date has changed
        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('offer_opened_date', resp['data'])
        self.assertEqual(resp['data']['offer_opened_date'], expected_offer_opened_date)
        self.assertNotEqual(resp['data']['modified_date'], modified_date)

        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('offer_opened_date', resp['data']['passenger'])
        self.assertEqual(resp['data']['passenger']['offer_opened_date'], expected_offer_opened_date)
        self.assertNotEqual(resp['data']['passenger']['modified_date'], modified_date)
        expected_modified_date = resp['data']['passenger']['modified_date']

        # re visit offer link
        resp = requests.get(url=offer_url)
        embedded_json = self._get_landing_page_embedded_json(resp)
        self.assertEqual(embedded_json['passenger']['offer_opened_date'], expected_offer_opened_date)

        # validate that passenger.offer_opened_date and modified_date has not changed
        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('offer_opened_date', resp['data'])
        self.assertEqual(resp['data']['offer_opened_date'], expected_offer_opened_date)
        self.assertEqual(resp['data']['modified_date'], expected_modified_date)

        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('offer_opened_date', resp['data']['passenger'])
        self.assertEqual(resp['data']['passenger']['modified_date'], expected_modified_date)

    def test_passenger_full_state_voucher_id_is_not_none(self):
        """
        validates passenger.voucher_id is null and not 'None' on FullState call
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer=customer)
        for passenger in passengers:
            self.assertIn('voucher_id', passenger)
            self.assertIsNone(passenger['voucher_id'])

        passenger = passengers[0]
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        full_state_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/state'

        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data'])
        self.assertIsNone(resp['data']['voucher_id'])

        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data']['passenger'])
        self.assertIsNone(resp['data']['passenger']['voucher_id'])

        self.assertIn('voucher', resp['data'])
        self.assertIsNone(resp['data']['voucher']['hotel_voucher'])
        self.assertEqual(len(resp['data']['voucher']['meal_vouchers']), 0)
        self.assertIsNone(resp['data']['voucher']['modified_date'])
        self.assertIsNone(resp['data']['voucher']['status'])

    def test_passenger_full_state_meal_only_voucher(self):
        """
        validates meal only voucher is valid on FullState call
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=False)
        for passenger in passengers:
            self.assertIn('voucher_id', passenger)
            UUID(passenger['voucher_id'], version=4)

        passenger = passengers[0]
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        voucher_url = self._api_host + '/api/v1/voucher/' + passenger['voucher_id']
        full_state_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/state'

        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data'])
        UUID(resp['data']['voucher_id'], version=4)

        resp = requests.get(url=voucher_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        if resp['data']['passengers'][0]['context_id'] == passenger['context_id']:
            meal_vouchers = resp['data']['passengers'][0]['meal_vouchers']
        else:
            meal_vouchers = resp['data']['passengers'][1]['meal_vouchers']

        self.assertGreater(len(meal_vouchers), 0)
        for meal in meal_vouchers:
            self.assertEqual(meal['provider'], 'tvl')

        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data']['passenger'])
        UUID(resp['data']['passenger']['voucher_id'], version=4)

        self.assertIn('voucher', resp['data'])
        self.assertIsNone(resp['data']['voucher']['hotel_voucher'])
        self.assertIsNotNone(resp['data']['voucher']['modified_date'])
        self.assertEqual(resp['data']['voucher']['status'], 'finalized')

        self.assertGreater(len(resp['data']['voucher']['meal_vouchers']), 0)
        for meal in resp['data']['voucher']['meal_vouchers']:
            UUID(meal['id'], version=4)
            self.assertEqual(meal['provider'], 'tvl')

    def test_passenger_full_state_meal_only_voucher_no_provider(self):
        """
        validates meal only voucher is valid on FullState call and provider is not returned
        """
        customer = 'American Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer=customer, hotel_accommodation=False)
        for passenger in passengers:
            self.assertIn('voucher_id', passenger)
            UUID(passenger['voucher_id'], version=4)

        passenger = passengers[0]
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        voucher_url = self._api_host + '/api/v1/voucher/' + passenger['voucher_id']
        full_state_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/state'

        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data'])
        UUID(resp['data']['voucher_id'], version=4)

        resp = requests.get(url=voucher_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        if resp['data']['passengers'][0]['context_id'] == passenger['context_id']:
            meal_vouchers = resp['data']['passengers'][0]['meal_vouchers']
        else:
            meal_vouchers = resp['data']['passengers'][1]['meal_vouchers']

        self.assertGreater(len(meal_vouchers), 0)
        for meal in meal_vouchers:
            self.assertEqual(meal['provider'], 'tvl')

        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data']['passenger'])
        UUID(resp['data']['passenger']['voucher_id'], version=4)

        self.assertIn('voucher', resp['data'])
        self.assertIsNone(resp['data']['voucher']['hotel_voucher'])
        self.assertIsNotNone(resp['data']['voucher']['modified_date'])
        self.assertEqual(resp['data']['voucher']['status'], 'finalized')

        self.assertGreater(len(resp['data']['voucher']['meal_vouchers']), 0)
        for meal in resp['data']['voucher']['meal_vouchers']:
            UUID(meal['id'], version=4)
            self.assertEqual(meal['provider'], 'tvl')

    def test_passenger_full_state_hotel_only_voucher(self):
        """
        validates hotel only voucher is valid on FullState call
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer=customer, meal_accommodation=False, port_accommodation='PHX')
        for passenger in passengers:
            self.assertIn('voucher_id', passenger)
            self.assertIsNone(passenger['voucher_id'])

        passenger = passengers[0]
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        full_state_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/state'

        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data'])
        self.assertIsNone(resp['data']['voucher_id'])

        # validate full state returns no voucher
        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data']['passenger'])
        self.assertIsNone(resp['data']['passenger']['voucher_id'])

        self.assertIn('voucher', resp['data'])
        self.assertIsNone(resp['data']['voucher']['hotel_voucher'])
        self.assertEqual(len(resp['data']['voucher']['meal_vouchers']), 0)
        self.assertIsNone(resp['data']['voucher']['modified_date'])
        self.assertIsNone(resp['data']['voucher']['status'])

        # do a booking
        hotel_id_good = 101307
        stormx_headers = self._generate_tvl_stormx_headers()
        hotel_id = 'tvl-' + str(hotel_id_good)

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)

        # validate full state contains voucher
        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data']['passenger'])
        UUID(resp['data']['passenger']['voucher_id'], version=4)

        self.assertIn('voucher', resp['data'])
        self.assertIsNotNone(resp['data']['voucher']['hotel_voucher'])
        UUID(resp['data']['voucher']['hotel_voucher']['id'], version=4)
        self.assertEqual(len(resp['data']['voucher']['meal_vouchers']), 0)
        self.assertIsNotNone(resp['data']['voucher']['modified_date'])
        self.assertEqual(resp['data']['voucher']['status'], 'finalized')

    def test_passenger_full_state_meal_and_hotel_voucher(self):
        """
        validates meal and hotel voucher is valid on FullState call
        """
        customer = 'Purple Rain Airlines'
        headers = self._generate_airline_headers(customer)

        passengers = self._create_2_passengers(customer=customer, port_accommodation='PHX')
        for passenger in passengers:
            self.assertIn('voucher_id', passenger)
            self.assertIsNone(passenger['voucher_id'])

        passenger = passengers[0]
        passenger_url = self._api_host + '/api/v1/passenger/' + passenger['context_id']
        full_state_url = self._api_host + '/api/v1/passenger/' + passenger['context_id'] + '/state'

        resp = requests.get(url=passenger_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data'])
        self.assertIsNone(resp['data']['voucher_id'])

        # validate full state returns no voucher
        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data']['passenger'])
        self.assertIsNone(resp['data']['passenger']['voucher_id'])

        self.assertIn('voucher', resp['data'])
        self.assertIsNone(resp['data']['voucher']['hotel_voucher'])
        self.assertEqual(len(resp['data']['voucher']['meal_vouchers']), 0)
        self.assertIsNone(resp['data']['voucher']['modified_date'])
        self.assertIsNone(resp['data']['voucher']['status'])

        # do a booking
        hotel_id_good = 101307
        stormx_headers = self._generate_tvl_stormx_headers()
        hotel_id = 'tvl-' + str(hotel_id_good)

        booking_payload = dict(
            context_ids=[passenger['context_id']],
            hotel_id=hotel_id,
            room_count=1,
            block_type='soft_block',
            hotel_rate=99
        )

        booking_url = self._api_host + '/api/v1/tvl/airline/294/hotels'
        booking_response = requests.post(booking_url, headers=stormx_headers, json=booking_payload)
        self.assertEqual(booking_response.status_code, 200)
        booking_response_json = booking_response.json()
        self.assertIs(booking_response_json['error'], False)
        self.assertEqual(booking_response_json['data']['hotel_voucher']['hotel_id'], hotel_id)

        # validate full state contains voucher
        resp = requests.get(url=full_state_url, headers=headers).json()
        self.assertEqual(resp['meta']['status'], 200)
        self.assertIn('voucher_id', resp['data']['passenger'])
        UUID(resp['data']['passenger']['voucher_id'], version=4)

        self.assertIn('voucher', resp['data'])
        self.assertIsNotNone(resp['data']['voucher']['hotel_voucher'])
        UUID(resp['data']['voucher']['hotel_voucher']['id'], version=4)

        self.assertGreater(len(resp['data']['voucher']['meal_vouchers']), 0)
        for meal in resp['data']['voucher']['meal_vouchers']:
            UUID(meal['id'], version=4)

        self.assertIsNotNone(resp['data']['voucher']['modified_date'])
        self.assertEqual(resp['data']['voucher']['status'], 'finalized')

    def test_get_passenger_state_send_queue_message_not_configured(self):
        """
        verify that the full state endpoint gracefully handles when the
        airline queue is not configured when a queue message send is requested
        """
        customer = 'Delta Air Lines'
        headers = self._generate_airline_headers(customer=customer)
        url_template = self._api_host + '/api/v1/passenger/{context_id}/state?send_queue_message=true'

        passenger = self._create_2_passengers(customer=customer)[0]

        url = url_template.format(context_id=passenger['context_id'])
        response = requests.get(url, headers=headers)

        self._validate_error_message(response.json(), 400, 'Bad Request', 'FEATURE_NOT_SUPPORTED',
                                     'Airline queue not configured. Cannot send passenger queue message.', [])
