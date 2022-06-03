from datetime import datetime, timedelta
from stormx_verification_framework import (
    StormxSystemVerification,
)


class AvailabilityOnPortTimezone(StormxSystemVerification):
    """
    Verify StormX PHP functionality.
    """
    akl_hotel_ids = [81152,81154,81155,81156]
    mdw_hotel_ids = [103210,100242,100241,100243]
    lax_hotel_ids = [98734,98695,102322,98731]

    akl_port_id = 15 # Auckland
    mdw_port_id = 654  # Chicago Midway International Airport
    lax_port_id = 16 # Los Angeles International Airport

    @classmethod
    def setUpClass(cls):
        super(AvailabilityOnPortTimezone, cls).setUpClass()

    def add_inventory(self):
        # AKL
        akl_airline_id = 63
        event_date_akl = self._get_event_date('Pacific/Auckland')
        for hotel_id in self.akl_hotel_ids:
            self.add_hotel_availability(hotel_id=hotel_id, airline_id=akl_airline_id, availability_date=event_date_akl, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # LAX
        lax_airline_id=74
        event_date_lax = self._get_event_date('America/Los_Angeles')
        for hotel_id in self.lax_hotel_ids:
            self.add_hotel_availability(hotel_id=hotel_id, airline_id=lax_airline_id, availability_date=event_date_lax, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

        # MDW chicago
        mdw_airline_id = 71
        event_date_mdw = self._get_event_date('America/Chicago')
        for hotel_id in self.mdw_hotel_ids:
            self.add_hotel_availability(hotel_id=hotel_id, airline_id=mdw_airline_id, availability_date=event_date_mdw, ap_block_type=1, block_price='100.99', blocks=5, pay_type='0')

    def test_fetch_inventory_without_now(self):
        """
        test verify inventory with now having 0 value
        """
        self.add_inventory()
        now=0
        inventory_date = self._get_event_date('America/Chicago').strftime('%Y-%m-%d')

        akl_inventory = self.fetch_inventory(self.akl_port_id, now, self.akl_hotel_ids, inventory_date)
        if akl_inventory and akl_inventory['blocks']:
            self._verify_inventory_respone(akl_inventory, inventory_date)

        lax_inventory = self.fetch_inventory(self.lax_port_id, now, self.lax_hotel_ids, inventory_date)
        if lax_inventory and lax_inventory['blocks']:
            self._verify_inventory_respone(lax_inventory, inventory_date)

        mdw_inventory = self.fetch_inventory(self.mdw_port_id, now, self.mdw_hotel_ids, inventory_date)
        if mdw_inventory and mdw_inventory['blocks']:
            self._verify_inventory_respone(mdw_inventory, inventory_date)

    def test_fetch_inventory_with_now(self):
        """
        test inventory with now having value 1
        """
        now=1

        block_date = self._get_port_date(self.akl_port_id)
        akl_inventory = self.fetch_inventory(self.akl_port_id, now, self.akl_hotel_ids, block_date)
        if akl_inventory and akl_inventory['blocks']:
            self._verify_inventory_respone(akl_inventory, block_date)

        block_date = self._get_port_date(self.lax_port_id)
        lax_inventory = self.fetch_inventory(self.lax_port_id, now, self.lax_hotel_ids, block_date)
        if lax_inventory and lax_inventory['blocks']:
            self._verify_inventory_respone(lax_inventory, block_date)

        block_date = self._get_port_date(self.mdw_port_id)
        mdw_inventory = self.fetch_inventory(self.mdw_port_id, now, self.mdw_hotel_ids, block_date)
        if mdw_inventory and mdw_inventory['blocks']:
            self._verify_inventory_respone(mdw_inventory, block_date)


    def test_search_hotel_with_port_and_hotel_ids(self):
        """
        test on search of hotel with port have inventory on port time zone
        """

        akl_port_date = self._get_port_date(self.akl_port_id)
        akl_hotel_ids = self._get_comma_seperated_hotels_from_list(self.akl_hotel_ids)
        response = self.search_hotel(akl_hotel_ids, self.akl_port_id)
        self._verify_hotel_response(response, akl_port_date)

        lax_port_date = self._get_port_date(self.lax_port_id)
        lax_hotel_ids = self._get_comma_seperated_hotels_from_list(self.lax_hotel_ids)
        response = self.search_hotel(lax_hotel_ids, self.lax_port_id)
        self._verify_hotel_response(response, lax_port_date)

        mdw_port_date = self._get_port_date(self.mdw_port_id)
        mdw_hotel_ids = self._get_comma_seperated_hotels_from_list(self.mdw_hotel_ids)
        response = self.search_hotel(mdw_hotel_ids, self.mdw_port_id)
        self._verify_hotel_response(response, mdw_port_date)

    def test_search_hotel_without_port(self):
        """
        test on search of hotel without port,inventory should be loaded on current central time
        """
        inventory_date = self._get_event_date('America/Chicago').strftime('%Y-%m-%d')

        akl_hotel_ids = self._get_comma_seperated_hotels_from_list(self.akl_hotel_ids)
        response = self.search_hotel(akl_hotel_ids)
        self._verify_hotel_response(response, inventory_date)

        lax_hotel_ids = self._get_comma_seperated_hotels_from_list(self.lax_hotel_ids)
        response = self.search_hotel(lax_hotel_ids)
        self._verify_hotel_response(response, inventory_date)

        mdw_hotel_ids = self._get_comma_seperated_hotels_from_list(self.mdw_hotel_ids)
        response = self.search_hotel(mdw_hotel_ids)
        self._verify_hotel_response(response, inventory_date)

    def test_search_hotel_with_port_only(self):
        """
        test on search of hotel with port,inventory should be loaded on port local central time
        """
        akl_port_date = self._get_port_date(self.akl_port_id)
        response = self.search_hotel('', self.akl_port_id)
        self._verify_hotel_response(response, akl_port_date)

        lax_port_date = self._get_port_date(self.lax_port_id)
        response = self.search_hotel('', self.lax_port_id)
        self._verify_hotel_response(response, lax_port_date)

        mdw_port_date = self._get_port_date(self.mdw_port_id)
        response = self.search_hotel('', self.mdw_port_id)
        self._verify_hotel_response(response, mdw_port_date)


    def _verify_inventory_respone(self, inventory, date):
        """
        for inventory blocks verifying these blocks have same date as of central date
        """
        for hotel_id, avails in inventory['blocks'].items():
            for item in avails:
                self.assertEqual(item['block_expiration_date'], date)

    def _get_port_date(self, port_id):
        timezone = self.get_port_timezone(port_id)
        return self._get_event_date(timezone).strftime('%Y-%m-%d')

    def _get_comma_seperated_hotels_from_list(self, hotels):
        return ",".join(str(hotel_id) for hotel_id in hotels)

    def _verify_hotel_response(self, response, date):
        """
        verifying on response that it has same expiration date as port current date
        """
        if response and response['results']:
            for hotel_data in response['results']:
                if hotel_data['ap_block_data_json']:
                    for block in hotel_data['ap_block_data_json']:
                        self.assertEqual(block['block_expiration_date'], date)
