"""This class contains unit tests for additional contacts"""

from stormx_verification_framework import (StormxSystemVerification)

class TestAdditionalContacts(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """

    hotel_id = 85690
    transport_id = 103224
    airline_id = 146

    def test_hotel_addition_contact_with_valid_data(self):
        """
        hotel addition contact with valid data is saved successfully
        """

        contact_post_data = self.get_addition_contact_post_data()
        response_json = self.add_addition_contact(contact_post_data, self.hotel_id, 'h')
        self.assertTrue(response_json['success'], "Success should be true on successful creation of contact")

    def test_hotel_addition_contact_with_invalid_data(self):
        """
        hotel addition contact with invalid data is not saved
        """

        contact_post_data = self.get_addition_contact_post_data()
        contact_post_data['email'] = 'test@tv(linc).blackhole'
        response_json = self.add_addition_contact(contact_post_data, self.hotel_id, 'h')
        self.assertFalse(response_json['success'], "Success should be false when invalid data is passed")

    def test_transport_addition_contact_with_valid_data(self):
        """
        transport addition contact with valid data is saved successfully
        """

        contact_post_data = self.get_addition_contact_post_data()
        response_json = self.add_addition_contact(contact_post_data, self.transport_id, 't')
        self.assertTrue(response_json['success'], "Success should be true on successful creation of contact")

    def test_transport_addition_contact_with_invalid_data(self):
        """
        transport addition contact with invalid data is not saved
        """

        contact_post_data = self.get_addition_contact_post_data()
        contact_post_data['email'] = 'test@tv(linc).blackhole'
        response_json = self.add_addition_contact(contact_post_data, self.transport_id, 't')
        self.assertFalse(response_json['success'], "Success should be false when invalid data is passed")

    def test_airline_addition_contact_with_valid_data(self):
        """
        airline addition contact with valid data is saved successfully
        """

        contact_post_data = self.get_addition_contact_post_data()
        response_json = self.add_addition_contact(contact_post_data, self.airline_id, 'a')
        self.assertTrue(response_json['success'], "Success should be true on successful creation of contact")

    def test_airline_addition_contact_with_invalid_data(self):
        """
        airline addition contact with invalid data is not saved
        """

        contact_post_data = self.get_addition_contact_post_data()
        contact_post_data['email'] = 'test@tv(linc).blackhole'
        response_json = self.add_addition_contact(contact_post_data, self.airline_id, 'a')
        self.assertFalse(response_json['success'], "Success should be false when invalid data is passed")
