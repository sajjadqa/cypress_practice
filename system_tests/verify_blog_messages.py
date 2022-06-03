import faker
from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestBlogMessages(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
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
        Create Airline users with different roles in order to test blog messages
        """
        super(TestBlogMessages, cls).setUpClass()
        cls.user_list = cls.get_login_users_list(cls.port_id, cls.airline_id, cls.hotel_id, cls.transport_id,
                                                 cls.user_types)

        cls.user_list.append({'username': cls.support_username, 'user_type': 'tva',
                              'cookies': cls.login_to_stormx(cls.support_username, cls.support_user_password)})

    def test_create_blog_message(self):
        """
        test verify create blog messages
        """
        arr = {
            't': self.transport_id,
            'a': self.airline_id,
            'h': self.hotel_id,
            'p': self.port_id
        }

        for user in self.user_list:
            for type, id in arr.items():
                fake = faker.Faker()
                message = fake.sentence()
                response = self.add_blog_message(id, type, message, user.get('cookies'))
                if user.get('user_type') != 'tva':
                    self.assertEqual(response.get('success'), False)
                    self.assertEqual("You are not allowed to view this page", response.get('error'))
                else:
                    self.assertGreater(len(response.get('messageLatest')), 0)
                    self.assertEqual(response.get('messageLatest')["message"], message)
                    self.assertEqual(response.get('success'), 'true')

    def test_create_blog_message_without_login(self):
        """
        test verify create blog messages without login
        """
        arr = {
            't': self.transport_id,
            'a': self.airline_id,
            'h': self.hotel_id,
            'p': self.port_id
        }

        for type, id in arr.items():
            fake = faker.Faker()
            message = fake.sentence()
            response = self.add_blog_message(id, type, message, {})
            self.assertEqual('You are not logged in' in response.get('loginError'), True)

    def test_create_blog_message_with_invalid_data(self):
        """
        test verify create blog messages with invalid data
        """

        # Test with invalid id
        arr = {
            't': '!#@',
            'a': '!#@',
            'h': '!#@',
            'p': '!#@'
        }
        for type, id in arr.items():
            fake = faker.Faker()
            message = fake.sentence()
            response = self.add_blog_message(id, type, message, None)
            self.assertEqual(response.get('success'), False)
            self.assertEqual(response.get('msg'), "Id should be an integer, string given.")

        # Test with invalid blog type
        arr = {
            'invalid1': self.transport_id,
            'invalid2': self.airline_id,
            'invalid3': self.hotel_id,
            'invalid3': self.port_id
        }
        for type, id in arr.items():
            fake = faker.Faker()
            message = fake.sentence()
            response = self.add_blog_message(id, type, message, None)
            self.assertEqual(response.get('success'), False)
            self.assertEqual(response.get('msg'), "Invalid blog type given.")

        # Test with empty id
        fake = faker.Faker()
        message = fake.sentence()
        response = self.add_blog_message("", 't', message, None)
        self.assertEqual(response.get('success'), False)
        self.assertEqual(response.get('msg'), "Id is required.")

        # Test with empty blog message
        arr = {
            't': self.transport_id,
            'a': self.airline_id,
            'h': self.hotel_id,
            'p': self.port_id
        }
        for type, id in arr.items():
            response = self.add_blog_message(int(id), type, "", None)
            self.assertEqual(response.get('success'), False)
            self.assertEqual(response.get('msg'), "Message is required.")


    def test_read_blog_message_without_login(self):
        """
        test verify read blog messages without login
        """
        arr = {
            't': self.transport_id,
            'a': self.airline_id,
            'h': self.hotel_id,
            'p': self.port_id
        }

        for type, id in arr.items():
            fake = faker.Faker()
            message = fake.sentence()
            response = self.add_blog_message(id, type, message, {})
            self.assertEqual('You are not logged in' in response.get('loginError'), True)

    def test_read_blog_message(self):
        """
        test verify read blog messages
        """
        arr = {
            't': self.transport_id,
            'a': self.airline_id,
            'h': self.hotel_id,
            'p': self.port_id
        }

        for user in self.user_list:
            for type, id in arr.items():
                fake = faker.Faker()
                message = fake.sentence()
                create_blog_response = self.add_blog_message(id, type, message, user.get('cookies'))
                read_blog_response = self.read_blog_messages(id, type, user.get('cookies'))

                if user.get('user_type') != 'tva':
                    self.assertEqual(create_blog_response.get('success'), False)
                    self.assertEqual("You are not allowed to view this page", create_blog_response.get('error'))
                    self.assertEqual(read_blog_response.get('success'), False)
                    self.assertEqual("You are not allowed to view this page", read_blog_response.get('error'))
                else:
                    self.assertGreater(len(create_blog_response.get('messageLatest')), 0)
                    self.assertEqual(create_blog_response.get('messageLatest')["message"], message)
                    self.assertEqual(create_blog_response.get('success'), 'true')

                    self.assertGreater(len(read_blog_response.get('messageLatest')), 0)
                    self.assertEqual(read_blog_response.get('messageLatest')["message"], message)
                    self.assertEqual(read_blog_response.get('success'), 'true')
                    self.assertEqual(read_blog_response.get('messageLatest'), create_blog_response.get('messageLatest'))

    def test_mark_blog_message_unread(self):
        """
        test verify mark blog message unread
        """
        arr = {
            't': self.transport_id,
            'a': self.airline_id,
            'h': self.hotel_id,
            'p': self.port_id
        }

        for user in self.user_list:
            for type, id in arr.items():
                fake = faker.Faker()
                message = fake.sentence()
                create_blog_response = self.add_blog_message(id, type, message, user.get('cookies'))

                if user.get('user_type') != 'tva':
                    self.assertEqual(create_blog_response.get('success'), False)
                    self.assertEqual("You are not allowed to view this page", create_blog_response.get('error'))
                else:
                    self.assertGreater(len(create_blog_response.get('messageLatest')), 0)
                    self.assertEqual(create_blog_response.get('messageLatest')["message"], message)
                    self.assertEqual(create_blog_response.get('success'), 'true')

                    #mark message unread
                    mark_blog_message_response = self.mark_blog_message_unread(id, type, create_blog_response.get(
                        'messageLatest')["id"], 0, user.get('cookies'))
                    self.assertEqual(mark_blog_message_response.get('success'), 'true')

                    # verify unread message recently marked unread
                    read_blog_response = self.read_blog_messages(id, type, user.get('cookies'))
                    self.assertEqual(int(read_blog_response.get("messages")[0]['isRead']), 0)
