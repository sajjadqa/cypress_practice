import requests

from stormx_verification_framework import StormxSystemVerification, uses_expedia


class TestApiHotelImages(StormxSystemVerification):
    """
    Verify hotel booking scenarios that test some of the details specific to Expedia inventory.

    This set of tests especially focuses on the the endpoint `POST /api/v1/hotels`.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelImages, cls).setUpClass()

    def test_tvl_hotel_with_hotel_image(self):
        """
        verify that TVL inventory can present a hotel's image URL across various endpoints.
        """
        customer = 'Purple Rain Airlines'
        airline_id = 294
        port = 'GRB'
        # Microtel Inn & Suites - Green Bay
        # hotel has expedia_rapid_id.
        hotel_id_raw = 96815
        tvl_hotel_id = 'tvl-' + str(hotel_id_raw)

        # add test inventory ----
        event_date = self._get_event_date(port_iata_code=port)
        self.add_hotel_availability(hotel_id_raw, airline_id, event_date, ap_block_type=1,
                                    block_price='100.00', blocks=5, pay_type='0')

        airline_client = self.get_airline_api_client(customer)

        # import passengers ----
        passengers = airline_client.import_passengers(self._generate_n_passenger_payload(2, port_accommodation=port))

        # verify hotel image in hotel listings ----
        hotels = airline_client.get_hotels(port=port, room_count=1, provider='tvl')
        picked_hotel = [h for h in hotels if h['hotel_id'] == tvl_hotel_id][0]
        listing_image_url = picked_hotel['image_url']
        self.assertTrue(listing_image_url)
        self.assertTrue(listing_image_url.startswith('http'))

        # verify hotel image in hotel voucher ----
        tvl_voucher = airline_client.book_hotel(
            context_ids=[p['context_id'] for p in passengers],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )
        hotel_voucher = tvl_voucher['hotel_voucher']
        self.assertEqual(hotel_voucher['image_url'], listing_image_url)

        # verify hotel image in passenger full state ----
        full_state = airline_client.get_passenger_full_state(passengers[0]['context_id'])
        self.assertEqual(full_state['voucher']['hotel_voucher']['image_url'], listing_image_url)

        # verify hotel image the passenger is presented ----
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']
        response = requests.get(passenger_offer_url, headers=self._generate_passenger_headers())
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertEqual(embedded_json['confirmation']['hotel_voucher']['image_url'], listing_image_url)

    def test_tvl_hotel_without_hotel_image(self):
        """
        verify that TVL inventory can present a null hotel image URL across various endpoints.
        """
        customer = 'Purple Rain Airlines'
        airline_id = 294
        port = 'CSX'  # in China
        # Longhua International Hotel Changsha
        # hotel has null expedia_rapid_id.
        hotel_id_raw = 92486
        tvl_hotel_id = 'tvl-' + str(hotel_id_raw)

        # add test inventory ----
        event_date = self._get_event_date(port_iata_code=port)
        self.add_hotel_availability(hotel_id_raw, airline_id, event_date, ap_block_type=1,
                                    block_price='100.00', blocks=5, pay_type='0')

        airline_client = self.get_airline_api_client(customer)

        # import passengers ----
        passengers = airline_client.import_passengers(self._generate_n_passenger_payload(2, port_accommodation=port))

        # verify hotel image in hotel listings ----
        hotels = airline_client.get_hotels(port=port, room_count=1, provider='tvl')
        picked_hotel = [h for h in hotels if h['hotel_id'] == tvl_hotel_id][0]
        listing_image_url = picked_hotel['image_url']
        self.assertIsNone(listing_image_url)

        # verify hotel image in hotel voucher ----
        tvl_voucher = airline_client.book_hotel(
            context_ids=[p['context_id'] for p in passengers],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )
        hotel_voucher = tvl_voucher['hotel_voucher']
        self.assertIsNone(hotel_voucher['image_url'])

        # verify hotel image in passenger full state ----
        full_state = airline_client.get_passenger_full_state(passengers[0]['context_id'])
        self.assertIsNone(full_state['voucher']['hotel_voucher']['image_url'])

        # verify hotel image the passenger is presented ----
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']
        response = requests.get(passenger_offer_url, headers=self._generate_passenger_headers())
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertIsNone(embedded_json['confirmation']['hotel_voucher']['image_url'])

    @uses_expedia
    def test_expedia_hotel_images(self):
        """
        verify that TVL inventory can present a hotel's image URL across various endpoints.
        """
        customer = 'Purple Rain Airlines'
        airline_id = 294
        port = self.select_airport_for_expedia_testing([
            ('LAX', 'America/Los_Angeles'),
            ('LGW', 'Europe/London')
        ])

        airline_client = self.get_airline_api_client(customer)

        # import passengers ----
        passengers = airline_client.import_passengers(self._generate_n_passenger_payload(2, port_accommodation=port))

        # verify hotel images are present in all Expedia hotel listings ----
        hotels = airline_client.get_hotels(port=port, room_count=1, provider='ean')
        for hotel in hotels:
            self.assertTrue(hotel['image_url'])
            self.assertTrue(hotel['image_url'].startswith('http'))
        self.assertGreater(len(hotels), 0, msg="no expedia inventory in port" + repr(port))
        picked_hotel = hotels[0]
        listing_image_url = picked_hotel['image_url']
        self.assertEqual(listing_image_url, listing_image_url)

        # verify hotel image in hotel voucher ----
        ean_voucher = airline_client.book_hotel(
            context_ids=[p['context_id'] for p in passengers],
            hotel_id=picked_hotel['hotel_id'],
            room_count=1
        )
        hotel_voucher = ean_voucher['hotel_voucher']
        self.assertEqual(hotel_voucher['image_url'], listing_image_url)

        # verify hotel image in passenger full state ----
        full_state = airline_client.get_passenger_full_state(passengers[0]['context_id'])
        self.assertEqual(full_state['voucher']['hotel_voucher']['image_url'], listing_image_url)

        # verify hotel image the passenger is presented ----
        passenger = passengers[0]
        passenger_offer_url = passenger['offer_url']
        response = requests.get(passenger_offer_url, headers=self._generate_passenger_headers())
        self.assertEqual(response.status_code, 200)
        embedded_json = self._get_landing_page_embedded_json(response)
        self.assertEqual(embedded_json['confirmation']['hotel_voucher']['image_url'], listing_image_url)
