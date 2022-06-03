#! /usr/bin/env python3
"""
These are standalone system tests that can be pointed at local or staging servers.

These tests require that a valid server be stood up.
These tests currently require that you manually set up the American Airlines and Delta Air Lines customers as documented in `$StormxAPI/aws/provision_servers.sh`.
These tests currently require that the server also contain reasonable inventory before the tests start.
These tests currently require that the WEX credit card system is funded with plenty of money.
TODO: try to remove/automate some of the above constraints/dependencies.

WARNING: the tests rely on randomness and generating shorter unique numbers, and may occasionally fail.
         Some of the number generators have an extra ~1/100,000,000 or so chance of failing each time a
         test case is run without clearing out the database.


DEVELOPER TIPS:

* when developing system tests, temporarily use the `display_response(response)`
  utility to pretty print a response object.


"""
import sys
import pathlib
STORMX_PACKAGES_DIR = str(pathlib.Path(__file__).resolve().parents[1] / 'Stormx')
sys.path.append(STORMX_PACKAGES_DIR)


import copy
import datetime
import json
import time
import unittest
from itertools import islice

import boto3
import faker
import requests
from pytz import timezone
import uuid
import random
import string

from StormxApp.tests.data_utilities import (
    generate_context_id,
    generate_pax_record_locator,
    generate_pax_record_locator_group,
    MOST_PASSENGERS_IN_LARGEST_AIRCRAFT
)

from stormx_api_client.environments import CUSTOMER_TOKENS, SUPPORTED_ENVIRONMENTS
from stormx_api_client.airline_api_client import AirlineApiClient
from stormx_api_client.sandbox_api_client import SandboxApiClient

from uuid import UUID


REGION_NAME = 'us-west-2'

SHOULD_SKIP_LOCAL_TEST = True  # if overridden do not check in value (used by @should_skip_local_test decorator)

TEMPLATE_DATE = time.strftime('%Y-%m-%d')

DATETIME_FORMAT_FOR_VOUCHERS = '%d/%m/%Y %H:%M'  # TODO: in the future, let's turn this into the standard %Y-%m-%d !
DATETIME_FORMAT_FOR_STORMX = '%m/%d/%Y'  # date format used for STORMX UI
TIME_FORMAT_FOR_VOUCHERS = '%H:%M'

PASSENGER_TEMPLATE = [
    {
        'context_id': '',
        'pax_record_locator': '',
        'pax_record_locator_group': '',
        'pnr_create_date': TEMPLATE_DATE,
        'flight_number': '1111',
        'disrupt_type': 'weather',
        'requester': 'Airline User',  # 'TVL System Test',
        'first_name': 'John',
        'last_name': 'Smith',
        'phone_numbers': ['+13129111111'],
        'emails': ['john.smith@test.travellianceinc.com'],
        'pax_status': 'status',
        'ticket_level': 'first',
        'port_origin': 'ORD',
        'port_accommodation': 'LAX',
        'hotel_accommodation': True,
        'meal_accommodation': True,
        'meals': [
            {
                'meal_amount': '12.00',
                'currency_code': 'USD',
                'number_of_days': 1
            },
            {
                'meal_amount': 10.99,
                'currency_code': 'USD',
                'number_of_days': 1
            }
        ],
        'transport_accommodation': False,
        'life_stage': 'adult',
        'service_pet': False,
        'handicap': False,
        'notify': False,
        'disrupt_depart': TEMPLATE_DATE + ' 18:30',
        'scheduled_depart': TEMPLATE_DATE + ' 19:30',
        'airline_pay': True,
        'number_of_nights': 1,
        'pet': False
    },
    {
        'context_id': '',
        'pax_record_locator': '',
        'pax_record_locator_group': '',
        'pnr_create_date': TEMPLATE_DATE,
        'flight_number': '1111',
        'disrupt_type': 'weather',
        'requester': 'Airline User',  # 'TVL System Test',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'phone_numbers': ['+13129111112'],
        'emails': ['jane.doe@test.travellianceinc.com'],
        'pax_status': 'status',
        'ticket_level': 'first',
        'port_origin': 'ORD',
        'port_accommodation': 'LAX',
        'hotel_accommodation': True,
        'meal_accommodation': True,
        'meals': [
            {
                'meal_amount': 12,
                'currency_code': 'USD',
                'number_of_days': 1
            },
            {
                'meal_amount': '10.99',
                'currency_code': 'USD',
                'number_of_days': 1
            }
        ],
        'transport_accommodation': False,
        'life_stage': 'adult',
        'service_pet': False,
        'handicap': False,
        'notify': False,
        'disrupt_depart': TEMPLATE_DATE + ' 18:30',
        'airline_pay': True,
        'number_of_nights': 1,
        'pet': False
    }
]

ERROR_SYSTEM_TESTS_OUTPUT = 'error_system_tests_output.txt'

passenger_sanitized_fields = ['voucher_id', 'requester', 'pax_status', 'life_stage', 'id']


def uses_expedia(func):
    # TODO: make some kind of auto-skipper setup as needed for expedia tests.
    return func


def random_chunk(fake, li, min_chunk=1, max_chunk=3):
    """
    randomly chunk a list

    reference: https://stackoverflow.com/questions/21439011/best-way-to-split-a-list-into-randomly-sized-chunks
    """
    it = iter(li)
    while True:
        nxt = list(islice(it, fake.random.randint(min_chunk,max_chunk)))
        if nxt:
            yield nxt
        else:
            break


def display_response(response):
    """
    param response -  a response object from the requests library.
    """
    print('- ' * 10)
    print('status code: ', response.status_code)
    print('reason:      ', response.reason)
    print('headers:')
    for key, value in response.headers.items():
        print('  * ' + repr(key) + ': ' + repr(value))
    print('cookies:')
    for key, value in response.cookies.items():
        print('  * ' + repr(key) + ': ' + repr(value))
    print('json:')
    try:
        json_string = json.dumps(response.json(), sort_keys=True, indent=4)
    except:  # TODO: which exception???
        json_string = '<<<INVALID JSON>>>\n' + response.text

    print(json_string)
    print('- ' * 10)
    print()


def pretty_print_json(json_text):
    __resp = json.dumps(json_text, sort_keys=True, indent=4)
    _resp = json.loads(__resp)
    resp = dict()
    resp['meta'] = _resp['meta']
    resp['error'] = _resp['error']
    resp['data'] = _resp['data']

    return json.dumps(resp, indent=4)


def log_error_system_tests_output(json_resp):
    # TODO: optimize constant opening of file
    with open(ERROR_SYSTEM_TESTS_OUTPUT, 'a') as error_output:
        error_output.write(json_resp + '\n\n')


# TODO remove but should not be here but when in setUpClass the file does not save
with open(ERROR_SYSTEM_TESTS_OUTPUT, 'w') as error_output:
    error_output.write('')


class StormxSystemVerification(unittest.TestCase):
    selected_environment_name = None  # NOTE: set in run_system_tests.


    @classmethod
    def setUpClass(cls):

        # stormx php system test setup ----------------------------------------------------
        cls._php_host = SUPPORTED_ENVIRONMENTS[cls.selected_environment_name]['php_host']
        # run a sanity check before diving into all of the tests ----
        url = cls._php_host + '/'
        headers = {}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            display_response(response)
            raise Exception(
                '\n\n\n' + ('*' * 80) + '\n' +
                'ERROR: Test environment is not sane! could not perform a simple PHP access to "/"' +
                'response code & reason: <{0} - {1}>.'.format(response.status_code, response.reason)
            )
        cls._support_cookies = cls.login_to_stormx()  # cookies for the stormx user 'support'

        # stormx api system test setup ------------------------------------------------------
        cls._api_host = SUPPORTED_ENVIRONMENTS[cls.selected_environment_name]['host']
        # run a sanity check before diving into all of the tests ----
        url = cls._api_host + '/api/v1/ping'
        headers = cls._generate_airline_headers(customer='American Airlines')
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            display_response(response)
            raise Exception(
                '\n\n\n' + ('*' * 80) + '\n' +
                'ERROR: Test environment is not sane! ' +
                'could not perform a simple API ping command for American Airlines. ' +
                'response code & reason: <{0} - {1}>.'.format(response.status_code, response.reason)
            )
        cls._passenger_faker = faker.Faker()

        # stormx api system test setup ------------------------------------------------------
        cls._sandbox_api_client = SandboxApiClient(cls._api_host)

    @classmethod
    def get_airline_api_client(cls, customer):
        """
        customer - string
        return AirlineApiClient
        """
        token = CUSTOMER_TOKENS[customer]
        return AirlineApiClient(host=cls._api_host, customer_token=token)

    @classmethod
    def login_user_to_stormx(cls, username='support', password='test'):
        """
        param username: string
        param password: string
        :return: response object from php endpoint`.
        """
        url = cls._php_host + "/admin/index.php"

        form_data = {
            'cPwd': '',
            'continue': 'admin/vouchers.php',
            'email': '',
            'mode': 'login',
            'nPwd': '',
            'pex': '',
            'rPwd': '',
            'token': '',
            'uID': username,
            'uPwd': password,
        }

        headers = {
            'accept': "*/*",
            'user-agent': "stormx_system_test",
            'content-type': "application/x-www-form-urlencoded",
        }

        return requests.post(url, data=form_data, headers=headers)

    @classmethod
    def login_to_stormx(cls, username='support', password='test', resetpassword='aTest!23', verbose_logging=False):
        """
        param username: string
        param password: string
        param resetpassword: string
        verbose_logging: bool
        :return: a the cookies to use the session. stores this value and pass to
                 the `requests` library like `requests.XXX(cookies=MY_COOKIES)`.
        """
        response = cls.login_user_to_stormx(username, password)

        if response.status_code != 200:
            if verbose_logging:
                display_response(response)
            raise Exception('login issue: unexpected status code: ' + repr(response.status_code))
        elif 'Incorrect Username or Password' in response.text:
            if verbose_logging:
                display_response(response)
            raise Exception('login issue: incorrect username or password')
        elif 'Please change it before you log in.' in response.text or \
                "Please change your password before you log in" in response.text:
            # reset password
            url = cls._php_host + "/admin/index.php"
            form_data = {
                'cPwd': resetpassword,
                'continue': 'admin/vouchers.php',
                'email': '',
                'mode': 'login',
                'nPwd': resetpassword,
                'pex': '',
                'rPwd': '',
                'token': '',
                'uID': username,
                'uPwd': password,
            }

            headers = {
                'accept': "*/*",
                'user-agent': "stormx_system_test",
                'content-type': "application/x-www-form-urlencoded",
            }
            response = requests.post(url, data=form_data, headers=headers)
            if response.status_code == 200 and 'Please wait redirecting...' in response.text:
                pass  # successful password reset
            else:
                if verbose_logging:
                    display_response(response)
                raise Exception('login issue: failed to reset password.')
        elif 'Please wait redirecting...' in response.text:
            pass  # successful login
        else:
            if verbose_logging:
                display_response(response)
            raise Exception('login issue: unexpected response.')

        session_cookies = response.cookies
        return session_cookies


    @staticmethod
    def _generate_airline_headers(customer='American Airlines'):
        """
        for API.
        """
        try:
            token = CUSTOMER_TOKENS[customer]
        except KeyError:
            raise Exception('test setup problem: Need token for this customer.')
        headers = {
            'Authorization': 'Basic ' + token,
            'User-Agent': 'stormx_system_test',
        }
        return headers

    @staticmethod
    def _generate_passenger_headers():
        """
        for API.
        """
        return {
            'User-Agent': 'stormx_system_test',
        }

    @staticmethod
    def _generate_stormx_php_headers():
        """
        for PHP.
        :return: dict
        """
        return {
            'User-Agent': 'stormx_system_test',
        }

    @staticmethod
    def _generate_tvl_stormx_headers():
        """
        for StormX to StormX API communication.
        return: dict
        """
        return {
            'Authorization': 'Token ' + CUSTOMER_TOKENS['StormX']
        }

    @staticmethod
    def _generate_tvl_stormx_headers_bad():
        """
        for StormX to StormX API communication bad header test
        return: dict
        """
        return {
            'Authorization': 'Token ' + 'aadhY2M0Y2YzMjUyYWUzNmIyYjE0OGFjNWNlMWI3NTRmY2ViNWY0ZmE1YzdiNWZmMWFlYWEzN2E0'
        }

    @staticmethod
    def _generate_tvl_stormx_user_headers(user_id):
        """
        for StormX to StormX API communication.
        param user_id: string
        return: dict
        """
        return {
            'Authorization': 'Token ' + CUSTOMER_TOKENS['StormX'],
            'X-Stormx-User-ID': user_id
        }

    @staticmethod
    def _generate_tvl_stormx_user_headers_bad(user_id):
        """
        for StormX to StormX API communication bad header test
        param user_id: string
        return: dict
        """
        return {
            'Authorization': 'Token ' + 'aadhY2M0Y2YzMjUyYWUzNmIyYjE0OGFjNWNlMWI3NTRmY2ViNWY0ZmE1YzdiNWZmMWFlYWEzN2E0',
            'X-Stormx-User-ID': user_id
        }

    @classmethod
    def get_object(cls, model_name, fields=None, **filter):
        return cls._sandbox_api_client.get_object(model_name, fields=fields, **filter)

    @classmethod
    def get_object_field(cls, model_name, field, **filter):
        return cls._sandbox_api_client.get_object_field(model_name, field, **filter)

    @classmethod
    def get_objects(cls, model_name, fields=None, limit=None, **filter):
        return cls._sandbox_api_client.get_objects(model_name, fields=fields, limit=limit, **filter)

    @classmethod
    def get_port_timezone_by_iata_code(cls, port_iata_code):
        return cls._sandbox_api_client.get_port_timezone(port_iata_code)

    def get_hotel_availability(self, hotel_id, availability_date=None):
        """
        Get hotel availability for a given date using the PHP admin site.

        :param hotel_id:  integer
        :param availability_date: None, `date` object, or string in form 'yyyy-mm-dd' (None means default date - today)
        :return:
        """
        # TODO: I followed the PHP code that this method calls and it does not return current availability.
        # TODO: It queries the hotel_availability_history table.
        # TODO: It does not return the correct ap_block count after creating a voucher and searching for the block.

        url = self._php_host + '/admin/hotels.php'
        query_parameters = {
            'type': 'availsHistory',
            'id': str(hotel_id)
        }
        if availability_date:
            query_parameters['date'] = str(availability_date)
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=self._support_cookies, params=query_parameters)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIsInstance(response_json, list)
        return response_json

    def add_hotel_availability(self, hotel_id, airline_id, availability_date,
                               blocks=0, block_price='0',
                               ap_block_type=0,
                               issued_by='Theresa May',
                               comment='bla bla bla, bla bla bla bla.',
                               room_type=1, pay_type='0',
                               verify_response_success=True,
                               hotel_contract_block_id=0,
                               hotel_soft_block_id=0):

        """
        Add hotel availability using PHP admin site.

        :param hotel_id:  integer
        :param availability_date: `date` object

        :return:
        """
        response = self.create_hotel_availability(hotel_id, airline_id, availability_date,
                                                  blocks, block_price, ap_block_type,
                                                  issued_by, comment, room_type, pay_type,
                                                  verify_response_success, hotel_contract_block_id, hotel_soft_block_id)
        response_json = response.json()
        if verify_response_success:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json['success'], '1')
        return response_json

    def create_hotel_availability(self, hotel_id, airline_id, availability_date,
                                  blocks=0, block_price='0',
                                  ap_block_type=0,
                                  issued_by='Theresa May',
                                  comment='bla bla bla, bla bla bla bla.',
                                  room_type=1, pay_type=0,
                                  verify_response_success=True, hotel_contract_block_id=0, hotel_soft_block_id=0):

        url = self._php_host + '/admin/remote/helper.php?type=updateAvailsNew'
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'id': str(hotel_id),
            'type': 'add',
            'blocks': str(blocks),
            'block_price': str(block_price),
            'block_expiration_date': str(availability_date),
            'airline_id': str(airline_id) if airline_id else '0',
            'year_no': str(availability_date.year),
            'month_no': str(availability_date.month).zfill(2),
            'day_no': str(availability_date.day).zfill(2),
            'issued_by': str(issued_by),
            'position': 'Front Desk Agent',
            'comment': str(comment),
            'ap_block_type': ap_block_type,
            'room_type': room_type,
            'pay_type':pay_type,
            'hotel_contract_block_id' : hotel_contract_block_id,
            'hotel_soft_block_id' : hotel_soft_block_id
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        return response

    def _load_queue_resource(self, testing_environment_queue_name):
        queue_info = SUPPORTED_ENVIRONMENTS[self.selected_environment_name][testing_environment_queue_name]
        if not queue_info:
            raise unittest.SkipTest('queue ' + repr(testing_environment_queue_name) +  ' not available for test')

        session = boto3.Session(
            aws_access_key_id=queue_info['user'],
            aws_secret_access_key=queue_info['secret'],
        )
        sqs = session.resource('sqs', region_name=REGION_NAME)
        queue = sqs.get_queue_by_name(QueueName=queue_info['name'])
        return (sqs, queue)

    def read_messages_from_customer_queue(self, testing_environment_queue_name, wait_time_in_seconds=1, max_number_of_messages=10):
        '''
        testing_environment_queue_name - can be 'purple_rain_airline_queue' or 'purple_rain_transaction_queue'.

        returns a list of dictionaries, where each dictionary is a message.

        NOTE: a calling test will automatically be skipped if the queue information
              is not available for the environment under test.
        '''
        sqs, queue = self._load_queue_resource(testing_environment_queue_name)

        json_messages = []
        for message in queue.receive_messages(WaitTimeSeconds=1, MaxNumberOfMessages=10):
            # convert message body from string into python dictionary structure
            data = json.loads(message.body)
            json_messages.append(data)
            # Let the queue know that the message is processed
            message.delete()

        # attempt to close the connection forcefully to keep this method self-contained (but slower as a side effect)
        # https://stackoverflow.com/questions/33461877/botocore-how-to-close-or-clean-up-a-session-or-client
        sqs.meta.client._endpoint.http_session.close()  # closing a boto3 resource

        return json_messages

    # def purge_customer_queue(self, testing_environment_queue_name, wait_time_in_seconds=1, max_number_of_messages=10):
    #     '''
    #     testing_environment_queue_name - can be 'purple_rain_airline_queue' or 'purple_rain_transaction_queue'.
    #
    #     WARNING: can only be called once every 60 seconds. Use sparingly! slows down tests...
    #
    #     NOTE: a calling test will automatically be skipped if the queue information
    #           is not available for the environment under test.
    #     '''
    #     sqs, queue = self._load_queue_resource(testing_environment_queue_name)
    #     print('sleeping 61 seconds to ensure purge queue is allowed....')
    #     time.sleep(61)
    #     queue.purge()
    #
    #     # attempt to close the connection forcefully to keep this method self-contained (but slower as a side effect)
    #     # https://stackoverflow.com/questions/33461877/botocore-how-to-close-or-clean-up-a-session-or-client
    #     sqs.meta.client._endpoint.http_session.close()  # closing a boto3 resource

    def create_quick_voucher(self, airline_id, hotel_id, airport_id, voucher_date,
                             number_of_rooms, passenger_names, number_of_nights,
                             flight_number,
                             verify_response_success=True,room_type=1, voucher_disruption_reason='12'):

        """
        TODO: currently this test exposes some of the problems with
        the quick voucher submission process. But it still documents
        the currently expected inputs and outputs. In the future,
        this this test should verify the minmal input to create
        a GOOD voucher instead of a DEGENERATE voucher... But before
        we do that, let's start validating some inputs to break this
        test, then update the test to submit the additional fields that
        the backend requires. see also `test_quick_voucher__submit_minimal_inputs()`

        NOTE: this test is subitting fewer fields than the UI calls the backend.
        """
        url = self._php_host + '/admin/remote/voucher.php?type=saveVoucherNew'
        headers = self._generate_stormx_php_headers()
        # headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        # headers['Accept-Language'] = 'en-US,en;q=0.9'

        airline_id = int(airline_id)
        hotel_id = int(hotel_id)
        number_of_rooms = int(number_of_rooms)
        airport_id = int(airport_id)

        # TODO: split apart the different airport ids, airline ids, etc. so that they can be different for testing.
        #       redundant data inputs means more required test case combinations (where redundant data is not equal)!
        form_data = {
            # NOTE: below many fields are commented out. This is the set of data that is submitted upon quick voucher.
            #       but I am commenting out data which doesn't appear to affect functionality, or at least we don't have
            #       good enough tests to verify issues.
            'voucher_id': '',
            'voucher_code': '',
            'voucher_disruption_date': voucher_date.strftime(DATETIME_FORMAT_FOR_VOUCHERS),
            'voucher_requesting_port': str(airport_id),
            # 'voucher_airline_auth_user': 'soft block',
            'voucher_disruption_reason': voucher_disruption_reason,
            'voucher_invoice_airline': str(airline_id),
            'voucher_departure_port': str(airport_id),
            'voucher_departure_airline': str(airline_id),
            # 'voucher_departure_flight': 'TVL',
            # 'voucher_departure_terminal': 'D',
            'voucher_departure_date': (voucher_date + datetime.timedelta(days=1)).strftime(DATETIME_FORMAT_FOR_VOUCHERS),  # TODO: make different date.
            # 'voucher_departure_time': '15:01',  # TODO: unhardcode?
            'hotel_id': str(hotel_id),
            'voucher_currency': 'USD',
            # 'transport_to_hotel': '80087',  # TODO what is this????
            # 'transport_from_hotel': '80087',  # TODO what is this????
            # 'transport_from_hotel_departure': '1.5',
            'voucher_disruption_port': str(airport_id),
            'voucher_disruption_airline': str(airline_id),
            'voucher_disruption_flight': flight_number,
            'voucher_pax_total': str(len(passenger_names)),
            'voucher_hotel_nights': str(number_of_nights),
            'voucher_room_total': str(number_of_rooms),
            # 'voucher_room_rate': '104',
            'voucher_room_type': str(room_type),
            'voucher_hotel_eta': voucher_date.strftime(TIME_FORMAT_FOR_VOUCHERS) ,
            # 'voucher_disruption_flight_type': 'D',
            # 'voucher_fasttrack_natwide_email': 'AR@tvlinc.com',
            'hotel_payment_type': 'G', # TODO: this does not appear to be validated, but looks important. Is this important?
            # 'transportIn_payment_type': 'A',
            # 'transportOut_payment_type': 'A',
            # 'passenger_phone': '',
            # 'passenger_email': '',
            # 'passenger_level': '',
            # 'life_stage': '',
            # 'hotel_availability_id': str(hotel_availability_id),
            # 'final_tax_per_rate': '0',
            # 'voucherTotalRate': '',
            # 'totals': '',
            'voucher_cutoff_time': voucher_date.strftime(DATETIME_FORMAT_FOR_VOUCHERS),  # TODO: revisit. maybe add a day?
            # 'isVoucherDetailLoaded': 'false',
            # 'isToCheckRevisioned': 'false',
            # 'isPassengerVoucher': 'false',
            # 'isManifestPaxInformationReloaded': 'false',
            # 'allowances_class': 'E',
            # 'allowances_phone': '0',
            'paxs_rooms': '[1,1]',  # TODO: What does this mean ?????
            'paxs_count': '[1,1]',  # TODO: What does this mean ?????
            'paxs_name': json.dumps(passenger_names),
            # 'paxs_id': '[""]',
            # 'paxs_no_show': '["0"]',
            # 'paxs_business_unit': '[""]',
            # 'paxs_cost_code': '[""]',
            # 'paxs_pickup_date': '[""]',
            # 'paxs_return_date': '[""]',
            # 'paxs_pnr': '[""]',
            # 'paxs_name_focus': '[null]',
            # 'roomRates_count': '[""]',
            # 'roomRates_rates': '[[""]]',
            # 'flightInfo': '{"code":"","number":"","airlines":"","airports":"","equipments":"","flights":"","errMsg":"The flight status information is unavailable for this flight number."}',
            # 'sendEmail_hotel[0]': 'carlos.argueta@brightonmgt.com',
            'isEditable': 'true',
            # 'isCancelled': 'false',
            # 'voucher_disruption_date_prev': '13/01/2018 15:01',
            # 'isAllowancesAllowed': 'true',
            # 'isMealAllowed': 'true',
            # 'isAmenityAllowed': 'true',
            # 'isPhoneAllowed': 'true',
            # 'totalAllowances': '0.00',
            # 'flight_prefix': 'TVL',
            # 'allow_depart_port': 'true',
            # 'allow_depart_airline': 'true',
            # 'allow_depart_flight': 'true',
            # 'allow_depart_ftype': 'true',
            # 'allow_trans_to': 'true',
            # 'allow_trans_from': 'true',
            # 'allow_leaving': 'true',
            # 'isVarious': 'false',
            # 'totalRates': '0',
            # 'totalRoomsCharge': '113.05',
            # 'totalRoomsChargeDetail': '1 x 1 x 104 USD = 113.05 USD',
            'totalPax': str(len(passenger_names)),  # TODO: verify this is okay
            'totalRooms': str(number_of_rooms),
            # 'quick_voucher_requesting_port': str(airport_id),
            # 'hotel_payment_type_prev': 'G',
            # 'voucher_room_rate_prev': '104',
            # 'voucher_commission': '10.40',
            # 'TaxString': '(104 + 9.05 ) = 113.05',  # TODO: we should stop submitting this. This is a bad design to rely on the frontend to supply the backend with computed data that the backend should be able to compute.  It also make setting up the test really hard (you need a full Selenium test running Javascript, etc).
            'mode': 'saveCont',
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        #print('response.text=', response.text)
        response_json = response.json()
        if verify_response_success:
            if not (response.status_code == 200 and response_json.get('success') == '1'):
                display_response(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json['success'], '1')
        return response_json

    def create_full_voucher(self, airline_id, hotel_id, airport_id, voucher_date,
                             number_of_rooms,passenger_names, number_of_nights,
                             flight_number,multi_night_availability, room_type=1):

        """
        long voucher creation with multi-night booking
        with minimum input at this point
        it will only create voucher would not finalize it


        """
        url = self._php_host + '/admin/remote/voucher.php?type=saveVoucherNew'
        headers = self._generate_stormx_php_headers()
        # headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        # headers['Accept-Language'] = 'en-US,en;q=0.9'

        airline_id = int(airline_id)
        hotel_id = int(hotel_id)
        number_of_rooms = int(number_of_rooms)
        airport_id = int(airport_id)

        form_data = {

            'voucher_id': '',
            'voucher_code': '',
            'voucher_disruption_date': voucher_date.strftime(DATETIME_FORMAT_FOR_VOUCHERS),
            'voucher_requesting_port': str(airport_id),
            'voucher_disruption_reason': '1',  # missed connection.
            'voucher_airline_auth_user': 'tests',
            'voucher_invoice_airline': str(airline_id),
            'voucher_departure_port': str(airport_id),
            'voucher_departure_airline': str(airline_id),
            'voucher_departure_date': (voucher_date + datetime.timedelta(days=number_of_nights)).strftime(
                DATETIME_FORMAT_FOR_VOUCHERS),
            'hotel_id': str(hotel_id),
            'voucher_currency': 'USD',
            'voucher_disruption_port': str(airport_id),
            'voucher_disruption_airline': str(airline_id),
            'voucher_disruption_flight': flight_number,
            'voucher_pax_total': str(len(passenger_names)),
            'voucher_hotel_nights': str(number_of_nights),
            'voucher_room_total': str(number_of_rooms),
            'voucher_room_type': str(room_type),
            'voucher_hotel_eta': voucher_date.strftime(TIME_FORMAT_FOR_VOUCHERS),
            'hotel_payment_type': 'G',
            'voucher_cutoff_time': voucher_date.strftime(DATETIME_FORMAT_FOR_VOUCHERS),
            'paxs_rooms': '[1,1]',  # TODO: What does this mean ?????
            'paxs_count': '[1,1]',  # TODO: What does this mean ?????
            'paxs_name': json.dumps(passenger_names),
            'isEditable': 'true',
            'totalPax': str(len(passenger_names)),  # TODO: verify this is okay
            'totalRooms': str(number_of_rooms),
            'multiNightRates': json.dumps(multi_night_availability),
            'mode': 'saveCont',
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        # display_response(response)
        response_json = response.json()
        return response_json


    def _multi_night_availability(self,hotel_availability,voucher_date,nights,number_of_rooms):
        """
        get availability of first night and create for rest of nights

        :param hotel_availability: dict
        :param voucher_date: string
        :param nights: int
        :param number_of_rooms: int
        :return: dict of multi-night availability
        """

        data =[{"date": voucher_date.strftime(DATETIME_FORMAT_FOR_STORMX),
                "availability": [{"hotel_availability_id": hotel_availability['hotel_availability_id'], "ap_block_type":  hotel_availability['ap_block_type'],
                        "price": hotel_availability['block_price'], "total_room_block": hotel_availability['blocks']}]}]

        for night in range(1,nights):
            data+=[{"date": (voucher_date + datetime.timedelta(days=night)).strftime(
                DATETIME_FORMAT_FOR_STORMX),"availability": [{"ap_block_type": 0,
                                                              "price": hotel_availability['block_price'],
                                                              "total_room_block": number_of_rooms}]}]

        return  data


    # TODO: write utility create_room_count_voucher() to create Room Count Vouchers
    # TODO: write utility/utilities to modify Room Count Report fields that user manually fills in.

    def _extract_embedded_app_vdata(self, response):
        """
        return the embedded JSON for `app.vData` which is set in a PHP page.
        """
        # it would be better to use BeautifulSoup to parse the HTML, but I am trying to limit system test dependencies for now.
        FIND_BEGIN = 'app.vData = '
        FIND_END = '</script>'

        begin_location = response.text.find(FIND_BEGIN)
        if begin_location != -1:
            begin_location = begin_location + len(FIND_BEGIN)
            end_location = response.text.find(FIND_END, begin_location)
            if end_location != -1:
                multiline_string = response.text[begin_location:end_location]
                first_line = multiline_string.split('\n')[0].strip()
                self.assertEqual(first_line[-1], ';')
                first_line = first_line[:-1]  # remove semicolon
                deserialized_object = json.loads(first_line)
                return deserialized_object
        raise Exception('could not find and load the app.vData.')

    def add_port_allowance(self, port_id, airline_id,allowance,port_room_allowance_id=0, type='save_allowance',cookies=None):

        """
        Add/Update port allowance using PHP admin site.

        :param port_id: integer
        :param airline_id: integer
        :param allowance: integer
        :param port_room_allowance_id: integer (i.e in case of edit)
        :return:
        """

        if cookies is None:
            cookies = self._support_cookies

        form_data = {
            'port_id': port_id,
            'airline_id': airline_id,
            'allowance': allowance
        }
        if port_room_allowance_id > 0:
            form_data['id'] = port_room_allowance_id

        url = self._php_host + '/admin/port_allowance.php?type={type}'.format(type=type)
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        response = requests.post(url, headers=headers, cookies=cookies, data=form_data)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json


    def add_temporary_port_allowance(self,port_room_allowance_id,allowance,cookies=None):

        """
        Add temporary port allowance using PHP admin site.
        :param allowance: integer
        :param port_room_allowance_id: integer
        :return:
        """
        if cookies is None:
            cookies = self._support_cookies
        form_data = {
            'port_room_allowance_id': port_room_allowance_id,
            'allowance': allowance
        }

        url = self._php_host + '/admin/port_allowance.php?type=save_temporary_allowance'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        response = requests.post(url, headers=headers, cookies=cookies, data=form_data)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json
    def list_port_allowance(self,page,port,airline,sortBy,perPage, type= 'search',cookies=None):
        """
        Search/List port allowance using PHP admin site.
        :param type: string
        :param page: integer
        :param port: integer (i.e in case of search)
        :param airline: integer (i.e in case of search)
        :param sortBy: integer
        :param perPage: integer
        :return:
        """

        if cookies is None:
            cookies = self._support_cookies
        query_parameters = {
            'type': type,
            'page': page,
            'port': port,
            'airline': airline,
            'sortBy': sortBy,
            'perPage': perPage
        }
        url = self._php_host + '/admin/port_allowance.php?type=search'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json

    def delete_port_allowance(self, allowance_id):

        """
        Delete port allowance using PHP admin site.
        :param allowance_id: integer
        :return:
        """
        post_data = {
            'id': allowance_id
        }
        url = self._php_host + '/admin/port_allowance.php?type=delete'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=post_data)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json

    def get_view_voucher_data(self, voucher_id):
        voucher_id = int(voucher_id)

        url = self._php_host + '/admin/app/templates/voucher_new.php?vid={voucher_id}'.format(voucher_id=voucher_id)
        headers = self._generate_stormx_php_headers()
        # headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        # headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.post(url, headers=headers, cookies=self._support_cookies)
        self.assertEqual(response.status_code, 200)

        return self._extract_embedded_app_vdata(response)['voucher']

    def get_voucher_data(self, voucher_id):
        voucher_id = int(voucher_id)

        url = self._php_host + '/admin/remote/helper.php?type=loadVoucher&id={voucher_id}'.format(voucher_id=voucher_id)
        headers = self._generate_stormx_php_headers()
        # headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        # headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.post(url, headers=headers, cookies=self._support_cookies)
        self.assertEqual(response.status_code, 200)

        return response.json()['result']

    def get_all_ports(self,query,include_name_in_label='0',user_specific_port_only='0',cookies=None):
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/helper.php'
        query_parameters = {
            'type': 'queryPortsByNameOrPrefix',
            'query': query,
            'include_name_in_label':include_name_in_label,
            'user_specific_port_only': user_specific_port_only

        }

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        #self.assertIsInstance(response_json, dict)
        return response

    def get_all_airlines(self,cookies=None):
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/voucher.php'
        query_parameters = {
            'type': 'airlines'

        }

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIsInstance(response_json, dict)
        return response

    def get_port_hotels_inventory(self,port_id,airline_id,room_type_id,cookies=None):
        """
        :param port_id: integer
        :param airline_id: integer
        :param room_type_id: integer
        :return:
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/helper.php'
        query_parameters = {
            'type': 'loadPortHotelWithPriceAndAvail',
            'pid': port_id,
            'airline_id': airline_id,
            'room_type_id': room_type_id

        }

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIsInstance(response_json, list)
        return response

    def get_hotel_usage_history(self,port_id,airline_id,cookies=None):
        """
        :param port_id: integer
        :param airline_id: integer
        :return:
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/voucher.php'
        query_parameters = {
            'type': 'getBookingHistory',
            'pid': port_id,
            'airline_id': airline_id

        }

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json



    def create_quick_room_transfer_voucher(self, form_data,cookies=None):

        """
        :param form_data: dict
        sample dict: {
                      "extension": "029",
                      "contact_phone": "+16015555555",
                      "comment": "test",
                      "price_list": [
                        {
                          "hotel_availability_id": "1",
                          "ap_block_type": "0",
                          "price": "0.00",
                          "ap_block": "84",
                          "total_room_block": "84",
                          "start_date": "2018-06-22",
                          "end_date": "2018-06-22",
                          "price_id": "1",
                          "room_type_id": "1",
                          "room_label": "ROH",
                          "note": "",
                          "priceTax": "0.00",
                          "hotel_merged_avails": "84",
                          "hotel_id": "93055",
                          "need": 21
                        },
                        {
                          "hotel_availability_id": "2,3",
                          "ap_block_type": "0",
                          "price": "322.00",
                          "ap_block": "10",
                          "total_room_block": 1222,
                          "start_date": "2018-06-22",
                          "end_date": "2018-06-22",
                          "price_id": "1",
                          "room_type_id": "1",
                          "room_label": "ROH",
                          "note": "",
                          "priceTax": "38.64",
                          "hotel_merged_avails": "10,1212",
                          "hotel_id": "93055",
                          "need": 123
                        }

                      ]
                    }
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/voucher.php?type=saveQuickVoucher'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'


        form_data = json.dumps(form_data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data={'data': form_data})
        response_json = response.json()
        if response_json and response_json.get('success') == True:
            self.assertEqual(response.status_code, 200)
        return response_json
    # TODO: implement a drain_hotel_inventory() utility to make testing certain test scenarios easier.

    @staticmethod
    def find_hotel_availability_block_by_comment(hotel_availability_block_list, comment):
        for hotel_availability_block in hotel_availability_block_list:
            if hotel_availability_block['comment'] == comment:
                return hotel_availability_block
        raise KeyError('could not find hotel availability block with comment ' + repr(comment))

    @staticmethod
    def find_hotel_availability_block_by_inventory_date(hotel_availability_block_list, inventory_date, airline_id=None,no_airline_room_blocks = None):
        room_avails = 0
        room_avail_ids = []
        for hotel_availability_block in hotel_availability_block_list:
            if str(hotel_availability_block['block_date'].strip()) == str(inventory_date.strftime('%d/%m/%Y')):
                if airline_id is None:
                    if int(hotel_availability_block['airline_id']) == 0:
                        no_airline_room_blocks.append(int(hotel_availability_block['hotel_availability_id']))
                else:
                    room_avails += int(hotel_availability_block['blocks'])
        if airline_id is None:
            return no_airline_room_blocks
        else:
            return int(room_avails)
        raise KeyError('could not find hotel availability blocks on this date ' + repr(inventory_date))

    @staticmethod
    def get_random_string(len):
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(len)])

    @classmethod
    def get_create_user_post_data(cls,port_id,role,is_invalid):
        fake = faker.Faker()
        if is_invalid == True:
            name = cls.get_random_string(100)
            username = name
            password = fake.password(length=80)
        else:
            name = cls.get_random_string(8)
            username = name
            password = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)
        return {
            'type': 'userSave',
            'edit': 1,
            'delete': 1,
            'user_id': username,
            'user_id_': password,
            'ports[0]': port_id,
            'role': role,
            'name': name,
            'email': fake.email(),
            'port_id': ''
        }

    def create_user_by_type(self, record_id, port_id, role_id, type, is_invalid=False):
        """
        Create user with valid data
        """

        user_form_data = self.get_create_user_post_data(port_id, role_id, is_invalid)

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        if type == 'airline':
            url = self._php_host + '/admin/airline_detail.php?airlineId=' + str(record_id) + '&type=saveUsers'
        else:
            url = self._php_host + '/admin/hotel_detail.php?hotelId=' + str(record_id) + '&type=saveUsers'
        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=user_form_data)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        response_json['request'] = user_form_data
        return response_json

    @classmethod
    def create_airline_users_with_different_roles(cls,port_id,airline_id):
        url = cls._php_host + '/admin/airline_detail.php?airlineId='+str(airline_id)+'&type=saveServicedPorts'
        fake = faker.Faker()

        form_data = {
            'type': 'add',
            'id': port_id
        }
        headers = cls._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        requests.post(url, headers=headers, cookies=cls._support_cookies, data=form_data)
        user_list = []
        url = cls._php_host + '/admin/airline_detail.php?airlineId=' + str(airline_id) + '&type=saveUsers'
        for i in range(11, 15):
            user_form_data = cls.get_create_user_post_data(port_id=port_id, role=i,is_invalid=False)
            response = requests.post(url, headers=headers, cookies=cls._support_cookies, data=user_form_data)
            if response.status_code== 200 and "There is an error while saving user." not in response.text:
                response_json = response.json()
                user_id = response_json['id']
                if int(user_id) > 0:
                    #Update fresh user password before login
                    user_form_data['id'] = user_id
                    user_form_data['airline_id'] = airline_id
                    user_form_data['user_id_'] = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)
                    user_form_data['edit'] = True
                    user_form_data['delete'] = True
                    user_form_data['access'] = 10
                    user_form_data['updated_by_user'] = 'support'
                    response = requests.post(url, headers=headers, cookies=cls._support_cookies, data=user_form_data)
                    if response.status_code == 200:
                        try:
                            user_list.append({'username': user_form_data.get('user_id'),'role_id': i,
                                              'cookies': cls.login_to_stormx(user_form_data.get('user_id'),
                                                                              user_form_data.get('user_id_'))})
                        except:
                            pass

        return user_list

    @classmethod
    def delete_hotel_user(cls, hotel_id, user_id):
        """
        Create user with valid data
        """

        user_form_data = {'id': user_id, 'type': 'userRemove'}

        headers = cls._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        url = cls._php_host + '/admin/hotel_detail.php?hotelId=' + str(hotel_id) + '&type=saveUsers'

        response = requests.post(url, headers=headers, cookies=cls._support_cookies, data=user_form_data)
        return True if response.status_code is 200 else False

    @classmethod
    def create_new_tva_user(cls, role="Operator", group_id=3, is_active=True):
        url = cls._php_host + '/admin/user_detail.php?type=saveRec'
        fake = faker.Faker()
        name = fake.name()
        username = uuid.uuid4().hex[:12]
        password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        user_data = {
            'user_id': 0,
            'username': username,
            'email': uuid.uuid4().hex + '@tvlinc.blackhole',
            'user_sname': name,
            'user_role': role,
            'is_active': 1 if is_active else 0,
            'supplier_id': 0,
            'group_id': group_id,
            'rid': 0,
            'id[group]': group_id,
            'label[group]': 'Limited access',
            'isSeniorManager': False,
            'newUserP': password,
            'newUserPCnf': password,
        }
        response = requests.post(url, headers=cls._generate_stormx_php_headers(), cookies=cls._support_cookies,
                                 data=user_data)
        response_data = response.json()
        user_data['user_id'] = response_data['data']['id']
        user_data['CREATION_RESPONSE'] = response_data
        return user_data

    @classmethod
    def delete_tva_user(cls, user_id):
        url = cls._php_host + '/admin/user_detail.php?type=delete'
        data = {
            'user_id': user_id,
        }
        requests.post(url, headers=cls._generate_stormx_php_headers(), cookies=cls._support_cookies,
                                 data=data)

    def logout(self,redirect = "&continue=admin/quick-room-transfer.php"):
        url = self._php_host + '/admin/index.php?logout=true'+str(redirect)
        query_parameters = {

        }
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        response = requests.get(url, headers=headers, cookies=self._support_cookies, params=query_parameters)
        self.assertEqual(response.status_code, 200)

    def _get_event_date(self, time_zone_region=None, port_iata_code=None):
        """
        helper method to determine which day test needs to add inventory (by timezone region or by port iata code)
        param time_zone_region: string
        param port: string -- port IATA code (three letters)
        return: date
        """
        if not time_zone_region:
            if not port_iata_code:
                raise Exception('must provide time_zone_region or port!')
            time_zone_region = self.get_object_field('PortMaster', 'port_timezone', port_prefix=port_iata_code)

        tz = timezone(time_zone_region)
        tz_now = datetime.datetime.now(tz)

        if tz_now.hour < 5:  # force inventory for previous day
            event_date = (tz_now - datetime.timedelta(days=1)).date()
        else:
            event_date = tz_now.date()

        return event_date

    @staticmethod
    def _calculate_event_datetime(time_zone_region):
        """
        :param time_zone_region: str, example: America/Los_Angeles
        :return: datetime
        """
        tz = timezone(time_zone_region)
        tz_now = datetime.datetime.now(tz)

        if tz_now.hour < 5:  # force inventory for previous day
            event_date = tz_now - datetime.timedelta(days=1)
        else:
            event_date = tz_now

        return event_date

    @staticmethod
    def _get_event_date_time(time_zone_region, event_date):
        """
        helper method to determine of what date time voucher creation would be.
        param time_zone_region: string
        event_date: datetime
        return: date time
        """
        tz = timezone(time_zone_region)
        tz_now = datetime.datetime.now(tz)

        if tz_now.hour < 5:  # set datetime to 23:45 of previous day
            event_date = event_date - datetime.timedelta(days=1)
            event_date = event_date.replace(hour=23, minute=45)

        return event_date

    @staticmethod
    def _is_event_date_yesterday(time_zone_region):
        """
        helper method to determine which day test needs to add inventory
        param time_zone_region: string
        return: date
        """
        tz = timezone(time_zone_region)
        tz_now = datetime.datetime.now(tz)

        return tz_now.hour < 5

    @staticmethod
    def _get_timezone_now(time_zone_region):
        """
        helper method to get time zone based now datetime
        param time_zone_region: string
        return: date
        """
        tz = timezone(time_zone_region)
        tz_now = datetime.datetime.now(tz)
        return tz_now

    def flush_stormx_internal_queue_now(self):
        # NOTE: this method could still prove unreliable if another process
        #       has already grabbed the messages and they are still pending processing.

        url = self._api_host + '/api/v1/tvl/control/flush-internal-queue'
        stormx_headers = self._generate_tvl_stormx_headers()
        response = requests.post(url, headers=stormx_headers)
        if response.status_code != 200:
            display_response(response)
            raise Exception('unexpected response when flushing queue: ' + str(response.status_code))

        if response.json()['error']:
            raise Exception('failed to flush internal queue. giving up on continuing test.')

    def add_edit_amenity(self, amenity_name="", amenity_id="0", is_available="0", operating_hours_allowed = "1",
                        fee_allowed = "1", show_icon_on_hotel_listing="0", icon=""):
        """
        create amenity configuration
        :param amenity_name: string
        :param amenity_id: string
        :param is_available: string
        :return: dict
        """
        url = self._php_host + '/api/v1/ui/amenities'
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        amenity_name = uuid.uuid4().hex[:12] if amenity_name == '' else amenity_name
        amenities = [
            {
                "id": amenity_id,
                "amenity_name": amenity_name,
                "icon": icon,
                "operating_hours_allowed": operating_hours_allowed,
                "fee_allowed": fee_allowed,
                "show_icon_on_hotel_listing": show_icon_on_hotel_listing,
                "is_available": is_available,
            }
        ]
        amenities = json.dumps(amenities, separators=(',', ':'))

        response = requests.post(url, headers=headers, cookies=self._support_cookies,
                                 data={'amenities': amenities})
        response = response.json()
        return response

     # TODO: update amenity route and data
    def add_edit_hotel_amenity(self, hotel_id='0', hotel_amenity_id='0', amenity_id='0', amenity_fee=0,
                               allow_operating_hours='0', hotel_amenity_operated_from=None,
                               hotel_amenity_operated_to=None, available='0', comment=None):
        """
        :param hotel_id: string
        :param hotel_amenity_id: string
        :param amenity_id:string
        :param amenity_fee:string
        :param allow_operating_hours:string
        :param hotel_amenity_operated_from:string
        :param hotel_amenity_operated_to:string
        :param available:string
        :param comment:string
        :return: dict
        """
        url = self._php_host + '/api/v1/ui/hotel/'+ str(hotel_id) +'/amenity'
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        hotel_amenities = [
            {
                'hotel_amenity_id': hotel_amenity_id,
                'amenity_master_id': amenity_id,
                'amenity_fee': amenity_fee,
                'allow_operating_hours': '0',
                'hotel_amenity_operated_from': "N/A" if hotel_amenity_operated_from is None \
                    else hotel_amenity_operated_from,
                'hotel_amenity_operated_to': "N/A" if hotel_amenity_operated_to is None else hotel_amenity_operated_to,
                'is_available': available,
                'comment': comment
            }
        ]

        hotel_amenities = json.dumps(hotel_amenities, separators=(',', ':'))

        response = requests.post(url, headers=headers, cookies=self._support_cookies,
                                 data={'amenities': hotel_amenities})
        self.assertEqual(response.status_code, 200)
        response = response.json()
        return response

    def add_edit_hotel_amenities(self, hotel_id='0', hotel_amenities=[]):
        """
        :param hotel_id: string
        :param amenities: list of dictionaries
        :return: dict
        """
        url = self._php_host + '/api/v1/ui/hotel/'+ str(hotel_id) +'/amenity'
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        hotel_amenities = json.dumps(hotel_amenities, separators=(',', ':'))

        response = requests.post(url, headers=headers, cookies=self._support_cookies,
                                 data={'amenities': hotel_amenities})
        self.assertEqual(response.status_code, 200)
        response = response.json()
        return response

    def get_available_amenities_for_a_hotel(self, hotel_id='0'):
        """
        :param hotel_id: string
        :return: dict - List of available amenities
        """
        url = self._php_host + '/api/v1/ui/hotel/'+ str(hotel_id) +'/amenity'
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=self._support_cookies)
        response = response.json()
        return response

    def add_or_update_hotel(self, hotel_post_data, hotel_id, cookies=None):
        """
        :param hotel_post_data: dict
        :param hotel_id: int
        :param cookies: str
        :return: json with success message and hotel id
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/hotel_detail.php?type=save&hotelId='+str(hotel_id)

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        response = requests.post(url, headers=headers, cookies=cookies, data=hotel_post_data)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json

    def add_hotel_serviced_port(self, port_id, hotel_id, cookies=None,
                                passenger_notes=None, ranking=99):
        """
        :param port_id: int
        :param hotel_id: int
        :param cookies: str
        :param passenger_notes: str
        :param ranking: int
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + \
            '/admin/hotel_detail.php?type=saveServicedPorts&hotelId=' + \
            str(hotel_id)
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        form_data = {
            'id': port_id,
            'type': 'add',
            'passenger_notes': passenger_notes,
            'ranking': ranking,
        }

        response = requests.post(url, headers=headers,
                                 cookies=cookies, data=form_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json

    def update_hotel_serviced_port(self, hotel_serviced_port_id, port_id, hotel_id,
                                   passenger_notes=None, ranking=99, cookies=None):
        """
        :param hotel_serviced_port_id: int
        :param port_id: int
        :param hotel_id: int
        :param passenger_notes: str
        :param ranking: int
        :param cookies: str
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + \
            '/admin/hotel_detail.php?type=saveServicedPorts&hotelId=' + \
            str(hotel_id)
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        form_data = {
            'hotel_serviced_port_id': hotel_serviced_port_id,
            'port_id': port_id,
            'passenger_notes': passenger_notes,
            'ranking': ranking,
        }

        response = requests.post(url, headers=headers,
                                 cookies=cookies, data=form_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json

    def remove_hotel_serviced_port(self, hotel_id, port_id, hotel_serviced_port_id, cookies=None):
        """
        :param hotel_id: int
        :param hotel_serviced_port_id: int
        :param cookies: str
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + \
            '/admin/hotel_detail.php?type=saveServicedPorts&hotelId=' + \
            str(hotel_id)
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        form_data = {
            'id': hotel_serviced_port_id,
            'port_id': port_id,
            'remove': 1,
        }

        response = requests.post(url, headers=headers,
                                 cookies=cookies, data=form_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json

    def room_return_quick_room_transfer_voucher(self, voucher_history, rooms, cookies=None):
        """
        :param voucher_history: dict
        :param rooms: int
        :param cookies: str
        :return: json
        """
        remaining_rooms = int(voucher_history.get('voucher_room_total')) - rooms
        form_data = {
            'usage': voucher_history,
            'rooms': rooms,
            'remaining_rooms': remaining_rooms
        }
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/voucher.php?type=return_rooms'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'
        form_data = json.dumps(form_data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data={'data': form_data})
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json

    def get_create_hotel_post_data(
            self, payment_type, tvl_blacklist_reason='', check_duplicate=1, hotel_currency='USD',
            hotel_timezone='America/Chicago', is_allowed_to_manage_inventory=False, is_allowed_to_exceed_rate_agreement=False
        ):
        """
        :param payment_type: str
        :param tvl_blacklist_reason:str
        :return: dict
        """
        fake = faker.Faker()
        hotel_name = self.get_random_string(30)
        hotel_gp_lat = str(fake.latitude())
        hotel_gp_lon = str(fake.longitude())
        hotel_contact_email = uuid.uuid4().hex + '@tvlinc.blackhole'
        return {
            'hotel_id': 0,
            'hotel_name': hotel_name,
            'hotel_country': 'USA',
            'hotel_address1': fake.street_address(),
            'hotel_state': 'Chicago',
            'hotel_postcode': '60007',
            'hotel_contact_email': hotel_contact_email,
            'hotel_is_available': 1,
            'hotel_ranking': 1,
            'hotel_city': 'Chicago',
            'hotel_contract_type': 'A',
            'hotel_brand_id': 0,
            'hotel_shuttle_enabled': 0,
            'hotel_gp': '',
            'hotel_gp_lat': hotel_gp_lat,
            'hotel_gp_lon': hotel_gp_lon,
            'hotel_rating': 0,
            'transport_id': 0,
            'hotel_currency': hotel_currency,
            'hotel_pets_allowed': 0,
            'hotel_service_pets_allowed': 0,
            'hotel_shuttle_timing': '00:00 00:00',
            'hotel_management_company_id': 0,
            'isNatWide': 1,
            'isAdmin': 1,
            'isSupervisorOrAbove': 1,
            'isSupport': 1,
            'star_rating_permission': True,
            'hotel_shuttle_time_in_hour': 0,
            'hotel_shuttle_time_in_min': 0,
            'hotel_shuttle_time_out_hour': 0,
            'hotel_shuttle_time_out_min': 0,
            'hotel_currency_prev': '',
            'errMsg': '',
            'hotelRates': '',
            'tvl_blacklist_reason':tvl_blacklist_reason,
            'supplier_default_pay_type':payment_type,
            'duplicationCheck': check_duplicate,
            'hotel_timezone': hotel_timezone,
            'is_allowed_to_manage_inventory':int(is_allowed_to_manage_inventory),
            'is_allowed_to_exceed_rate_agreement':int(is_allowed_to_exceed_rate_agreement)

        }

    def get_addition_contact_post_data(self, contactType=34):
        """
        :return: dict
        """
        fake = faker.Faker()
        name = self.get_random_string(10)
        email = uuid.uuid4().hex + '@tvlinc.blackhole'
        return {
            'email': fake.email(),
            'last_updated': '',
            'contactType': contactType,
            'phone': fake.random_number(7),
            'name': name
        }

    def search_hotel(self, hotel_id, port_id = None):
        """
        :param hotel_id: integer
        :pram port_id: integer
        :return: dict
        """
        url = self._php_host + '/admin/hotels.php'
        query_parameters = {
            'type': 'search',
            'status': 1,
            'hid': hotel_id

        }
        if port_id is not None:
            query_parameters['pid']=port_id

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=self._support_cookies, params=query_parameters)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json


    def search_expedia_hotels(self, hotel_id, cookies=None):
        """
        :param hotel_id: integer
        :return: dict
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/hotels.php'
        query_parameters = {
            'type': 'searchExpediaHotels',
            'id': hotel_id

        }

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json

    def link_to_expedia_hotel(self, hotel_id, expedia_rapid_id, cookies=None):
        """
        :param hotel_id: int
        :param expedia_rapid_id: int
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/hotels.php?type=linkToExpediaHotel'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        post_data = {
            'id': hotel_id,
            'expedia_rapid_id': expedia_rapid_id
        }

        response = requests.post(url, headers=headers, cookies=cookies, data=post_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json

    @classmethod
    def get_login_users_list(cls, port_id, airline_id, hotel_id, transport_id, types):
        """
        :param port_id: int
        :param airline_id: int
        :param hotel_id: int
        :param transport_id: int
        :param types: list
        :return: dict
        """
        user_list = []
        for type in types:
            if type == 'hotel':
                id = hotel_id
                add_serviced_port_url = cls._php_host + '/admin/hotel_detail.php?hotelId='+str(hotel_id)+'&type=saveServicedPorts'
                add_user_url = cls._php_host + '/admin/hotel_detail.php?hotelId=' + str(hotel_id) + '&type=saveUsers'
                roles = range(30, 32)
            elif type == 'airline':
                id = airline_id
                add_serviced_port_url = cls._php_host + '/admin/airline_detail.php?airlineId=' + str(airline_id) + '&type=saveServicedPorts'
                add_user_url = cls._php_host + '/admin/airline_detail.php?airlineId=' + str(airline_id) + '&type=saveUsers'
                roles = range(11, 15)
            else:
                id = transport_id
                add_serviced_port_url = cls._php_host + '/admin/transport_detail.php?transportId='+str(transport_id)+'&type=saveServicedPorts'
                add_user_url = cls._php_host + '/admin/transport_detail.php?transportId=' + str(transport_id) + '&type=saveUsers'
                roles = range(20, 21)

            form_data = {
                'type': 'add',
                'id': port_id
            }
            headers = cls._generate_stormx_php_headers()
            headers['Accept'] = 'application/json, text/plain, */*'
            headers['X-TVA-Internal'] = '1'
            headers['Accept-Language'] = 'en-US,en;q=0.9'
            requests.post(add_serviced_port_url, headers=headers, cookies=cls._support_cookies, data=form_data)
            for user in cls.create_and_login_users_with_different_roles(port_id, id, add_user_url, roles, type, headers):
                user_list.append(user)

        return user_list

    @classmethod
    def create_and_login_users_with_different_roles(cls, port_id, id, url, roles, type, headers):
        """
        :param port_id: int
        :param id: int
        :param url: str
        :param roles: list
        :param type: list
        :param headers: list
        :return: dict
        """
        user_list = []
        fake = faker.Faker()
        for i in roles:
            user_form_data = cls.get_create_user_post_data(port_id=port_id, role=i,is_invalid=False)
            response = requests.post(url, headers=headers, cookies=cls._support_cookies, data=user_form_data)
            if response.status_code== 200 and "There is an error while saving user." not in response.text:
                response_json = response.json()
                user_id = response_json['id']
                if int(user_id) > 0:
                    #Update fresh user password before login
                    user_form_data['id'] = user_id
                    if type == 'hotel':
                        user_form_data['hotel_id'] = id
                    elif type == 'airline':
                        user_form_data['airline_id'] = id
                    else:
                        user_form_data['transport_id'] = id
                    user_form_data['user_id_'] = fake.password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True)
                    user_form_data['edit'] = True
                    user_form_data['delete'] = True
                    user_form_data['access'] = 10
                    user_form_data['updated_by_user'] = 'support'
                    response = requests.post(url, headers=headers, cookies=cls._support_cookies, data=user_form_data)
                    if response.status_code == 200:
                        try:
                            user_list.append({'username': user_form_data.get('user_id'),'role_id': i, 'user_type': type,
                                              'cookies': self.login_to_stormx(user_form_data.get('user_id'),
                                                                              user_form_data.get('user_id_'))})
                        except:
                            pass

        return user_list

    def add_blog_message(self, id, btype, message, cookies=None):
        """
        :param id: int
        :param btype: str
        :param message: str
        :param cookies: dict
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/helper.php?type=blogs&btype={btype}&id={id}'.format(btype=btype, id=id)
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        post_data = {
            'type': 'add',
            'message': message
        }

        response = requests.post(url, headers=headers, cookies=cookies, data=post_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json

    def mark_blog_message_unread(self, id, btype,message_id, isRead, cookies=None):
        """
        :param id: int
        :param btype: str
        :param message_id: int
        :param isRead: int
        :param cookies: dict
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/helper.php?type=blogs&btype={btype}&id={id}'.format(btype=btype, id=id)
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        post_data = {
            'id': message_id,
            'type': 'markRead',
            'isRead': isRead
        }

        response = requests.post(url, headers=headers, cookies=cookies, data=post_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json

    def read_blog_messages(self, id,type, cookies=None):
        """
        :param id: integer
        :param type: str
        :return: dict
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/remote/helper.php'
        query_parameters = {
            'type': 'blogs',
            'btype': type,
            'id': id

        }

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json
    @staticmethod
    def _generate_n_passenger_payload(number_of_passengers, **kwargs):
        passengers = [copy.deepcopy(PASSENGER_TEMPLATE[0]) for i in range(0, number_of_passengers)]
        pax_record_locator = generate_pax_record_locator()
        pax_record_locator_group = generate_pax_record_locator_group()
        for passenger in passengers:
            passenger['context_id'] = generate_context_id()
            passenger['pax_record_locator'] = pax_record_locator
            passenger['pax_record_locator_group'] = pax_record_locator_group
            passenger.update(kwargs)
        return passengers

    @staticmethod
    def _generate_2_passenger_payload(**kwargs):
        passengers = copy.deepcopy(PASSENGER_TEMPLATE)
        pax_record_locator = generate_pax_record_locator()
        pax_record_locator_group = generate_pax_record_locator_group()
        for passenger in passengers:
            passenger['context_id'] = generate_context_id()
            passenger['pax_record_locator'] = pax_record_locator
            passenger['pax_record_locator_group'] = pax_record_locator_group
            passenger.update(kwargs)
        return passengers

    def _generate_bulk_passenger_payload(self, size=MOST_PASSENGERS_IN_LARGEST_AIRCRAFT):
        fake = self._passenger_faker
        # def generate_distinct_random_indexes(fake, list_size, ratio_to_pick):
        #     picked = set()
        #     number_to_pick = int(list_size*ratio_to_pick)
        #     list_size_minus_one = list_size - 1
        #
        #     # use `max_tries` to make sure the function will never get stuck in an infinite loop if unlucky.
        #     max_tries = int(number_to_pick * 2.1)
        #
        #     while (max_tries > 0) and len(picked) < number_to_pick:
        #         picked.add(fake.random.randint(0, list_size_minus_one))
        #         max_tries -= 1
        #     return picked
        passengers = [self._generate_passenger_incomplete() for i in range(0, size)]
        one_percent = int(0.01*size)
        five_percent = int(0.05*size)
        eighty_percent = int(0.80*size)
        ninty_percent = int(0.90*size)
        adults = passengers[0:eighty_percent]
        young_adults = passengers[eighty_percent:ninty_percent]
        children = passengers[ninty_percent:]

        # group all passengers in `groups`
        big_group = adults[0:five_percent]
        small_groups = list(random_chunk(fake, adults[five_percent:], min_chunk=1, max_chunk=3))
        groups =  [big_group] + small_groups
        # assign young adults and children to groups of adults, and set their stage of life.
        for passenger in young_adults:
            passenger['life_stage'] = 'young_adult'
            fake.random.choice(groups).append(passenger)
        for passenger in children:
            passenger['life_stage'] = 'child'
            # remove/blank out fields children are not likely to have

            fake.random.choice(groups).append(passenger)

        # make roughly one percent of the passengers handicapped.
        for i in range(0, one_percent):
            fake.random.choice(passengers)['handicap'] = True

        # add one service pet.
        fake.random.choice(passengers)['service_pet'] = True

        # make a few of the groups families with the same last name and address
        for i in range(0, len(small_groups)//5):
            group = fake.random.choice(small_groups)
            primary_passenger = group[0]
            for passenger in group[1:]:
                passenger['last_name'] = primary_passenger['last_name']

        flat_passengers = []
        for group in groups:
            pax_record_locator = generate_pax_record_locator()
            pax_record_locator_group = generate_pax_record_locator_group()
            for passenger in group:
                passenger['context_id'] = generate_context_id()
                passenger['pax_record_locator'] = pax_record_locator
                passenger['pax_record_locator_group'] = pax_record_locator_group
                flat_passengers.append(passenger)

        # split out half of the passengers in `big_group` to be under a different pax_record_locator_group, but
        # still the same pax_record_locator
        different_pax_record_locator_group = generate_pax_record_locator_group()
        for passenger in big_group[0:len(big_group)//2]:
            passenger['pax_record_locator_group'] = different_pax_record_locator_group

        return flat_passengers

    def _generate_passenger_incomplete(self):
        """
        generate a reasonable, semi-realistic set of data about a passenger.
        """
        fake = self._passenger_faker
        passenger = copy.deepcopy(PASSENGER_TEMPLATE[0])
        passenger.update({
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'phone_numbers': [fake.msisdn()],
            'emails':  [fake.safe_email().split('@')[0] + '@x.blackhole'],
        })
        return passenger

    def _create_2_passengers(self, customer, **kwargs):
        """
        utility to create passengers.
        :param: kwargs - keys to set in every passenger.
        :return: list of dictionaries of the created customers
        """
        airline_client = self.get_airline_api_client(customer)
        passengers = self._generate_2_passenger_payload()
        if kwargs:
            for passenger in passengers:
                passenger.update(kwargs)

        return airline_client.import_passengers(passengers)

    def _get_passenger_hotel_offerings(self, passenger_dictionary, room_count=1):
        """
        utility to look up a passenger's hotel offerings.
        :param : passenger_dictionary - needs to contain the 'ak1' and 'ak2' keys.
        :return: a list of hotels
        """
        url = self._api_host + '/api/v1/offer/hotels'
        headers = self._generate_passenger_headers()
        room_count_string = str(int(room_count))

        query_parameters = dict(
            ak1=passenger_dictionary['ak1'],
            ak2=passenger_dictionary['ak2'],
            room_count=room_count_string,
        )
        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        returned_hotels = response.json()['data']

        return returned_hotels

    def _airline_get_passenger_hotel_offerings(self, customer, port, room_count):
        """
        utility that allows an airline to look up hotels for a passenger.
        param port: string
        param room_count: int
        return: a list of hotels
        """
        url = self._api_host + '/api/v1/hotels'
        headers = self._generate_airline_headers(customer=customer)

        query_parameters = dict(
            port=port,
            room_count=str(int(room_count)),
        )

        response = requests.get(url, headers=headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        hotels = response_json['data']

        return hotels

    def _passenger_book_hotel(self, passenger_dictionary, hotel_dictionary, context_ids, room_count=1):
        """
        return just the data portion of the response's JSON.
        """
        url = self._api_host + '/api/v1/offer/hotels'
        headers = self._generate_passenger_headers()

        booking_query_parameters = dict(
            ak1=passenger_dictionary['ak1'],
            ak2=passenger_dictionary['ak2'],
        )
        booking_payload = dict(
            context_ids=context_ids,
            hotel_id=hotel_dictionary['hotel_id'],
            room_count=room_count,
        )
        response = requests.post(url, headers=headers, params=booking_query_parameters, json=booking_payload)
        if (response.status_code != 200):
            display_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        response_json = response.json()
        self.assertIs(response_json['error'], False)
        self.assertEqual(response_json['meta']['message'], 'OK')
        return response_json['data']

    def _airline_book_hotel(self, customer, hotel_dictionary, context_ids, room_count=1):
        """
        return just the data portion of the response's JSON.
        """
        airline_client = self.get_airline_api_client(customer)
        return airline_client.book_hotel(
            context_ids=context_ids,
            hotel_id=hotel_dictionary['hotel_id'],
            room_count=room_count,
        )

    def _passenger_decline_offer(self, passenger_dictionary):
        """
        return just the data portion of the response's JSON.
        """
        decline_url = self._api_host + '/api/v1/offer/decline'
        passenger_headers = self._generate_passenger_headers()

        query_parameters = dict(
            ak1=passenger_dictionary['ak1'],
            ak2 = passenger_dictionary['ak2']
        )

        response = requests.put(decline_url, headers=passenger_headers, params=query_parameters)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json['data']

    def _validate_error_message(self, response_json, expected_status_code, expected_message, expected_error_code,
                                expected_error_description, expected_error_detail):
        """
        param response_json: JSON (API response)
        param expected_status_code: int
        param expected_message: string
        param expected_error_code: string
        param expected_error_description: string
        param expected_error_detail: string
        return: None
        """
        self.assertEqual(response_json['error'], True)
        self.assertEqual(response_json['meta']['status'], expected_status_code)
        self.assertEqual(response_json['meta']['message'], expected_message)
        self.assertEqual(response_json['meta']['error_code'], expected_error_code)
        self.assertEqual(response_json['meta']['error_description'], expected_error_description)

        # validate that all error messages that expected to be present in the error detail list
        # can be validated in any order (non deterministic)
        for error_message in expected_error_detail:
            self.assertIn(error_message, response_json['meta']['error_detail'])
        self.assertEqual(len(response_json['meta']['error_detail']), len(expected_error_detail))

    def select_airport_for_expedia_testing(self, port_and_timezone_pairs):
        """
        return the first airport iata code that is currently testable (i.e., will use *today's* inventory at the local port, and not *yesterday's*
        :param port_and_timezone_pairs: list of (airport_iata_code, timezone_name) tuples.
        :return:
        """
        for port, timezone_name in port_and_timezone_pairs:
            if not self._is_event_date_yesterday(timezone_name):
                return port
        raise ValueError('Unfortunately, no test ports in the list. Choose ports with a larger timezone difference.')

    def select_multiple_airports_for_expedia_testing(self, port_and_timezone_pairs):
        """
        return the list of airport iata codes that are currently testable (i.e., will use *today's* inventory at the local port, and not *yesterday's*
        :param port_and_timezone_pairs: list of (airport_iata_code, timezone_name) tuples.
        :return: list(string)
        """
        ports = []
        for port, timezone_name in port_and_timezone_pairs:
            if not self._is_event_date_yesterday(timezone_name):
                ports.append(port)

        return ports

    def _get_landing_page_embedded_json(self, response):
        # it would be better to use BeautifulSoup to parse the HTML, but I am trying to limit system test dependencies for now.
        LANDING_PAGE_EMBEDDED_JSON_BEGIN = '<script type="application/json" id="initial_data">'
        LANDING_PAGE_EMBEDDED_JSON_END = '</script>'

        begin_location = response.text.find(LANDING_PAGE_EMBEDDED_JSON_BEGIN)
        if begin_location != -1:
            begin_location = begin_location + len(LANDING_PAGE_EMBEDDED_JSON_BEGIN)
            end_location = response.text.find(LANDING_PAGE_EMBEDDED_JSON_END, begin_location)
            if end_location != -1:
                embedded_json_string = response.text[begin_location:end_location]
                deserialized_object = json.loads(embedded_json_string)
                return deserialized_object
        raise Exception('could not find and load the initial_data.')

    def charge_single_use_card(self, card_number, currency_code, amount,
                               merchant_acceptor_id, merchant_description,
                               merchant_city, merchant_state, merchant_zip,
                               merchant_country_code, sic_mcc_code, note=''):
        url = self._api_host + '/sandbox/transaction'
        headers = self._generate_tvl_stormx_headers()

        json_payload = dict(
            card_number=card_number,
            currency_code=currency_code,
            amount=str(amount),
            merchant_acceptor_id=merchant_acceptor_id,
            merchant_description=merchant_description,
            merchant_city=merchant_city,
            merchant_state=merchant_state,
            merchant_zip=merchant_zip,
            merchant_country_code=merchant_country_code,
            sic_mcc_code=sic_mcc_code,
            note=note,
        )
        response = requests.post(url, headers=headers, data=json_payload)
        response.raise_for_status()
        return response.json()

    def get_port_timezone(self, port_id, cookies=None):
        """
        :param port_id: int
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/port_detail.php?type=get_port_timezone'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        post_data = {
            'port_id':port_id
        }

        response = requests.post(url, headers=headers, cookies=cookies, data=post_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)

        if not 'timezone' in response_json or response_json['timezone'] == "":
            self.fail('No timezone found for port having id = '+ str(port_id))

        return response_json['timezone'] if response_json['timezone'] else ""

    def fetch_inventory(self, port_id, now, hotel_ids, avails_date, cookies=None):
        """
        :param port_id: int
        :param now: int
        :param hotel_ids: list
        :param avails_date: date
        :return: json
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/hotels.php?type=fetch_inventory'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        post_data = {
            'avails_date': avails_date,
            'ids':json.dumps(hotel_ids),
            'now':now,
            'pid':port_id
        }
        response = requests.post(url, headers=headers, cookies=cookies, data=post_data)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        return response_json



    # HMT Recon Test

    def reconcilliation_access_authorization(self, endpoint ='getReconTotals', test_user = None, user_cookie =None ):

        url = self._php_host + '/admin/remote/reconHelper.php?type='+ endpoint

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
             'aid': 294,  # Purple Rain
        }

        if user_cookie is not None:
            cookie =user_cookie
        elif test_user is None:
            cookie = self._support_cookies
        else:
            cookie = self.login_to_stormx(username=test_user['username'], password=test_user['newUserP'])

        response = requests.post(url, headers=headers, cookies=cookie, data=form_data)
        response_json = response.json()
        return response_json

    def get_reconcilliation_data(self, airline_id=0, recon_for='H', port_id=0, hotel_id=0,
                                 status='', name='', pnr='', voucher_id='', date_from='',
                                 date_to='', page_number=1):

        url = self._php_host + '/admin/remote/reconHelper.php?type=getReconData'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'pid': str(port_id),
            'aid': airline_id,
            'hid': str(hotel_id),
            'status': str(status),
            'name': str(name),
            'pnr': str(pnr),
            'voucher_id': str(voucher_id),
            'dateFrom': str(date_from),
            'dateTo': str(date_to),
            'page_number': str(page_number),
            'recon_for': recon_for,
        }
        response = requests.post(url, headers=headers, cookies=self._support_cookies, data= form_data)
        response_json = response.json()
        return response_json

    def get_reconcilliation_Totals(self, airline_id=0):

        url = self._php_host + '/admin/remote/reconHelper.php?type=getReconTotals'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'aid': airline_id,
        }
        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        response_json = response.json()
        return response_json

    def update_reconcilliation_transaction_status(self, transaction_id=0, status=0, transactions_ids=None):

        url = self._php_host + '/admin/remote/reconHelper.php?type=updateReconTransactionsStatus'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        if transactions_ids is None:
            form_data = {
                'idList[0]': transaction_id,
                'idStatus': status,
            }
        else:
            form_data = {'idList[' + str(i) + ']': transactions_ids[i] for i in range(len(transactions_ids))}
            form_data['idStatus']= status

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data= form_data)
        response_json = response.json()
        return response_json

    def get_transaction_history(self, transaction_id):

        url = self._php_host + '/admin/remote/reconHelper.php?type=card_transactions_history'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'transaction_id': transaction_id,
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        response_json = response.json()
        return response_json

    def create_hmt_invoice(self, airline_id=0, recon_for='H', port_id=0,currency='USD', date_from='', date_to='',airline_prfix='PRP'):

        url = self._php_host + '/admin/remote/reconHelper.php?type=pre_invoice_save'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'aid': airline_id,
            'pid': port_id,
            'dateFrom': date_from,
            'dateTo': date_to,
            'currency': currency,
            'recon_for': recon_for,
            'airline_prefix': airline_prfix,
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        response_json = response.json()
        return response_json

    def get_hmt_recon_invoices(self, airline_id=0, recon_for='H',currency='USD', date_from='',
                                 date_to='',invoice_number='', page_number=1):

        url = self._php_host + '/admin/remote/reconHelper.php?type=invoice_search'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'aid': str(airline_id),
            'dateFrom': str(date_from),
            'dateTo': str(date_to),
            'currency':currency,
            'invoice_no':invoice_number,
            'page_number': str(page_number),
            'recon_for': recon_for,
        }
        response = requests.post(url, headers=headers, cookies=self._support_cookies, data= form_data)
        response_json = response.json()
        return response_json


    # Rate Cap Tests

    def get_available_currencies_for_rate_cap(self):

        url = self._php_host + '/admin/remote/helper.php?type=fetchRateCapCurrencies'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.post(url, headers=headers, cookies=self._support_cookies)
        response_json = response.json()
        return response_json

    def add_edit_rate_cap(self, rate_cap_currency, rate_cap_warning, rate_cap_id = None):

        url = self._php_host + '/admin/configurations.php?type=saveRateCap'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        rate_cap_id = '' if rate_cap_id is None else str(rate_cap_id)
        form_data = {
            'rate_cap': str(rate_cap_warning),
            'currency': str(rate_cap_currency),
            'id': rate_cap_id,
        }
        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        response_json = response.json()
        return response_json

    def remove_rate_cap(self, rate_cap_id):

        url = self._php_host + '/admin/configurations.php?type=removeRateCaps'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'id': str(rate_cap_id),
        }
        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        response_json = response.json()
        return response_json

    def get_rate_caps(self):

        url = self._php_host + '/admin/configurations.php?type=fetchRateCaps'

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=None)
        response_json = response.json()
        return response_json

    def add_addition_contact(self, contact_post_data, entity_id, contact_type, cookies=None):
        """
        :param contact_post_data: dict
        :param entity_id: int
        :param cookies: str
        :return: json with success or failure
        """
        if cookies is None:
            cookies = self._support_cookies
        url = self._php_host + '/admin/contacts.php?type=save&rid='+str(entity_id)+'ctype='+contact_type

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        response = requests.post(url, headers=headers, cookies=cookies, data=contact_post_data)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json
    def _test_passenger_notifications(self, notifications, emails, phone_numbers, expected_email_count,
                                      expected_text_count, expected_offer_count, expected_confirmation_count,
                                      notification_sent=True, public_notification=False,
                                      expected_passenger_pay_count=0):
        """
        helper function for testing passenger notifications
        param notifications: JSON notifications
        param emails: list(string)
        param phone_numbers: list(string)
        param expected_email_count: int
        param expected_text_count: int
        param expected_offer_count: int
        param expected_confirmation_count: int
        param notification_sent: bool (default True)
        param public_notificationL bool (default False)
        return: None
        """
        text_count = 0
        email_count = 0
        offer_count = 0
        confirmation_count = 0
        passenger_pay_count = 0

        # check if this notification object is coming from POST passenger/{context_id}/notifications
        if len(notifications) == 1 and 'passenger' in notifications[0]:
            self.assertIsNotNone(notifications[0]['passenger']['context_id'])
            self.assertIsNotNone(notifications[0]['passenger']['modified_date'])
            notifications = [notifications[0]['notification']]

        for notification in notifications:
            if notification['notification_type'] == 'confirmation':
                confirmation_count += 1
            elif notification['notification_type'] == 'passenger_pay':
                passenger_pay_count += 1
            else:
                self.assertEqual(notification['notification_type'], 'offer')
                offer_count += 1

            if notification['sent_to'] in emails:
                self.assertEqual(notification['sent_via'], 'email')
                email_count += 1
            else:
                self.assertIn(notification['sent_to'], phone_numbers)
                self.assertEqual(notification['sent_via'], 'text')
                text_count += 1

            if notification_sent:
                self.assertIsNotNone(notification['sent_date'])
            else:
                self.assertIsNone(notification['sent_date'])

            if not public_notification:
                UUID(notification['id'], version=4)

        self.assertEqual(email_count, expected_email_count)
        self.assertEqual(text_count, expected_text_count)
        self.assertEqual(offer_count, expected_offer_count)
        self.assertEqual(confirmation_count, expected_confirmation_count)
        self.assertEqual(passenger_pay_count, expected_passenger_pay_count)
        self.assertEqual(len(notifications), expected_offer_count + expected_confirmation_count + expected_passenger_pay_count)

    def create_hotel_block(self, hotel_id= 1,status = 1,port_id = 1,room_type_id = 1,airline_id = 1,
                                    rate = 1,start_date ='',end_date ='',room_count_mon = 50,room_count_tue = 50,
                                    room_count_wed = 50,room_count_thu = 50,room_count_fri = 50,
                                    room_count_sat = 50,room_count_sun = 50,consume_blocks = 0, type='hardblock'):
        url = self._php_host + '/admin/hotel_detail.php?type={}'.format(type)
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'hotel_id': str(hotel_id),
            'type': 'save',
            'status': status,
            'port_id': port_id,
            'room_type_id' : room_type_id,
            'airline_id' : airline_id,
            'rate' : rate,
            'start_date' :start_date,
            'end_date' :end_date,
            'room_count_mon' : room_count_mon,
            'room_count_tue' : room_count_tue,
            'room_count_wed' : room_count_wed,
            'room_count_thu' : room_count_thu,
            'room_count_fri' : room_count_fri,
            'room_count_sat' : room_count_sat,
            'room_count_sun' : room_count_sun,
            'consume_blocks' : consume_blocks
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        return response

    def update_hotel_availability(self, hotel_id, hotel_availability_id, airline_id, availability_date,
                                  blocks=0, block_price='10',
                                  ap_block_type=0,
                                  issued_by='Theresa May',
                                  comment='test',
                                  room_type=1,pay_type=0,
                                  verify_response_success=True):

        url = self._php_host + '/admin/remote/helper.php?type=updateAvailsByID'
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        form_data = {
            'id': str(hotel_id),
            'hotel_availability_id': str(hotel_availability_id),
            'type': 'add',
            'blocks': str(blocks),
            'block_price': str(block_price),
            'block_expiration_date': str(availability_date),
            'airline_id': str(airline_id) if airline_id else '0',
            'year_no': str(availability_date.year),
            'month_no': str(availability_date.month).zfill(2),
            'day_no': str(availability_date.day).zfill(2),
            'issued_by': str(issued_by),
            'position': 'Front Desk Agent',
            'comment': str(comment),
            'ap_block_type': ap_block_type,
            'room_type': room_type,
            'pay_type':pay_type,
            'action_type':'edit'
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        return response

    def save_transport_only_voucher(self, voucher_id, airline_id, transport, airport_id, voucher_date,
                             passenger_names,
                             flight_number,
                             mode='saveCont',
                             verify_response_success=True):

        url = self._php_host + '/admin/remote/voucher.php?type=saveVoucherNew'
        headers = self._generate_stormx_php_headers()
        headers['X-TVA-Internal'] = '1'

        airline_id = int(airline_id)
        transport_to_id = int(transport[0])
        transport_from_id = int(transport[1])

        airport_id = int(airport_id)

        form_data = {
            'voucher_id': voucher_id,
            'voucher_code': '',
            'voucher_disruption_date': voucher_date.strftime(DATETIME_FORMAT_FOR_VOUCHERS),
            'voucher_requesting_port': str(airport_id),
            'voucher_airline_auth_user': 'tests',
            'voucher_disruption_reason': '7',
            'voucher_invoice_airline': str(airline_id),
            'voucher_departure_port': str(airport_id),
            'voucher_departure_airline': str(airline_id),
            'voucher_departure_date': (voucher_date + datetime.timedelta(days=1)).strftime(DATETIME_FORMAT_FOR_VOUCHERS),  # TODO: make different date.
            'voucher_currency': 'USD',
            'transport_to_hotel': str(transport_to_id),
            'transport_from_hotel': str(transport_from_id),
            'transportIn_payment_type': 'A',
            'transportOut_payment_type': 'A',
            'voucher_disruption_port': str(airport_id),
            'voucher_disruption_airline': str(airline_id),
            'voucher_disruption_flight': flight_number,
            'voucher_pax_total': str(len(passenger_names)),
            'voucher_hotel_nights': 0,
            'voucher_room_total': 0,
            'voucher_cutoff_time': voucher_date.strftime(DATETIME_FORMAT_FOR_VOUCHERS),
            'isEditable': 'true',
            'allow_trans_to': 'true',
            'allow_trans_from': 'true',
            'totalPax': 0,
            'totalRooms': 0,
            'mode': mode,
        }

        response = requests.post(url, headers=headers, cookies=self._support_cookies, data=form_data)
        response_json = response.json()
        if verify_response_success:
            if not (response.status_code == 200 and response_json.get('success') == '1'):
                display_response(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json['success'], '1')
        return response_json

def should_skip_local_test(decoratee):
    def custom_decorator(self, *args, **kwargs):
        if self.selected_environment_name == 'dev' and SHOULD_SKIP_LOCAL_TEST:
            raise unittest.SkipTest('passenger pay tests skipped on dev environment.')
        return decoratee(self, *args, **kwargs)
    return custom_decorator
