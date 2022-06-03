
import uuid
import math
from datetime import datetime, timedelta
import requests


from stormx_verification_framework import (
    SUPPORTED_ENVIRONMENTS,
    display_response,
    CUSTOMER_TOKENS,
    StormxSystemVerification,
)


class TestPassengerPayAPI(StormxSystemVerification):
    """
    Verify StormX PHP code's Passenger Pay App API behaves properly.
    """

    # TODO: SECURITY: in general, the API seems to be meant for consumption by the DisconneX .NET backend server.
    #                 it looks like the full API should be secured so only authorized systems can access it and not
    #                 just probe all of our data (customer lists, inventory, etc.)

    REASON_PASSENGER_PAY = '11'

    def test_ping(self):
        url = self._php_host + '/api/v1/ping'
        headers = self._generate_stormx_php_headers()

        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json, {'result': True})

    def test_get_airports(self):
        url = self._php_host + '/api/v1/airports'
        headers = self._generate_stormx_php_headers()

        def verify_airports_response(response, page_number, per_page):
            self.assertEqual(response.status_code, 200)
            response_json = response.json()
            self.assertEqual(response_json['error'], [])
            self.assertEqual(response_json['page'], page_number)
            self.assertEqual(response_json['per_page'], per_page)
            self.assertGreaterEqual(response_json['total_count'], 550)  # verify a reasonable amount of data loaded.
            self.assertEqual(response_json['page_count'],
                             math.ceil(response_json['total_count']/response_json['per_page']))
            self.assertEqual(len(response_json['results']), 200)
            first_airport = response_json['results'][0]
            self.assertEqual(sorted(first_airport.keys()), ['PortID', 'PortName', 'prefix'])
            self.assertGreater(int(first_airport['PortID']), 0)

        # call to URL without query parameters
        response = requests.get(url, headers=headers)
        verify_airports_response(response, page_number=1, per_page=200)

        # second page of 200 airports
        response = requests.get(url, headers=headers, params={'page': '2', 'per_page': '200'})
        verify_airports_response(response, page_number=2, per_page=200)

        # first page of 100 airports
        response = requests.get(url, headers=headers, params={'page': '1', 'per_page': '100'})
        # print('URL called:', response.url)  # TODO: fix bug and then delete line.
        # verify_airports_response(response, page_number=1, per_page=100)  # TODO: fix bug and then uncomment. fails verification of apiDocumentationV1.md:93

        # second page of 200 airports
        response = requests.get(url, headers=headers, params={'page': '2', 'per_page': '19'})
        # print('URL called:', response.url)  # TODO: fix bug and then delete line.
        # verify_airports_response(response, page_number=2, per_page=19)  # TODO: fix bug and then uncomment. fails verification of apiDocumentationV1.md:93

    def test_get_airlines(self):
        url = self._php_host + '/api/v1/airlines'
        headers = self._generate_stormx_php_headers()

        # verify error response when aiport code not provided
        response = requests.get(url, headers=headers)
        response_json = response.json()
        EXPECTED_ERROR_JSON = {
            'error': {
                'city': 'The City field is required'
            },
            'page': 1,
            'page_count': 0,
            'per_page': 200,
            'results': [],
            'total_count': 0
        }
        self.assertEqual(response.status_code, 200)  # NOTE: might be better to return 400.
        self.assertEqual(response_json, EXPECTED_ERROR_JSON)

        # verify error response when aiport code of less than 3 characters is provided.
        response = requests.get(url, headers=headers, params={'city': 'XY'})
        response_json = response.json()
        EXPECTED_ERROR_JSON = {
            'error': {
                'city': 'The City field needs to be exactly 3 characters'
            },
            'page': 1,
            'page_count': 0,
            'per_page': 200,
            'results': [],
            'total_count': 0
        }
        self.assertEqual(response.status_code, 200)  # NOTE: might be better to return 400.
        self.assertEqual(response_json, EXPECTED_ERROR_JSON)

        # verify happy response for airport SYD.
        response = requests.get(url, headers=headers, params={'city': 'SYD'})
        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['error'], [])
        self.assertEqual(response_json['page'], 1)
        self.assertEqual(response_json['page_count'], 1)
        self.assertGreaterEqual(response_json['total_count'], 55)
        self.assertEqual(len(response_json['results']), response_json['total_count'])
        first_airline = response_json['results'][0]
        self.assertEqual(sorted(first_airline.keys()), ['AirlineID', 'AirlineName', 'flight_prefix', 'prefix'])
        self.assertGreater(int(first_airline['AirlineID']), 0)

    def test_get_airports_inventory__invalid_parameters(self):
        url = self._php_host + '/api/v1/airports/inventory'
        headers = self._generate_stormx_php_headers()

        # verify error response when no query parameters provided
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        EXPECTED_ERROR_JSON = {
            'error': {
                'city': 'The City field is required',
                'ratetype': 'The Ratetype field is required'
            },
            'page': 1,
            'page_count': 0,
            'per_page': 200,
            'results': [],
            'total_count': 0
        }
        self.assertEqual(response.json(), EXPECTED_ERROR_JSON)

    # TODO: review passing in ap and when endpoint if/should return inventory tied to airline. right now only softblocks not tied to an airline are returned.
    # def test_get_airports_inventory__airline_pay(self):
    #     url = self._php_host + '/api/v1/airports/inventory'
    #     headers = self._generate_stormx_php_headers()
    #
    #     # TODO: SECURITY / COMPETITION: we are exposing our full inventory to the Internet without any authentication, including all airline pay and passenger pay rates.
    #
    #     # airline pay inventory for LAX.  assumes LAX inventory already loaded by add_test_inventory.
    #     response = requests.get(url, headers=headers, params={'city': 'LAX', 'ratetype': 'AP'})
    #     self.assertEqual(response.status_code, 200)
    #     response_json = response.json()
    #     self.assertEqual(response_json['error'], [])
    #     self.assertEqual(response_json['page'], 1)
    #     #self.assertGreaterEqual(response_json['page_count'], 1)  # TODO: fix bug. page_count coming back as 0 when there are records!
    #     self.assertGreaterEqual(len(response_json['results']), 1)
    #     #self.assertGreaterEqual(response_json['total_count'], 1)  # TODO: fix bug. total_count coming back as 0 when there are records!
    #
    #     EXPECTED_INVENTORY_KEYS = [
    #         'address', 'airportCode', 'available',
    #         'blockId',
    #         'currency',
    #         'distance',
    #          'eanId','eanImageUrl',
    #         'expediaRapidId',
    #         'hard_block', 'hotelId', 'hotel_name', 'imageUrl',
    #         'latitude', 'longitude',
    #         'p_latitude', 'p_longitude', 'petsAllowed', 'petsFee', 'phone_no', 'propertyCode',
    #         'rate',
    #         'servicePetsAllowed', 'servicePetsFee', 'shuttle', 'shuttleTiming', 'starRating',
    #         'tax',
    #         'worldSpanId',
    #     ]
    #
    #     for inventory_result in response_json['results']:
    #         self.assertEqual(sorted(inventory_result.keys()), EXPECTED_INVENTORY_KEYS)
    #         self.assertGreater(int(inventory_result['available']), 0)
    #         self.assertGreater(int(inventory_result['blockId']), 0)
    #         self.assertIn(inventory_result['hard_block'], ('1', '0'))
    #         self.assertEqual(inventory_result['airportCode'], 'LAX')
    #         #TODO: shuttleTiming format is not intuitive. it comes back as "0:0 23:59". Would be nice to fix interface,  -Lee
    #         #      like it is in the Django API.

    def test_get_airports_inventory__passenger_pay(self):
        url = self._php_host + '/api/v1/airports/inventory'
        headers = self._generate_stormx_php_headers()

        # TODO: SECURITY / COMPETITION: we are exposing our full inventory to the Internet without any authentication, including all airline pay and passenger pay rates.

        # load some inventory ---
        today = datetime.utcnow().date()
        hotel_id = 80654  # Travelodge LAX South
        airline_id = None
        # TODO: we really need a better solution for getting inventory into the system and handling the time of day problem.
        #       add inventory for yesterday in case near time early in the morning.
        self.add_hotel_availability(hotel_id, airline_id, today-timedelta(days=1),
                                    blocks=57, block_price='123.45', pay_type='1',
                                    issued_by='Justin Trudeau',
                                    comment='passenger pay get airports ' + str(uuid.uuid4()))
        # add inventory for yesterday in case of after early morning.
        self.add_hotel_availability(hotel_id, airline_id, today,
                                    blocks=57, block_price='123.45', pay_type='1',
                                    issued_by='Justin Trudeau',
                                    comment='passenger pay get airports ' + str(uuid.uuid4()))

        # check passenger pay inventory for LAX. ----
        response = requests.get(url, headers=headers, params={'city': 'LAX', 'ratetype': 'PP'})
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json['error'], [])
        self.assertEqual(response_json['page'], 1)
        # self.assertGreaterEqual(response_json['page_count'], 1)  # TODO: fix bug. page_count coming back as 0 when there are records!
        self.assertGreaterEqual(len(response_json['results']), 1)
        # self.assertGreaterEqual(response_json['total_count'], 1)  # TODO: fix bug. total_count coming back as 0 when there are records!

        EXPECTED_INVENTORY_KEYS = [
            'address', 'airportCode', 'available',
            'blockId',
            'currency',
            'distance',
            'eanId', 'eanImageUrl',
            'expediaRapidId',
            'hard_block', 'hotelId', 'hotel_name', 'imageUrl',
            'latitude', 'longitude',
            'p_latitude', 'p_longitude', 'petsAllowed', 'petsFee', 'phone_no', 'propertyCode',
            'rate',
            'servicePetsAllowed', 'servicePetsFee', 'shuttle', 'shuttleTiming', 'starRating',
            'tax',
            'worldSpanId',
        ]

        hotel_found_in_inventory = False
        for inventory_result in response_json['results']:
            self.assertEqual(sorted(inventory_result.keys()), EXPECTED_INVENTORY_KEYS)
            self.assertGreater(int(inventory_result['available']), 0)
            self.assertGreater(int(inventory_result['blockId']), 0)
            self.assertIn(inventory_result['hard_block'], ('1', '0'))
            self.assertEqual(inventory_result['airportCode'], 'LAX')
            self.assertEqual(inventory_result['currency'], 'USD')

            if int(inventory_result['hotelId']) == hotel_id:
                hotel_found_in_inventory = True
                self.assertEqual(inventory_result['distance'], '1.2 miles')

        self.assertEqual(hotel_found_in_inventory, True)

    # TODO: test GET /api/v1/airports/inventory/block ; verify endpoint is secure and does not expose our full
    # inventory to the internet
    def test_book_inventory_valid_params(self):
        """
        test inventory booking through PHP API
        """

        # TODO: SECURITY / COMPETITION: we are exposing our full inventory to the Internet without any authentication,
        # including all airline pay and passenger pay rates.

        # load some inventory ---
        today = datetime.utcnow().date()
        port = "LAX"
        hotel_id = 80654  # Travelodge LAX South
        rooms = 10
        airline_id = 71
        rate_type = {
            "id": "1",
            "label": "PP"
        }

        block = self.add_hotel_availability(hotel_id, None, today,
                                            blocks=rooms, block_price="123.45", pay_type=rate_type["id"],
                                            issued_by="Justin Trudeau",
                                            comment="passenger pay get airports " + str(uuid.uuid4()))

        block = block["info"]
        self.assertGreater(int(block["inserted_id"]), 0)

        response_json = self.book_inventory(port=port, airline_id=airline_id, hotel_id=hotel_id,
                                            rate_type=rate_type["label"], block_id=block["inserted_id"], rooms=rooms,
                                            first_name="Jane", last_name="Doe", agent="Test", flight_no="TBA")
        self.assertGreater(int(response_json["voucherId"]), 0)

    def test_book_inventory_invalid_params(self):
        """
        test inventory booking with invalid params
        """

        # TODO: SECURITY / COMPETITION: we are exposing our full inventory to the Internet without any authentication,
        # including all airline pay and passenger pay rates.

        # CASE 1
        EXPECTED_ERROR_JSON = {
            "airline": "The Airline field is required",
            "ratetype": "The Ratetype field is required",
            "flightno": "The Flightno field is required",
            "rooms": "The Rooms field is required",
            "portid": "The Portid field is required",
            "firstname": "The Firstname field is required",
            "hotelid": "The Hotelid field is required",
            "agent": "The Agent field is required",
            "blockid": "The Blockid field is required",
            "lastname": "The Lastname field is required",
        }

        response_json = self.book_inventory()
        self.validate_booking_errors(response_json, EXPECTED_ERROR_JSON)

        # CASE 2
        EXPECTED_ERROR_JSON = {
            "ratetype": "The Ratetype field is invalid",
            "hotelid": "The Hotelid field is invalid",
            "firstname": "The Firstname field is required",
            "agent": "The Agent field is required",
            "blockid": "The Blockid field is invalid",
            "lastname": "The Lastname field is required",
            "portid": "The Portid field needs to be exactly 3 characters",
        }

        response_json = self.book_inventory(port="A", airline_id=123, hotel_id=123, rate_type="ZZ", block_id=123,
                                            rooms=2, first_name="", last_name="", agent="", flight_no="T")
        self.validate_booking_errors(response_json, EXPECTED_ERROR_JSON)

        # CASE 3
        EXPECTED_ERROR_JSON = {
            "hotelid": "The Hotelid field needs to be 8 characters or less",
            "rooms": "The Rooms field needs to be 6 characters or less",
            "airline": "The Airline field must be a number",
            "lastname": "The Lastname field needs to be 22 characters or less",
            "ratetype": "The Ratetype field is invalid",
            "portid": "The Portid field needs to be exactly 3 characters",
            "blockid": "The Blockid field is invalid",
            "firstname": "The Firstname field needs to be 22 characters or less",
        }

        response_json = self.book_inventory(port="AAAA", airline_id="123a", hotel_id="2222222123", rate_type="ZZZ",
                                            block_id=123, rooms="99999999", first_name="Long First Name Which is More than Limit",
                                            last_name="Long Last Name Which is More than Limit", agent="Test", flight_no="TBAAA")
        self.validate_booking_errors(response_json, EXPECTED_ERROR_JSON)

    def test_booking_inventory_insufficient_rooms(self):
        """
        test inventory booking with no available rooms
        """

        # TODO: SECURITY / COMPETITION: we are exposing our full inventory to the Internet without any authentication,
        # including all airline pay and passenger pay rates.

        # load some inventory ---
        today = datetime.utcnow().date()
        port = "LAX"
        hotel_id = 80654  # Travelodge LAX South
        rooms = 10
        airline_id = 71
        rate_type = {
            "id": "1",
            "label": "PP"
        }

        # create inventory
        block = self.add_hotel_availability(hotel_id, None, today,
                                            blocks=rooms, block_price="123.45", pay_type=rate_type["id"],
                                            issued_by="Justin Trudeau",
                                            comment="passenger pay get airports " + str(uuid.uuid4()))

        block = block["info"]
        self.assertGreater(int(block["inserted_id"]), 0)

        # consume inventory
        response_json = self.book_inventory(port=port, airline_id=airline_id, hotel_id=hotel_id,
                                            rate_type=rate_type["label"], block_id=block["inserted_id"], rooms=rooms,
                                            first_name="Jane", last_name="Doe", agent="Test", flight_no="TBA")
        self.assertGreater(int(response_json["voucherId"]), 0)

        # try to consume inventory again
        EXPECTED_ERROR_JSON = {
            "blockid": "Insufficient rooms available in block. Rooms required: " + str(rooms) + ", available: 0"
        }

        response_json = self.book_inventory(port=port, airline_id=airline_id, hotel_id=hotel_id,
                                            rate_type=rate_type["label"], block_id=block["inserted_id"], rooms=rooms,
                                            first_name="Jane", last_name="Doe", agent="Test", flight_no="TBA")
        self.validate_booking_errors(response_json, EXPECTED_ERROR_JSON)

    def test_booking_inventory_with_previous_date(self):
        """
        test inventory booking with date less than current port date
        """

        # TODO: SECURITY / COMPETITION: we are exposing our full inventory to the Internet without any authentication,
        # including all airline pay and passenger pay rates.

        # load some inventory ---
        date = (datetime.utcnow()-timedelta(days=5)).date()
        port = "LAX"
        hotel_id = 80654  # Travelodge LAX South
        rooms = 10
        airline_id = 71
        rate_type = {
            "id": "1",
            "label": "PP"
        }

        # create inventory
        block = self.add_hotel_availability(hotel_id, None, date,
                                            blocks=rooms, block_price="123.45", pay_type=rate_type["id"],
                                            issued_by="Justin Trudeau",
                                            comment="passenger pay get airports " + str(uuid.uuid4()))

        block = block["info"]
        self.assertGreater(int(block["inserted_id"]), 0)

        # consume inventory
        response_json = self.book_inventory(port=port, airline_id=airline_id, hotel_id=hotel_id,
                                            rate_type=rate_type["label"], block_id=block["inserted_id"], rooms=rooms,
                                            first_name="Jane", last_name="Doe", agent="Test", flight_no="TBA")
        self.assertEqual(int(response_json["voucherId"]), 0)

        # try to consume inventory again
        EXPECTED_ERROR_JSON = {
            "blockid": "Block has expired and can not be booked"
        }
        self.validate_booking_errors(response_json, EXPECTED_ERROR_JSON)

    def book_inventory(self, port=None, airline_id=None, hotel_id=None, rate_type=None, block_id=None, rooms=None,
                       first_name=None, last_name=None, agent=None, flight_no=None):
        """
        book rooms through PHP API
        param port: string
        param airline_id: int
        param hotel_id: int
        param rate_type: string
        param block_id: int
        param rooms: int
        param first_name: string
        param last_name: string
        param agent: string
        param flight_no: string

        return json
        """

        url = self._php_host + "/api/v1/airports/inventory/block"
        headers = self._generate_stormx_php_headers()

        payload = {
            "blockid": block_id,
            "hotelid": hotel_id,
            "rooms": rooms,
            "airline": airline_id,
            "firstname": first_name,
            "lastname": last_name,
            "agent": agent,
            "ratetype": rate_type,
            "portid": port,
            "flightno": flight_no,
        }

        response = requests.post(url, headers=headers, json=payload)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def validate_booking_errors(self, response_json, expected_error_json):
        """
        verify errors in booking
        param response_json: json
        param expected_error_json: json
        """

        self.assertEqual(int(response_json["voucherId"]), 0)
        self.assertEqual(response_json["error"], expected_error_json)

    def test_finalize_voucher_with_valid_params(self):
        """
        test finalize voucher with invalid first and last name params
        """
        # load some inventory ---
        today = datetime.utcnow().date()
        port = "LAX"
        hotel_id = 80654  # Travelodge LAX South
        rooms = 15
        airline_id = 71
        rate_type = {
            "id": "1",
            "label": "PP"
        }
        paxs = 10

        # create inventory
        block = self.add_hotel_availability(hotel_id, None, today,
                                            blocks=rooms, block_price="123.45", pay_type=rate_type["id"],
                                            issued_by="Justin Trudeau",
                                            comment="passenger pay get airports " + str(uuid.uuid4()))

        block = block["info"]
        self.assertGreater(int(block["inserted_id"]), 0)
        # create voucher
        voucher_response = self.create_quick_voucher(airline_id, hotel_id, 1,
                                               today, rooms, 'test', 1, '123', True, rate_type["id"], self.REASON_PASSENGER_PAY)
        response_json = self.finalize_voucher(voucher_response['voucher']['voucher_id'], rooms, paxs,"John", "Doe")
        self.assertEqual(int(response_json["status"]), 1)
        # # try to consume inventory again
        
    def test_finalize_voucher_invalid_params(self):
        """
        test finalize voucher with invalid first and last name params
        """
        # load some inventory ---
        today = datetime.utcnow().date()
        port = "LAX"
        hotel_id = 80654  # Travelodge LAX South
        rooms = 15
        airline_id = 71
        rate_type = {
            "id": "1",
            "label": "PP"
        }
        paxs = 10

        # create inventory
        block = self.add_hotel_availability(hotel_id, None, today,
                                            blocks=rooms, block_price="123.45", pay_type=rate_type["id"],
                                            issued_by="Justin Trudeau",
                                            comment="passenger pay get airports " + str(uuid.uuid4()))

        block = block["info"]
        self.assertGreater(int(block["inserted_id"]), 0)
        # create voucher
        voucher_response = self.create_quick_voucher(airline_id, hotel_id, 1,
                                               today, rooms, 'test', 1, '123', True, rate_type["id"], self.REASON_PASSENGER_PAY)
        response_json = self.finalize_voucher(voucher_response['voucher']['voucher_id'], rooms, paxs)
        self.assertEqual(int(response_json["status"]), 0)
        # # try to consume inventory again
        EXPECTED_ERROR_JSON = {
            "firstname": "The Firstname field is required",
            "lastname": "The Lastname field is required",
        }
        self.assertEqual(response_json["error"], EXPECTED_ERROR_JSON)

    def finalize_voucher(self, voucher_id=None, rooms=None, paxs=None, first_name=None, last_name=None):
        """
        Finalize voucher through PHP API
        param voucher_id: int
        param rooms: int
        param paxs: int
        param first_name: string
        param last_name: string
        return json
        """

        url = self._php_host + "/api/v1/airports/inventory/finalize"
        headers = self._generate_stormx_php_headers()

        payload = {
            "voucherid": voucher_id,
            "paxs": paxs,
            "rooms": rooms,
            "firstname": first_name,
            "lastname": last_name,
        }

        response = requests.post(url, headers=headers, json=payload)
        self.assertEqual(response.status_code, 200)
        return response.json()

    # TODO: test POST /api/v1/airports/inventory/finalize ; verify endpoint is secure and sane.

    # TODO: test GET /api/v1/airlines/id ; verify endpoint is secure and sane.

    # TODO: test GET /api/v1/hotels ; verify endpoint is secure and sane.

    # TODO: test GET /api/v1/hotels/detail/{id} ; verify endpoint is secure and sane.

    # TODO: test GET /api/v1/hotels/amenities/{id} ; verify endpoint is secure and sane.

    # TODO: test GET /api/v1/hotels/tax ; verify endpoint is secure and sane.

    # TODO: test POST /api/v1/accommodation/test ; verify endpoint is secure and sane.

    # TODO: test POST /api/v1/accommodation/request ; verify endpoint is secure and sane.

    # TODO: test POST /api/v1/accommodation/detail ; verify endpoint is secure and sane.

    # TODO: test POST /api/v1/accommodation/receive_response ; verify endpoint is secure and sane.

    # TODO: test POST /api/v1/accommodation/receive_detail ; verify endpoint is secure and sane.

    # TODO: test POST /api/v1/accommodation/send_response ; verify endpoint is secure and sane.

    # TODO: test POST /api/v1/accommodation/send_preferred_hotels ; verify endpoint is secure and sane.
