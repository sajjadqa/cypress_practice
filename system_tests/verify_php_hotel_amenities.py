"""This class contains unit tests for amenities and hotel amenities"""

import uuid
import requests
import faker

from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestPhpAmenities(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    HOTEL = 83900  # Hilton Pasadena
    HOTEL_PORT = 'LAX'
    AIRLINE = 'Purple Rain Airlines'

    @classmethod
    def setUpClass(cls):
        super(TestPhpAmenities, cls).setUpClass()

    def test_amenity_creation(self):
        """test amenity creation with default data"""

        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '1',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)
        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        self.deactivate_amenity(amenity)

    def test_amenity_edit(self):
        """test amenity update after creation"""

        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '1',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # Edit amenity

        amenity['is_available'] = '0'
        amenity['operating_hours_allowed'] = '1'
        amenity['fee_allowed'] = '0'
        amenity['show_icon_on_hotel_listing'] = '1'
        amenity['icon'] = 'fas fa-hammer'

        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        self.deactivate_amenity(amenity)

    def test_amenity_name_should_not_be_updated(self):
        """test amenity name can not be updated through UI"""

        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '1',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # Edit amenity name
        amenity_name_updated = uuid.uuid4().hex[:12]

        response = self.add_edit_amenity(
            amenity_name=amenity_name_updated,
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        # compare response against original amenity
        self.verify_amenity_in_response(amenity, response['amenities'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity(self):
        """test enabling amenity for a hotel"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '0',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel
        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': None,
            'hotel_amenity_operated_to': None,
            'amenity_fee': '0',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_updating_hotel_amenity(self):
        """test updating amenity details for hotel"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '1',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel
        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': None,
            'hotel_amenity_operated_to': None,
            'amenity_fee': '0',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        # updating amenity
        hotel_amenity['amenity_fee'] = '12.98'
        hotel_amenity['comment'] = 'testing update via system test'
        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_deactivating_hotel_amenity(self):
        """test disabling amenity for hotel"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '0',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel
        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': None,
            'hotel_amenity_operated_to': None,
            'amenity_fee': '0',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        # Disabling amenity for hotel
        hotel_amenity['is_available'] = '0'
        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity_long_comment(self):
        """test adding long amenity comment for hotel"""
        fake = faker.Faker()

        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '0',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel
        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': None,
            'hotel_amenity_operated_to': None,
            'amenity_fee': '0',
            'is_available': '1',
            'comment': fake.pystr(min_chars=76, max_chars=150)
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], False)
        self.assertNotIn('amenities', response)
        self.assertIn('error', response)
        self.assertIn('Invalid comment - max length allowed:', response['error'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity_with_fee_allowed(self):
        """test adding hotel amenity with valid fee"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '1',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel

        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': None,
            'hotel_amenity_operated_to': None,
            'amenity_fee': '10.08',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity_with_fee_not_allowed(self):
        """test adding hotel amenity with fee not allowed"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '0',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel

        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': None,
            'hotel_amenity_operated_to': None,
            'amenity_fee': '20.08',
            'is_available': '1',
            'comment': 'testing via system test'

        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity_with_invalid_fee(self):
        """test adding hotel amenity with invalid fee"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '1',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel

        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': None,
            'hotel_amenity_operated_to': None,
            'amenity_fee': 'abcd',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        # amenity fee should be 0
        hotel_amenity['amenity_fee'] = '0'
        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity_with_operating_hours_allowed(self):
        """test adding hotel amenity with operating hours allowed"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '1',
            'fee_allowed': '0',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel

        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': "08:00",
            'hotel_amenity_operated_to': "10:30",
            'amenity_fee': '0',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity_with_operating_hours_not_allowed(self):
        """test adding hotel amenity with operating hours not allowed"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '0',
            'fee_allowed': '0',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel

        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': "09:00",
            'hotel_amenity_operated_to': "11:30",
            'amenity_fee': '0',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        hotel_amenity = self.verify_hotel_amenity_in_response(
            hotel_amenity, response['amenities'], amenity['fee_allowed'], amenity['operating_hours_allowed'])

        self.deactivate_amenity(amenity)

    def test_adding_hotel_amenity_with_invalid_operating_hours(self):
        """test adding hotel amenity with invalid operating hours"""
        amenity = {
            'id': 0,
            'amenity_name': uuid.uuid4().hex[:12],
            'is_available': '1',
            'operating_hours_allowed': '1',
            'fee_allowed': '0',
            'show_icon_on_hotel_listing': '0',
            'icon': None
        }

        # Add new amenity
        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )
        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        amenity = self.verify_amenity_in_response(amenity, response['amenities'])

        # enable newly added amenity on hotel

        hotel_amenity = {
            'id': 0,
            'amenity_master_id': amenity['id'],
            'allow_operating_hours': '0',
            'hotel_amenity_operated_from': "33:00",
            'hotel_amenity_operated_to': "34:30",
            'amenity_fee': '0',
            'is_available': '1',
            'comment': 'testing via system test'
        }

        response = self.add_edit_hotel_amenity(hotel_id=self.HOTEL,
                                               hotel_amenity_id=hotel_amenity['id'],
                                               amenity_id=hotel_amenity['amenity_master_id'],
                                               amenity_fee=hotel_amenity['amenity_fee'],
                                               allow_operating_hours=hotel_amenity['allow_operating_hours'],
                                               hotel_amenity_operated_from=hotel_amenity['hotel_amenity_operated_from'],
                                               hotel_amenity_operated_to=hotel_amenity['hotel_amenity_operated_to'],
                                               available=hotel_amenity['is_available'],
                                               comment=hotel_amenity['comment'])

        self.assertEqual(response['success'], False)
        self.assertNotIn('amenities', response)
        self.assertIn('error', response)
        self.assertIn('Invalid operating hours found', response['error'])

        self.deactivate_amenity(amenity)

    def test_hotel_amenities_mapping_with_master_activating_amenities(self):
        """test default amenities on hotel master are updated with hotel amenities"""
        hotel_id = self.HOTEL

        pets_amenity = {
                'id': 0,
                'amenity_master_id': 3,
                'amenity_name': 'Pets Allowed',
                'allow_operating_hours': False,
                'hotel_amenity_operated_from': None,
                'hotel_amenity_operated_to': None,
                'amenity_fee': '10.23',
                'is_available': True,
                'comment': 'testing via system test'
            }
        serviced_pets_amenity = {
                'id': 0,
                'amenity_master_id': 20,
                'amenity_name': 'Service Pets',
                'allow_operating_hours': False,
                'hotel_amenity_operated_from': None,
                'hotel_amenity_operated_to': None,
                'amenity_fee': '20.55',
                'is_available': True,
                'comment': 'testing via system test'
            }
        shuttle_amenity = {
                'id': 0,
                'amenity_master_id': 1,
                'amenity_name': 'Hotel Shuttle',
                'allow_operating_hours': False,
                'hotel_amenity_operated_from': '08:00',
                'hotel_amenity_operated_to': '18:00',
                'amenity_fee': '12.05',
                'is_available': True,
                'comment': 'testing via system test'
            }

        response = self.add_edit_hotel_amenities(hotel_id=hotel_id, hotel_amenities=[
            pets_amenity, serviced_pets_amenity, shuttle_amenity])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        headers = self._generate_airline_headers(customer=self.AIRLINE)
        hotel_url = self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=' + self.HOTEL_PORT

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id, 294, event_date, ap_block_type=1, block_price='150.00',
                                    blocks=5, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)

        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        self.assertIsNotNone(hotel_object)

        # validate pets amenity
        self.assertIn({'name': pets_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(pets_amenity['is_available'], hotel_object['pets_allowed'])
        self.assertEqual(pets_amenity['amenity_fee'], hotel_object['pets_fee'])

        # validate serviced pet amenity
        self.assertIn({'name': serviced_pets_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(serviced_pets_amenity['is_available'], hotel_object['service_pets_allowed'])
        self.assertEqual(serviced_pets_amenity['amenity_fee'], hotel_object['service_pets_fee'])

        # validate hotel shuttle amenity
        self.assertIn({'name': shuttle_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(shuttle_amenity['is_available'], hotel_object['shuttle'])
        self.validate_shuttle_time(shuttle_amenity['hotel_amenity_operated_from'], shuttle_amenity['hotel_amenity_operated_to'],hotel_object['shuttle_timing'])

    def test_hotel_amenities_mapping_with_master_deactivating_amenities(self):
        hotel_id = self.HOTEL

        pets_amenity = {
                'id': 0,
                'amenity_master_id': 3,
                'amenity_name': 'Pets Allowed',
                'allow_operating_hours': False,
                'hotel_amenity_operated_from': None,
                'hotel_amenity_operated_to': None,
                'amenity_fee': '50.23',
                'is_available': False,
                'comment': 'testing via system test'
            }
        serviced_pets_amenity = {
                'id': 0,
                'amenity_master_id': 20,
                'amenity_name': 'Service Pets',
                'allow_operating_hours': False,
                'hotel_amenity_operated_from': None,
                'hotel_amenity_operated_to': None,
                'amenity_fee': '100.55',
                'is_available': False,
                'comment': 'testing via system test'
            }
        shuttle_amenity = {
                'id': 0,
                'amenity_master_id': 1,
                'amenity_name': 'Hotel Shuttle',
                'allow_operating_hours': False,
                'hotel_amenity_operated_from': None,
                'hotel_amenity_operated_to': None,
                'amenity_fee': '12.05',
                'is_available': False,
                'comment': 'testing via system test'
            }

        response = self.add_edit_hotel_amenities(hotel_id=hotel_id, hotel_amenities=[
            pets_amenity, serviced_pets_amenity, shuttle_amenity])

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        headers = self._generate_airline_headers(customer=self.AIRLINE)
        hotel_url = self._api_host + '/api/v1/hotels?provider=tvl&room_count=1&port=' + self.HOTEL_PORT

        # add inventory
        event_date = self._get_event_date('America/Los_Angeles')
        self.add_hotel_availability(hotel_id, 294, event_date, ap_block_type=1,
                                    block_price='150.00', blocks=5, pay_type='0')

        hotel_response = requests.get(hotel_url, headers=headers)

        self.assertEqual(hotel_response.status_code, 200)
        hotel_response_json = hotel_response.json()
        self.assertIs(hotel_response_json['error'], False)
        self.assertGreater(len(hotel_response_json['data']), 0)

        hotel_object = None
        for hotel in hotel_response_json['data']:
            if hotel['hotel_id'] == 'tvl-' + str(hotel_id):
                hotel_object = hotel

        self.assertIsNotNone(hotel_object)

        # validate pets amenity
        self.assertNotIn({'name': pets_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(pets_amenity['is_available'], hotel_object['pets_allowed'])

        # validate serviced pet amenity
        self.assertNotIn({'name': serviced_pets_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(serviced_pets_amenity['is_available'], hotel_object['service_pets_allowed'])

        # validate hotel shuttle amenity
        self.assertNotIn({'name': shuttle_amenity['amenity_name']}, hotel_object['amenities'])
        self.assertEqual(shuttle_amenity['is_available'], hotel_object['shuttle'])

    def verify_amenity_in_response(self, amenity, amenities):
        """
        verify php response, find updated amenity in the response and verify the information
        param amenity: Dict
        param amenities: List of Dict
        return Dict
        """
        updated_amenity = None
        amenity['id'] = int(amenity['id'])

        for a in amenities:
            a['id'] = int(a['id'])
            if((amenity['id'] > 0 and amenity['id'] == a['id']) or amenity['amenity_name'] == a['amenity_name']):
                updated_amenity = a

        self.assertIsNot(updated_amenity, None, 'Updated amenity not found in response')

        self.assertGreater(updated_amenity['id'], 0)
        self.assertEqual(amenity['amenity_name'], updated_amenity['amenity_name'])
        self.assertEqual(amenity['is_available'], updated_amenity['is_available'])
        self.assertEqual(amenity['operating_hours_allowed'], updated_amenity['operating_hours_allowed'])
        self.assertEqual(amenity['fee_allowed'], updated_amenity['fee_allowed'])
        self.assertEqual(amenity['show_icon_on_hotel_listing'], updated_amenity['show_icon_on_hotel_listing'])
        self.assertEqual('' if amenity['icon'] is None else amenity['icon'], updated_amenity['icon'])

        return updated_amenity

    def deactivate_amenity(self, amenity):
        """
        disable amenity
        param amenity: Dict
        """
        amenity['is_available'] = '0'

        response = self.add_edit_amenity(
            amenity_name=amenity['amenity_name'],
            amenity_id=amenity['id'],
            is_available=amenity['is_available'],
            operating_hours_allowed=amenity['operating_hours_allowed'],
            fee_allowed=amenity['fee_allowed'],
            show_icon_on_hotel_listing=amenity['show_icon_on_hotel_listing'],
            icon=amenity['icon']
        )

        self.assertEqual(response['success'], True)
        self.assertIn('amenities', response)

        self.verify_amenity_in_response(amenity, response['amenities'])

    def verify_hotel_amenity_in_response(self, hotel_amenity, amenities, fee_allowed=True,
                                         operating_hours_allowed=True):
        """
        verify php response, find updated hotel amenity in the response and verify the information
        param hotel_amenity: Dict
        param amenities: List of Dict
        param fee_allowed: bool
        param operating_hours_allowed: bool
        return Dict
        """
        updated_amenity = self.extract_hotel_amenity_from_response(hotel_amenity, amenities)

        self.assertIsNot(updated_amenity, None, 'Updated hotel amenity not found in response')

        self.assertGreater(int(updated_amenity['id']), 0)
        self.assertEqual(int(hotel_amenity['amenity_master_id']), int(updated_amenity['amenity_master_id']))

        self.assertEqual(hotel_amenity['hotel_amenity_operated_from'] if int(operating_hours_allowed) else None,
                         updated_amenity['hotel_amenity_operated_from'])
        self.assertEqual(hotel_amenity['hotel_amenity_operated_to'] if int(operating_hours_allowed) else None,
                         updated_amenity['hotel_amenity_operated_to'])

        self.assertEqual(
            '0' if hotel_amenity['amenity_fee'] == '' or not int(fee_allowed) else hotel_amenity['amenity_fee'],
            '0' if updated_amenity['amenity_fee'] == '' else updated_amenity['amenity_fee'])

        self.assertEqual(hotel_amenity['is_available'], updated_amenity['is_available'])
        self.assertEqual('' if hotel_amenity['comment']
                         is None else hotel_amenity['comment'], updated_amenity['comment'])

        return updated_amenity

    def extract_hotel_amenity_from_response(self, hotel_amenity, amenities):
        """
        extract updated hotel amenity in the response
        param hotel_amenity: Dict
        param amenities: List of Dict
        return Dict
        """
        updated_amenity = None
        hotel_amenity['amenity_master_id'] = int(hotel_amenity['amenity_master_id'])

        for amenity in amenities:
            amenity['amenity_master_id'] = int(amenity['amenity_master_id'])
            if(hotel_amenity['amenity_master_id'] == amenity['amenity_master_id']):
                amenity['hotel_amenity_operated_from'] = amenity['hotel_amenity_operated_from']['label'] \
                    if amenity['hotel_amenity_operated_from'] else None
                amenity['hotel_amenity_operated_to'] = amenity['hotel_amenity_operated_to']['label'] \
                    if amenity['hotel_amenity_operated_to'] else None
                updated_amenity = amenity
                break

        return updated_amenity

    def validate_shuttle_time(self, operating_from, operating_to, shuttle_timing):
        """
            format operating hours and validate against shuttle time returned from server
        """
        operating_time = '' #shuttle is not serviced
        if operating_from and operating_to:
            start_hours, start_minutes = operating_from.split(':')
            end_hours, end_minutes = operating_to.split(':')
            hours_minutes_list = [start_hours, start_minutes, end_hours, end_minutes]
            if all(value == "00" for value in hours_minutes_list):
                operating_time = '0:00 23:59'
            else:
                operating_time = str(int(start_hours)) + ':' + start_minutes.zfill(2) + ' ' + str(int(end_hours)) + ':' + end_minutes.zfill(2)
        
        self.assertEqual(operating_time, shuttle_timing)

