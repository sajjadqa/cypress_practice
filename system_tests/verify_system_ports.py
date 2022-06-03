"""This class contains unit tests for search system ports"""

from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestSystemPorts(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    HOTEL_LIST = [103210,
                  100241]   # 103210 = Holiday Inn - Chicago / Oakbrook,
                            # 100241 = Fairfield Inn & Suites - Chicago Midway
    AIRLINE_ID = 146  # Jetstar Asia
    PORT_ID = 654  # Chicago Midway International Airport
    SUPPORT_USERNAME = 'support'
    SUPPORT_USERPASSWORD = 'test'
    user_list = []
    allowance = 2

    @classmethod
    def setUpClass(cls):
        """
        Create Airline users with different roles in order to test quick room transfer voucher
        """
        super(TestSystemPorts, cls).setUpClass()
        cls.user_list = cls.create_airline_users_with_different_roles(cls.PORT_ID,
                                                                      cls.AIRLINE_ID)
        cls.user_list.append({'username': cls.SUPPORT_USERNAME,
                              'cookies': cls.login_to_stormx(cls.SUPPORT_USERNAME,
                                                             cls.SUPPORT_USERPASSWORD)})

    def test_ports_by_name_or_prefix(self):
        """
        Port list search test
        :return: a list of ports
        """
        for user in self.user_list:
            if user.get('role_id') == 11 or user.get('role_id') == 12:
                response = self.get_all_ports(query='MDW',
                                              user_specific_port_only='1',
                                              cookies=user.get('cookies'))
            else:
                response = self.get_all_ports(query='MDW', cookies=user.get('cookies'))

            response_json = response.json()
            self.assertEqual(len(response_json), 1)
            self.assertEqual(response_json[0]['prefix'], 'MDW')

    def test_ports_with_no_query(self):
        """
        Port list search with no query test
        :return: a list of ports
        """
        for user in self.user_list:
            if user.get('role_id') == 11 or user.get('role_id') == 12:
                response = self.get_all_ports(query='',
                                              user_specific_port_only='1',
                                              cookies=user.get('cookies'))
                response_json = response.json()
                self.assertEqual(len(response_json), 1)
            else:
                response = self.get_all_ports(query='', cookies=user.get('cookies'))
                response_json = response.json()
                self.assertGreater(len(response_json), 0)

    def test_search_ports_by_invalid_name_or_prefix(self):
        """
        Port list search with invalid name or prefix test
        :return: empty list of ports
        """
        for user in self.user_list:
            response = self.get_all_ports(query='%$SSW@DEW',
                                          cookies=user.get('cookies'))
            response_json = response.json()
            self.assertEqual(len(response_json), 0)

    def test_ports_without_cookies(self):
        """
        Port list search test with no cookies(without login)
        :return: json with login error message
        """
        response = self.get_all_ports(query='', cookies={})
        response_json = response.json()
        self.assertEqual('You are not logged in' in response_json.get('loginError'), True)
