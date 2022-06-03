"""This class contains unit tests for port allowance"""

from random import randint
from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestPortAllowance(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    airline_id = 146  # Jetstar Asia
    port_id = 1  # Sydney
    allowance = 100
    temporary_allowance = 15
    additional_allowance = 10

    def test_add_port_allowance(self):
        """
        add port allowance test
        :param port_id: integer
        :param airline_id: integer
        :param allowance: integer
        :return: json with message and success flag
        """
        response = self.add_port_allowance(port_id=self.port_id, airline_id=self.airline_id,
                                           allowance=self.allowance)
        if response['success'] is True:
            self.assertEqual(response['success'], True)
            self.assertGreater(response['id'], 0)
            self.assertEqual(response['message'], "Allowance saved successfully.")

    def test_add_port_allowance_without_cookies(self):
        """
        add port allowance test
        :param port_id: integer
        :param airline_id: integer
        :param allowance: integer
        :return: json with login error message
        """
        response = self.add_port_allowance(port_id=self.port_id, airline_id=self.airline_id,
                                           allowance=self.allowance, cookies={})
        self.assertEqual('You are not logged in' in response.get('loginError'), True)

    def test_add_port_allowance_already_exists(self):
        """
        add port allowance test
        :param port_id: integer
        :param airline_id: integer
        :param allowance: integer
        :return: json with message and success flag
        """
        self.get_or_create_allowance()
        response = self.add_port_allowance(port_id=self.port_id, airline_id=self.airline_id,
                                           allowance=self.allowance)
        self.assertEqual(response['success'], False)
        self.assertEqual(response['message'], "A record with same port and airline already exists.")

    def test_add_port_allowance_with_invalid_inputs(self):
        """
        add port allowance test
        :param port_id: None
        :param airline_id: None
        :param allowance: string
        :return: json with message and success flag
        """

        response = self.add_port_allowance(port_id=None, airline_id=None,
                                           allowance='A')
        self.assertEqual(response['success'], False)
        self.assertEqual(response['message'], "Invalid value for allowance.")

    def test_add_temporary_port_allowance(self):
        """
        add port allowance test
        :param allowance: integer
        :param port_room_allowance_id: integer
        :return: json with message and success flag
        """

        allowance_id = self.get_or_create_allowance()
        response = self.add_temporary_port_allowance(
            port_room_allowance_id=int(allowance_id),
            allowance=self.temporary_allowance)
        if response['success'] is True:
            self.assertEqual(response['success'], True)
            self.assertGreater(response['id'], 0)
            self.assertEqual(response['message'], "Temporary allowance saved successfully.")

    def test_add_temporary_port_allowance_without_cookies(self):
        """
        add port allowance test
        :param allowance: integer
        :param port_room_allowance_id: integer
        :return: json with login error message
        """

        allowance_id = self.get_or_create_allowance()
        response = self.add_temporary_port_allowance(
            port_room_allowance_id=int(allowance_id),
            allowance=self.temporary_allowance, cookies={})
        self.assertEqual('You are not logged in' in response.get('loginError'), True)

    def test_add_temporary_port_allowance_with_invalid_inputs(self):
        """
        add temporary port allowance test
        :param port_room_allowance_id: None (expected int)
        :param allowance: string (expected int)
        :return: json with message and success flag
        """
        response = self.add_temporary_port_allowance(port_room_allowance_id=randint(10000, 100000), allowance='A')
        self.assertEqual(response['success'], False)
        self.assertEqual(response['message'], "Invalid value for temporary allowance.")

    def test_update_port_allowance(self):
        """
        update port allowance test
        :param id: integer
        :param port_id: integer
        :param airline_id: integer
        :param allowance: integer
        :return: json with message and success flag
        """
        allowance_id = self.get_or_create_allowance()
        if int(allowance_id) > 0:
            self.allowance = self.allowance + self.additional_allowance
            response = self.add_port_allowance(port_id=self.port_id,
                                               airline_id=self.airline_id,
                                               allowance=self.allowance, port_room_allowance_id=int(allowance_id),
                                               type="save_allowance")
            self.assertEqual(response['success'], True)
            self.assertEqual(str(response['id']), allowance_id)
            self.assertEqual(response['message'], "Allowance saved successfully.")

    def test_list_port_allowance(self):
        """
        list port allowance test
        :param type: string
        :param page: None
        :param port: None
        :param airline: None
        :param sortBy: integer
        :param perPage: integer
        :return: json with pagination array and results array
        """
        self.get_or_create_allowance()
        response = self.list_port_allowance(type='search',
                                            page=None,
                                            port=None,
                                            airline=None,
                                            sortBy=0,
                                            perPage=20)
        self.verify_port_allowance_list_response(response, per_page=20)

    def test_list_port_allowance_without_cookies(self):
        """
        list port allowance test
        :param type: string
        :param page: None
        :param port: None
        :param airline: None
        :param sortBy: integer
        :param perPage: integer
        :return: json with login error message
        """
        self.get_or_create_allowance()
        response = self.list_port_allowance(type='search',
                                            page=None,
                                            port=None,
                                            airline=None,
                                            sortBy=0,
                                            perPage=20,
                                            cookies={})
        self.assertEqual('You are not logged in' in response.get('loginError'), True)

    def test_search_in_list_port_allowance(self):
        """
        search port allowance list test
        :param type: string
        :param page: None
        :param port: integer
        :param airline: integer
        :param sortBy: integer
        :param perPage: integer
        return: json with pagination array and results array
        """
        allowance_id = self.get_or_create_allowance()
        response = self.list_port_allowance(type='search',
                                            page=None,
                                            port=self.port_id,
                                            airline=self.airline_id,
                                            sortBy=0,
                                            perPage=20)
        self.assertGreater(len(response['pagi']), 0)
        self.assertEqual(response['pagi']['perPage'], 20)
        self.assertEqual(type(response['pagi']['perPage']), int)
        self.assertEqual(response['pagi']['currentPage'], 1)
        self.assertEqual(type(response['pagi']['currentPage']), int)
        self.assertEqual(type(response['pagi']['totalRecords']), int)
        self.assertEqual(response['pagi']['recTo'], 1)
        self.assertEqual(response['pagi']['totalRecords'], 1)
        self.assertGreater(len(response['results']), 0)
        result = response['results'][0]
        new_allowance = self.allowance
        if int(result['allowance']) > self.allowance:
            new_allowance = self.allowance + self.additional_allowance
        self.assertEqual(result['airline_id'], str(self.airline_id))
        self.assertEqual(result['port_id'], str(self.port_id))
        self.assertEqual(result['allowance'], str(new_allowance))
        self.assertEqual(result['id'], str(allowance_id))
        total_allowance = int(new_allowance)
        temporary_allowance = 0
        if int(result['total_allowance']) > total_allowance:
            total_allowance = int(new_allowance) + int(self.temporary_allowance)
            temporary_allowance = str(self.temporary_allowance)
        self.assertEqual(result['total_allowance'], str(total_allowance))
        self.assertEqual(result['temporary_allowance'], str(temporary_allowance))

    def test_search_in_list_port_allowance_with_invalid_inputs(self):
        """
        list port allowance test
        :param type: string
        :param page: None
        :param port: string
        :param airline: string
        :param sortBy: string
        :param perPage: string
        :return: json with pagination array and results array
        """
        self.get_or_create_allowance()
        response = self.list_port_allowance(type='search',
                                            page=None,
                                            port='A',
                                            airline='B',
                                            sortBy='C',
                                            perPage='D')
        self.verify_port_allowance_list_response(response)

    def verify_port_allowance_list_response(self, response, per_page=None):
        """
       verify port allowance response
       :param response: dict
       :param per_page: bool
       """
        self.assertGreater(len(response['pagi']), 0)
        if per_page is not None:
            self.assertEqual(response['pagi']['perPage'], per_page)
        self.assertEqual(type(response['pagi']['perPage']), int)
        self.assertEqual(response['pagi']['currentPage'], 1)
        self.assertEqual(type(response['pagi']['currentPage']), int)
        self.assertEqual(type(response['pagi']['totalRecords']), int)
        self.assertGreater(len(response['results']), 0)
        for result in response['results']:
            if result['airline_id'] == str(self.airline_id) and result['port_id'] == str(self.port_id):
                new_allowance = self.allowance
                if int(result['allowance']) > self.allowance:
                    new_allowance = self.allowance + self.additional_allowance
                self.assertEqual(result['allowance'], str(new_allowance))
                total_allowance = int(new_allowance)
                temporary_allowance = 0
                if int(result['total_allowance']) > total_allowance:
                    total_allowance = int(new_allowance) + int(self.temporary_allowance)
                    temporary_allowance = str(self.temporary_allowance)
                self.assertEqual(result['total_allowance'], str(total_allowance))
                self.assertEqual(result['temporary_allowance'], str(temporary_allowance))

    def test_delete_port_allowance(self):
        """
        delete port allowance test
        :param allowance_id: integer
        :return: json with message and success flag
        """
        allowance_id = self.get_or_create_allowance()
        if int(allowance_id) > 0:
            response = self.delete_port_allowance(allowance_id=allowance_id)
            self.assertEqual(response['message'], "Record successfully deleted.")
            self.assertEqual(response['success'], True)

    def test_delete_port_allowance_with_invalid_input(self):
        """
        delete port allowance test with invalid inputs
        :param allowance_id: string
        :return: json with error message and success flag
        """

        allowance_id = 'A'
        response = self.delete_port_allowance(allowance_id=allowance_id)
        self.assertEqual(response['message'], "Unable to delete record.")
        self.assertEqual(response['success'], None)
        return response

    def get_or_create_allowance(self):
        """
        get port allowance record by port and airline or create new one if does not exist
        :return int
        """
        response = self.add_port_allowance(port_id=self.port_id, airline_id=self.airline_id,
                                           allowance=self.allowance)
        if response['success'] is True:
            return response['id']
        else:
            response = self.list_port_allowance(type='search',
                                                page=None,
                                                port=self.port_id,
                                                airline=self.airline_id,
                                                sortBy=0,
                                                perPage=20)

            if response['results']:
                return response['results'][0]['id']
