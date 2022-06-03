import datetime
import uuid

import requests

from stormx_verification_framework import (
    StormxSystemVerification,
    DATETIME_FORMAT_FOR_VOUCHERS,
)


HOTEL_AVAILABILITY_BLOCK_DATE_FORMAT = '%d/%m/%Y '  # TODO: that space at the end just looks wrong.


class TestStormxUI(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """

    def test_dashboard_doesnt_crash(self):
        """
        perform rudimentary check that the PHP dashboard is working and not
        broken (i.e., due to exception from database issue, etc)
        """
        url = self._php_host + '/admin/index.php'
        headers = self._generate_stormx_php_headers()
        response = requests.get(url, headers=headers, cookies=self._support_cookies)

        self.assertIn('travellianceApp', response.text)
        self.assertNotIn('ERROR', response.text)
        # TODO: look for more common text on success, and
        #       actually test page content for reasonable information on it.
        #       (3 dashboard views available: Hotel Users, Airline Users, everyone else)

    def test_vouchers_page_session_security(self):
        """
        verify that the system allows access to the vouchers page when logged in
        and prevents access to the vouchers page when not logged in.
        """
        url = self._php_host + '/admin/vouchers.php'
        headers = self._generate_stormx_php_headers()

        response = requests.get(url, headers=headers, cookies=self._support_cookies)
        self.assertIn('<title>Vouchers | Travelliance</title>', response.text)

        response = requests.get(url, headers=headers, cookies={})
        self.assertIn('<title>Login | Travelliance</title>', response.text)

    def test_zero_rate_availability(self):
        """
        This test will check that no AP or PP block should be created with zero rate.

        """
        hotel_id = 85690
        airline_id = 71
        today = self._get_event_date('America/Chicago')

        # add passenger pay block
        comment = 'availability test ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        number_of_rooms = 5
        price = '0'
        response = self.create_hotel_availability(hotel_id, airline_id, today,
                                                  blocks=number_of_rooms, block_price=price,
                                                  issued_by='David Cameron', pay_type='1',
                                                  comment=comment)
        response = response.json()
        self.assertEqual(response['success'], '0')

    def test_zero_rate_zero_room_availability(self):
        """
        This test will check that no row should added with all zeros
        zero rates
        and
        zero blocks

        """
        hotel_id = 85690
        airline_id = 71
        today = self._get_event_date('America/Chicago')

        # add passenger pay block
        comment = 'availability test all zeros ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        number_of_rooms = 0
        price = '0'
        response = self.create_hotel_availability(hotel_id, airline_id, today,
                                                  blocks=number_of_rooms, block_price=price,
                                                  issued_by='Tester', pay_type='0',
                                                  comment=comment)
        response = response.json()
        self.assertEqual(response['success'], '0')

    def test_hotel_availability__passenger_pay(self):
        """
        """
        hotel_id = 85690
        airline_id = 71
        today = self._get_event_date('America/Chicago')

        # add passenger pay block
        comment = 'PP test ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        number_of_rooms = 5
        price = '21.27'
        pay_type = '1'
        self.add_hotel_availability(hotel_id, airline_id, today,
                                    blocks=number_of_rooms, block_price=price,
                                    issued_by='David Cameron', pay_type=pay_type,
                                    comment=comment)

        hotel_availability = self.get_hotel_availability(hotel_id, today)
        new_block = self.find_hotel_availability_block_by_comment(hotel_availability, comment)

        self.assertEqual(new_block['hotel_id'], str(hotel_id))
        self.assertEqual(new_block['airline_name'], 'American Airlines')
        self.assertEqual(new_block['airline_id'], str(airline_id))

        self.assertEqual(new_block['block_date'],
                         today.strftime(HOTEL_AVAILABILITY_BLOCK_DATE_FORMAT))  # TODO: what is the space after it???
        self.assertEqual(new_block['block_expiration_date'], str(today))  # TODO: verify if correct logic....
        self.assertEqual(new_block['day_no'], str(today.day))
        self.assertEqual(new_block['month_no'], str(today.month))
        self.assertEqual(new_block['year_no'], str(today.year))
        self.assertEqual(new_block['expired'], '1')  # TODO: this looks wrong.

        self.assertEqual(new_block['blocks'], str(number_of_rooms))
        self.assertEqual(new_block['block_price'], '21.27')
        self.assertEqual(new_block['pay_type'], pay_type)
        self.assertEqual(new_block['ap_block_type'], '0')  # 0: normal, 1: hard block, 2: contracted block

        self.assertGreater(int(new_block['hotel_availability_id']), 0)  # verify its a positive integer
        # TODO: should we verify '_id' field?  Is it always 1, or when does it change?
        self.assertEqual(new_block['hotel_availability_updated_user'], 'Support')
        self.assertEqual(new_block['issued_by'], 'David Cameron')
        self.assertEqual(new_block['position'], 'Front Desk Agent')
        self.assertEqual(new_block['comment'], comment)

    def test_hotel_availability__airline_pay_soft_block(self):
        """
        """
        hotel_id = 80213
        airline_id = 72
        number_of_rooms = 7
        pay_type = '0'  # 0 = AP, 1 = PP
        today = self._get_event_date('Australia/Brisbane')

        # add airline pay soft block
        comment = 'AP soft block test ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, today,
                                    blocks=number_of_rooms, block_price='27.99', ap_block_type=0,
                                    issued_by='Theresa May', pay_type=pay_type,
                                    comment=comment)

        hotel_availability = self.get_hotel_availability(hotel_id, today)
        new_block = self.find_hotel_availability_block_by_comment(hotel_availability, comment)

        self.assertEqual(new_block['hotel_id'], str(hotel_id))
        self.assertEqual(new_block['airline_name'], 'Delta Air Lines')
        self.assertEqual(new_block['airline_id'], str(airline_id))

        self.assertEqual(new_block['block_date'],
                         today.strftime(HOTEL_AVAILABILITY_BLOCK_DATE_FORMAT))  # TODO: what is the space after it???
        self.assertEqual(new_block['block_expiration_date'], str(today))  # TODO: verify if correct logic....
        self.assertEqual(new_block['day_no'], str(today.day))
        self.assertEqual(new_block['month_no'], str(today.month))
        self.assertEqual(new_block['year_no'], str(today.year))
        self.assertEqual(new_block['expired'], '1')  # TODO: this looks wrong.

        self.assertEqual(new_block['blocks'], str(number_of_rooms))
        self.assertEqual(new_block['block_price'], '27.99')
        self.assertEqual(new_block['pay_type'], pay_type)
        self.assertEqual(new_block['ap_block_type'], '0')  # 0: normal, 1: hard block, 2: contracted block

        self.assertGreater(int(new_block['hotel_availability_id']), 0)  # verify its a positive integer
        # TODO: should we verify '_id' field?  Is it always 1, or when does it change?
        self.assertEqual(new_block['hotel_availability_updated_user'], 'Support')
        self.assertEqual(new_block['issued_by'], 'Theresa May')
        self.assertEqual(new_block['position'], 'Front Desk Agent')
        self.assertEqual(new_block['comment'], comment)

    def test_hotel_availability__airline_pay_contracted_block(self):
        """
        """
        hotel_id = 80213
        airline_id = 72
        number_of_rooms = 7
        pay_type = '0'  # 0 = AP, 1 = PP
        today = self._get_event_date('Australia/Brisbane')

        # add airline pay soft block
        comment = 'AP contracted block test ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, today,
                                    blocks=number_of_rooms, block_price='120.00', ap_block_type=2,
                                    issued_by='Theresa May', pay_type=pay_type,
                                    comment=comment)

        hotel_availability = self.get_hotel_availability(hotel_id, today)
        new_block = self.find_hotel_availability_block_by_comment(hotel_availability, comment)

        self.assertEqual(new_block['hotel_id'], str(hotel_id))
        self.assertEqual(new_block['airline_name'], 'Delta Air Lines')
        self.assertEqual(new_block['airline_id'], str(airline_id))

        self.assertEqual(new_block['block_date'],
                         today.strftime(HOTEL_AVAILABILITY_BLOCK_DATE_FORMAT))  # TODO: what is the space after it???
        self.assertEqual(new_block['block_expiration_date'], str(today))  # TODO: verify if correct logic....
        self.assertEqual(new_block['day_no'], str(today.day))
        self.assertEqual(new_block['month_no'], str(today.month))
        self.assertEqual(new_block['year_no'], str(today.year))
        self.assertEqual(new_block['expired'], '1')  # TODO: this looks wrong.

        self.assertEqual(new_block['blocks'], str(number_of_rooms))
        self.assertEqual(new_block['pay_type'], pay_type)
        self.assertEqual(new_block['block_price'], '120.00')
        self.assertEqual(new_block['ap_block_type'], '2')  # 0: normal, 1: hard block, 2: contracted block

        self.assertGreater(int(new_block['hotel_availability_id']), 0)  # verify its a positive integer
        # TODO: should we verify '_id' field?  Is it always 1, or when does it change?
        self.assertEqual(new_block['hotel_availability_updated_user'], 'Support')
        self.assertEqual(new_block['issued_by'], 'Theresa May')
        # self.assertEqual(new_block['position'], 'Front Desk Agent')
        self.assertEqual(new_block['comment'], comment)

    def test_hotel_availability__airline_pay_hard_block(self):
        """
        """
        hotel_id = 80536
        airline_id = 71
        number_of_rooms = 13
        pay_type = '0'  # 0 = AP, 1 = PP
        today = self._get_event_date('Australia/Perth')

        # add airline pay hard block
        comment = 'AP hard block test' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, today,
                                    blocks=number_of_rooms, block_price='50', ap_block_type=1,
                                    issued_by='Gordon Brown', pay_type=pay_type,
                                    comment=comment)

        hotel_availability = self.get_hotel_availability(hotel_id, today)
        new_block = self.find_hotel_availability_block_by_comment(hotel_availability, comment)

        self.assertEqual(new_block['hotel_id'], str(hotel_id))
        self.assertEqual(new_block['airline_name'], 'American Airlines')
        self.assertEqual(new_block['airline_id'], str(airline_id))

        self.assertEqual(new_block['block_date'],
                         today.strftime(HOTEL_AVAILABILITY_BLOCK_DATE_FORMAT))  # TODO: what is the space after it???
        self.assertEqual(new_block['block_expiration_date'], str(today))  # TODO: verify if correct logic....
        self.assertEqual(new_block['day_no'], str(today.day))
        self.assertEqual(new_block['month_no'], str(today.month))
        self.assertEqual(new_block['year_no'], str(today.year))
        self.assertEqual(new_block['expired'], '1')  # TODO: this looks wrong.

        self.assertEqual(new_block['blocks'], str(number_of_rooms))
        self.assertEqual(new_block['pay_type'], pay_type)
        self.assertEqual(new_block['block_price'], '50.00')
        self.assertEqual(new_block['ap_block_type'], '1')  # 0: normal, 1: hard block, 2: contracted block

        self.assertGreater(int(new_block['hotel_availability_id']), 0)  # verify its a positive integer
        # TODO: should we verify '_id' field?  Is it always 1, or when does it change?
        self.assertEqual(new_block['hotel_availability_updated_user'], 'Support')
        self.assertEqual(new_block['issued_by'], 'Gordon Brown')
        self.assertEqual(new_block['position'], 'Front Desk Agent')
        self.assertEqual(new_block['comment'], comment)

    def test_quick_voucher__submit_minimal_inputs(self):
        """
        TODO: currently this test exposes some of the problems with
        the quick voucher submission process. But it still documents
        the currently expected inputs and outputs. In the future,
        this this test should verify the minmal input to create
        a GOOD voucher instead of a DEGENERATE voucher... But before
        we do that, let's start validating some inputs to break this
        test, then update the test to submit the additional fields that
        the backend requires.

        NOTE: this test is subitting fewer fields than the UI calls the backend.

        Scenario:
        * setup: add one room of inventory to a hotel.
        * TVL staff creates a Quick Voucher:
            - two people (husband and wife)
            - one room
            - one night
        * submit the minimum inputs where the backend will still accept the inputs
          (i.e., not crash or report an input error).
        """
        hotel_id = 82926 #pan pacific seattle
        airline_id = 294  # Purple Rain
        tz = 'America/Los_Angeles'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)
        number_of_rooms = 1
        number_of_nights = 1
        airport_id = 16
        pay_type = '0'
        passenger_names = ['Johnny Appleseed', 'Elizabeth Chapman']
        flight_number = 'PR-4321'

        # ensure there is sufficient inventory for the booking ----
        unique_comment = 'for quick voucher ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=1, block_price='81.81', ap_block_type=1,
                                    issued_by='Shahid Khaqan Abbasi', pay_type=pay_type,
                                    comment=unique_comment)

        # pick a block to book ----
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        # create a Quick Voucher ----
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  voucher_date=voucher_creation_date_time,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights,
                                                  flight_number=flight_number)

        # verify response of Quick Voucher creation endpoint ----
        self.assertEqual(response_json['success'], '1')
        voucher_id = response_json['voucher']['voucher_id']
        self.assertEqual(response_json['errMsg'], '')
        self.assertEqual(response_json['message'],
                         "Voucher {voucher_id} has been finalised successfully! Do you wish to send voucher?".format(
                             voucher_id=voucher_id))
        self.assertEqual(response_json['type'], 'finalized')
        self.assertEqual(response_json['voucher']['isCancelled'], False)
        self.assertEqual(response_json['voucher']['isEditable'], False)
        self.assertEqual(len(response_json['voucher']['paxs_id']), len(passenger_names))
        self.assertTrue(response_json['voucher']['voucher_code'].startswith(
            'NHA'))  # TODO: FINDING: I think we may want to revisit this.. It looks like we communicate the exact number of vouchers to our customers and partners!
        self.assertGreaterEqual(len(response_json['voucher']['voucher_code']), 4)
        self.assertGreater(voucher_id, 0)
        self.assertEqual(response_json['voucher']['voucher_status'],
                         '50')  # TODO:  What is 50??? Voucher finalize status
        self.assertEqual(response_json['voucher']['voucher_status_text'], 'Finalized')

        # load up the 'Preview Voucher' modal and verify loaded JSON data embedded in the HTML ----
        voucher = self.get_view_voucher_data(voucher_id)
        # print('voucher:')
        # print(json.dumps(voucher, indent='    '))
        EXPECTED_ALLOWANCES = {
            "pax_class": "",
            "phones": [
                {
                    "id": "0",
                    "label": "None"
                }
            ],
            "phone": "0",
            "mealsDefault": {
                "dinner": 0,
                "breakfast": 21,
                "hotelshuttle": 0,
                "lunch": 0,
                "amenity": 0
            },
            "meals": []
        }
        # self.assertEqual(voucher['allowances'], EXPECTED_ALLOWANCES)
        self.assertEqual(voucher['final_tax_per_rate'], '0.00')  # TODO: is this correct, or a money issue?
        self.assertEqual(voucher['flightInfo'], [])
        # self.assertGreater(int(voucher['hotel_availability_id']), 0) TODO: remove once removed in php code (commented out now)
        self.assertEqual(voucher['hotel_id'], str(hotel_id))
        self.assertEqual(voucher['hotel_payment_type'], 'G')
        self.assertEqual(voucher['isCancelled'], False)
        self.assertEqual(voucher['isManifestPaxInformationReloaded'], False)
        self.assertEqual(voucher['isPassengerVoucher'], False)
        self.assertEqual(voucher['passenger_email'], '')
        self.assertEqual(voucher['transportOut_payment_type'], '')
        self.assertEqual(voucher['isEditable'], False)
        self.assertEqual(voucher['isToCheckRevisioned'], False)
        self.assertEqual(voucher['isVoucherDetailLoaded'], False)
        self.assertEqual(voucher['life_stage'], '')
        self.assertEqual(voucher['manifest_id'], '0')
        # TODO: handle logic to verify `voucher['notes']`, which can be `[]` or something like the following, depending on conditions:
        # [
        #     {
        #         'can_view': '1',
        #         'detail': 'If the passenger does not arrive within 3 hours of "ETA at hotel" advised, please call and alert Travelliance so we can follow up with the airline.',
        #         'date': '07/05/2018 19:05',
        #         'user_name': 'Support',
        #         'user_id': '1',
        #         'id': '2'
        #     },
        # ]
        self.assertEqual(len(voucher['paxs']), 2)
        johnny_appleseed = [_p for _p in voucher['paxs'] if _p['name'] == 'Johnny Appleseed'][0]
        elizabeth_chapman = [_p for _p in voucher['paxs'] if _p['name'] == 'Elizabeth Chapman'][0]

        total_rooms = 0
        total_count = 0
        for passenger in voucher['paxs']:
            self.assertGreater(int(passenger['id']), 0)
            self.assertEqual(passenger['cost_code'], '')
            self.assertEqual(passenger['pnr'], '')
            self.assertEqual(passenger['count'], '1')  # TODO: QUSTION: when is this not 1??
            self.assertEqual(passenger['return_date'], '')
            self.assertEqual(passenger['pickup_date'], '')
            self.assertEqual(passenger['business_unit'], '')
            self.assertEqual(passenger['no_show'], '0')
            self.assertEqual(passenger['return_date'], '')

            total_rooms += int(passenger['rooms'])
            total_count += int(passenger['count'])
        self.assertEqual(total_rooms, 1)
        self.assertEqual(total_count, 2)

        self.assertEqual(voucher['passenger_level'], '')
        self.assertEqual(voucher['passenger_phone'], '')
        EXPECTED_ROOM_RATES = [
            {
                'rates': [
                    ''  # TODO: this looks bad! investigate!
                ],
                'count': ''  # TODO: this looks bad! investigate!
            }
        ]
        self.assertEqual(voucher['roomRates'], EXPECTED_ROOM_RATES)
        EXPECTED_SEND_EMAIL_VALUES = {
            "transportTo": {
                "email": "",
                "emails": []
            },
            "transportFrom": {
                "email": "",
                "emails": []
            },
            "airline": {
                "email": "",
                "emails": []
            },
            "hotel": {
                "email": "",
                "emails": []
            }
        }
        self.assertEqual(voucher['sendEmail'], EXPECTED_SEND_EMAIL_VALUES)
        self.assertEqual(voucher['totals'], '')  # TODO: this looks like a money bug!
        self.assertEqual(voucher['transport_from_hotel_departure'], '0.0')
        self.assertEqual(voucher['transport_to_hotel'], '0')
        self.assertEqual(voucher['transportIn_payment_type'], '')
        self.assertEqual(voucher['voucher_airline_auth_user'], '')
        self.assertEqual(voucher['voucher_blocks_price'], 81.81)
        self.assertEqual(voucher['voucher_conference'], '0')
        self.assertEqual(voucher['voucher_currency'], 'USD')
        self.assertEqual(voucher['voucher_departure_flight'], '')
        self.assertEqual(voucher['voucher_disruption_date'],
                         voucher_creation_date_time.strftime(DATETIME_FORMAT_FOR_VOUCHERS))
        self.assertEqual(voucher['voucher_departure_date'],
                         (voucher_creation_date_time + datetime.timedelta(days=1)).strftime(
                             DATETIME_FORMAT_FOR_VOUCHERS))
        # self.assertEqual(voucher['voucher_departure_time'], '???')  # TODO verify voucher_departure_time
        self.assertEqual(voucher['voucher_departure_port'], str(airport_id))
        self.assertEqual(voucher['voucher_disruption_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_date_o'], voucher_creation_date_time.strftime('%Y-%m-%d'))
        self.assertEqual(voucher['voucher_disruption_flight_type'], '')
        self.assertEqual(voucher['voucher_disruption_port_currency'], None)
        self.assertEqual(voucher['voucher_disruption_port'], str(airport_id))
        self.assertEqual(voucher['voucher_fasttrack_hotel_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transport_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transportOut_email'], '')
        # self.assertEqual(voucher['voucher_finalization_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_finalization_ts
        self.assertEqual(voucher['voucher_hotel_nights'], str(number_of_nights))
        self.assertEqual(voucher['voucher_id'], str(voucher_id))
        self.assertEqual(voucher['voucher_invoice_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_invoice_notification'], '0')
        self.assertEqual(voucher['voucher_room_rate_commission'], '0.00')  # TODO: investigate if money issue!
        self.assertEqual(voucher['voucher_room_type']['id'], '1')
        self.assertEqual(voucher['voucher_room_rate'], '0')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_room_total'], '1')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_varied_room_rates'], '0')
        self.assertEqual(voucher['voucherTotalRate'], '')
        self.assertGreaterEqual(len(voucher['voucher_code']), 4)
        self.assertTrue(voucher['voucher_code'].startswith('NHA'))
        self.assertEqual(voucher['voucher_commission_type'], 'percentage')
        self.assertEqual(voucher['voucher_commission_value'], '10.00')
        # self.assertEqual(voucher['voucher_cutoff_time'], now.strftime(DATETIME_FORMAT_FOR_VOUCHERS))  # TODO: this is failing! time is 5 hours off of supplied input. Need to investigate.
        self.assertEqual(voucher['voucher_departure_terminal'], '')
        self.assertEqual(voucher['voucher_departure_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_arrival_port'], '0')
        self.assertEqual(voucher['voucher_disruption_flight'], 'PR-4321')
        self.assertEqual(voucher['voucher_disruption_reason'], '12')
        self.assertEqual(voucher['voucher_fasttrack_natwide_email'], 'opssupport@tvlinc.com')
        self.assertEqual(voucher['voucher_fasttrack_airline_email'], '')

        # self.assertEqual(voucher_view_data['voucher_hotel_eta'], '???')  # TODO verify voucher_hotel_eta
        self.assertEqual(voucher['voucher_notes'], '')
        self.assertEqual(len(voucher['voucher_room_blocks']), 1)

        self.assertEqual(voucher['voucher_room_blocks'][0]['rate'], '81.81')
        self.assertEqual(voucher['voucher_room_blocks'][0]['count'], '1')

        self.assertEqual(voucher['voucher_requesting_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_requesting_port'], str(airport_id))
        self.assertEqual(voucher['voucher_status_text'], 'finalised')
        self.assertEqual(voucher['voucher_status'], '50')
        self.assertEqual(voucher['voucher_pax_total'], str(len(passenger_names)))
        self.assertEqual(voucher['voucher_update_user'], 'Support')
        # self.assertEqual(voucher['voucher_update_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_update_ts
        self.assertIsNotNone(voucher['voucher_uuid'])
        uuid.UUID(voucher['voucher_uuid'], version=4)

        # TODO: could extend scenario to modify the voucher or send the voucher or voucher communications.

    def test_quick_voucher__with_future_inventory(self):
        """
        Scenario:
        * setup: add one room of inventory to a hotel, five days ahead of today.
        * TVL staff creates a Quick Voucher for the day five days ahead of today:
            - two people (husband and wife)
            - one room
            - one night
        * submit the minimum inputs where the backend will still accept the inputs
          (i.e., not crash or report an input error).
        """
        hotel_id = 89271 #hotel regency
        airline_id = 294  # Purple Rain
        tz = 'America/Los_Angeles'
        now_p_5_days =  self._get_timezone_now(tz) + datetime.timedelta(days=5)
        availability_date = self._get_event_date(tz) + datetime.timedelta(days=5)
        voucher_creation_date_time = self._get_event_date_time(tz, now_p_5_days)
        number_of_rooms = 1
        number_of_nights = 1
        airport_id = 41
        passenger_names = ['Johnny Appleseed', 'Elizabeth Chapman']
        flight_number = 'PR-4321'

        # ensure there is sufficient inventory for the booking ----
        unique_comment = 'for quick voucher ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=1, block_price='81.81', ap_block_type=1,
                                    issued_by='Shahid Khaqan Abbasi', pay_type='0',
                                    comment=unique_comment)

        # pick a block to book ----
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        new_block = self.find_hotel_availability_block_by_comment(hotel_availability, unique_comment)
        # print(json.dumps(new_block, indent='    '))
        hotel_availability_id = int(new_block['hotel_availability_id'])

        # create a Quick Voucher ----
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights,
                                                  voucher_date=voucher_creation_date_time,
                                                  flight_number=flight_number)

        # verify response of Quick Voucher creation endpoint ----
        self.assertEqual(response_json['success'], '1')
        voucher_id = response_json['voucher']['voucher_id']
        self.assertEqual(response_json['errMsg'], '')
        self.assertEqual(response_json['message'],
                         "Voucher {voucher_id} has been finalised successfully! Do you wish to send voucher?".format(
                             voucher_id=voucher_id))
        self.assertEqual(response_json['type'], 'finalized')
        self.assertEqual(response_json['voucher']['isCancelled'], False)
        self.assertEqual(response_json['voucher']['isEditable'], False)
        self.assertEqual(len(response_json['voucher']['paxs_id']), len(passenger_names))
        self.assertTrue(response_json['voucher']['voucher_code'].startswith('NHA'))
        self.assertGreaterEqual(len(response_json['voucher']['voucher_code']), 4)
        self.assertGreater(voucher_id, 0)
        self.assertEqual(response_json['voucher']['voucher_status'], '50')  # Voucher finalize status
        self.assertEqual(response_json['voucher']['voucher_status_text'], 'Finalized')

        # load up the 'Preview Voucher' modal and verify loaded JSON data embedded in the HTML ----
        voucher = self.get_view_voucher_data(voucher_id)
        # print('voucher:')
        # print(json.dumps(voucher, indent='    '))
        EXPECTED_ALLOWANCES = {
            "pax_class": "",
            "phones": [
                {
                    "id": "0",
                    "label": "None"
                }
            ],
            "phone": "0",
            "mealsDefault": {
                "dinner": 0,
                "breakfast": 21,
                "hotelshuttle": 0,
                "lunch": 0,
                "amenity": 0
            },
            "meals": []
        }
        # self.assertEqual(voucher['allowances'], EXPECTED_ALLOWANCES)
        self.assertEqual(voucher['final_tax_per_rate'], '0.00')  # TODO: is this correct, or a money issue?
        self.assertEqual(voucher['flightInfo'], [])
        # self.assertGreater(int(voucher['hotel_availability_id']), 0) TODO: remove once removed in php code (commented out now)
        self.assertEqual(voucher['hotel_id'], str(hotel_id))
        self.assertEqual(voucher['hotel_payment_type'], 'G')
        self.assertEqual(voucher['isCancelled'], False)
        self.assertEqual(voucher['isManifestPaxInformationReloaded'], False)
        self.assertEqual(voucher['isPassengerVoucher'], False)
        self.assertEqual(voucher['passenger_email'], '')
        self.assertEqual(voucher['transportOut_payment_type'], '')
        self.assertEqual(voucher['isEditable'], False)
        self.assertEqual(voucher['isToCheckRevisioned'], False)
        self.assertEqual(voucher['isVoucherDetailLoaded'], False)
        self.assertEqual(voucher['life_stage'], '')
        self.assertEqual(voucher['manifest_id'], '0')
        # TODO: handle logic to verify `voucher['notes']`, which can be `[]` or something like the following, depending on conditions:
        # [
        #     {
        #         'can_view': '1',
        #         'detail': 'If the passenger does not arrive within 3 hours of "ETA at hotel" advised, please call and alert Travelliance so we can follow up with the airline.',
        #         'date': '07/05/2018 19:05',
        #         'user_name': 'Support',
        #         'user_id': '1',
        #         'id': '2'
        #     },
        # ]
        self.assertEqual(len(voucher['paxs']), 2)
        johnny_appleseed = [_p for _p in voucher['paxs'] if _p['name'] == 'Johnny Appleseed'][0]
        elizabeth_chapman = [_p for _p in voucher['paxs'] if _p['name'] == 'Elizabeth Chapman'][0]

        total_rooms = 0
        total_count = 0
        for passenger in voucher['paxs']:
            self.assertGreater(int(passenger['id']), 0)
            self.assertEqual(passenger['cost_code'], '')
            self.assertEqual(passenger['pnr'], '')
            self.assertEqual(passenger['count'], '1')  # TODO: QUSTION: when is this not 1??
            self.assertEqual(passenger['return_date'], '')
            self.assertEqual(passenger['pickup_date'], '')
            self.assertEqual(passenger['business_unit'], '')
            self.assertEqual(passenger['no_show'], '0')
            self.assertEqual(passenger['return_date'], '')

            total_rooms += int(passenger['rooms'])
            total_count += int(passenger['count'])
        self.assertEqual(total_rooms, 1)
        self.assertEqual(total_count, 2)

        self.assertEqual(voucher['passenger_level'], '')
        self.assertEqual(voucher['passenger_phone'], '')
        EXPECTED_ROOM_RATES = [
            {
                'rates': [
                    ''  # TODO: this looks bad! investigate!
                ],
                'count': ''  # TODO: this looks bad! investigate!
            }
        ]
        self.assertEqual(voucher['roomRates'], EXPECTED_ROOM_RATES)
        EXPECTED_SEND_EMAIL_VALUES = {
            "transportTo": {
                "email": "",
                "emails": []
            },
            "transportFrom": {
                "email": "",
                "emails": []
            },
            "airline": {
                "email": "",
                "emails": []
            },
            "hotel": {
                "email": "",
                "emails": []
            }
        }
        self.assertEqual(voucher['sendEmail'], EXPECTED_SEND_EMAIL_VALUES)
        self.assertEqual(voucher['totals'], '')  # TODO: this looks like a money bug!
        self.assertEqual(voucher['transport_from_hotel_departure'], '0.0')
        self.assertEqual(voucher['transport_to_hotel'], '0')
        self.assertEqual(voucher['transportIn_payment_type'], '')
        self.assertEqual(voucher['voucher_airline_auth_user'], '')
        self.assertEqual(voucher['voucher_blocks_price'], 81.81)
        self.assertEqual(voucher['voucher_conference'], '0')
        self.assertEqual(voucher['voucher_currency'], 'USD')
        self.assertEqual(voucher['voucher_departure_flight'], '')
        self.assertEqual(voucher['voucher_disruption_date'],
                         voucher_creation_date_time.strftime(DATETIME_FORMAT_FOR_VOUCHERS))
        self.assertEqual(voucher['voucher_departure_date'],
                         (voucher_creation_date_time + datetime.timedelta(days=1)).strftime(
                             DATETIME_FORMAT_FOR_VOUCHERS))
        # self.assertEqual(voucher['voucher_departure_time'], '???')  # TODO verify voucher_departure_time
        self.assertEqual(voucher['voucher_departure_port'], str(airport_id))
        self.assertEqual(voucher['voucher_disruption_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_date_o'], voucher_creation_date_time.strftime('%Y-%m-%d'))
        self.assertEqual(voucher['voucher_disruption_flight_type'], '')
        self.assertEqual(voucher['voucher_disruption_port_currency'], None)
        self.assertEqual(voucher['voucher_disruption_port'], str(airport_id))
        self.assertEqual(voucher['voucher_fasttrack_hotel_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transport_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transportOut_email'], '')
        # self.assertEqual(voucher['voucher_finalization_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_finalization_ts
        self.assertEqual(voucher['voucher_hotel_nights'], str(number_of_nights))
        self.assertEqual(voucher['voucher_id'], str(voucher_id))
        self.assertEqual(voucher['voucher_invoice_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_invoice_notification'], '0')
        self.assertEqual(voucher['voucher_room_rate_commission'], '0.00')  # TODO: investigate if money issue!
        self.assertEqual(voucher['voucher_room_type']['id'], '1')
        self.assertEqual(voucher['voucher_room_rate'], '0')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_room_total'], '1')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_varied_room_rates'], '0')
        self.assertEqual(voucher['voucherTotalRate'], '')
        self.assertGreaterEqual(len(voucher['voucher_code']), 4)
        self.assertTrue(voucher['voucher_code'].startswith('NHA'))
        self.assertEqual(voucher['voucher_commission_type'], 'percentage')
        self.assertEqual(voucher['voucher_commission_value'], '10.00')
        # self.assertEqual(voucher['voucher_cutoff_time'], now_p_5_days.strftime(DATETIME_FORMAT_FOR_VOUCHERS))  # TODO: this is failing! time is 5 hours off of supplied input. Need to investigate.
        self.assertEqual(voucher['voucher_departure_terminal'], '')
        self.assertEqual(voucher['voucher_departure_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_arrival_port'], '0')
        self.assertEqual(voucher['voucher_disruption_flight'], 'PR-4321')
        self.assertEqual(voucher['voucher_disruption_reason'], '12')
        self.assertEqual(voucher['voucher_fasttrack_natwide_email'], 'opssupport@tvlinc.com')
        self.assertEqual(voucher['voucher_fasttrack_airline_email'], '')

        # self.assertEqual(voucher_view_data['voucher_hotel_eta'], '???')  # TODO verify voucher_hotel_eta
        self.assertEqual(voucher['voucher_notes'], '')
        self.assertEqual(len(voucher['voucher_room_blocks']), 1)

        self.assertEqual(voucher['voucher_room_blocks'][0]['rate'], '81.81')
        self.assertEqual(voucher['voucher_room_blocks'][0]['count'], '1')

        self.assertEqual(voucher['voucher_requesting_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_requesting_port'], str(airport_id))
        self.assertEqual(voucher['voucher_status_text'], 'finalised')
        self.assertEqual(voucher['voucher_status'], '50')
        self.assertEqual(voucher['voucher_pax_total'], str(len(passenger_names)))
        self.assertEqual(voucher['voucher_update_user'], 'Support')
        # self.assertEqual(voucher['voucher_update_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_update_ts
        self.assertIsNotNone(voucher['voucher_uuid'])
        uuid.UUID(voucher['voucher_uuid'], version=4)

    def test_quick_voucher__with_past_inventory(self):
        """
        Scenario:
        * setup: add one room of inventory to a hotel, five days back from today.
        * TVL staff creates a Quick Voucher for the day five days back from today:
            - two people (husband and wife)
            - one room
            - one night
        * submit the minimum inputs where the backend will still accept the inputs
          (i.e., not crash or report an input error).
        """
        hotel_id = 99509 #westin seattle
        airline_id = 294  # Purple Rain
        tz = 'America/Los_Angeles'
        now = self._get_timezone_now(tz) - datetime.timedelta(days=5)
        availability_date = self._get_event_date(tz) - datetime.timedelta(days=5)
        voucher_creation_date_time = self._get_event_date_time(tz, now)

        number_of_rooms = 1
        number_of_nights = 1
        airport_id = 41
        passenger_names = ['Johnny Appleseed', 'Elizabeth Chapman']
        flight_number = 'PR-4321'

        # ensure there is sufficient inventory for the booking ----
        unique_comment = 'for quick voucher ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=1, block_price='81.81', ap_block_type=1,
                                    issued_by='Shahid Khaqan Abbasi', pay_type='0',
                                    comment=unique_comment)

        # pick a block to book ----
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        new_block = self.find_hotel_availability_block_by_comment(hotel_availability, unique_comment)
        # print(json.dumps(new_block, indent='    '))
        hotel_availability_id = int(new_block['hotel_availability_id'])

        # create a Quick Voucher ----
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights,
                                                  voucher_date=voucher_creation_date_time,
                                                  flight_number=flight_number)

        # verify response of Quick Voucher creation endpoint ----
        self.assertEqual(response_json['success'], '1')
        voucher_id = response_json['voucher']['voucher_id']
        self.assertEqual(response_json['errMsg'], '')
        self.assertEqual(response_json['message'],
                         "Voucher {voucher_id} has been finalised successfully! Do you wish to send voucher?".format(
                             voucher_id=voucher_id))
        self.assertEqual(response_json['type'], 'finalized')
        self.assertEqual(response_json['voucher']['isCancelled'], False)
        self.assertEqual(response_json['voucher']['isEditable'], False)
        self.assertEqual(len(response_json['voucher']['paxs_id']), len(passenger_names))
        self.assertTrue(response_json['voucher']['voucher_code'].startswith('NHA'))
        self.assertGreaterEqual(len(response_json['voucher']['voucher_code']), 4)
        self.assertGreater(voucher_id, 0)
        self.assertEqual(response_json['voucher']['voucher_status'], '50')  # Voucher finalize status
        self.assertEqual(response_json['voucher']['voucher_status_text'], 'Finalized')

        # load up the 'Preview Voucher' modal and verify loaded JSON data embedded in the HTML ----
        voucher = self.get_view_voucher_data(voucher_id)
        # print('voucher:')
        # print(json.dumps(voucher, indent='    '))
        EXPECTED_ALLOWANCES = {
            "pax_class": "",
            "phones": [
                {
                    "id": "0",
                    "label": "None"
                }
            ],
            "phone": "0",
            "mealsDefault": {
                "dinner": 0,
                "breakfast": 21,
                "hotelshuttle": 0,
                "lunch": 0,
                "amenity": 0
            },
            "meals": []
        }
        # self.assertEqual(voucher['allowances'], EXPECTED_ALLOWANCES)
        self.assertEqual(voucher['final_tax_per_rate'], '0.00')  # TODO: is this correct, or a money issue?
        self.assertEqual(voucher['flightInfo'], [])
        # self.assertGreater(int(voucher['hotel_availability_id']), 0) TODO: remove once removed in php code (commented out now)
        self.assertEqual(voucher['hotel_id'], str(hotel_id))
        self.assertEqual(voucher['hotel_payment_type'], 'G')
        self.assertEqual(voucher['isCancelled'], False)
        self.assertEqual(voucher['isManifestPaxInformationReloaded'], False)
        self.assertEqual(voucher['isPassengerVoucher'], False)
        self.assertEqual(voucher['passenger_email'], '')
        self.assertEqual(voucher['transportOut_payment_type'], '')
        self.assertEqual(voucher['isEditable'], False)
        self.assertEqual(voucher['isToCheckRevisioned'], False)
        self.assertEqual(voucher['isVoucherDetailLoaded'], False)
        self.assertEqual(voucher['life_stage'], '')
        self.assertEqual(voucher['manifest_id'], '0')
        # TODO: handle logic to verify `voucher['notes']`, which can be `[]` or something like the following, depending on conditions:
        # [
        #     {
        #         'can_view': '1',
        #         'detail': 'If the passenger does not arrive within 3 hours of "ETA at hotel" advised, please call and alert Travelliance so we can follow up with the airline.',
        #         'date': '07/05/2018 19:05',
        #         'user_name': 'Support',
        #         'user_id': '1',
        #         'id': '2'
        #     },
        # ]
        self.assertEqual(len(voucher['paxs']), 2)
        johnny_appleseed = [_p for _p in voucher['paxs'] if _p['name'] == 'Johnny Appleseed'][0]
        elizabeth_chapman = [_p for _p in voucher['paxs'] if _p['name'] == 'Elizabeth Chapman'][0]

        total_rooms = 0
        total_count = 0
        for passenger in voucher['paxs']:
            self.assertGreater(int(passenger['id']), 0)
            self.assertEqual(passenger['cost_code'], '')
            self.assertEqual(passenger['pnr'], '')
            self.assertEqual(passenger['count'], '1')  # TODO: QUSTION: when is this not 1??
            self.assertEqual(passenger['return_date'], '')
            self.assertEqual(passenger['pickup_date'], '')
            self.assertEqual(passenger['business_unit'], '')
            self.assertEqual(passenger['no_show'], '0')
            self.assertEqual(passenger['return_date'], '')

            total_rooms += int(passenger['rooms'])
            total_count += int(passenger['count'])
        self.assertEqual(total_rooms, 1)
        self.assertEqual(total_count, 2)

        self.assertEqual(voucher['passenger_level'], '')
        self.assertEqual(voucher['passenger_phone'], '')
        EXPECTED_ROOM_RATES = [
            {
                'rates': [
                    ''  # TODO: this looks bad! investigate!
                ],
                'count': ''  # TODO: this looks bad! investigate!
            }
        ]
        self.assertEqual(voucher['roomRates'], EXPECTED_ROOM_RATES)
        EXPECTED_SEND_EMAIL_VALUES = {
            "transportTo": {
                "email": "",
                "emails": []
            },
            "transportFrom": {
                "email": "",
                "emails": []
            },
            "airline": {
                "email": "",
                "emails": []
            },
            "hotel": {
                "email": "",
                "emails": []
            }
        }
        self.assertEqual(voucher['sendEmail'], EXPECTED_SEND_EMAIL_VALUES)
        self.assertEqual(voucher['totals'], '')  # TODO: this looks like a money bug!
        self.assertEqual(voucher['transport_from_hotel_departure'], '0.0')
        self.assertEqual(voucher['transport_to_hotel'], '0')
        self.assertEqual(voucher['transportIn_payment_type'], '')
        self.assertEqual(voucher['voucher_airline_auth_user'], '')
        self.assertEqual(voucher['voucher_blocks_price'], 81.81)
        self.assertEqual(voucher['voucher_conference'], '0')
        self.assertEqual(voucher['voucher_currency'], 'USD')
        self.assertEqual(voucher['voucher_departure_flight'], '')
        self.assertEqual(voucher['voucher_disruption_date'],
                         voucher_creation_date_time.strftime(DATETIME_FORMAT_FOR_VOUCHERS))
        self.assertEqual(voucher['voucher_departure_date'],
                         (voucher_creation_date_time + datetime.timedelta(days=1)).strftime(
                             DATETIME_FORMAT_FOR_VOUCHERS))
        # self.assertEqual(voucher['voucher_departure_time'], '???')  # TODO verify voucher_departure_time
        self.assertEqual(voucher['voucher_departure_port'], str(airport_id))
        self.assertEqual(voucher['voucher_disruption_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_date_o'], voucher_creation_date_time.strftime('%Y-%m-%d'))
        self.assertEqual(voucher['voucher_disruption_flight_type'], '')
        self.assertEqual(voucher['voucher_disruption_port_currency'], None)
        self.assertEqual(voucher['voucher_disruption_port'], str(airport_id))
        self.assertEqual(voucher['voucher_fasttrack_hotel_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transport_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transportOut_email'], '')
        # self.assertEqual(voucher['voucher_finalization_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_finalization_ts
        self.assertEqual(voucher['voucher_hotel_nights'], str(number_of_nights))
        self.assertEqual(voucher['voucher_id'], str(voucher_id))
        self.assertEqual(voucher['voucher_invoice_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_invoice_notification'], '0')
        self.assertEqual(voucher['voucher_room_rate_commission'], '0.00')  # TODO: investigate if money issue!
        self.assertEqual(voucher['voucher_room_type']['id'], '1')
        self.assertEqual(voucher['voucher_room_rate'], '0')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_room_total'], '1')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_varied_room_rates'], '0')
        self.assertEqual(voucher['voucherTotalRate'], '')
        self.assertGreaterEqual(len(voucher['voucher_code']), 4)
        self.assertTrue(voucher['voucher_code'].startswith('NHA'))
        self.assertEqual(voucher['voucher_commission_type'], 'percentage')
        self.assertEqual(voucher['voucher_commission_value'], '10.00')
        # self.assertEqual(voucher['voucher_cutoff_time'], now_m_5_days.strftime(DATETIME_FORMAT_FOR_VOUCHERS))  # TODO: this is failing! time is 5 hours off of supplied input. Need to investigate.
        self.assertEqual(voucher['voucher_departure_terminal'], '')
        self.assertEqual(voucher['voucher_departure_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_arrival_port'], '0')
        self.assertEqual(voucher['voucher_disruption_flight'], 'PR-4321')
        self.assertEqual(voucher['voucher_disruption_reason'], '12')
        self.assertEqual(voucher['voucher_fasttrack_natwide_email'], 'opssupport@tvlinc.com')
        self.assertEqual(voucher['voucher_fasttrack_airline_email'], '')

        # self.assertEqual(voucher_view_data['voucher_hotel_eta'], '???')  # TODO verify voucher_hotel_eta
        self.assertEqual(voucher['voucher_notes'], '')
        self.assertEqual(len(voucher['voucher_room_blocks']), 1)

        self.assertEqual(voucher['voucher_room_blocks'][0]['rate'], '81.81')
        self.assertEqual(voucher['voucher_room_blocks'][0]['count'], '1')

        self.assertEqual(voucher['voucher_requesting_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_requesting_port'], str(airport_id))
        self.assertEqual(voucher['voucher_status_text'], 'finalised')
        self.assertEqual(voucher['voucher_status'], '50')
        self.assertEqual(voucher['voucher_pax_total'], str(len(passenger_names)))
        self.assertEqual(voucher['voucher_update_user'], 'Support')
        # self.assertEqual(voucher['voucher_update_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_update_ts
        self.assertIsNotNone(voucher['voucher_uuid'])
        uuid.UUID(voucher['voucher_uuid'], version=4)

    def test_quick_voucher__accessibility_room_type(self):
        """

        Scenario:
        * setup: add one accessibility room of inventory to a hotel.
        * TVL staff creates a Quick Voucher:
            - one person
            - one room
            - one night
        * submit the minimum inputs where the backend will still accept the inputs
          (i.e., not crash or report an input error).
        """
        hotel_id = 108050 # Atton brickell miami
        airline_id = 294  # Purple Rain
        tz = 'America/New_York'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)
        number_of_rooms = 1
        number_of_nights = 1
        airport_id = 192 #miami
        passenger_names = ['Michael']
        flight_number = 'PR-1234'

        # ensure there is sufficient inventory for the booking ----
        unique_comment = 'for quick voucher ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=1, block_price='100.50', ap_block_type=1,
                                    issued_by='Donald Trump', pay_type='0',
                                    comment=unique_comment, room_type=2)

        # pick a block to book ----
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        # create a Quick Voucher ----
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights,
                                                  voucher_date=voucher_creation_date_time,
                                                  flight_number=flight_number, room_type=2)

        # verify response of Quick Voucher creation endpoint ----
        self.assertEqual(response_json['success'], '1')
        voucher_id = response_json['voucher']['voucher_id']
        self.assertEqual(response_json['errMsg'], '')
        self.assertEqual(response_json['message'],
                         "Voucher {voucher_id} has been finalised successfully! Do you wish to send voucher?".format(
                             voucher_id=voucher_id))
        self.assertEqual(response_json['type'], 'finalized')
        self.assertEqual(response_json['voucher']['isCancelled'], False)
        self.assertEqual(response_json['voucher']['isEditable'], False)
        self.assertEqual(len(response_json['voucher']['paxs_id']), len(passenger_names))
        self.assertTrue(response_json['voucher']['voucher_code'].startswith(
            'NHA'))  # TODO: FINDING: I think we may want to revisit this.. It looks like we communicate the exact number of vouchers to our customers and partners!
        self.assertGreaterEqual(len(response_json['voucher']['voucher_code']), 4)
        self.assertGreater(voucher_id, 0)
        self.assertEqual(response_json['voucher']['voucher_status'],
                         '50')  # TODO:  What is 50??? Voucher finalize status
        self.assertEqual(response_json['voucher']['voucher_status_text'], 'Finalized')

        # load up the 'Preview Voucher' modal and verify loaded JSON data embedded in the HTML ----
        voucher = self.get_view_voucher_data(voucher_id)
        # print('voucher:')
        # print(json.dumps(voucher, indent='    '))
        EXPECTED_ALLOWANCES = {
            "pax_class": "",
            "phones": [
                {
                    "id": "0",
                    "label": "None"
                }
            ],
            "phone": "0",
            "mealsDefault": {
                "dinner": 0,
                "breakfast": 21,
                "hotelshuttle": 0,
                "lunch": 0,
                "amenity": 0
            },
            "meals": []
        }
        # self.assertEqual(voucher['allowances'], EXPECTED_ALLOWANCES)
        self.assertEqual(voucher['final_tax_per_rate'], '0.00')  # TODO: is this correct, or a money issue?
        self.assertEqual(voucher['flightInfo'], [])
        # self.assertGreater(int(voucher['hotel_availability_id']), 0) TODO: remove once removed in php code (commented out now)
        self.assertEqual(voucher['hotel_id'], str(hotel_id))
        self.assertEqual(voucher['hotel_payment_type'], 'G')
        self.assertEqual(voucher['isCancelled'], False)
        self.assertEqual(voucher['isManifestPaxInformationReloaded'], False)
        self.assertEqual(voucher['isPassengerVoucher'], False)
        self.assertEqual(voucher['passenger_email'], '')
        self.assertEqual(voucher['transportOut_payment_type'], '')
        self.assertEqual(voucher['isEditable'], False)
        self.assertEqual(voucher['isToCheckRevisioned'], False)
        self.assertEqual(voucher['isVoucherDetailLoaded'], False)
        self.assertEqual(voucher['life_stage'], '')
        self.assertEqual(voucher['manifest_id'], '0')
        # TODO: handle logic to verify `voucher['notes']`, which can be `[]` or something like the following, depending on conditions:
        # [
        #     {
        #         'can_view': '1',
        #         'detail': 'If the passenger does not arrive within 3 hours of "ETA at hotel" advised, please call and alert Travelliance so we can follow up with the airline.',
        #         'date': '07/05/2018 19:05',
        #         'user_name': 'Support',
        #         'user_id': '1',
        #         'id': '2'
        #     },
        # ]
        self.assertEqual(len(voucher['paxs']), 1)
        Michael = [_p for _p in voucher['paxs'] if _p['name'] == 'Michael'][0]

        total_rooms = 0
        total_count = 0
        for passenger in voucher['paxs']:
            self.assertGreater(int(passenger['id']), 0)
            self.assertEqual(passenger['cost_code'], '')
            self.assertEqual(passenger['pnr'], '')
            self.assertEqual(passenger['count'], '1')  # TODO: QUSTION: when is this not 1??
            self.assertEqual(passenger['return_date'], '')
            self.assertEqual(passenger['pickup_date'], '')
            self.assertEqual(passenger['business_unit'], '')
            self.assertEqual(passenger['no_show'], '0')
            self.assertEqual(passenger['return_date'], '')

            total_rooms += int(passenger['rooms'])
            total_count += int(passenger['count'])
        self.assertEqual(total_rooms, 1)
        self.assertEqual(total_count, 1)

        self.assertEqual(voucher['passenger_level'], '')
        self.assertEqual(voucher['passenger_phone'], '')
        EXPECTED_ROOM_RATES = [
            {
                'rates': [
                    ''  # TODO: this looks bad! investigate!
                ],
                'count': ''  # TODO: this looks bad! investigate!
            }
        ]
        self.assertEqual(voucher['roomRates'], EXPECTED_ROOM_RATES)
        EXPECTED_SEND_EMAIL_VALUES = {
            "transportTo": {
                "email": "",
                "emails": []
            },
            "transportFrom": {
                "email": "",
                "emails": []
            },
            "airline": {
                "email": "",
                "emails": []
            },
            "hotel": {
                "email": "",
                "emails": []
            }
        }
        self.assertEqual(voucher['sendEmail'], EXPECTED_SEND_EMAIL_VALUES)
        self.assertEqual(voucher['totals'], '')  # TODO: this looks like a money bug!
        self.assertEqual(voucher['transport_from_hotel_departure'], '0.0')
        self.assertEqual(voucher['transport_to_hotel'], '0')
        self.assertEqual(voucher['transportIn_payment_type'], '')
        self.assertEqual(voucher['voucher_airline_auth_user'], '')
        self.assertEqual(voucher['voucher_blocks_price'], 100.50)
        self.assertEqual(voucher['voucher_conference'], '0')
        self.assertEqual(voucher['voucher_currency'], 'USD')
        self.assertEqual(voucher['voucher_departure_flight'], '')
        self.assertEqual(voucher['voucher_departure_date'],
                         (voucher_creation_date_time + datetime.timedelta(days=1)).strftime(
                             DATETIME_FORMAT_FOR_VOUCHERS))
        # self.assertEqual(voucher['voucher_departure_time'], '???')  # TODO verify voucher_departure_time
        self.assertEqual(voucher['voucher_disruption_date'],
                         voucher_creation_date_time.strftime(DATETIME_FORMAT_FOR_VOUCHERS))
        self.assertEqual(voucher['voucher_departure_port'], str(airport_id))
        self.assertEqual(voucher['voucher_disruption_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_date_o'], voucher_creation_date_time.strftime('%Y-%m-%d'))
        self.assertEqual(voucher['voucher_disruption_flight_type'], '')
        self.assertEqual(voucher['voucher_disruption_port_currency'], None)
        self.assertEqual(voucher['voucher_disruption_port'], str(airport_id))
        self.assertEqual(voucher['voucher_fasttrack_hotel_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transport_email'], '')
        self.assertEqual(voucher['voucher_fasttrack_transportOut_email'], '')
        # self.assertEqual(voucher['voucher_finalization_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_finalization_ts
        self.assertEqual(voucher['voucher_hotel_nights'], str(number_of_nights))
        self.assertEqual(voucher['voucher_id'], str(voucher_id))
        self.assertEqual(voucher['voucher_invoice_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_invoice_notification'], '0')
        self.assertEqual(voucher['voucher_room_rate_commission'], '0.00')  # TODO: investigate if money issue!
        self.assertEqual(voucher['voucher_room_type']['id'], '2')
        self.assertEqual(voucher['voucher_room_rate'], '0')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_room_total'], '1')  # TODO: this looks wrong!
        self.assertEqual(voucher['voucher_varied_room_rates'], '0')
        self.assertEqual(voucher['voucherTotalRate'], '')
        self.assertGreaterEqual(len(voucher['voucher_code']), 4)
        self.assertTrue(voucher['voucher_code'].startswith('NHA'))
        self.assertEqual(voucher['voucher_commission_type'], 'percentage')
        self.assertEqual(voucher['voucher_commission_value'], '10.00')
        # self.assertEqual(voucher['voucher_cutoff_time'], now.strftime(DATETIME_FORMAT_FOR_VOUCHERS))  # TODO: this is failing! time is 5 hours off of supplied input. Need to investigate.
        self.assertEqual(voucher['voucher_departure_terminal'], '')
        self.assertEqual(voucher['voucher_departure_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_disruption_arrival_port'], '0')
        self.assertEqual(voucher['voucher_disruption_flight'], 'PR-1234')
        self.assertEqual(voucher['voucher_disruption_reason'], '12')
        self.assertEqual(voucher['voucher_fasttrack_natwide_email'], 'opssupport@tvlinc.com')
        self.assertEqual(voucher['voucher_fasttrack_airline_email'], '')

        # self.assertEqual(voucher_view_data['voucher_hotel_eta'], '???')  # TODO verify voucher_hotel_eta
        self.assertEqual(voucher['voucher_notes'], '')
        self.assertEqual(len(voucher['voucher_room_blocks']), 1)

        self.assertEqual(voucher['voucher_room_blocks'][0]['rate'], '100.50')
        self.assertEqual(voucher['voucher_room_blocks'][0]['count'], '1')

        self.assertEqual(voucher['voucher_requesting_airline'], str(airline_id))
        self.assertEqual(voucher['voucher_requesting_port'], str(airport_id))
        self.assertEqual(voucher['voucher_status_text'], 'finalised')
        self.assertEqual(voucher['voucher_status'], '50')
        self.assertEqual(voucher['voucher_pax_total'], str(len(passenger_names)))
        self.assertEqual(voucher['voucher_update_user'], 'Support')
        # self.assertEqual(voucher['voucher_update_ts'], '2018-05-07 14:30:08.000000')  # TODO: verify voucher_update_ts
        self.assertIsNotNone(voucher['voucher_uuid'])
        uuid.UUID(voucher['voucher_uuid'], version=4)

        # TODO: could extend scenario to modify the voucher or send the voucher or voucher communications.

    def test_quick_voucher__airline_block_first(self):
        """

        Scenario:
        * setup: add inventory hardblock, then softblock, then airline_softblock.
          each with 1 room.
          then use quick voucher method and make sure that hardblock and airline_softblock are the two blocks used. .
        * TVL staff creates a Quick Voucher:
            - two room
            - one night
        * submit the minimum inputs where the backend will still accept the inputs
          (i.e., not crash or report an input error).
        """
        hotel_id = 88137  #hilton miami downtown
        airline_id = 294  # Purple Rain
        tz = 'America/New_York'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)
        number_of_rooms = 2
        number_of_nights = 1
        airport_id = 192 #miami
        passenger_names = ['Linda']
        flight_number = 'PR-1234'

        # ensure there is sufficient inventory for the booking ----
        comment_1 = 'first ' + str(uuid.uuid4())
        comment_2 = 'second ' + str(uuid.uuid4())
        comment_3 = 'third ' + str(uuid.uuid4())

        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='149.99', blocks=1,
                                    pay_type='0', comment=comment_1)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='160.99', blocks=1,
                                    pay_type='0', comment=comment_2)
        self.add_hotel_availability(hotel_id, 0, availability_date, ap_block_type=0, block_price='149.99', blocks=1,
                                    pay_type='0', comment=comment_3)

        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        # create a Quick Voucher ----
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights,
                                                  voucher_date=voucher_creation_date_time,
                                                  flight_number=flight_number, room_type=1)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_1 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_1)
        block_2 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_2)

        expected_room_blocks = [
            dict({'comment': comment_1, 'room_count': '1', 'ap_block_type': '1', 'block': block_1}),
            dict({'comment': comment_2, 'room_count': '1', 'ap_block_type': '0', 'block': block_2})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 2, expected_room_blocks)

    def test_quick_voucher__airline_block_first_no_hardblock(self):
        """
        Scenario:
        * setup: add inventory  softblock, then airline_softblock.
          each with 1 room.
          then use quick voucher method and make sure that airline_softblock is used. .
        * TVL staff creates a Quick Voucher:
            - one person
            - one room
            - one night
        * submit the minimum inputs where the backend will still accept the inputs
          (i.e., not crash or report an input error).
        """
        hotel_id = 101312 # Hyatt Place Phoenix/Gilbert
        airline_id = 294  # Purple Rain
        tz = 'America/Phoenix'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)
        number_of_rooms = 1
        number_of_nights = 1
        airport_id = 217 #phx
        passenger_names = ['Linda']
        flight_number = 'PR-1234'

        # ensure there is sufficient inventory for the booking ----
        comment_1 = 'first ' + str(uuid.uuid4())
        comment_2 = 'second ' + str(uuid.uuid4())

        self.add_hotel_availability(hotel_id, 0, availability_date, ap_block_type=0, block_price='149.99', blocks=1,
                                    pay_type='0', comment=comment_2)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='160.99',
                                    blocks=1, pay_type='0', comment=comment_1)

        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        # create a Quick Voucher ----
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights,
                                                  voucher_date=voucher_creation_date_time,
                                                  flight_number=flight_number, room_type=1)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_1 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_1)

        expected_room_blocks = [
            dict({'comment': comment_1, 'room_count': '1', 'ap_block_type': '0', 'block': block_1})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 1, expected_room_blocks)

    def test_quick_voucher_multi_block_booking(self):
        """
        quick voucher test for multi block booking
        """
        airline_id = 294  # Purple Rain Airlines
        hotel_id = 107981  # A Victory Inn Tolleson
        tz = 'America/Phoenix'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)

        comment_1 = 'first ' + str(uuid.uuid4())
        comment_2 = 'second ' + str(uuid.uuid4())
        comment_3 = 'third ' + str(uuid.uuid4())
        comment_4 = 'fourth ' + str(uuid.uuid4())
        comment_5 = 'fifth ' + str(uuid.uuid4())
        comment_6 = 'sixth ' + str(uuid.uuid4())
        comment_7 = 'seventh ' + str(uuid.uuid4())
        comment_8 = 'eighth ' + str(uuid.uuid4())
        comment_9 = 'ninth ' + str(uuid.uuid4())
        comment_10 = 'tenth ' + str(uuid.uuid4())
        comment_11 = 'eleventh ' + str(uuid.uuid4())
        comment_12 = 'twelfth ' + str(uuid.uuid4())
        comment_13 = 'thirteenth ' + str(uuid.uuid4())
        comment_14 = 'fourteenth ' + str(uuid.uuid4())
        comment_15 = 'fifteenth ' + str(uuid.uuid4())

        # blocks should be returned/sorted/used by:
        # ap_block_type (greatest), ap_block_price (lowest), then ap_block (lowest)

        # soft blocks
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='149.99', blocks=1,
                                    pay_type='0', comment=comment_12)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='149.99', blocks=2,
                                    pay_type='0', comment=comment_14)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='149.99', blocks=1,
                                    pay_type='0', comment=comment_13)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='150.00', blocks=1,
                                    pay_type='0', comment=comment_15)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='148.00', blocks=1,
                                    pay_type='0', comment=comment_11)

        # contract blocks
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='139.99', blocks=1,
                                    pay_type='0', comment=comment_2)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='139.99', blocks=2,
                                    pay_type='0', comment=comment_4)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='139.99', blocks=1,
                                    pay_type='0', comment=comment_3)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='140.00', blocks=1,
                                    pay_type='0', comment=comment_5)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='138.00', blocks=1,
                                    pay_type='0', comment=comment_1)

        # hard blocks
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='129.99', blocks=1,
                                    pay_type='0', comment=comment_7)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='129.99', blocks=2,
                                    pay_type='0', comment=comment_9)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='129.99', blocks=1,
                                    pay_type='0', comment=comment_8)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='130.00', blocks=1,
                                    pay_type='0', comment=comment_10)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='128.00', blocks=1,
                                    pay_type='0', comment=comment_6)

        # voucher data

        number_of_rooms = 3
        number_of_nights = 1
        airport_id = 217  # phx
        passenger_names = []
        flight_number = 'PR 1111'

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # get availability blocks by hotel_id
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        # create block objects that should have been used by quick voucher creation
        block_1 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_1)
        block_2 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_2)
        block_3 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_3)

        expected_room_blocks = [
            dict({'comment': comment_1, 'room_count': '1', 'ap_block_type': '2', 'block': block_1}),
            dict({'comment': comment_2, 'room_count': '1', 'ap_block_type': '2', 'block': block_2}),
            dict({'comment': comment_3, 'room_count': '1', 'ap_block_type': '2', 'block': block_3})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_4 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_4)
        block_5 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_5)

        expected_room_blocks = [
            dict({'comment': comment_4, 'room_count': '2', 'ap_block_type': '2', 'block': block_4}),
            dict({'comment': comment_5, 'room_count': '1', 'ap_block_type': '2', 'block': block_5}),
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_6 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_6)
        block_7 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_7)
        block_8 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_8)

        expected_room_blocks = [
            dict({'comment': comment_6, 'room_count': '1', 'ap_block_type': '1', 'block': block_6}),
            dict({'comment': comment_7, 'room_count': '1', 'ap_block_type': '1', 'block': block_7}),
            dict({'comment': comment_8, 'room_count': '1', 'ap_block_type': '1', 'block': block_8})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_9 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_9)
        block_10 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_10)

        expected_room_blocks = [
            dict({'comment': comment_9, 'room_count': '2', 'ap_block_type': '1', 'block': block_9}),
            dict({'comment': comment_10, 'room_count': '1', 'ap_block_type': '1', 'block': block_10})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_11 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_11)
        block_12 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_12)
        block_13 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_13)

        expected_room_blocks = [
            dict({'comment': comment_11, 'room_count': '1', 'ap_block_type': '0', 'block': block_11}),
            dict({'comment': comment_12, 'room_count': '1', 'ap_block_type': '0', 'block': block_12}),
            dict({'comment': comment_13, 'room_count': '1', 'ap_block_type': '0', 'block': block_13})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_14 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_14)
        block_15 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_15)

        expected_room_blocks = [
            dict({'comment': comment_14, 'room_count': '2', 'ap_block_type': '0', 'block': block_14}),
            dict({'comment': comment_15, 'room_count': '1', 'ap_block_type': '0', 'block': block_15})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

    def test_quick_voucher_multi_block_booking_different_block_types(self):
        """
        quick voucher test for multi block booking using different ap_block_type
        """
        airline_id = 294  # Purple Rain Airlines
        hotel_id = 103210  # Holiday Inn - Chicago / Oakbrook
        tz = 'America/Los_Angeles'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)

        comment_1 = 'first ' + str(uuid.uuid4())
        comment_2 = 'second ' + str(uuid.uuid4())
        comment_3 = 'third ' + str(uuid.uuid4())
        comment_4 = 'fourth ' + str(uuid.uuid4())
        comment_5 = 'fifth ' + str(uuid.uuid4())
        comment_6 = 'sixth ' + str(uuid.uuid4())
        comment_7 = 'seventh ' + str(uuid.uuid4())
        comment_8 = 'eighth ' + str(uuid.uuid4())
        comment_9 = 'ninth ' + str(uuid.uuid4())
        comment_10 = 'tenth ' + str(uuid.uuid4())
        comment_11 = 'eleventh ' + str(uuid.uuid4())
        comment_12 = 'twelfth ' + str(uuid.uuid4())
        comment_13 = 'thirteenth ' + str(uuid.uuid4())
        comment_14 = 'fourteenth ' + str(uuid.uuid4())
        comment_15 = 'fifteenth ' + str(uuid.uuid4())

        # blocks should be returned/sorted/used by:
        # ap_block_type (greatest), ap_block_price (lowest), then ap_block (lowest)

        # soft blocks
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='149.99', blocks=1,
                                    pay_type='0', comment=comment_12)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='149.99', blocks=2,
                                    pay_type='0', comment=comment_14)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='149.99', blocks=1,
                                    pay_type='0', comment=comment_13)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='150.00', blocks=2,
                                    pay_type='0', comment=comment_15)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=0, block_price='148.00', blocks=1,
                                    pay_type='0', comment=comment_11)

        # contract blocks
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='139.99', blocks=1,
                                    pay_type='0', comment=comment_2)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='139.99', blocks=2,
                                    pay_type='0', comment=comment_4)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='139.99', blocks=1,
                                    pay_type='0', comment=comment_3)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='140.00', blocks=1,
                                    pay_type='0', comment=comment_5)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='138.00', blocks=1,
                                    pay_type='0', comment=comment_1)

        # hard blocks
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='129.99', blocks=1,
                                    pay_type='0', comment=comment_7)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='129.99', blocks=2,
                                    pay_type='0', comment=comment_9)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='129.99', blocks=1,
                                    pay_type='0', comment=comment_8)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='130.00', blocks=1,
                                    pay_type='0', comment=comment_10)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='128.00', blocks=1,
                                    pay_type='0', comment=comment_6)

        # voucher data
        number_of_nights = 1
        airport_id = 925  # FAT
        passenger_names = []
        flight_number = 'PR 1111'

        # get availability blocks by hotel_id
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=1, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_1 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_1)

        expected_room_blocks = [
            dict({'comment': comment_1, 'room_count': '1', 'ap_block_type': '2', 'block': block_1})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 1, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=3, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_2 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_2)
        block_3 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_3)
        block_4 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_4)

        expected_room_blocks = [
            dict({'comment': comment_2, 'room_count': '1', 'ap_block_type': '2', 'block': block_2}),
            dict({'comment': comment_3, 'room_count': '1', 'ap_block_type': '2', 'block': block_3}),
            dict({'comment': comment_4, 'room_count': '1', 'ap_block_type': '2', 'block': block_4})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=1, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        expected_room_blocks = [
            dict({'comment': comment_4, 'room_count': '1', 'ap_block_type': '2', 'block': block_4})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 1, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=2, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_5 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_5)
        block_6 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_6)

        expected_room_blocks = [
            dict({'comment': comment_5, 'room_count': '1', 'ap_block_type': '2', 'block': block_5}),
            dict({'comment': comment_6, 'room_count': '1', 'ap_block_type': '1', 'block': block_6})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 2, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=2, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_7 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_7)
        block_8 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_8)

        expected_room_blocks = [
            dict({'comment': comment_7, 'room_count': '1', 'ap_block_type': '1', 'block': block_7}),
            dict({'comment': comment_8, 'room_count': '1', 'ap_block_type': '1', 'block': block_8})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 2, expected_room_blocks)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=9, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_9 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_9)
        block_10 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_10)
        block_11 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_11)
        block_12 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_12)
        block_13 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_13)
        block_14 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_14)
        block_15 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_15)

        expected_room_blocks = [
            dict({'comment': comment_9, 'room_count': '2', 'ap_block_type': '1', 'block': block_9}),
            dict({'comment': comment_10, 'room_count': '1', 'ap_block_type': '1', 'block': block_10}),
            dict({'comment': comment_11, 'room_count': '1', 'ap_block_type': '0', 'block': block_11}),
            dict({'comment': comment_12, 'room_count': '1', 'ap_block_type': '0', 'block': block_12}),
            dict({'comment': comment_13, 'room_count': '1', 'ap_block_type': '0', 'block': block_13}),
            dict({'comment': comment_14, 'room_count': '2', 'ap_block_type': '0', 'block': block_14}),
            dict({'comment': comment_15, 'room_count': '1', 'ap_block_type': '0', 'block': block_15})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 9, expected_room_blocks)

        # add additional inventory for final test
        comment_16 = 'sixteenth ' + str(uuid.uuid4())
        comment_17 = 'seventeenth ' + str(uuid.uuid4())
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=1, block_price='150.00', blocks=1,
                                    pay_type='0', comment=comment_16)
        self.add_hotel_availability(hotel_id, airline_id, availability_date, ap_block_type=2, block_price='148.00', blocks=1,
                                    pay_type='0', comment=comment_17)

        # get availability blocks by hotel_id
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        # create quick voucher
        response_json = self.create_quick_voucher(airline_id, hotel_id, airport_id,
                                                  number_of_rooms=3, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights, flight_number=flight_number,
                                                  voucher_date=voucher_creation_date_time,)

        self.assertEqual(response_json['success'], '1')
        self.assertIsNotNone(response_json['voucher']['voucher_id'])

        # create block objects that should have been used by quick voucher creation
        block_16 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_16)
        block_17 = self.find_hotel_availability_block_by_comment(hotel_availability, comment_17)

        expected_room_blocks = [
            dict({'comment': comment_15, 'room_count': '1', 'ap_block_type': '0', 'block': block_15}),
            dict({'comment': comment_16, 'room_count': '1', 'ap_block_type': '1', 'block': block_16}),
            dict({'comment': comment_17, 'room_count': '1', 'ap_block_type': '2', 'block': block_17})
        ]

        # validate voucher blocks used
        self._test_voucher_used_correct_blocks(response_json['voucher']['voucher_id'], 3, expected_room_blocks)

    def _test_voucher_used_correct_blocks(self, voucher_id, expected_voucher_rooms, expected_blocks):
        """
        common shared utility that voucher tests can use to validate the voucher used the correct blocks
        param voucher_id: int
        param expected_voucher_rooms: int
        param expected_blocks: list(dict) where dict contains the following keys and values:
        dict = {
            comment:  (string) availability_block_comment,
            room_count: (string) expected room count used,
            ap_block_type: (sting) ap_block_type 0, 1, or 2, (where 0 = soft_block, 1 = hard_block, 2 = contract_block)
            block: (JSON) hotel_availability_block object
        }
        return: None
        """
        room_total = 0
        voucher = self.get_voucher_data(voucher_id)
        voucher_room_blocks = voucher['voucher_room_blocks']
        for expected_block in expected_blocks:
            used_expected_block = False
            for voucher_room_block in voucher_room_blocks:
                if voucher_room_block['fk_block_id'] == expected_block['block']['hotel_availability_id']:
                    used_expected_block = True
                    room_total += int(voucher_room_block['count'])
                    self.assertEqual(voucher_room_block['count'], expected_block['room_count'])
                    self.assertEqual(voucher_room_block['ap_block_type'], expected_block['ap_block_type'])
                    # TODO: validate inventory has decremented once GET hotel_availability process has been updated

            if not used_expected_block:
                print('Voucher did not use expected block for ' + expected_block['comment'])
            self.assertTrue(used_expected_block)

        self.assertEqual(int(voucher['voucher_room_total']), room_total)
        self.assertEqual(int(voucher['voucher_room_total']), expected_voucher_rooms)
        self.assertEqual(len(voucher_room_blocks), len(expected_blocks))

    def test_multi_night_voucher(self):
        """
        Scenario:
        * setup: add one room of inventory to a hotel.
        * create inventory  for rest of nights
        * TVL staff creates a 3 night Voucher:
            - two people (husband and wife)
            - one room
            - one night

        voucher should be created successfully
        """
        hotel_id = 94701 # Sheraton - Cleveland Airport
        airline_id = 294  # Purple Rain
        tz = 'America/Los_Angeles'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)
        number_of_rooms = 1
        number_of_nights = 3
        airport_id = 688
        pay_type = '0'
        passenger_names = ['Johnny Appleseed', 'Elizabeth Chapman']
        flight_number = 'PR-4321'

        # ensure there is sufficient inventory for the booking ----
        unique_comment = 'for full voucher ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=1, block_price='81.81', ap_block_type=1,
                                    issued_by='test user', pay_type=pay_type,
                                    comment=unique_comment)

        # pick a block to book ----
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        multinight_availability= self._multi_night_availability( hotel_availability[0], voucher_creation_date_time,
                                                                number_of_nights,number_of_rooms)

        response_json = self.create_full_voucher(airline_id, hotel_id, airport_id,
                                                  voucher_date=voucher_creation_date_time,
                                                  number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                  number_of_nights=number_of_nights,
                                                  flight_number=flight_number,multi_night_availability=multinight_availability)

        self.assertEqual(response_json['success'], '1')
        voucher_id = response_json['voucher']['voucher_id']
        self.assertGreater(voucher_id, 0)

    def test_multi_night_voucher__with_less_days_inventory(self):
        """
        * setup: add 1 rooms for first day.
        * create inventory  for rest of nights but less 1 night
        * TVL staff creates a 4 night Voucher:

        get an error message

        """
        hotel_id = 94709  # Hampton Inn & Suites - Middleburg Heights
        airline_id = 294  # Purple Rain
        tz = 'America/Los_Angeles'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)
        number_of_rooms = 1
        number_of_nights = 4
        airport_id = 688
        pay_type = '0'
        passenger_names = ['Johnny Appleseed', 'Elizabeth Chapman']
        flight_number = 'PR-4321'

        # ensure there is sufficient inventory for the booking ----
        unique_comment = 'for full voucher ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=1, block_price='81.81', ap_block_type=1,
                                    issued_by='test user', pay_type=pay_type,
                                    comment=unique_comment)

        # pick a block to book ----
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        multinight_availability = self._multi_night_availability(hotel_availability[0], voucher_creation_date_time,
                                                                 number_of_nights-1, number_of_rooms)

        response_json = self.create_full_voucher(airline_id, hotel_id, airport_id,
                                                 voucher_date=voucher_creation_date_time,
                                                 number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                 number_of_nights=number_of_nights,
                                                 flight_number=flight_number,
                                                 multi_night_availability=multinight_availability)

        self.assertEqual(response_json['errMsg'], 'Unable to book hotel. We do not have room for all nights.')

    def test_multi_night_voucher__with_insufficient_inventory(self):
        """
        Scenario:
        * setup: add 3 rooms for first day.
        * for remaining day inventory is 2 rooms
        * TVL staff creates a 5 night Voucher:

        get an error message in return:
        "Unable to book hotel. reason: For 04/01/2020 we only have 1 room(s) available. For 04/02/2020 we only have 2 room(s) available. For 04/03/2020 we only have 2 room(s) available. For 04/04/2020 we only have 2 room(s) available. For 04/05/2020 we only have 2 room(s) available."


        """
        hotel_id = 94705  # Courtyard - Cleveland Airport South
        airline_id = 294  # Purple Rain
        tz = 'America/Los_Angeles'
        now = self._get_timezone_now(tz)
        availability_date = self._get_event_date(tz)
        voucher_creation_date_time = self._get_event_date_time(tz, now)
        number_of_rooms = 3
        number_of_nights = 5
        airport_id = 688
        pay_type = '0'
        passenger_names = ['Johnny Appleseed', 'Elizabeth Chapman']
        flight_number = 'PR-4321'

        # ensure there is sufficient inventory for the booking ----
        unique_comment = 'for full voucher ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        self.add_hotel_availability(hotel_id, airline_id, availability_date,
                                    blocks=1, block_price='81.81', ap_block_type=1,
                                    issued_by='test user', pay_type=pay_type,
                                    comment=unique_comment)

        # pick a block to book ----
        hotel_availability = self.get_hotel_availability(hotel_id, availability_date)

        multinight_availability = self._multi_night_availability(hotel_availability[0], voucher_creation_date_time,
                                                                 number_of_nights, number_of_rooms-1)

        response_json = self.create_full_voucher(airline_id, hotel_id, airport_id,
                                                 voucher_date=voucher_creation_date_time,
                                                 number_of_rooms=number_of_rooms, passenger_names=passenger_names,
                                                 number_of_nights=number_of_nights,
                                                 flight_number=flight_number,
                                                 multi_night_availability=multinight_availability)

        self.assertIn( 'Unable to book hotel. reason: For',response_json['errMsg'])

    def test_create_airline_user(self):
        """
        Create airline user with valid data
        """
        airline_id = 146  # Jetstar Asia
        port_id = 654  # Chicago Midway International Airport
        response = self.create_user_by_type(airline_id, port_id, 11, 'airline')
        self.assertGreater(int(response['id']), 0)
        self.assertEqual(str(response['updated_by_user']), 'Support')

    def test_create_airline_user_with_invalid_input(self):
        """
        Create airline user with invalid data
        User Id > required length
        Name > required length
        Password > required length
        """
        airline_id = 146  # Jetstar Asia
        port_id = 654  # Chicago Midway International Airport
        response = self.create_user_by_type(airline_id, port_id, 11, 'airline', True)
        error_messages = [
            "User Name should be between 6 and 15 characters",
            "Person's name should be between 2 and 45 characters",
            "Password must contain at least 8 characters, 1 number, 1 Uppercase letter, 1 Lowercase letter, and a Special Character.",
            "This user name is not allowed. Please select another user name for the new user."
        ]
        if 'errMsg' in response:
            for msg in response['errMsg']:
                self.assertEqual(msg in error_messages, True)

    def test_create_hotel_user(self):
        """
        Create hotel user with valid data
        """
        hotel_id = 103210  # Holiday Inn - Chicago / Oakbrook
        port_id = 654  # Chicago Midway International Airport
        response = self.create_user_by_type(hotel_id, port_id, 11, 'hotel')
        self.assertGreater(int(response['id']), 0)
        self.assertEqual(str(response['updated_by_user']), 'Support')

    def test_create_hotel_user_with_invalid_input(self):
        """
        Create hotel user with invalid data
        User Id > required length
        Name > required length
        Password > required length
        """
        hotel_id = 103210  # Holiday Inn - Chicago / Oakbrook
        port_id = 654  # Chicago Midway International Airport
        response = self.create_user_by_type(hotel_id, port_id, 11, 'hotel', True)
        error_messages = [
            "User Name should be between 6 and 15 characters",
            "Person's name should be between 2 and 45 characters",
            "Password must contain at least 8 characters, 1 number, 1 Uppercase letter, 1 Lowercase letter, and a Special Character.",
            "This user name is not allowed. Please select another user name for the new user."
        ]
        if 'errMsg' in response:
            for msg in response['errMsg']:
                self.assertEqual(msg in error_messages, True)
            # TODO: test book room functionality.

    # TODO: test logout feature: GET /admin/index.php?logout=true&continue=admin%2Fhotels.php
    # TODO: add tests to verify user creation and login (for different types of users)
    # TODO: add *more* tests to verify Quick Voucher functionality (input-checking, different scenarios, different number or rooms, passengers)
    # TODO: add tests to verify normal (non-quick) Voucher functionality
    # TODO: add tests to verify Room Count Voucher functionality

    def test_user_locking(self):
        """
         scenarios:
         create a user login 5 times with wrong password on 6th attempt check if user is locked
        """

        # Create user
        response = self.create_new_tva_user(role="Operator", group_id=3, is_active=True)
        self.assertGreater(response['user_id'], 0)
        user_name = response['username']
        password = 'anything wrong'
        login_attempts_threshold = 5

        # Login user with wrong password, 5times
        for x in range(login_attempts_threshold):
            self.login_user_to_stormx(username=user_name, password=password)

        final_response = self.login_user_to_stormx(username=user_name,
                                                   password=password)  # account should be lock by now

        # update this text when lockout message is changed again
        self.assertIn('locked your account after too many failed login attempts', final_response.text)

    def test_hotel_with_invalid_contact_email(self):
        """
        when a hotel is created with invalid contact email it returns error from server
        """

        hotel_post_data = self.get_create_hotel_post_data('G')
        hotel_post_data['hotel_contact_email'] = 'test@tv(linc).blackhole'
        response_json = self.add_or_update_hotel(hotel_post_data, 0, None)
        error_message = ["Contact Email is invalid",]
        if 'errMsg' in response_json:
            for msg in response_json['errMsg']:
                self.assertEqual(msg in error_message, True)
        self.assertEqual(response_json['success'], '0')

    def test_hotel_blacklisting_for_tvl(self):
        """
        when a hotel is black listed for tvl it should not show up in voucher creation inventory
        """
        # create new hotel with tvl blacklisting reason
        hotel_post_data = self.get_create_hotel_post_data('G', 'Do not use this hotel')
        response_json = self.add_or_update_hotel(hotel_post_data, 0, None)
        hotel_id = response_json['id']
        airline_id = 71
        port_id = 16
        today = self._get_event_date('America/Chicago')

        # attach port with new hotel
        serviced_port_response = self.add_hotel_serviced_port(port_id, hotel_id, cookies=None, ranking=2)
        self.assertGreater(serviced_port_response['id'], 0)

        # add airline  pay block for the blacklisted hotel
        comment = 'hotel blacklisting test ' + str(uuid.uuid4())  # generate unique comment so we can search for it.
        number_of_rooms = 5
        price = '100'
        response = self.create_hotel_availability(hotel_id, airline_id, today,
                                                  blocks=number_of_rooms, block_price=price,
                                                  issued_by='tester', pay_type='0',
                                                  comment=comment)
        response = response.json()
        self.assertEqual(response['success'], '1')

        # get blocks for port and airline
        blocks_by_hotel = self.get_port_hotels_inventory(port_id, airline_id, 1).json()

        # find blacklisted hotel in availability listing
        hotel_found = False
        if len(blocks_by_hotel) > 0:
            for blocks in blocks_by_hotel:
                if blocks['name'] == hotel_post_data['hotel_name']:
                    hotel_found = True
                    break

        self.assertEqual(hotel_found, False)

    def test_hotel_duplication_warning(self):
        """
        create two identical hotels to check if it warns on second attempt
        """
        # create new hotel
        hotel_post_data = self.get_create_hotel_post_data('G', 'Do not use - test hotel',0)
        response_json = self.add_or_update_hotel(hotel_post_data, 0, None)
        hotel_id = response_json['id']

        # try adding same hotel 1 more time
        response_json = self.add_or_update_hotel(hotel_post_data, 0, None)

        self.assertEqual(response_json['success'], '0')
        self.assertIn('duplicateFound',response_json)
        self.assertIn(response_json['duplicateFound'],'1')

    def test_hotel_with_invalid_finance_email(self):
        """
        when a hotel is created with invalid finance email it returns error from server
        """

        hotel_post_data = self.get_create_hotel_post_data('G')
        hotel_post_data['hotel_finance_email'] = 'test@tv(linc).blackhole'
        response_json = self.add_or_update_hotel(hotel_post_data, 0, None)
        error_message = ["Finance Email is invalid",]
        if 'errMsg' in response_json:
            for msg in response_json['errMsg']:
                self.assertEqual(msg in error_message, True)
        self.assertEqual(response_json['success'], '0')

    def test_invalid_url_response(self):
        url = self._php_host + '/asdf/1234'
        response = requests.get(url, allow_redirects=False)
        self.assertEqual(response.status_code, 404)

    def test_forbidden_url_response(self):
        url = self._php_host + '/admin/app/'
        response = requests.get(url, allow_redirects=False)
        self.assertEqual(response.status_code, 403)
