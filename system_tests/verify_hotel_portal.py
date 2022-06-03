import random
from datetime import datetime
from decimal import Decimal

import requests

import faker
from stormx_verification_framework import StormxSystemVerification


class TestHotelPortal(StormxSystemVerification):
    cookie = None
    user_id = None

    hotel_id = None
    hotel_currency = 'USD'
    port_id = 16  # LAX
    hotel_timezone = 'America/Los_Angeles'
    hotel_id_invalid = 83900  # Hilton Pasadena - LAX - Not allowed to manage inventory

    hotel_user_types = [{'id': 30, 'type': 'Finance'}, {'id': 31, 'type': 'Sales'}, {'id': 32, 'type': 'Corporate'}]
    block_types = ['soft_block', 'hard_block', 'contract_block']
    rate_cap_limit = None

    @classmethod
    def setUpClass(cls):
        super(TestHotelPortal, cls).setUpClass()
        cls.base_url = cls._php_host + '/api/v1/ui?u=/api/v1/tvl/hotel/inventory/'

    def test_hotel_inventory_stats__security(self):
        """
        verify that the php-to-django proxy is working as expected.
        """
        url = self.base_url + 'stats'

        # verify response when nobody is logged in ----
        response = requests.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                'loginError': 'You are not logged in. '
                              'Please click <a target="_blank" href="' +
                              self._php_host +
                              '/admin/index.php">here</a> to login.'
            }
        )

        self.setup_test_hotel()
        self.setup_hotel_user_cookie()
        response = requests.get(url, cookies=self.cookie)

        self.assertEqual(response.status_code, 200)   # PHP Proxy response
        response_json = response.json()
        self.assertEqual(response_json['meta']['status'], 200)  # API response

        self.assertIn('data', response_json)
        self.verify_inventory_stats_response(response_json['data'])

    def test_hotel_inventory_stats__with_different_hotel_users(self):
        self.setup_test_hotel()
        url = self.base_url + 'stats'

        for user_type in self.hotel_user_types:
            user_id, cookie = self.create_hotel_user_cookie(user_type=user_type['id'])

            response = requests.get(url, cookies=cookie)

            self.assertEqual(response.status_code, 200)   # PHP Proxy response
            response_json = response.json()
            self.assertEqual(response_json['meta']['status'], 200)  # API response

            self.assertIn('data', response_json)
            self.verify_inventory_stats_response(response_json['data'])
            self.delete_hotel_user(hotel_id=self.hotel_id, user_id=user_id)

    def test_hotel_inventory_stats__with_support_user(self):
        self.setup_test_hotel()
        self.setup_hotel_user_cookie()

        url = self.base_url + 'stats'

        response = requests.get(url, cookies=self._support_cookies)

        self.assertEqual(response.status_code, 401)   # PHP Proxy response
        response_json = response.json()
        self.assertEqual(response_json['meta']['status'], 401)  # API response

    def test_add_hotel_vacancy__with_different_hotel_users(self):
        self.setup_test_hotel()
        url = self.base_url + 'vacancy'

        for user_type in self.hotel_user_types:
            user_id, cookie = self.create_hotel_user_cookie(user_type=user_type['id'])

            rooms = random.randint(1, 65535)  # max positive smallint limit

            response = requests.post(url, cookies=cookie, data={'rooms': rooms})

            self.assertEqual(response.status_code, 200)   # PHP Proxy response
            response_json = response.json()
            self.assertEqual(response_json['meta']['status'], 200)  # API response

            self.assertIn('data', response_json)
            self.verify_vacancy_response(response_json['data'], rooms)

    def test_add_hotel_vacancy__with_tvl_user(self):
        self.setup_test_hotel()
        url = self.base_url + str(self.hotel_id) + '/vacancy'

        rooms = random.randint(1, 65535)  # max positive smallint limit

        response = requests.post(url, cookies=self._support_cookies, data={'rooms': rooms})

        self.assertEqual(response.status_code, 200)   # PHP Proxy response
        response_json = response.json()
        self.assertEqual(response_json['meta']['status'], 200)  # API response

        self.assertIn('data', response_json)
        self.verify_vacancy_response(response_json['data'], rooms)

    def test_add_hotel_vacancy__with_invalid_rooms(self):
        self.setup_test_hotel()
        self.setup_hotel_user_cookie()

        url = self.base_url + 'vacancy'

        # case 1 - invalid rooms - above max positive smallint limit
        rooms = 65536

        response = requests.post(url, cookies=self.cookie, data={'rooms': rooms})

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()
        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertIn('INVALID_INPUT', response_json['meta']['error_code'])

        # case 2 - no rooms param in request
        rooms = 65536
        response = requests.post(url, cookies=self.cookie)

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()
        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertIn('INVALID_INPUT', response_json['meta']['error_code'])

    def test_add_hotel_vacancy__with_invalid_hotel(self):
        hotel = self.hotel_id_invalid
        user_id, cookie = self.create_hotel_user_cookie(hotel_id=hotel)

        url = self.base_url + 'vacancy'

        rooms = random.randint(1, 65535)

        response = requests.post(url, cookies=cookie, data={'rooms': rooms})

        self.assertEqual(response.status_code, 401)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 401)  # API response

    def test_add_hotel_availability_block__with_different_hotel_users(self):
        fake = faker.Faker()
        self.setup_test_hotel()

        url = self.base_url + 'block'

        block = {
            'date': self._get_event_date(self.hotel_timezone),
            'rooms': random.randint(1, 65535),
            'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True,
                                        min_value=1, max_value=self.rate_cap_limit),
        }
        for user_type in self.hotel_user_types:
            user_id, cookie = self.create_hotel_user_cookie(user_type=user_type['id'])
            response = requests.post(url, cookies=cookie, data=block)

            self.assertEqual(response.status_code, 200)   # PHP Proxy response
            response_json = response.json()

            self.assertEqual(response_json['meta']['status'], 200)  # API response

            self.assertIn('data', response_json)
            self.assertIn('success', response_json['data'])
            self.assertTrue(response_json['data']['success'])

    def test_add_hotel_availability_block__with_different_room_type(self):
        fake = faker.Faker()
        self.setup_test_hotel()
        self.setup_hotel_user_cookie()

        url = self.base_url + 'block'

        blocks = [
            {
                'date': self._get_event_date(self.hotel_timezone),
                'rooms':  random.randint(1, 65535),
                'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True, min_value=1, max_value=self.rate_cap_limit),
                'room_type': "roh"  # ROH
            },
            {
                'date': self._get_event_date(self.hotel_timezone),
                'rooms':  random.randint(1, 65535),
                'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True, min_value=1, max_value=self.rate_cap_limit),
                'room_type': "ssr"  # ASR
            },
        ]

        for block in blocks:
            response = requests.post(url, cookies=self.cookie, data=block)
            self.assertEqual(response.status_code, 200)   # PHP Proxy response
            response_json = response.json()

            self.assertEqual(response_json['meta']['status'], 200)  # API response

            self.assertIn('data', response_json)
            self.assertIn('success', response_json['data'])
            self.assertTrue(response_json['data']['success'])

    def test_add_hotel_availability_block__with_different_rate_cap_reasons(self):
        fake = faker.Faker()
        self.setup_test_hotel()
        self.setup_hotel_user_cookie()

        # Get rate cap reasons
        url = self.base_url + 'stats'
        response = requests.get(url, cookies=self.cookie)

        self.assertEqual(response.status_code, 200)   # PHP Proxy response
        response_json = response.json()
        self.assertEqual(response_json['meta']['status'], 200)  # API response

        self.assertIn('data', response_json)

        self.verify_inventory_stats_response(response_json['data'])

        rate_cap_reasons = response_json['data']['rate_cap_reasons']

        # Add blocks with different rate cap reasons
        url = self.base_url + 'block'
        for reason in rate_cap_reasons:
            block = {
                'date': self._get_event_date(self.hotel_timezone),
                'rooms':  random.randint(1, 65535),
                'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True,
                                            min_value=1, max_value=self.rate_cap_limit),
                'room_type': "roh",  # ROH
                'rate_cap_reason': reason['id']
            }

            response = requests.post(url, cookies=self.cookie, data=block)
            response_json = response.json()

            self.assertEqual(response_json['meta']['status'], 200)  # API response

            self.assertIn('data', response_json)
            self.assertIn('success', response_json['data'])
            self.assertTrue(response_json['data']['success'])

    def test_add_hotel_availability_block__with_rate_limits(self):
        fake = faker.Faker()
        self.setup_test_hotel(
            update=True, is_allowed_to_manage_inventory=True, is_allowed_to_exceed_rate_agreement=False)

        self.setup_hotel_user_cookie()

        # Get inventory stats
        url = self.base_url + 'stats'
        response = requests.get(url, cookies=self.cookie)

        self.assertEqual(response.status_code, 200)   # PHP Proxy response
        response_json = response.json()
        self.assertEqual(response_json['meta']['status'], 200)  # API response

        self.assertIn('data', response_json)

        self.verify_inventory_stats_response(response_json['data'])

        inventory = response_json['data']['inventory']

        # Add blocks
        url = self.base_url + 'block'

        for index in inventory:
            room_type_inventory = inventory[index]

            for block in room_type_inventory['blocks']:
                if not block['rate_cap_limit']:
                    continue
                # Add block within rate cap limit
                new_block = {
                    'date': block['date'],
                    'rooms':  random.randint(1, 65535),
                    'room_rate': block['rate_cap_limit'],
                    'room_type': room_type_inventory['room_type']['code']
                }

                response = requests.post(url, cookies=self.cookie, data=new_block)
                response_json = response.json()

                self.assertEqual(response_json['meta']['status'], 200)  # API response

                self.assertIn('data', response_json)
                self.assertIn('success', response_json['data'])
                self.assertTrue(response_json['data']['success'])

                # Add block with rate exceeding cap limit
                new_block['room_rate'] += 1
                response = requests.post(url, cookies=self.cookie, data=new_block)

                self.assertEqual(response.status_code, 400)   # PHP Proxy response
                response_json = response.json()

                self.assertEqual(response_json['meta']['status'], 400)  # API response

                self.assertIn('INVALID_INPUT', response_json['meta']['error_code'])
                self.assertEqual(response_json['meta']['error_description'], "Rate exceeds limit.")

        self.setup_test_hotel(update=True)

    def test_add_hotel_availability_block__with_pay_types(self):
        fake = faker.Faker()
        self.setup_test_hotel()

        url = self.base_url + str(self.hotel_id) + '/block'

        blocks = [
            {
                'date': self._get_event_date(self.hotel_timezone),
                'rooms':  random.randint(1, 65535),
                'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True,
                                            min_value=1, max_value=self.rate_cap_limit),
                'room_type': "roh",
                'pay_type': 'airline_pay',
            },
            {
                'date': self._get_event_date(self.hotel_timezone),
                'rooms':  random.randint(1, 65535),
                'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True,
                                            min_value=1, max_value=self.rate_cap_limit),
                'room_type': "roh",
                'pay_type': 'passenger_pay',
            }
        ]

        for block in blocks:
            response = requests.post(url, cookies=self._support_cookies, data=block)
            response_json = response.json()

            self.assertEqual(response_json['meta']['status'], 200)  # API response

            self.assertIn('data', response_json)
            self.assertIn('success', response_json['data'])
            self.assertTrue(response_json['data']['success'])

    def test_add_hotel_availability_block__with_block_types(self):
        fake = faker.Faker()
        self.setup_test_hotel()

        url = self.base_url + str(self.hotel_id) + '/block'

        for block_type in self.block_types:
            block = {
                'date': self._get_event_date(self.hotel_timezone),
                'rooms':  random.randint(1, 65535),
                'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True,
                                            min_value=1, max_value=self.rate_cap_limit),
                'room_type': "roh",
                'block_type': block_type,
            }
            response = requests.post(url, cookies=self._support_cookies, data=block)
            response_json = response.json()

            self.assertEqual(response_json['meta']['status'], 200)  # API response

            self.assertIn('data', response_json)
            self.assertIn('success', response_json['data'])
            self.assertTrue(response_json['data']['success'])

    def test_add_hotel_availability_block__with_wrong_input(self):
        fake = faker.Faker()
        self.setup_test_hotel()
        self.setup_hotel_user_cookie()
        today = self._get_event_date(self.hotel_timezone)

        url = self.base_url + 'block'

        # CASE 1 - missing required data
        block = {}

        response = requests.post(url, cookies=self.cookie, data=block)

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

        # CASE 2 - wrong date format
        block = {
            'date': today.strftime("%Y/%m/%d"),
            'rooms': random.randint(1, 65535),
            'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True, min_value=1, max_value=self.rate_cap_limit),
        }

        response = requests.post(url, cookies=self.cookie, data=block)

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

        # CASE 3 - old date
        block = {
            'date': '2020-02-01',
            'rooms': random.randint(1, 65535),
            'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True, min_value=1, max_value=self.rate_cap_limit),
        }

        response = requests.post(url, cookies=self.cookie, data=block)

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

        # CASE 4 - wrong rooms format
        block = {
            'date': str(today),
            'rooms': 'abc',
            'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True, min_value=1, max_value=self.rate_cap_limit),
        }

        response = requests.post(url, cookies=self.cookie, data=block)

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

        # CASE 5 - wrong room rate format
        block = {
            'date': str(today),
            'rooms': random.randint(1, 65535),
            'room_rate': 'abc',
        }

        response = requests.post(url, cookies=self.cookie, data=block)

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

        # CASE 6 - wrong rate cap reason

        block = {
            'date': self._get_event_date(self.hotel_timezone),
            'rooms':  random.randint(1, 65535),
            'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True, min_value=1, max_value=self.rate_cap_limit),
            'room_type': "roh",  # ROH
            'rate_cap_reason': 99
        }

        response = requests.post(url, cookies=self.cookie, data=block)

        self.assertEqual(response.status_code, 400)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 400)  # API response
        self.assertEqual(response_json['meta']['error_code'], 'INVALID_INPUT')

    def test_add_hotel_availability_block__with_invalid_hotel(self):
        fake = faker.Faker()
        hotel = self.hotel_id_invalid
        user_id, cookie = self.create_hotel_user_cookie(hotel_id=hotel)

        url = self.base_url + 'block'

        block = {
            'date': self._get_event_date(self.hotel_timezone),
            'rooms':  random.randint(1, 65535),
            'room_rate': fake.pydecimal(left_digits=7, right_digits=2, positive=True, min_value=1, max_value=self.rate_cap_limit),
        }

        response = requests.post(url, cookies=cookie, data=block)

        self.assertEqual(response.status_code, 401)   # PHP Proxy response
        response_json = response.json()

        self.assertEqual(response_json['meta']['status'], 401)  # API response

    def verify_inventory_stats_response(self, stats):
        today = self._get_event_date(self.hotel_timezone)

        self.assertEqual('tvl-' + str(self.hotel_id), stats['hotel_id'])
        self.assertIn('hotel_name', stats)
        self.assertIsNotNone(stats['hotel_name'])
        self.assertIn('currency', stats)
        self.assertIsNotNone(stats['currency'])
        self.assertIn('start_date', stats)
        self.assertEqual(str(today), stats['start_date'])
        self.assertIn('end_date', stats)

        self.assertIn('rate_cap_reasons', stats)

        self.assertIn('inventory', stats)
        self.verify_inventory_response(stats['inventory'])

        self.assertIn('vacancy', stats)
        if stats['vacancy']:
            self.verify_vacancy_response(stats['vacancy'])

    def verify_vacancy_response(self, vacancy, rooms=None):
        self.assertIn('rooms', vacancy)
        if rooms:
            self.assertEqual(rooms, int(vacancy['rooms']))
        self.assertIn('updated_by', vacancy)
        self.assertIn('updated_at', vacancy)

    def verify_inventory_response(self, inventory):
        for rooms_type_index in inventory:
            self.assertIn('room_type', inventory[rooms_type_index])
            self.assertIn('code', inventory[rooms_type_index]['room_type'])
            self.assertIn('label', inventory[rooms_type_index]['room_type'])
            self.assertIn('blocks', inventory[rooms_type_index])

            blocks = inventory[rooms_type_index]['blocks']
            self.assertGreater(len(blocks), 0)

            for block in blocks:
                self.assertIn('date', block)
                self.assertIn('available_rooms', block)
                self.assertIn('booked_rooms', block)
                self.assertIn('rate_agreement', block)
                self.assertIn('rate_cap_limit', block)

    def setup_test_hotel(self, update=False, is_allowed_to_manage_inventory=True,
                         is_allowed_to_exceed_rate_agreement=True):
        if TestHotelPortal.hotel_id and not update:
            return

        hotel_post_data = self.get_create_hotel_post_data(
            payment_type='G',
            check_duplicate=0,
            hotel_timezone=self.hotel_timezone,
            is_allowed_to_manage_inventory=is_allowed_to_manage_inventory,
            is_allowed_to_exceed_rate_agreement=is_allowed_to_exceed_rate_agreement,
            hotel_currency=self.hotel_currency
        )

        hotel_id = TestHotelPortal.hotel_id if update and TestHotelPortal.hotel_id else 0

        response_json = self.add_or_update_hotel(hotel_post_data=hotel_post_data, hotel_id=hotel_id)

        if not update or not TestHotelPortal.hotel_id:
            TestHotelPortal.hotel_id = int(response_json['id'])

            # attach port with new hotel
            serviced_port_response = self.add_hotel_serviced_port(self.port_id, TestHotelPortal.hotel_id, ranking=2)
            self.assertGreater(serviced_port_response['id'], 0)

        self.set_get_rate_cap_limit()

    def set_get_rate_cap_limit(self):
        currency_rate_cap = None
        currency_rate_caps = self.get_rate_caps()

        for currency_cap in currency_rate_caps:
            if(currency_cap['currency'] == self.hotel_currency):
                currency_rate_cap = currency_cap

        if not currency_rate_cap or not float(currency_rate_cap['rate_cap']):
            rate_cap_warning = random.randint(200, 1000)
            response = self.add_edit_rate_cap(
                rate_cap_currency=self.hotel_currency,
                rate_cap_warning=rate_cap_warning,
                rate_cap_id=currency_rate_cap['id'] if currency_rate_cap else None
            )
            if response > 0:
                TestHotelPortal.rate_cap_limit = rate_cap_warning
        else:
            TestHotelPortal.rate_cap_limit = int(float(currency_rate_cap['rate_cap']))

    def setup_hotel_user_cookie(self, user_type=None):
        if TestHotelPortal.cookie is not None:
            return False

        TestHotelPortal.user_id, TestHotelPortal.cookie = self.create_hotel_user_cookie(user_type)

    def create_hotel_user_cookie(self, user_type=None, hotel_id=None):
        user_type = user_type if user_type else self.hotel_user_types[2]['id']
        hotel_id = hotel_id if hotel_id else self.hotel_id

        response = self.create_user_by_type(
            record_id=hotel_id, port_id=self.port_id, role_id=user_type, type='hotel')

        self.assertGreater(int(response['id']), 0)
        self.assertEqual(str(response['updated_by_user']), 'Support')

        user_id = response['id']
        user_name = response['request']['user_id']
        user_password = response['request']['user_id_']

        try:
            cookie = self.login_to_stormx(username=user_name, password=user_password, verbose_logging=False)
        except Exception:
            raise Exception('TestHotelPortal - Login failed user_name: ' + user_name + ' password: ' + user_password)

        return user_id, cookie

    @classmethod
    def tearDownClass(cls):
        if cls.delete_hotel_user(hotel_id=cls.hotel_id, user_id=cls.user_id):
            cls.user_id = None
            cls.cookie = None
