import random
import string
import faker
import time
import datetime
from pytz import timezone
from datetime import timedelta
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import warnings
from e2e_selenium_tests.BaseClasses.constant import sleep, BOOKING_PREVIOUS_DAY_INVENTORY_HOUR
ITEM_FILTER = 'div[ng-model="%s"] button:first-of-type'
ITEM_FILTER_CLASS = '[class="%s"] div[ng-model="%s"] button:first-of-type'
ITEM_INPUT = 'input[placeholder="%s"]'
ITEM_INPUT_CLASS_HIDE = '[class="%s"] input[placeholder="%s"].ng-hide'
ITEM_INPUT_CLASS = '[class="%s"] input[placeholder="%s"]'
ITEM_LIST = 'ul li div[class*="ui-select-choices-row"]'


def ignore_warnings(test_func):
    """

    :param test_func: string
    :return: function
    """
    """It is used to overcome 'ResourceWarning: unclosed socket.socket' when we run the unit tests from cmd. It's a
    known bug: http://code.google.com/p/selenium/issues/detail?id=5923
    """
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test


def generate_random_name_and_email():
    """
    This fake data would be used on QRT page for issued by and comments section.
    :return: strings
    """
    fake = faker.Faker()
    issued_by = fake.name()
    comments = fake.email()
    return issued_by, comments


def generate_random_data_for_sso_enabled_user_ids_pattern():
    fake = faker.Faker()
    random_number_for_user_id = ''.join(random.choice(string.digits) for _ in range(6))
    random_lower_case_letter = fake.random_lowercase_letter()
    u_combination_ids = str(random_lower_case_letter) + str(random_number_for_user_id)
    assert (len(u_combination_ids) == 7)
    return u_combination_ids


def get_hotel_block_fields(
    date="", airline_client="", pax_pay_block="", pax_pay_rate="", airline_pay_block="", airline_pay_rate="",
        room_type="", issued_by="", position="", comments=""):
    """
    :param date: string
    :param airline_client: string
    :param pax_pay_block: string
    :param pax_pay_rate: string
    :param airline_pay_block: string
    :param airline_pay_rate: string
    :param room_type: string
    :param issued_by: string
    :param position: string
    :param comments: string
    :return: dictionary
    """
    get_issued_by_name, get_comments_values = generate_random_name_and_email()
    block_fields = {
        'airline_client': airline_client,
        'pax_pay_block': pax_pay_block or 100,
        'pax_pay_rate': pax_pay_rate or "30.00",
        'issued_by': issued_by or get_issued_by_name,
        'position': position,
        'comments': comments or get_comments_values,
        'date': date,
        'room_type': room_type,
        'airline_pay_block': airline_pay_block or 25,
        'airline_pay_rate': airline_pay_rate or "170.00",
    }
    return block_fields


def fill_quick_room_transfer_form(airline="", port="", room_need="", direct_phone_number=None, phone_extension=None,
                                  comment=None, flight_number=""):
    """

    :param airline: string (Example: 3K Jetstar Asia)
    :param port: string
    :param room_need: string
    :param direct_phone_number: string
    :param phone_extension: string
    :param comment: string
    :param flight_number: string
    :return: dictionary
    """
    quick_room_transfer_fields = {
        'airline': airline,
        'port': port,
        'room_need': room_need or "2",
        'direct_phone_number': direct_phone_number or '123456789654',
        'phone_extension': phone_extension or "152",
        'comments': comment or "For the sake of practicing automation!",
        'flight_number': flight_number or "AC123"

    }
    return quick_room_transfer_fields


def value_selector_for_drop_downs(page, parent_css, query_text):
    """ It will be used to find and select given input from drop downs"""
    page.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, parent_css)))
    parent_obj = page.driver.find_element_by_css_selector(parent_css)
    parent_obj.click()
    parent_obj.click()
    page.wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR,
                                                           '{} ul li div[class*="ui-select-choices-row"]'
                                                           .format(parent_css))))
    child_obj = page.driver.find_elements_by_css_selector('{} ul li div[class*="ui-select-choices-row"]'
                                                          .format(parent_css))
    for element in child_obj:
        if query_text == element.text:
            element.click()
            break


def value_selector_for_searchable_drop_downs(page, query_text, dropdown_modal, dropdown_placeholder, prefix_only=False,
                                             need_item_class=False, item_class_name=""):
    """
    It will be used to find and select given input from searchable drop downs(Ajax calls).
    :param page:
    :param query_text: string
    :param dropdown_modal: string
    :param dropdown_placeholder: string
    :param prefix_only: string
    :param need_item_class: bool
    :param item_class_name: string
    :return:
    """
    if need_item_class:
        page.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ITEM_FILTER_CLASS %
                                                          (item_class_name, dropdown_modal))))
        page.driver.find_element_by_css_selector(ITEM_FILTER_CLASS % (item_class_name, dropdown_modal)).click()
        page.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ITEM_INPUT_CLASS_HIDE %
                                                            (item_class_name, dropdown_placeholder))))
        page.driver.find_element_by_css_selector(ITEM_INPUT_CLASS % (item_class_name, dropdown_placeholder))\
            .send_keys(query_text)
    else:
        page.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ITEM_FILTER % dropdown_modal)))
        page.driver.find_element_by_css_selector(ITEM_FILTER % dropdown_modal).click()
        page.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ITEM_INPUT % dropdown_placeholder)))
        page.driver.find_element_by_css_selector(ITEM_INPUT % dropdown_placeholder).send_keys(query_text)
    page.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ITEM_LIST)))
    item_list = page.driver.find_elements_by_css_selector(ITEM_LIST)
    for element in item_list:
        if prefix_only and (query_text == element.text.split()[0]):
            element.click()
            sleep(1)
            break
        else:
            if query_text == element.text:
                element.click()
                sleep(1)
                break


def get_availability_date(region):
    """
    param region: string (Example: America/New_York)
    return: Date
    """
    time_zone = timezone(region)
    today = datetime.datetime.now(time_zone)

    if today.hour < BOOKING_PREVIOUS_DAY_INVENTORY_HOUR:
        yesterday = today - datetime.timedelta(days=1)
        event_date = datetime.datetime(yesterday.year, yesterday.month, yesterday.day).replace(hour=23, minute=45)
    else:
        event_date = datetime.datetime(today.year, today.month, today.day).replace(hour=today.hour, minute=today.minute)
    return event_date


def get_date():
    """
    :return: Date
    """
    today = datetime.datetime.now()
    today_date = datetime.date(today.year, today.month, today.day)
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_date = datetime.date(tomorrow.year, tomorrow.month, tomorrow.day)
    return today_date, tomorrow_date


def get_system_current_date_time(region, room_count_history=False):
    time_zone = timezone(region)
    today = datetime.datetime.now(time_zone)
    event_date = datetime.datetime(today.year, today.month, today.day).replace(hour=today.hour, minute=today.minute)
    today = event_date + timedelta(seconds=60)
    if room_count_history:
        return event_date.strftime('%m/%d/%Y %I:%M%p'), today.strftime('%m/%d/%Y %I:%M%p')
    else:
        return event_date.strftime('%m/%d/%Y %I:%M %p'), today.strftime('%m/%d/%Y %I:%M %p')
