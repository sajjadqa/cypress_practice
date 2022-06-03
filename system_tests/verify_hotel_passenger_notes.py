"""This class contains unit tests for linking expedia hotels"""
import faker
from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestHotelPassengerNotes(StormxSystemVerification):
    """
    Verify Hotel port specific passenger notes
    """
    hotel_id = 103210  # 103210 = Holiday Inn - Chicago / Oakbrook
    transport_id = 103224  # 103224 = Airport Limo
    airline_id = 146  # Jetstar Asia
    port_id_serviced = 654  # MDW - Chicago Midway International Airport
    port_id_non_serviced = 1  # SYD - Sydney Airport

    support_username = 'support'
    support_user_password = 'test'
    user_list = []
    user_types = ["airline", "hotel", "transport"]

    @classmethod
    def setUpClass(cls):
        """
        Create users with different roles for testing
        """
        super(TestHotelPassengerNotes, cls).setUpClass()
        cls.user_list = cls.get_login_users_list(
            cls.port_id_serviced, cls.airline_id,
            cls.hotel_id, cls.transport_id, cls.user_types)

        cls.user_list.append({'username': cls.support_username,
                              'user_type': 'tva',
                              'cookies': cls.login_to_stormx(
                                  cls.support_username,
                                  cls.support_user_password)})

    def test_add_port_with_passenger_notes(self):
        """
        test add new port to hotel with passenger notes
        """
        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        inserted_id = serviced_port_response['id']
        self.assertGreater(inserted_id, 0)

        # remove port after test
        self.remove_hotel_serviced_port(self.hotel_id,
                                        self.port_id_non_serviced,
                                        inserted_id, None)

    def test_add_port_with_invalid_passenger_notes(self):
        """
        test add new port to hotel with passenger notes
        """
        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_invalid_passenger_note(),
            self.get_valid_ranking())

        self.assertGreater(len(serviced_port_response['error']), 0)
        self.assertEqual(
            serviced_port_response['error'],
            'Passenger notes should not be longer than 255 characters.')

    def test_add_existing_port_with_passenger_notes(self):
        """
        test add new port to hotel with passenger notes
        """
        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        self.assertGreater(len(serviced_port_response['error']), 0)
        self.assertEqual(serviced_port_response['error'],
                         'This port is already serviced by this hotel')

    def test_add_port_passenger_notes_with_different_users(self):
        """
        test addition of new ports to hotel with passenger notes with
        different user types (airline/hotel/transport/tva). Only TVA user is
        allowed to add/update hotel serviced ports
        """
        for user in self.user_list:
            user_type = user.get('user_type')
            user_cookie = user.get('cookies')

            serviced_port_response = self.add_hotel_serviced_port(
                self.port_id_non_serviced,
                self.hotel_id,
                user_cookie,
                self.get_valid_passenger_note(),
                self.get_valid_ranking())

            if user_type == "tva":
                inserted_id = serviced_port_response['id']
                self.assertGreater(inserted_id, 0)

                # remove port after test
                self.remove_hotel_serviced_port(
                    self.hotel_id, self.port_id_non_serviced,
                    inserted_id, user_cookie)
            elif user_type == "transport":
                self.assertGreater(
                    len(serviced_port_response['errMsgLogin']), 0)
                self.assertEqual(
                    serviced_port_response['errMsgLogin'],
                    'You do not have access to this page.')
            else:
                self.assertGreater(len(serviced_port_response['error']), 0)
                self.assertEqual(
                    serviced_port_response['error'],
                    'You are not authorized to perform this action.')

    def test_update_port_passenger_notes_with_different_users(self):
        """
        test modification of port passenger notes with different user
        types (airline/hotel/transport/tva). Only TVA user is
        allowed to add/update hotel serviced ports
        """

        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        inserted_id = serviced_port_response['id']
        self.assertGreater(inserted_id, 0)

        for user in self.user_list:
            user_type = user.get('user_type')
            user_cookie = user.get('cookies')

            update_response = self.update_hotel_serviced_port(
                inserted_id,
                self.port_id_non_serviced,
                self.hotel_id,
                self.get_valid_passenger_note(),
                self.get_valid_ranking(),
                user_cookie)

            if user_type == "tva":
                self.assertEqual(inserted_id, update_response['id'])
            elif user_type == "transport":
                self.assertGreater(
                    len(update_response['errMsgLogin']), 0)
                self.assertEqual(
                    update_response['errMsgLogin'],
                    'You do not have access to this page.')
            else:
                self.assertGreater(len(update_response['error']), 0)
                self.assertEqual(
                    update_response['error'],
                    'You are not authorized to perform this action.')

        # remove port after test
        self.remove_hotel_serviced_port(self.hotel_id,
                                        self.port_id_non_serviced,
                                        inserted_id, None)

    def test_update_port_passenger_note(self):
        """
        test updating serviced port with valid passenger notes
        """

        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        inserted_id = serviced_port_response['id']
        self.assertGreater(inserted_id, 0)

        update_response = self.update_hotel_serviced_port(
            inserted_id,
            self.port_id_non_serviced,
            self.hotel_id,
            self.get_valid_passenger_note(),
            self.get_valid_ranking(),
            None)
        self.assertEqual(inserted_id, update_response['id'])

        # remove port after test
        self.remove_hotel_serviced_port(self.hotel_id,
                                        self.port_id_non_serviced,
                                        inserted_id, None)

    def test_update_port_with_invalid_passenger_note(self):
        """
        test updating serviced port with invalid passenger notes
        """

        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        inserted_id = serviced_port_response['id']
        self.assertGreater(inserted_id, 0)

        update_response = self.update_hotel_serviced_port(
            inserted_id,
            self.port_id_non_serviced,
            self.hotel_id,
            self.get_invalid_passenger_note(),
            self.get_valid_ranking(),
            None)

        self.assertGreater(len(update_response['error']), 0)
        self.assertEqual(
            update_response['error'],
            'Passenger notes should not be longer than 255 characters.')

        # remove port after test
        self.remove_hotel_serviced_port(self.hotel_id,
                                        self.port_id_non_serviced,
                                        inserted_id, None)

    def test_add_port_with_invalid_ranking(self):
        """
        test add new port to hotel with invalid ranking
        """
        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_invalid_ranking())

        self.assertGreater(len(serviced_port_response['error']), 0)
        self.assertEqual(
            serviced_port_response['error'], 'Invalid hotel port ranking.')

    def test_update_port_with_invalid_ranking(self):
        """
        test updating serviced port with invalid ranking
        """

        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        inserted_id = serviced_port_response['id']
        self.assertGreater(inserted_id, 0)

        update_response = self.update_hotel_serviced_port(
            inserted_id,
            self.port_id_non_serviced,
            self.hotel_id,
            self.get_valid_passenger_note(),
            self.get_invalid_ranking(),
            None)

        self.assertGreater(len(update_response['error']), 0)
        self.assertEqual(
            update_response['error'], 'Invalid hotel port ranking.')

        # remove port after test
        self.remove_hotel_serviced_port(self.hotel_id,
                                        self.port_id_non_serviced,
                                        inserted_id, None)

    def test_remove_port_passenger_note(self):
        """
        test removing passenger notes from serviced port
        """
        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        inserted_id = serviced_port_response['id']
        self.assertGreater(inserted_id, 0)

        update_response = self.update_hotel_serviced_port(
            inserted_id,
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_ranking(),
            None)

        self.assertEqual(inserted_id, update_response['id'])

        # remove port after test
        self.remove_hotel_serviced_port(self.hotel_id,
                                        self.port_id_non_serviced,
                                        inserted_id, None)

    def test_port_remove(self):
        """
        test deleting port from hotel's serviced ports
        """
        serviced_port_response = self.add_hotel_serviced_port(
            self.port_id_non_serviced,
            self.hotel_id,
            None,
            self.get_valid_passenger_note(),
            self.get_valid_ranking())

        inserted_id = serviced_port_response['id']
        self.assertGreater(inserted_id, 0)

        # remove port after test
        self.remove_hotel_serviced_port(self.hotel_id,
                                        self.port_id_non_serviced,
                                        inserted_id, None)

    def get_valid_passenger_note(self):
        fake = faker.Faker()
        return fake.text(max_nb_chars=255, ext_word_list=None)

    def get_invalid_passenger_note(self):
        fake = faker.Faker()
        return fake.pystr(min_chars=260, max_chars=400)

    def get_valid_ranking(self):
        fake = faker.Faker()
        return fake.random_int(1, 999999)

    def get_invalid_ranking(self):
        fake = faker.Faker()
        return fake.word()
