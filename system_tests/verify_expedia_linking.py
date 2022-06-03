"""This class contains unit tests for linking expedia hotels"""

from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestExpediaLinking(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    expedia_rapid_id = 888888
    hotel_id = 103210  # 103210 = Holiday Inn - Chicago / Oakbrook
    transport_id = 103224  # 103224 = Airport Limo
    airline_id = 146  # Jetstar Asia
    port_id = 654  # Chicago Midway International Airport
    support_username = 'support'
    support_user_password = 'test'
    user_list = []
    user_types = ["airline", "hotel", "transport"]

    @classmethod
    def setUpClass(cls):
        """
        Create Airline users with different roles in order to test quick room transfer voucher
        """
        super(TestExpediaLinking, cls).setUpClass()
        cls.user_list = cls.get_login_users_list(cls.port_id, cls.airline_id, cls.hotel_id, cls.transport_id,
                                                 cls.user_types)

        cls.user_list.append({'username': cls.support_username, 'user_type': 'tva',
                              'cookies': cls.login_to_stormx(cls.support_username, cls.support_user_password)})

    def test_add_duplicate_expedia_id(self):
        """
        test verify duplicate expedia id in hotel
        """

        hotel_post_data = self.get_create_hotel_post_data('G')
        hotel_post_data['expedia_rapid_id'] = self.expedia_rapid_id
        response = self.add_or_update_hotel(hotel_post_data, 0, None)
        if int(response['success']) == 0:
            self.assertEqual(response['errMsg'], 'Expedia Rapid ID is associated to another hotel')
        else:
            self.assertEqual(response['success'], '1')
            self.assertGreater(response['id'], 0)
            self.assertEqual(response['errMsg'], 'Hotel information saved successfully.')

        hotel_post_data['expedia_rapid_id'] = self.expedia_rapid_id
        response = self.add_or_update_hotel(hotel_post_data, 0, None)
        self.assertEqual(response['success'], '0')
        self.assertEqual(response['errMsg'], 'Expedia Rapid ID is associated to another hotel')

    def test_verify_null_expedia_id(self):
        """
        test verify empty or zero expedia id
        """

        hotel_post_data = self.get_create_hotel_post_data('G')
        hotel_post_data['expedia_rapid_id'] = 0
        response = self.add_or_update_hotel(hotel_post_data, 0, None)
        self.assertEqual("id" in response, True)
        self.assertEqual(response['success'], '1')
        self.assertGreater(response['id'], 0)
        self.assertEqual(response['errMsg'], 'Hotel information saved successfully.')
        hotel_id = response['id']
        response = self.search_hotel(hotel_id)
        self.assertEqual(response['results'][0]['expedia_rapid_id'], None)

    def test_search_expedia_hotels_without_login_cookies(self):
        """
        test verify search expedia hotels without login
        """

        response = self.search_expedia_hotels(self.hotel_id, {})
        self.assertEqual('You are not logged in' in response.get('loginError'), True)

    def test_search_expedia_hotels_without_hotel_id(self):
        """
        test verify search expedia hotels without hotel id
        """

        response = self.search_expedia_hotels(0)
        self.assertEqual('Hotel ID is required to search for similar Expedia Hotels', response.get('error'))
        self.assertEqual(len(response.get('expedia_hotels')), 0)
        self.assertEqual(response.get('success'), False)

    def test_search_expedia_hotels(self):
        """
        test verify search expedia hotels
        """
        for user in self.user_list:
            response = self.search_expedia_hotels(self.hotel_id, user.get('cookies'))
            if user.get('user_type') != 'tva':
                self.assertEqual(len(response.get('expedia_hotels')), 0)
                self.assertEqual(response.get('success'), False)
                self.assertEqual("You are not authorized to perform this action.", response.get('error'))
            else:
                self.assertGreaterEqual(len(response.get('expedia_hotels')), 0)
                self.assertEqual(response.get('success'), True)

    def test_link_to_expedia_hotel_without_login_cookies(self):
        """
        test verify link to expedia hotel
        """

        expedia_rapid_id = 9090901
        response = self.link_to_expedia_hotel(self.hotel_id, expedia_rapid_id, {})
        self.assertEqual('You are not logged in' in response.get('loginError'), True)

    def test_link_to_expedia_hotel(self):
        """
        test verify link to expedia hotel
        """
        expedia_rapid_id = 9090901
        for user in self.user_list:
            if user.get('user_type') != 'tva':
                response = self.link_to_expedia_hotel(self.hotel_id, expedia_rapid_id, user.get('cookies'))
                self.assertEqual(response.get('success'), '0')
                self.assertEqual("You are not authorized to perform this action.", response.get('error'))
            else:
                response = self.link_to_expedia_hotel(self.hotel_id, expedia_rapid_id)
                error = 'Another Expedia rapid ID'
                if response.get('error') and error in response.get('error'):
                    self.assertEqual(error in response.get('error'), True)
                    self.assertEqual(response.get('success'), 0)
                else:
                    self.assertEqual(response.get('success'), '1')

                    hotel_post_data = self.get_create_hotel_post_data('G')
                    response = self.add_or_update_hotel(hotel_post_data, 0, None)
                    self.assertEqual("id" in response, True)
                    self.assertEqual(response['success'], '1')
                    self.assertGreater(response['id'], 0)
                    self.assertEqual(response['errMsg'], 'Hotel information saved successfully.')
                    hotel_id = response['id']
                    # Add hotel serviced port
                    serviced_port_response = self.add_hotel_serviced_port(self.port_id, hotel_id, cookies=None)
                    self.assertGreater(int(serviced_port_response['id']), 0)

                    response = self.link_to_expedia_hotel(hotel_id, expedia_rapid_id)
                    error = "Expedia Rapid ID ({}) is already assigned to another hotel(s)".format(expedia_rapid_id)
                    self.assertEqual(error in response.get('error'), True)

    def test_search_expedia_hotel_with_no_port(self):
        """
        test verify link to expedia hotel
        """
        hotel_post_data = self.get_create_hotel_post_data('G')
        hotel_post_response = self.add_or_update_hotel(hotel_post_data, 0, None)
        self.assertEqual("id" in hotel_post_response, True)
        hotel_id = hotel_post_response['id']
        response = self.search_expedia_hotels(hotel_id, None)
        self.assertEqual(response.get(
            'error'), 'Error occurred while trying to fetch Expedia hotels. Please make sure port is assigned to this hotel and try again. If the issue still persists contact Travelliance IT support.')
        self.assertEqual(response.get('success'), False)
