"""This class contains unit tests for quick room transfer"""

import uuid
from random import randint


from stormx_verification_framework import (
    StormxSystemVerification,
)


class TestQuickRoomTransfer(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    HOTEL_LIST = [103210,
                  100241]  # 103210 = Holiday Inn - Chicago / Oakbrook, 100241 = Fairfield Inn & Suites - Chicago Midway
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
        super(TestQuickRoomTransfer, cls).setUpClass()
        cls.user_list = cls.create_airline_users_with_different_roles(cls.PORT_ID, cls.AIRLINE_ID)
        cls.user_list.append({'username': cls.SUPPORT_USERNAME,
                              'cookies': cls.login_to_stormx(cls.SUPPORT_USERNAME, cls.SUPPORT_USERPASSWORD)})

    def test_quick_room_transfer_airlines(self):
        """
        quick room transfer airlines test with airline user and stormx user
        return: an airline data array of the airline user and count =1 in case of airline user and list of airlines for stormx user
        """
        for user in self.user_list:
            response = self.get_all_airlines(user.get('cookies'))
            response_json = response.json()
            self.assertEqual(response_json['success'], True)
            self.assertEqual(len(response_json['data']), response_json['airline_count'])
            if user.get('username') != self.SUPPORT_USERNAME:
                self.assertEqual(response_json['airline_count'], 1)
                self.assertEqual(response_json['data'][0]['label'], '3K Jetstar Asia')

    def test_quick_room_transfer_airlines_without_cookies(self):
        """
        quick room transfer airlines test with no cookies(without login)
        return: json with login error message
        """
        response = self.get_all_airlines(cookies={})
        response_json = response.json()
        self.assertEqual('You are not logged in' in response_json.get('loginError'), True)

    def test_quick_room_transfer_inventory(self):
        """
        quick room transfer inventory test.
        param port_id: int
        param airline_id: int
        param room_type_id: int
        return: a list of inventory for different blocks
        """

        inventory_date = self._get_event_date('America/Chicago')
        room_type_id = randint(1, 1)

        hotel_availability = self.add_inventory(self.HOTEL_LIST,
                                                self.AIRLINE_ID,
                                                inventory_date,
                                                room_type_id)
        room_avails = 0
        for hotel_id in hotel_availability:
            room_avails += self.find_hotel_availability_block_by_inventory_date(hotel_availability[hotel_id],
                                                                                inventory_date, True)
        for user in self.user_list:
            port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                user.get('cookies'))
            response_json = port_hotels_avails.json()
            self.assertGreater(len(response_json), 0)
            # self.assertEqual(response_json[0]['port_rooms_available'], room_avails)
            self.assertGreater(len(response_json[0]['hotel_price_list']), 0)
            self.assertGreater(len(response_json[1]['hotel_price_list']), 0)
            self.assertEqual(response_json[0]['hotel_price_list'][0]['start_date'], inventory_date.strftime('%Y-%m-%d'))
            self.assertEqual(response_json[1]['hotel_price_list'][0]['start_date'], inventory_date.strftime('%Y-%m-%d'))
            if user.get('username') == self.SUPPORT_USERNAME:
                self.assertEqual("max_allowed" not in response_json, True)
            else:
                self.assertGreaterEqual(int(response_json[0]['max_allowed']), 0)

    def test_quick_room_transfer_inventory__invalid_parameters(self):

        """
        quick room transfer vouchers post test.
        verify error response when no query parameters provided
        :param port_id: None
        :param airline_id: None
        :param room_type_id: None
        :return: Empty list
        """
        inventory_date = self._get_event_date('America/Chicago')
        room_type_id = randint(1, 1)
        self.add_inventory(hotel_list=self.HOTEL_LIST, airline_id=self.AIRLINE_ID, inventory_date=inventory_date, room_type=room_type_id)
        for user in self.user_list:
            port_hotels_avails = self.get_port_hotels_inventory(None, None, None, user.get('cookies'))
            response_json = port_hotels_avails.json()
            self.assertEqual(len(response_json), 0)
            self.assertIsNotNone(response_json)

    def test_save_quick_room_transfer_voucher(self):
        """
        quick room transfer vouchers post test.
        Add some inventory and build quick room transfer post data

        SCENARIO:1
        :param port_id: None
        :param airline_id: int
        :param room_type_id: int
        :param rooms_needed < inventory block
        :return: message should be 'Port is required'

        SCENARIO:2
        :param port_id: int
        :param airline_id: None
        :param room_type_id: int
        :param rooms_needed < inventory block
        :return: message should be 'Airline is required'

        SCENARIO:3
        :param port_id: int
        :param airline_id: int
        :param room_type_id: int
        :param rooms_needed > inventory block
        :return: message should be 'Hotel availability is insufficient'

        SCENARIO:4
        :param port_id: int
        :param airline_id: int
        :param room_type_id: int
        :param rooms_needed < inventory block
        :return: message should be 'Save was successful.' with list of vouchers created and a success flag
        """
        inventory_date = self._get_event_date('America/Chicago')
        room_type_id = randint(1, 1)
        quick_voucher_comment = 'Quick room transfer ' + str(uuid.uuid4())

        # add some hotel availability for the booking ----
        self.add_inventory(self.HOTEL_LIST,
                           self.AIRLINE_ID,
                           inventory_date,
                           room_type_id)
        alowance_id = self.get_or_create_allowance_id()
        for user in self.user_list:

            # Check case if rooms needed > hotel inventory
            port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                user.get('cookies'))
            inventory_json = port_hotels_avails.json()
            self.assertGreater(len(inventory_json), 0)
            # Check if rooms needed > port allowance value
            if user.get('username') != self.SUPPORT_USERNAME:
                form_data = self.build_form_data(airport_id=self.PORT_ID,
                                                 airline_id=self.AIRLINE_ID,
                                                 comment=quick_voucher_comment,
                                                 inventory_json=inventory_json,
                                                 check_with_greater_room_need_value=True,
                                                 check_with_greater_port_allowance_value=True)

                response_json = self.create_quick_room_transfer_voucher(form_data, user.get('cookies'))
                if response_json and response_json.get('success') is False:
                    self.assertEqual(response_json['success'], False)
                    self.assertEqual(response_json['msg'],
                                     "Inventory allowance exceeded. Please call (800) 642-7310 for assistance")

            # Check case if rooms needed > hotel inventory

            form_data = self.build_form_data(airport_id=self.PORT_ID,
                                             airline_id=self.AIRLINE_ID,
                                             comment=quick_voucher_comment,
                                             inventory_json=inventory_json,
                                             check_with_greater_room_need_value=True)

            response_json = self.create_quick_room_transfer_voucher(form_data, user.get('cookies'))
            if response_json and response_json.get('success') is False:
                self.assertEqual(response_json['success'], False)
                if user.get('username') == self.SUPPORT_USERNAME:
                    self.assertEqual(response_json['msg'], "Hotel availability is insufficient for booking.")
                else:
                    self.assertEqual(response_json['msg'],
                                     "Inventory allowance exceeded. Please call (800) 642-7310 for assistance")
            # Check case port id is empty
            port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                user.get('cookies'))
            inventory_json = port_hotels_avails.json()
            self.assertGreater(len(inventory_json), 0)

            form_data = self.build_form_data(airport_id=None,
                                             airline_id=self.AIRLINE_ID,
                                             comment=quick_voucher_comment,
                                             inventory_json=inventory_json,
                                             check_with_greater_room_need_value=True)

            response_json = self.create_quick_room_transfer_voucher(form_data, user.get('cookies'))
            if response_json and response_json.get('success') is False:
                self.assertEqual(response_json['success'], False)
                self.assertEqual(response_json['msg'], "Port is required")

            # Check case airline id is empty
            port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id)
            inventory_json = port_hotels_avails.json()
            self.assertGreater(len(inventory_json), 0)

            form_data = self.build_form_data(airport_id=self.PORT_ID,
                                             airline_id=None,
                                             comment=quick_voucher_comment,
                                             inventory_json=inventory_json,
                                             check_with_greater_room_need_value=True)

            response_json = self.create_quick_room_transfer_voucher(form_data, user.get('cookies'))
            if response_json and response_json.get('success') is False:
                self.assertEqual(response_json['success'], False)
                self.assertEqual(response_json['msg'], "Airline is required")

            port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                user.get('cookies'))
            inventory_json = port_hotels_avails.json()
            self.assertGreater(len(inventory_json), 0)

            self.assertGreater(len(inventory_json[0]['hotel_price_list']), 0)
            self.assertGreater(len(inventory_json[1]['hotel_price_list']), 0)
            self.assertEqual(inventory_json[0]['hotel_price_list'][0]['start_date'],
                             inventory_date.strftime('%Y-%m-%d'))
            self.assertEqual(inventory_json[1]['hotel_price_list'][0]['start_date'],
                             inventory_date.strftime('%Y-%m-%d'))

            # Check case if rooms needed < hotel inventory

            form_data = self.build_form_data(airport_id=self.PORT_ID,
                                             airline_id=self.AIRLINE_ID,
                                             comment=quick_voucher_comment,
                                             inventory_json=inventory_json,
                                             check_with_greater_room_need_value=False)
            response_json = self.create_quick_room_transfer_voucher(form_data, user.get('cookies'))
            if response_json and response_json.get('success') is True:
                self.assertEqual(response_json['success'], True)
                self.assertEqual(response_json['msg'], "Save was successful.")
                hotel_usage_history_response = self.get_hotel_usage_history(self.PORT_ID, self.AIRLINE_ID,
                                                                                 user.get('cookies'))
                self.assertGreater(len(hotel_usage_history_response), 0)
                port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                    user.get('cookies'))
                inventory_json = port_hotels_avails.json()
                # Checks whether the rooms used are equal to port_rooms_used in usage history
                self.compare_hotel_usage_with_inventory(hotel_usage_history_response, inventory_json)

                if response_json['voucherList']:
                    # Checks whether the invoices created are valid and exists in usage history
                    self.check_invoices_exist_in_usage_history(hotel_usage_history_response,
                                                               response_json['voucherList'])
        self.delete_port_allowance_record(alowance_id)

    def test_quick_room_transfer_hotel_usage_history(self):
        """
        quick room transfer hotel usage history test
        """
        airline_id = self.AIRLINE_ID  # Jetstar Asia
        port_id = self.PORT_ID  # MDW
        for user in self.user_list:
            response_json = self.get_hotel_usage_history(port_id, airline_id, user.get('cookies'))
            self.assertGreaterEqual(len(response_json), 0)
            # TODO: change to assertGreater
            # TODO: call this test after voucher tests so there is usage

    def add_inventory(self, hotel_list, airline_id, inventory_date, room_type):
        """
        add inventory for different blocks
        :param hotel_list: dict
        :param airline_id: int
        :param inventory_date: date
        :param room_type: int
        :return dict
        """
        # add some hotel availability for the booking ----
        comment1 = 'comment1 ' + str(uuid.uuid4())
        comment2 = 'comment2 ' + str(uuid.uuid4())
        comment3 = 'comment3 ' + str(uuid.uuid4())
        comment4 = 'comment3 ' + str(uuid.uuid4())
        soft_block_inventory = 5
        contract_block_inventory = 6
        hard_block_inventory = 7
        hotel_availability = {}
        for hotel_id in hotel_list:
            # soft blocks
            self.add_hotel_availability(hotel_id, airline_id, inventory_date, ap_block_type=0, block_price='149.99',
                                        blocks=soft_block_inventory, issued_by='Haroon Rashid', comment=comment1,
                                        room_type=room_type,pay_type='0')

            self.add_hotel_availability(hotel_id, airline_id, inventory_date, ap_block_type=0, block_price='149.99',
                                        blocks=soft_block_inventory, issued_by='Haroon Rashid', comment=comment2,
                                        room_type=room_type,pay_type='0')

            if hotel_id == 100241:
                # contract blocks
                self.add_hotel_availability(hotel_id, airline_id, inventory_date, ap_block_type=2,
                                            block_price='139.99',
                                            blocks=contract_block_inventory, issued_by='Haroon Rashid',
                                            comment=comment3,
                                            room_type=room_type, pay_type='0')

                # hard blocks
                self.add_hotel_availability(hotel_id, airline_id, inventory_date, ap_block_type=1,
                                            block_price='129.99',
                                            blocks=hard_block_inventory, issued_by='Haroon Rashid', comment=comment4,
                                            room_type=room_type, pay_type='0')

            hotel_availability[hotel_id] = self.get_hotel_availability(hotel_id, inventory_date)

        return hotel_availability

    def build_form_data(self,
                        airport_id,
                        airline_id,
                        comment,
                        inventory_json,
                        check_with_greater_room_need_value=False,
                        check_with_greater_port_allowance_value=False,
                        allow_more_rooms=False):
        """
        build quick room transfer post data
        :param airport_id: int
        :param airline_id: int
        :param comment: str
        :param inventory_json: dict
        :param check_with_greater_room_need_value: bool
        :param check_with_greater_port_allowance_value: bool
        :param allow_more_rooms: bool
        :return: dict
        """
        grouped = {}
        for hotel in inventory_json:

            hotel_price_list = hotel['hotel_price_list']
            hotel_id = hotel['id']
            block = {}
            for hotel_inventory in hotel_price_list:
                key = hotel_id + "-" + hotel_inventory['ap_block_type'] + "-" + hotel_inventory['price']
                block['hotel_merged_avails'] = ''
                if key not in grouped:
                    grouped[key] = hotel_inventory
                    grouped[key]['hotel_merged_avails'] = hotel_inventory['total_room_block']
                    grouped[key]['hotel_id'] = hotel_id
                    if check_with_greater_port_allowance_value is True:
                        grouped[key]['need'] = self.allowance + 1
                    elif check_with_greater_room_need_value is True:
                        grouped[key]['need'] = int(hotel_inventory['total_room_block']) + 1
                    elif allow_more_rooms is True:
                        grouped[key]['need'] = int(hotel_inventory['total_room_block']) - 1
                    else:
                        grouped[key]['need'] = 1
                else:
                    block_old = grouped[key]
                    block_old['hotel_availability_id'] = str(block_old['hotel_availability_id']) + "," + str(
                        hotel_inventory[
                            'hotel_availability_id'])
                    block_old['total_room_block'] = int(block_old['total_room_block']) + int(
                        hotel_inventory['total_room_block'])
                    block_old['hotel_merged_avails'] = str(block_old['hotel_merged_avails']) + "," + str(
                        hotel_inventory[
                            'total_room_block'])
                    block_old['hotel_id'] = hotel_id
                    if check_with_greater_port_allowance_value is True:
                        block_old['need'] = self.allowance + 1
                    elif check_with_greater_room_need_value is True:
                        block_old['need'] = int(block_old['total_room_block']) + 1
                    elif allow_more_rooms is True:
                        block_old['need'] = int(block_old['total_room_block']) - 1
                    else:
                        block_old['need'] = 1
                    grouped[key] = block_old
        grouped = list(grouped.values())
        form_data = {
            'extension': '+92311',
            'contact_phone': '48759856',
            'comment': comment,
            'rooms_needed': grouped
        }
        if airport_id != None:
            form_data['port_id'] = airport_id
        if airline_id != None:
            form_data['airline_id'] = airline_id

        return form_data

    def compare_hotel_usage_with_inventory(self, hotel_usage_history, inventory_json):
        """
        :param hotel_usage_history: dict
        :param inventory_json: dict
        :return: int
        """
        room_used = 0
        for history in hotel_usage_history:
            room_used += int(history['voucher_room_total'])

        self.assertEqual(room_used, inventory_json[0]['port_rooms_used'])
        return int(room_used)

    def check_invoices_exist_in_usage_history(self, hotel_usage_history, voucher_list):
        """
        :param hotel_usage_history: dict
        :param voucher_list: dict
        :return: int
        """
        voucher_ids = 0
        for history in hotel_usage_history:
            if int(history['voucher_id']) in voucher_list:
                voucher_ids += 1

        self.assertEqual(voucher_ids, len(voucher_list))
        return int(voucher_ids)

    def get_or_create_allowance_id(self):
        """
        get port allowance record by port and airline or create new one if does not exist
        :return int
        """
        response = self.add_port_allowance(port_id=self.PORT_ID, airline_id=self.AIRLINE_ID,
                                           allowance=self.allowance)
        if response['success'] is True:
            return response['id']
        else:
            response = self.list_port_allowance(type='search',
                                                page=None,
                                                port=self.PORT_ID,
                                                airline=self.AIRLINE_ID,
                                                sortBy=0,
                                                perPage=20)

            if response['results']:
                return response['results'][0]['id']

        return 0
    def delete_port_allowance_record(self, allowance_id):
        """
        delete port allowance record
        :param allowance_id: int
        """
        response = self.delete_port_allowance(allowance_id=allowance_id)
        self.assertEqual(response['message'], "Record successfully deleted.")
        self.assertEqual(response['success'], True)

    def test_room_return_quick_room_transfer_voucher_with_valid_data(self):
        """
        quick room transfer vouchers room return with valid data test.
        Add hotel,hotel serviced port and some inventory and build quick room transfer post data

        :param port_id: int
        :param airline_id: int
        :param room_type_id: int
        :param rooms_needed < inventory block
        :return: message should be 'Save was successful.' with list of vouchers created and a success flag
        """
        room_type_id = randint(1, 1)
        quick_voucher_comment = 'Quick room transfer ' + str(uuid.uuid4())

        # Add hotel with soft block inventory
        self.add_hotel_with_inventory(0, 'A')

        for user in self.user_list:

            # Check case if rooms needed > hotel inventory
            port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                user.get('cookies'))
            inventory_json = port_hotels_avails.json()
            self.assertGreater(len(inventory_json), 0)
            # Check case if rooms needed < hotel inventory
            form_data = self.build_form_data(airport_id=self.PORT_ID,
                                             airline_id=self.AIRLINE_ID,
                                             comment=quick_voucher_comment,
                                             inventory_json=inventory_json,
                                             check_with_greater_room_need_value=False,
                                             allow_more_rooms=True)
            response_json = self.create_quick_room_transfer_voucher(form_data, user.get('cookies'))
            if response_json and response_json.get('success') is True:
                self.assertEqual(response_json['success'], True)
                self.assertEqual(response_json['msg'], "Save was successful.")
                usage_history_response_json_old = self.get_hotel_usage_history(self.PORT_ID, self.AIRLINE_ID,
                                                                               user.get('cookies'))
                self.assertGreater(len(usage_history_response_json_old), 0)

                for voucher_history in usage_history_response_json_old:
                    response = self.room_return_quick_room_transfer_voucher(voucher_history, 1, user.get('cookies'))
                    if voucher_history.get('is_rooms_return_allowed') is False:
                        self.assertEqual(response['success'], False)
                        self.assertEqual(response['message'], 'Rooms return not allowed')
                    else:
                        self.assertGreater(int(response['success']), 0)
                        self.assertEqual(response['message'], '')

                    # check whethere is_rooms_return_allowed is returning correct value
                    if voucher_history.get('hotel_payment_type') == 'G':
                        self.assertEqual(voucher_history.get('is_rooms_return_allowed'), False)
                usage_history_response_json_new = self.get_hotel_usage_history(self.PORT_ID, self.AIRLINE_ID,
                                                                               user.get('cookies'))
                self.assertGreater(len(usage_history_response_json_new), 0)

                self.compare_voucher_old_usage_with_new_usage_after_room_return(usage_history_response_json_old,
                                                                                usage_history_response_json_new)

                # get hotel inventory after rooms returned
                port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                    user.get('cookies'))
                inventory_json = port_hotels_avails.json()
                self.assertGreater(len(inventory_json), 0)
                # compare hotel inventory with new voucher usage history after rooms returned
                self.compare_hotel_usage_with_inventory(usage_history_response_json_new, inventory_json)

    def test_room_return_quick_room_transfer_voucher_with_invalid_data(self):
        """
        quick room transfer vouchers room return with invlid data test.
        Add hotel,hotel serviced port and some inventory and build quick room transfer post data

        :param port_id: int
        :param airline_id: int
        :param room_type_id: int
        :param rooms_needed < inventory block
        :return: message should be 'Save was successful.' with list of vouchers created and a success flag
        """
        room_type_id = randint(1, 1)
        quick_voucher_comment = 'Quick room transfer ' + str(uuid.uuid4())

        # Add hotel with soft block inventory
        self.add_hotel_with_inventory(1, 'G')

        for user in self.user_list:

            # Check case if rooms needed > hotel inventory
            port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                user.get('cookies'))
            inventory_json = port_hotels_avails.json()
            self.assertGreater(len(inventory_json), 0)
            # Check case if rooms needed < hotel inventory

            form_data = self.build_form_data(airport_id=self.PORT_ID,
                                             airline_id=self.AIRLINE_ID,
                                             comment=quick_voucher_comment,
                                             inventory_json=inventory_json,
                                             check_with_greater_room_need_value=False,
                                             allow_more_rooms=True)
            response_json = self.create_quick_room_transfer_voucher(form_data, user.get('cookies'))
            if response_json and response_json.get('success') is True:
                self.assertEqual(response_json['success'], True)
                self.assertEqual(response_json['msg'], "Save was successful.")
                usage_history_response_json_old = self.get_hotel_usage_history(self.PORT_ID, self.AIRLINE_ID,
                                                                               user.get('cookies'))
                self.assertGreater(len(usage_history_response_json_old), 0)

                for voucher_history in usage_history_response_json_old:

                    response = self.room_return_quick_room_transfer_voucher(voucher_history, 1, user.get('cookies'))
                    if voucher_history.get('is_rooms_return_allowed') is False:
                        self.assertEqual(response['success'], False)
                        self.assertEqual(response['message'], 'Rooms return not allowed')
                    else:
                        self.assertGreater(int(response['success']), 0)
                        self.assertEqual(response['message'], '')

                    # check whethere is_rooms_return_allowed is returning correct value
                    if voucher_history.get('hotel_payment_type') == 'G':
                        self.assertEqual(voucher_history.get('is_rooms_return_allowed'), False)

                usage_history_response_json_new = self.get_hotel_usage_history(self.PORT_ID, self.AIRLINE_ID,
                                                                               user.get('cookies'))
                self.assertGreater(len(usage_history_response_json_new), 0)

                # get hotel inventory after rooms returned
                port_hotels_avails = self.get_port_hotels_inventory(self.PORT_ID, self.AIRLINE_ID, room_type_id,
                                                                    user.get('cookies'))
                inventory_json = port_hotels_avails.json()
                self.assertGreater(len(inventory_json), 0)
                # compare hotel inventory with new voucher usage history after rooms returned
                self.compare_hotel_usage_with_inventory(usage_history_response_json_new, inventory_json)

    def add_hotel_with_inventory(self, ap_block_type, payment_type):
        """
        add hotel with some inventory
        :param ap_block_type: int
        :param payment_type: str
        """
        inventory_date = self._get_event_date('America/Chicago')
        room_type_id = randint(1, 1)

        hotel_post_data = self.get_create_hotel_post_data(payment_type)
        hotel_details_response = self.add_or_update_hotel(hotel_post_data, 0, None)
        self.assertEqual("id" in hotel_details_response, True)
        hotel_id = hotel_details_response['id']
        self.assertEqual(hotel_details_response['success'], '1')
        self.assertEqual(hotel_details_response['errMsg'], 'Hotel information saved successfully.')

        # Add hotel serviced port
        serviced_port_response = self.add_hotel_serviced_port(self.PORT_ID, hotel_id, cookies=None)
        self.assertGreater(int(serviced_port_response['id']), 0)

        # Add hotel inventory
        comment1 = 'comment1 ' + str(uuid.uuid4())
        comment2 = 'comment2 ' + str(uuid.uuid4())
        if ap_block_type == 0:
            block_inventory = 5
        else:
            block_inventory = 7

        self.add_hotel_availability(hotel_id, self.AIRLINE_ID, inventory_date, ap_block_type=ap_block_type,
                                    block_price='149.99',
                                    blocks=block_inventory, issued_by='Haroon Rashid', comment=comment1,
                                    room_type=room_type_id, pay_type='0')

        self.add_hotel_availability(hotel_id, self.AIRLINE_ID, inventory_date, ap_block_type=ap_block_type,
                                    block_price='149.99',
                                    blocks=block_inventory, issued_by='Haroon Rashid', comment=comment2,
                                    room_type=room_type_id, pay_type='0')
        return hotel_id

    def compare_voucher_old_usage_with_new_usage_after_room_return(self, usage_history_old, usage_history_new):
        """
        compare old and new hotel usage after room return
        :param usage_history_old: dict
        :param usage_history_new: dict
        :return: int
        """
        room_used_old = 0
        room_used_new = 0
        for history in usage_history_old:
            room_used_old += int(history['voucher_room_total'])

        for history in usage_history_new:
            room_used_new += int(history['voucher_room_total'])
        self.assertGreater(room_used_old, room_used_new)
        return int(room_used_new)
# TODO: test get port hotels inventory without login.Currently the API is public
