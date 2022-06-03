from e2e_selenium_tests.BaseClasses.constant import STORMX_URL
from e2e_selenium_tests.TestCases import base_test

import unittest
import requests
import datetime
from pytz import timezone
_php_host = STORMX_URL


class StormxApiMethods(unittest.TestCase):

    @classmethod
    def login_user_to_stormx(cls, username, password):
        """
        param username: string
        param password: string
        :return: response object from php endpoint`.
        """
        url = _php_host + "admin/index.php"

        form_data = {
            'cPwd': '',
            'continue': '',
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

    def reset_pass(username, password, resetpassword):
        # reset password
        url = _php_host + "/admin/index.php"
        form_data = {
            'cPwd': '',
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
            'content-type': "application/x-www-form-urlencoded"
        }
        response = requests.post(url, data=form_data, headers=headers)
        if response.status_code == 200 and 'Please wait redirecting...' in response.text:
            pass  # successful password reset
        else:
            print(response)
            raise Exception('login issue: failed to reset password.')
        return response

    @classmethod
    def login_to_stormx(cls, username, password, resetpassword):
        """
        param username: string
        param password: string
        :return: a the cookies to use the session. stores this value and pass to
                 the `requests` library like `requests.XXX(cookies=MY_COOKIES)`.
        """
        response = cls.login_user_to_stormx(username, password)
        if response.status_code != 200:
            print(response)
            raise Exception('login issue: unexpected status code: ' + repr(response.status_code))
        elif 'Incorrect Username or Password' in response.text:
            print(response)
            raise Exception('login issue: incorrect username or password')
        elif 'Please change your password before you log in.' in response.text:
            response = cls.reset_pass(username, password, resetpassword)
        elif 'Your password has expired. Please change it before you log in.' in response.text:
            response = cls.reset_pass(username, password, resetpassword)
        elif 'Please wait redirecting...' in response.text:
            pass  # successful login
        else:
            print(response)
            raise Exception('login issue: unexpected response.')
        session_cookies = response.cookies
        return session_cookies

    @staticmethod
    def _generate_stormx_php_headers():
        """
        for PHP.
        :return:
        """
        return {
            'User-Agent': 'stormx_selenium_test'
        }

    def logout(self, cookies):
        url = _php_host + '/admin/index.php?logout=true'
        query_parameters = {

        }
        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'
        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)
        self.assertEqual(response.status_code, 200)

    def search_hotel(self, hotel_id, cookies, port_id):
        """
        :param hotel_id: integer
        :pram port_id: integer
        :return: dict
        """
        url = _php_host + '/admin/hotels.php'
        query_parameters = {
            'type': 'search',
            'status': 1,
            'hid': hotel_id

        }
        if port_id is not None:
            query_parameters['pid'] = port_id

        headers = self._generate_stormx_php_headers()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['X-TVA-Internal'] = '1'
        headers['Accept-Language'] = 'en-US,en;q=0.9'

        response = requests.get(url, headers=headers, cookies=cookies, params=query_parameters)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        return response_json

    def add_hotel_availability(self, hotel_id, airline_id, availability_date, cookies,
                               blocks=0, block_price='0',
                               ap_block_type=0,
                               issued_by='Theresa May',
                               comment='Automated avails by Selenium...',
                               room_type=1, pay_type='0',
                               verify_response_success=True,
                               hotel_contract_block_id = 0,
                               hotel_soft_block_id=0):

        """
        Add hotel availability using PHP admin site.

        :param hotel_id:  integer
        :param availability_date: `date` object

        :return:
        """
        response = self.create_hotel_availability(hotel_id, airline_id, availability_date, cookies,
                                                  blocks, block_price, ap_block_type,
                                                  issued_by, comment, room_type, pay_type,
                                                  verify_response_success, hotel_contract_block_id, hotel_soft_block_id)
        response_json = response.json()
        if verify_response_success:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json['success'], '1')
        return response_json

    def create_hotel_availability(self, hotel_id, airline_id, availability_date, cookies,
                                  blocks=0, block_price='0',
                                  ap_block_type=0,
                                  issued_by='Theresa May',
                                  comment='Automated avails by Selenium...',
                                  room_type=1, pay_type=0,
                                  verify_response_success=True, hotel_contract_block_id=0, hotel_soft_block_id=0):

        url = _php_host + '/admin/remote/helper.php?type=updateAvailsNew'
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
            'pay_type': pay_type,
            'hotel_contract_block_id': hotel_contract_block_id,
            'hotel_soft_block_id': hotel_soft_block_id
        }

        response = requests.post(url, headers=headers, cookies=cookies, data=form_data)
        return response
