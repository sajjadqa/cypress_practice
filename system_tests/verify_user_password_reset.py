"""This class contains unit tests for password reset"""

import hashlib
import faker
import unittest
import requests

from stormx_verification_framework import StormxSystemVerification


class UserPasswordResetTestCase(StormxSystemVerification):
    response_codes = {'reset_password': {'success': 1003, 'passwords_not_matching': 1002, 'url_expired': 1001, 'invalid_pattern':1004}}

    @classmethod
    def setUpClass(cls):
        super(UserPasswordResetTestCase, cls).setUpClass()
        cls.tva_user = cls.create_new_tva_user(cls)

    @classmethod
    def tearDownClass(cls):
        cls.delete_tva_user(cls.tva_user['user_id'])

    def test_password_reset_api_with_new_user(self):
        """
        test password reset when new user is created
        """
        if self.selected_environment_name == "dev":
            raise unittest.SkipTest("requires an email to be sent and emails don't work on local")
        response = self.submit_reset_password_request(self.tva_user['user_login_id'])
        self.assertTrue(response['status'])

    def test_password_reset_api_with_invalid_username(self):
        """
        test password reset with invalid username
        """
        response = self.submit_reset_password_request("invalid_username")
        self.assertFalse(response['status'])

    def test_password_reset_api_with_empty_username(self):
        """
        test password reset with empty username
        """
        response = self.submit_reset_password_request("")
        self.assertFalse(response['status'])

    def test_change_password_api_with_valid_data(self):
        """
        test change password with valid post data
        """
        fake = faker.Faker()
        new_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        response = self.submit_change_password_request(self.tva_user['user_id'], self.tva_user['newUserP'],
                                                       new_password, new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['success'])

    def test_change_password_api_with_different_confirm_new_password(self):
        """
        test change password with different confirm new password
        """
        fake = faker.Faker()
        new_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        confirm_new_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        response = self.submit_change_password_request(self.tva_user['user_id'], self.tva_user['newUserP'],
                                                       new_password, confirm_new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['passwords_not_matching'])

    def test_change_password_api_for_invalid_data(self):
        """
        test change password with invalid post data
        """
        fake = faker.Faker()
        new_password = fake.password(length=10)
        response = self.submit_change_password_request(fake.pyint(), fake.password(length=10),
                                                       new_password, new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['url_expired'])

    def test_change_password_api_with_invalid_length(self):
        fake = faker.Faker()
        new_password = fake.password(length=80, special_chars=True, digits=True, upper_case=True, lower_case=True)
        response = self.submit_change_password_request(self.tva_user['user_id'], self.tva_user['newUserP'],
                                                       new_password, new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['invalid_pattern'])

    def test_change_password_api_with_no_digit(self):
        fake = faker.Faker()
        new_password = fake.password(length=10, special_chars=True, digits=False, upper_case=True, lower_case=True)
        response = self.submit_change_password_request(self.tva_user['user_id'], self.tva_user['newUserP'],
                                                       new_password, new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['invalid_pattern'])

    def test_change_password_api_with_no_special_char(self):
        fake = faker.Faker()
        new_password = fake.password(length=10, special_chars=False, digits=True, upper_case=True, lower_case=True)
        response = self.submit_change_password_request(self.tva_user['user_id'], self.tva_user['newUserP'],
                                                       new_password, new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['invalid_pattern'])


    def test_change_password_api_with_no_upper_case(self):
        fake = faker.Faker()
        new_password = fake.password(length=10, special_chars=True, digits=True, upper_case=False, lower_case=True)
        response = self.submit_change_password_request(self.tva_user['user_id'], self.tva_user['newUserP'],
                                                       new_password, new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['invalid_pattern'])

    def test_change_password_api_with_no_lower_case(self):
        fake = faker.Faker()
        new_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=False)
        response = self.submit_change_password_request(self.tva_user['user_id'], self.tva_user['newUserP'],
                                                       new_password, new_password)
        self.assertEqual(response['status_code'], self.response_codes['reset_password']['invalid_pattern'])

    def submit_reset_password_request(self, username):
        """
        test submit reset password request
        :param username: str
        :return: json
        """
        url = self._php_host + '/admin/user_detail.php?type=resetPassword'
        data = {
            'username': username,
        }
        response = requests.post(url, headers=self._generate_stormx_php_headers(), cookies=self._support_cookies,
                                 data=data)
        return response.json()

    def submit_change_password_request(self, user_id, password, new_password, confirm_new_password):
        """
        test submit change password request
        :param user_id: str
        :param password: str
        :param new_password: str
        :param confirm_new_password: str
        :return: json
        """
        url = self._php_host + '/admin/index.php'
        token = 'sha256$$' + hashlib.sha256(str(password).encode('utf-8')).hexdigest() + "***" + str(user_id)
        data = {
            'token': token,
            'rPwd': new_password,
            'cPwd': confirm_new_password,
            'mode': 'reset'
        }
        response = requests.post(url, headers=self._generate_stormx_php_headers(),
                                 data=data)
        return response.json()
