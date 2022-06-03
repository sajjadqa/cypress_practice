import datetime
import os
import re
import faker
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from e2e_selenium_tests.BaseClasses.base import BasePage
from e2e_selenium_tests.BaseClasses.constant import sleep, STORMX_URL
from e2e_selenium_tests.BaseClasses.helper import get_availability_date, value_selector_for_searchable_drop_downs, \
    value_selector_for_drop_downs, get_date, generate_random_data_for_sso_enabled_user_ids_pattern
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_random_data_for_new_hotel():
    fake = faker.Faker()
    hotel_name = fake.first_name()
    hotel_property_id = fake.first_name()
    world_span = fake.first_name()
    ean_id = fake.random_number(5)
    street_address = fake.first_name()
    state = fake.state()
    post_code = fake.random_number(4)
    city = fake.city_suffix()
    notes = fake.text()
    special_instructions = fake.text()
    corporate_person = fake.name()
    corporate_email = fake.email()
    corporate_phone = fake.random_number(7)
    corporate_url = fake.url()
    finance_person = fake.name()
    finance_phone = fake.random_number(7)
    finance_email = fake.email()
    breakfast = fake.random_number(3)
    lunch = fake.random_number(3)
    dinner = fake.random_number(3)
    return hotel_name, hotel_property_id, world_span, ean_id, street_address, state, post_code, city, notes,\
           special_instructions, corporate_person, corporate_email, corporate_phone, corporate_url, finance_person,\
           finance_phone, finance_email, breakfast, lunch, dinner


def set_values_to_new_hotel_fields(hotel_name="", hotel_property_id="", world_span="", ean_id="", street_address="",
                                   state="", post_code="", country="", city="", notes="", special_instructions="",
                                   corporate_person="", corporate_phone="", corporate_email="", corporate_fax="",
                                   corporate_url="", finance_person="", finance_email="", finance_phone="",
                                   breakfast="", lunch="", dinner=""):
    """
    Assigning random generated values to new hotel fields.
    :param  * strings
    :return: dictionary
    """
    get_hotel_name, get_hotel_property_id, get_world_span,  get_ean_id,  get_street_address, get_state, get_post_code, \
     get_city, get_notes, get_special_instructions, get_corporate_person, get_corporate_email, get_corporate_phone, \
     get_corporate_url, get_finance_person, get_finance_phone, get_finance_email, get_breakfast, get_lunch, \
     get_dinner = generate_random_data_for_new_hotel()
    add_new_hotel_fields = {
        'hotel_name': hotel_name or "Hotel " + get_hotel_name,
        'hotel_property_id': hotel_property_id or get_hotel_property_id,
        'world_span': world_span or get_world_span,
        'ean_id': ean_id,
        'address': street_address or get_street_address,
        'state': state or get_state,
        'post_code': post_code or get_post_code,
        'city': city or get_city,
        'country': country,
        'notes': notes or get_notes,
        'special_instructions': special_instructions or get_special_instructions,
        'corporate_person': corporate_person or get_corporate_person,
        'corporate_phone': corporate_phone or get_corporate_phone,
        'corporate_email': corporate_email or get_corporate_email,
        'corporate_fax': corporate_fax,
        'corporate_url': corporate_url or get_corporate_url,
        'finance_person': finance_person or get_finance_person,
        'finance_email': finance_email or get_finance_email,
        'finance_phone': finance_phone or get_finance_phone,
        'breakfast': breakfast or get_breakfast,
        'lunch': lunch or get_lunch,
        'dinner': dinner or get_dinner
    }
    return add_new_hotel_fields


def generate_random_data_for_hotel_users():
    fake = faker.Faker()
    person_name = fake.name()
    user_email = fake.email()
    user_id = fake.profile(fields=['username'])['username']
    random_number_for_user_id = fake.random_number(3)
    user_name = user_id + str(random_number_for_user_id)
    user_name = user_name if len(user_name) < 15 else user_name[:14]
    user_password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    return person_name, user_email, user_name, user_password


def set_values_to_add_new_hotel_user(person_name="", user_email="", user_id="", user_password="",
                                     user_role="", sso_user_format=False):
    """
    Assigning random generated values to new hotel user fields.
    :param : * string
    :return: dictionary
    """
    get_person_name, get_user_email,  get_user_name, get_user_password = generate_random_data_for_hotel_users()
    get_sso_user_format_ids = generate_random_data_for_sso_enabled_user_ids_pattern()
    add_new_airline_user_fields = {
        'person_name': person_name or get_person_name,
        'user_email': user_email or get_user_email,
        'user_id': (get_sso_user_format_ids if sso_user_format else get_user_name),
        'user_password': user_password or get_user_password,
        'user_role': user_role
    }
    return add_new_airline_user_fields


class HotelMainPage(BasePage):
    HOTEL_INFORMATION = '#page_links'
    HOTEL_ID = 'tr:not(.ng-hide):first-of-type td strong'
    HOTEL_ADDRESS_TEXT_FIELD = '[ng-model="filter.address"]'
    EDIT_AVAILABILITY_BUTTON_OF_FIRST_HOTEL = 'tr:first-of-type div>button[title="Edit Availability"]'
    EDIT_AVAILABILITY_BUTTON_OF_SECOND_HOTEL = 'tr:nth-of-type(2) div>button[title="Edit Availability"]'
    BLOCK_DATE = 'input[name="block_date"]'
    AP_COUNT_SPECIFIC_AIRLINE = '//table[@class="rate-table"]//tr[./td[1][.//text()[contains(., "%s")] ]]' \
                                '[not(./td[2]//text()[contains(., "AR")])][not(./td[2]' \
                                '//text()[contains(., "PP")])]/td[3]'
    AP_COUNT_HARD_BLOCKS = '//table[@class="rate-table"]//tr[./td[1][.//text()[contains(., "%s")] ]]' \
                           '[(./td[2]//text()[contains(., "HB")])]/td[3]'
    AP_COUNT_FOR_ACCESSIBILITY_ROOM = '//table[@class="rate-table"]//tr[./td[1][.//text()[contains(., "%s")] or ' \
                                      'not(.//text()[normalize-space()])]][(./td[2]//text()[contains(., "AR")])]/td[3]'
    AP_COUNT = 'tbody tr:nth-of-type(1) td [class="rate-table"] tr td:nth-of-type(2)'
    AP_COUNTS = '//table[@class="rate-table"]//tr[./td[1][.//text()[contains(., "%s")] or ' \
                'not(.//text()[normalize-space()])]][not(./td[2]//text()[contains(., "AR")])] ' \
                '[not(./td[2]//text()[contains(., "PP")])]/td[3]'
    PORT_FILTER = 'div[ng-model="%s"] button:first-of-type'
    PORT_INPUT = 'input[placeholder="%s"]'
    PORT_DROPDOWN_PLACEHOLDER = 'Type port name or prefix'
    DISABLED_AIRLINE_MODAL = 'div[ng-model="data.selected_airline"][disabled=disabled]'
    COUNTRY_DROPDOWN_PLACEHOLDER = 'Choose country'
    PORTS_LIST = 'ul li div[class*="ui-select-choices-row"]'
    AVAIL_BLOCKS_FOR_FIRST_HOTEL = 'tr:nth-of-type(1) [class="rate-table"] tbody tr'
    AVAIL_BLOCKS_FOR_SECOND_HOTEL = 'tr:nth-of-type(2) [class="rate-table"] tbody tr'
    MODAL_HEADER = '.modal-header h4'
    NO_HOTEL_FOUND = 'td [class="alert alert-danger"]'
    CURRENT_DATE = '//ul[not(contains(@style, "display: none"))]//button[contains(@class,"btn btn-default btn-sm")]' \
                   '[span[text()=%s][not(contains(@class, "muted"))]]'
    PREVIOUS_DATE = '//td[contains(@id, "datepicker")][.//button[contains(@class, "active")]]''/preceding-sibling''::' \
                    'td[not(contains(@ng-show,"showWeeks"))][1]'
    DATE_LIST = 'button[ng-click="select(dt.date)"] span'
    DATE_MODAL = 'input[name="block_date"]'
    # TIME_OUT = "setTimeout(function(){ }, 50)"
    DATE_MODAL_CLICK = '$(\'[name="formAvailsEdit"] div input[name="block_date"]\').trigger("click").focus()'
    AP_BLOCK_CLICK = "$('[name=\"formAvailsEdit\"] input[name=\"blocks\"]').click().focus()"
    # DATE_PICKER_MODAL = 'ul[ng-model="date"] table'
    DATE_PICKER_MODAL = '//ul[(contains(@style, "display: block"))]'
    ALERT_SUCCESS = '.alert-success strong'
    AIRLINE_CLIENT = 'div[ng-model="data.selected_airline"]'
    BLOCKS = 'input[name="blocks"]'
    BLOCKS_XPATH = '//div/form[@name="formAvailsEdit"]/div[@class="modal-body"]/div/div/div/input[@name="blocks"]'
    BLOCKS_DISABLED = 'input[name="blocks"][disabled="disabled"]'
    RATE = 'input[ng-model="data.block_price"]'
    PAX_PAY_BLOCK = 'input[name="pp_block"]'
    PAX_PAY_RATE = 'input[name="pp_block_price"]'
    AIRLINE_PAY_BLOCK = '[name="formAvailsEdit"] input[ng-model="data.ap_block"]'
    AIRLINE_PAY_RATE = 'input[name="ap_block_price"]'
    # HARD_BLOCK = 'div[class="toggle-switch ng-isolate-scope"]'
    BLOCK_PAY_TYPE = 'div[model="data.pay_type"] .toggle-switch-animate span[title="AP"]'
    HARD_BLOCK = 'div[model="data.ap_block_type"] .toggle-switch-animate span[title="No"]'
    ROOM_TYPE = 'div[ng-model="data.selected_room_type"]'
    ROOM_TYPE_DISABLE = 'div[ng-model="data.selected_room_type"][disabled="disabled"]'
    ISSUED_BY = 'input[ng-model="data.issued_by"]'
    ISSUED_BY_DISABLE = 'input[ng-model="data.issued_by"][disabled="disabled"]'
    POSITION = 'div[ng-model="data.position"]'
    COMMENTS = 'textarea[ng-model="data.comment"]'
    UPDATE_BUTTON = '[class="modal-footer"]>button:first-of-type'
    CHILD_CSS = '{} ul li div[class*="ui-select-choices-row"]'
    REFRESH_SPINNER = '[class="dropdown ng-hide"] strong'
    HOTEL_ID_COPY = '.page-listing-results tr:nth-of-type(1) .form-inline span input.copy-text-input'
    HOTELS_PER_PAGE = '[class="dropdown"]:nth-of-type(1) strong'
    ADDITIONAL_CONTACTS_BUTTON = 'tr:nth-of-type(1) button[title="Additonal Contacts"]'
    MAIN_WINDOW_HANDLER = ""
    CONTACT_TYPE = 'tr:nth-of-type(2) div[ng-model="d.contactType"]'
    CONTACT_NAME = 'tr:nth-of-type(2) input[ng-model="d.name"]'
    CONTACT_PHONE = 'tr:nth-of-type(2) input[id="phone"]'
    CONTACT_EMAIL = 'tr:nth-of-type(2) input[id="email"]'
    CONTACT_ADDRESS = 'tr:nth-of-type(2) textarea[id="address"]'
    CONTACT_ADD_BUTTON = 'tr:nth-of-type(2) [type="button"] i'
    LAST_UPDATED_BY = 'tr:nth-of-type(3) [id="lastUpdated"]'
    LAST_UPDATED_BY_TEXT = 'tr [id="lastUpdated"]'
    CONTACT_DELETE = 'tr:nth-of-type(3) td button[ng-click="del($event, d);"]'
    DELETE_ALL_CONTACTS = 'tr td button[ng-click="del($event, d);"]:not(.ng-hide)'
    DISABLE_CONTACT_DELETE_BUTTON = 'button[class="btn btn-link text-black no-padding ng-scope ng-hide"]'
    DELETE_ALL_CONTACTS_CLICK = "$('tr td button[ng-click=\"del($event, d);\"]:not(.ng-hide)').click()"
    NO_CONTACT_MESSAGE = 'tr[ng-if="filteredContacts.length==0"] td'
    ADD_NEW_HOTEL_BUTTON = '//a[@title="Add New Hotel"]//i'
    HOTEL_NAME = 'input[ng-model="data.hotel.hotel_name"][required="required"]'
    RANKING = 'input[name="hotel_ranking"]'
    RATING = 'td span[ng-model="data.hotel.hotel_rating"] i:nth-of-type(5)'
    CONTRACT_TYPE = 'span[title="Contract"]'
    PROPERTY_ID = 'input[name="property_id"]'
    WORLD_SPAN = 'input[name="world_span"]'
    EXPEDIA_RAPID_ID = 'input[ng-model="data.hotel.expedia_rapid_id"]'
    ADDRESS = 'input[name="hotel_address1"]'
    STATE = 'input[name="hotel_state"]'
    POST_CODE = 'input[name="hotel_postcode"]'
    CITY = 'input[name="hotel_city"]'
    NOTES = 'textarea[name="hotel_notes"]'
    SPECIAL_INSTRUCTIONS = 'textarea[name="airport_attached_instructions"]'
    AIRPORT_ATTACHED = 'span[title="Yes"]'
    PETS = '[model="data.hotel.hotel_pets_allowed"] span[title="Not allowed"]'
    SERVICED_PETS = '[model="data.hotel.hotel_service_pets_allowed"] span[title="Not allowed"]'
    SHUTTLE = '[model="data.hotel.hotel_shuttle_enabled"] span[title="Not available"]'
    CORPORATE_CONTACT_PERSON = 'input[name="hotel_contact_person"]'
    CORPORATE_CONTACT_PHONE = 'input[name="hotel_contact_phone"]'
    PASSENGER_PAY_EMAIL = 'input[name="hotel_contact_email"]'
    PASSENGER_PAY_FAX = 'input[name="hotel_contact_fax"]'
    CORPORATE_CONTACT_URL = 'input[name="hotel_url"]'
    FINANCE_CONTACT_PERSON = 'input[name="hotel_finance_contact"]'
    FINANCE_CONTACT_PHONE = 'input[name="hotel_finance_phone"]'
    FINANCE_CONTACT_EMAIL = 'input[name="hotel_finance_email"]'
    BREAKFAST_ALLOWANCE = 'input[name="hotel_breakfast_allowance"]'
    LUNCH_ALLOWANCE = 'input[name="hotel_lunch_allowance"]'
    DINNER_ALLOWANCE = 'input[name="hotel_dinner_allowance"]'
    SAVE_BUTTON = '.page-header>.pull-right>.btn-primary'
    MANDATORY_FIELDS_ERRORS = '//form[@name="formDetail"]//tr//td[2]//input[@ng-required="true"]' \
                              '/following-sibling::div[1][not(contains(@class, "ng-hide"))]'
    COUNTRY_MANDATORY_ERROR = '[ng-model="data.hotel.hotel_country"]+div:not(.ng-hide)'
    COUNTRY_MODAL = 'div[ng-model="data.hotel.hotel_country"]'
    COUNTRY_NAME = 'AUS - Australia'
    USA_COUNTRY = 'USA - United States'
    USA_STATE_ERROR = '[ng-model="data.hotel.hotel_state"]+div:not(.ng-hide)'
    BRAND_MODAL = 'div[ng-model="data.hotel.hotel_brand_id"]'
    BRAND_PLACEHOLDER = 'Choose brand'
    BRAND_NAME = 'Avari Hotels International'
    ROOM_TYPE_MODAL = 'div[ng-model="data.selected_room_type"]'
    ROOM_TYPE_PLACEHOLDER = 'Choose or search...'
    ROOM_TYPE_NAME = 'Accessibility Room'
    POSITION_MODAL = 'data.position'
    POSITION_PLACEHOLDER = 'Choose Position'
    POSITION_NAME = 'Director of Sales'
    AIRLINE_MODAL = 'div[ng-model="data.selected_airline"]'
    AIRLINE_MODAL_CLICK = '$(\'div[ng-model="data.selected_airline"] button:last-of-type\').click()'
    AIRLINE_PLACEHOLDER = 'Choose Airline (optional)'
    CONTACT_TYPE_VALUE = 'IT Personnel'
    CONTACT_TYPE_MODAL = 'd.contactType'
    CONTACT_TYPE_PLACEHOLDER = 'Type'
    IMAGE_UPLOAD_SUCCESS_MESSAGE = '[id="uploadZoneImage"] span.text-success'
    RFP_CONTRACT_UPLOAD_MESSAGE = '[id="uploadZoneRFP"] span.text-success'
    CREDIT_APPLICATION_UPLOAD_MESSAGE = '[id="uploadZoneCAF"] span.text-success'
    SELF_BILLING_CONTRACT_UPLOAD_MESSAGE = '[id="uploadZoneSelfBillingContract"] span.text-success'
    TEST_DATA_PATH = '/vagrant/system_tests/test_data/'
    SERVICED_PORTS_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'1\'"]'
    PORTS_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'1\'"]'
    USER_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'2\'"]'
    USER_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'2\'"]'
    ROOM_RATE_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'3\'"]'
    ROOM_RATE_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'3\'"]'
    RATE_TYPE = '[model="data.hotel.hotel_rate_type"]'
    CONTRACTED_RATE_MONDAY_RATE = '[name="formPrices"] input[ng-model="d.mon"]'
    CONTRACTED_RATE_TUESDAY_RATE = '[name="formPrices"] input[ng-model="d.tue"]'
    CONTRACTED_RATE_WEDNESDAY_RATE = '[name="formPrices"] input[ng-model="d.wed"]'
    CONTRACTED_RATE_THURSDAY_RATE = '[name="formPrices"] input[ng-model="d.thu"]'
    CONTRACTED_RATE_FRIDAY_RATE = '[name="formPrices"] input[ng-model="d.fri"]'
    CONTRACTED_RATE_SATURDAY_RATE = '[name="formPrices"] input[ng-model="d.sat"]'
    CONTRACTED_RATE_SUNDAY_RATE = '[name="formPrices"] input[ng-model="d.sun"]'
    SPECIAL_RATE_MONDAY_RATE = '[ng-controller="HotelRatesController"]:last-of-type [name="formPrices"] ' \
                               'input[ng-model="d.mon"]'
    SPECIAL_RATE_TUESDAY_RATE = '[ng-controller="HotelRatesController"]:last-of-type [name="formPrices"] ' \
                                'input[ng-model="d.tue"]'
    SPECIAL_RATE_WEDNESDAY_RATE = '[ng-controller="HotelRatesController"]:last-of-type [name="formPrices"] ' \
                                  'input[ng-model="d.wed"]'
    SPECIAL_RATE_THURSDAY_RATE = '[ng-controller="HotelRatesController"]:last-of-type [name="formPrices"] ' \
                                 'input[ng-model="d.thu"]'
    SPECIAL_RATE_FRIDAY_RATE = '[ng-controller="HotelRatesController"]:last-of-type [name="formPrices"] ' \
                               'input[ng-model="d.fri"]'
    SPECIAL_RATE_SATURDAY_RATE = '[ng-controller="HotelRatesController"]:last-of-type [name="formPrices"] ' \
                                 'input[ng-model="d.sat"]'
    SPECIAL_RATE_SUNDAY_RATE = '[ng-controller="HotelRatesController"]:last-of-type [name="formPrices"] ' \
                               'input[ng-model="d.sun"]'
    RATE_CAP_WARNING_FOR_CONTRACTED_RATE = 'form[name="formPrices"] input.alert-danger'
    RATE_CAP_WARNING_FOR_SPECIAL_RATE = '[ng-controller="HotelRatesController"]:last-of-type form[name="formPrices"]' \
                                        ' input.alert-danger'
    TVA_SETTINGS_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'5\'"]'
    TVA_SETTINGS_ACTIVE_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'5\'"]'
    AMENITIES_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'6\'"]'
    AMENITIES_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'6\'"]'
    TAX_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'7\'"]'
    TAX_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'7\'"]'
    DAILY_CONTRACTED_BLOCK_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'9\'"]'
    CONTRACTED_BLOCK_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'9\'"]'
    DAILY_SOFT_BLOCK_TAB = '[role ="tablist"] li a[ng-click="tabSelected=\'10\'"]'
    SOFT_BLOCK_ACTIVE_TAB = '[role ="tablist"] li.active a[ng-click="tabSelected=\'10\'"]'
    SERVICED_PORT_MODAL = 'data.portServiceNew.port'
    SERVICED_PORT_PLACEHOLDER = 'Type port name or prefix'
    SERVICED_PORT_RANKING = 'input[ng-model="data.portServiceNew.ranking"]'
    PASSENGER_NOTES = 'textarea[ng-model="data.portServiceNew.passenger_notes"]'
    ADD_PORT_BUTTON = 'button[ng-click="ports.add()"] i'
    ADD_PORT_BUTTON_DISABLE = 'button[ng-click="ports.add()"][disabled="disabled"] i'
    SERVICED_PORTS_LIST = 'table tr[ng-repeat="d in data.portsServiced"] strong'
    DELETE_SERVICED_PORT = 'tr:nth-of-type(4) td a[ng-click="ports.remove(d,$index)"] I'
    PERSON_NAME = 'input[name="name"]'
    USER_EMAIL = 'input[name="email"]'
    USER_ID = 'input[name="login"]'
    USER_PASSWORD = 'input[name="password"]'
    USER_ROLE = 'select[name="role"]'
    SAVE_NEW_USER_BUTTON = '[name="formUser"] .table-no-borders .btn-primary'
    EDIT_USER_BUTTON = 'td a .fa-edit'
    AMENITY_NAME = 'tr:nth-of-type(1)[ng-repeat="amenity in amenities "] td:nth-of-type(1)'
    AMENITY_AVAILABLE = 'tr:nth-of-type(1) [model="amenity.available"] [title="No"]'
    AMENITY_ADD_HOUR = 'tr:nth-of-type(1) [model="amenity.allow_operating_hours"] [title="Add Hours"]'
    AMENITY_OPEN_HOUR_MODAL = 'amenity.open'
    AMENITY_PLACEHOLDER = 'Choose Time'
    AMENITY_CLOSE_HOUR_MODAL = 'amenity.close'
    AMENITY_FEE = 'tr:nth-of-type(1) input[ng-model="amenity.amenity_fee"]'
    AMENITY_NOTES = 'tr:nth-of-type(1) input[ng-model="amenity.amenity_note"]'
    AMENITY_HOUR_VALUE = '00:00'
    SAVE_AMENITY_BUTTON = 'button[ng-click="updateAmenities(data.hotel.hotel_id,amenities)"]'
    HOTEL_SEARCH_FIELD = 'input[ng-model="filter.hid"]'
    HOTEL_SEARCH_FIELD_XPATH = '//form[@name="formSearch"]//td//input[@ng-model="filter.hid"]'
    SEARCH_BUTTON = 'button[id="btnSearch"]'
    SEARCH_BUTTON_DISABLE = 'button[id="btnSearch"][disabled="disabled"]'
    VIEW_HOTEL_AMENITY_BUTTON = 'tr:nth-of-type(1) button[title="View Hotel Amenities"]'
    VIEW_AMENITIES_MODAL = 'div[class="modal-content"]'
    AMENITIES_LIST = 'tr[ng-repeat-start="d in data.results"] td:nth-of-type(1)'
    EDIT_TAX_BUTTON = 'tr:nth-of-type(2) td button[title="Edit Tax"]'
    TAX_NAME = '[ng-model="data.selected.tax_name"]'
    TAX_STATUS_PARENT_SELECTOR = 'div[ng-model="data.selected.status"]'
    TAX_STATUS_PARENT_MODAL_CLICK = '$(\'div[ng-model="data.selected.status"] button:last-of-type\').click()'
    TAX_STATUS_ACTIVE = '//div[@ng-model="data.selected.status"]//ul//a//div[contains(text(),"Active")]'
    TAX_STATUS_BUTTON = 'div[ng-model="data.selected.status"] button:last-of-type'
    TAX_STATUS_PLACEHOLDER = 'Choose Status'
    TAX_TYPE_PARENT_SELECTOR = 'div[ng-model="data.selected.tax_type_id"]'
    TAX_TYPE_PARENT_MODAL_CLICK = '$(\'div[ng-model="data.selected.tax_type_id"] button:last-of-type\').click()'
    TAX_TYPE_PLACEHOLDER = 'Choose Type'
    TAX_AMOUNT = 'input[name="tax_amount"]'
    TAX_START_DATE = 'input[name="start_date"]'
    TAX_END_DATE = 'input[name="end_date"]'
    TAX_START_DATE_TODAY = 'ul[ng-model="date"]:nth-of-type(11) button.btn-info'
    TAX_END_DATE_TODAY = 'ul[ng-model="date"]:nth-of-type(12) button.btn-info'
    TAX_ORDER = 'input[name="tax_order"]'
    TAX_ORDER_DISABLE = 'form [name="tax_order"].ng-invalid-required'
    TAX_ADD_BUTTON = '[name="formTaxEdit"] button.btn-success'
    TAX_UPDATE_BUTTON = '[name="formTaxEdit"] button.btn-primary'
    TAX_CLOSE_POPUP_BUTTON = '[name="formTaxEdit"] button.btn-warning'
    TAX_PER_HOTEL_RECORD = '[ng-controller="HotelTaxesController"] tr:last-of-type td'
    TAX_PER_HOTEL_XPATH = '//div[@ng-controller="HotelTaxesController"]//tr/td[text()="Active "]'
    TAX_AMOUNT_VALUE = '10.00'
    TAX_ORDER_VALUE = '1'
    TAX_TYPE_VALUE = 'Fixed'
    TAX_STATUS_VALUE = 'Active'
    TAX_MODAL = 'div form[name="formTaxEdit"]'
    TAX_ERROR = 'form[name="formTaxEdit"] .alert-danger'
    NO_PORTS_TEXT = 'tr[ng-if="data.portsServiced.length==0"]'
    HOTEL_ID_VALUE = 'input[value="%s"]'
    EDIT_AVAIL_MODAL = 'form[name="formAvailsEdit"]'
    EXCLUDE_EXPEDIA_FLAG = 'form[name="formSearch"] .toggle-switch-animate span[title="No"]'
    EXPEDIA_SEARCH_BUTTONS = 'button[title="Search for hotel on Expedia"]:not(.ng-hide)'
    EXPEDIA_SEARCH_BUTTONS_HIDE = 'button[title="Search for hotel on Expedia"].ng-hide'
    SEARCH_ON_EXPEDIA = 'button[title="Search for hotel on Expedia"]'
    EXPEDIA_MODAL = 'form[name="formLinkEanHotel"]'
    LOGIN_ERROR = 'form[name="formLinkEanHotel"] .alert-danger'
    LOGIN_ERROR_ON_HOTEL = '.page-listing-results .alert-danger'
    EXPEDIA_FIRST_HOTEL = '.modal-body tr:nth-of-type(2)'
    EXPEDIA_FIRST_HOTEL_LINK = '.modal-body tr:nth-of-type(2) td button'
    EXPEDIA_HOTEL_LINK = '.modal-body tr td button'
    EXPEDIA_DUPLICATE_ID = '//form[@name="formLinkEanHotel"]//td [.//strong[contains(text(), "%s")]]' \
                           '/following-sibling::td//button'
    EXPEDIA_LINKS = '//form[@name="formLinkEanHotel"] //td[not(.//strong[contains( text(),"%s")])][2]/button'
    SUCCESS_ALERT = '[name="formLinkEanHotel"] div.alert-success a'
    NO_RECORD_FOUND = 'form[name="formLinkEanHotel"] .text-danger'
    PORT_ATTACHED_ERROR = 'form[name="formLinkEanHotel"] .alert-danger span'
    EXPEDIA_REFRESH_SPINNER = '[name="formLinkEanHotel"] .fa-spin'
    EXPEDIA_RAPID_ID_ERROR_MESSAGE = 'span[ng-bind-html="data.response.msg | to_trusted"]'
    EXPEDIA_RAPID_ID_SUCCESS_MESSAGE = '[name="formLinkEanHotel"] div.alert-success'
    EXPEDIA_RAPID_ID_MESSAGE = 'div[ng-if="data.response&&data.response.msg"]'
    CLOSE_EXPEDIA_MODAL = '[name="formLinkEanHotel"] button.btn-warning'
    CLOSE_AVAIL_BUTTON = '[name="formAvailsEdit"] button.btn-warning'
    EXPEDIA_HOTEL_INFO = 'tr[ng-repeat="hotel in data.expedia_hotels"]:nth-of-type(%s) ' \
                         'td:first-of-type strong.text-success'
    HOTEL_DETAILS_BUTTON = 'button[title="Detail"]'
    ROOM_TYPE_MODAL_CLICK = '$(\'[name="formAvailsEdit"] [ng-model="data.selected_room_type"] button\').click()'
    ROOM_TYPE_ACCESSIBILITY = '$(\'[ng-model="data.selected_room_type"] .ui-select-choices-row:last-of-type\').click()'
    POSITION_MODAL_CLICK = '$(\'div[ng-model="data.position"] button:last-of-type\').click()'
    POSITION_MODAL_DISABLE = 'div[ng-model="data.position"][disabled="disabled"]'
    RESET_NEW_USER_BUTTON = '[name="formUser"] .table-no-borders .btn-danger'
    SEND_AVAIL_BUTTON = 'a[title="Send Avail/Rate Emails"] i.icon-envelope'
    SOFT_BLOCK_AIRLINE = '[name="formSoftBlock"] select[data-ng-model="d.airline_id"]'
    SOFT_BLOCK_AIRLINE_DISABLE = '[name="formSoftBlock"] select[data-ng-model="d.airline_id"][disabled="disabled"]'
    SOFT_BLOCK_PORT = '[name="formSoftBlock"] select[data-ng-model="d.port_id"]'
    SOFT_BLOCK_ROOM_TYPE = '[name="formSoftBlock"] select[data-ng-model="d.room_type_id"]'
    SOFT_BLOCK_PAY_TYPE = '[name="formSoftBlock"] select[name="rateTypes"]'
    SOFT_BLOCK_RATE = '[name="formSoftBlock"] div [ng-model="d.rate"]'
    SOFT_BLOCK_RATE_CAP_WARNING = 'form[name="formSoftBlock"] input[ng-model="d.rate"].alert-danger'
    CONTRACTED_BLOCK_RATE = '[name="formHardBlock"] div [ng-model="d.rate"]'
    CONTRACTED_BLOCK_RATE_CAP_WARNING = 'form[name="formHardBlock"] input[ng-model="d.rate"].alert-danger'
    SOFT_BLOCK_FROM_DATE_MODAL = '[name="formSoftBlock"] input[ng-model="d.start_date"]'
    SOFT_BLOCK_FROM_DATE_MODAL_CLICK = \
        '$(\'[name="formSoftBlock"] div [ng-model="d.start_date"]\').trigger("click").focus()'
    SOFT_BLOCK_UNTILL_DATE_MODAL = '[name="formSoftBlock"] input[ng-model="d.end_date"]'
    SOFT_BLOCK_UNTILL_DATE_MODAL_CLICK = \
        '$(\'[name="formSoftBlock"] div [ng-model="d.end_date"]\').trigger("click").focus()'
    SOFT_BLOCK_MONDAY_RATE = '[name="formSoftBlock"] input[ng-model="d.room_count_mon"]'
    SOFT_BLOCK_TUESDAY_RATE = '[name="formSoftBlock"] input[ng-model="d.room_count_tue"]'
    SOFT_BLOCK_WEDNESDAY_RATE = '[name="formSoftBlock"] input[ng-model="d.room_count_wed"]'
    SOFT_BLOCK_THURSDAY_RATE = '[name="formSoftBlock"] input[ng-model="d.room_count_thu"]'
    SOFT_BLOCK_FRIDAY_RATE = '[name="formSoftBlock"] input[ng-model="d.room_count_fri"]'
    SOFT_BLOCK_SATURDAY_RATE = '[name="formSoftBlock"] input[ng-model="d.room_count_sat"]'
    SOFT_BLOCK_SUNDAY_RATE = '[name="formSoftBlock"] input[ng-model="d.room_count_sun"]'
    SOFT_BLOCK_NOTES = '[name="formSoftBlock"] input[ng-model="d.notes"]'
    SOFT_BLOCK_SAVE_BUTTON = '[name="formSoftBlock"] div button i'
    SOFT_BLOCK_SAVED_DATA = '[name="formSoftBlock"].ng-valid-required'
    SOFT_BLOCK_EDIT_BUTTON = \
        '.tab-pane.active .grid-div-header ~ .grid-div-data:nth-of-type(3) div button:first-of-type i'
    SOFT_BLOCK_ERROR_MESSAGE = 'form[name="formSoftBlock"].ng-valid-required .alert-danger'
    # '.tab-pane.active .grid-div-header ~ .grid-div-data:nth-of-type(3) form[name="formSoftBlock"] div.alert-danger'
    DISABLED_HOTEL_ACTIVE_BUTTON = 'div[model="data.hotel.hotel_is_available"][disabled="disabled"]'
    ENABLED_HOTEL_ACTIVE_BUTTON = 'div[model="data.hotel.hotel_is_available"]'
    DEACTIVATION_REASON = 'input[name="hotel_deactivation_reason"]'
    SELECTED_CURRENCY = '[ng-model="data.hotel.hotel_currency"] span.ng-scope'
    SAVE_SETTINGS_BUTTON = '.tab-content button.btn-sm[ng-click="save()"]'
    SUCCESS_MESSAGE = 'button + .alert-success'
    ERROR_MESSAGE = 'button + .alert-danger'
    STATUS_MODAL = 'div[ng-model="filter.status"]'
    ACTIVE_HOTEL = '.form-inline i[title="Active"]'
    INACTIVE_HOTEL = '.form-inline i[title="In-Active"]'
    STATUS_TYPE_FILTER = 'div[ng-model="filter.status"] span.ng-scope'
    RATE_CAPS_WARNING = '[name="formAvailsEdit"] .alert-warning'

    def verify_browser_on_the_page(self):
        """Check for the presence of Hotel address text field Text on hotel listing page. """
        assert self.is_visible(self.HOTEL_ADDRESS_TEXT_FIELD)

    def select_status_filter(self, status):
        value_selector_for_drop_downs(self, self.STATUS_MODAL, status)

    def verify_default_selected_status_filter_hotels_on_page(self):
        """
        Verify that on clicking search button, only active status hotels should be visible.
        :return:
        """
        self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        selected_status_type = self.driver.find_element_by_css_selector(self.STATUS_TYPE_FILTER).text
        if selected_status_type == 'Active':
            inactive_hotels = self.driver.find_elements_by_css_selector(self.INACTIVE_HOTEL)
            if inactive_hotels:
                return False
            else:
                return True
        if selected_status_type == 'In-Active':
            active_hotels = self.driver.find_elements_by_css_selector(self.ACTIVE_HOTEL)
            if active_hotels:
                return False
            else:
                return True

    def click_on_add_new_hotel_button(self):
        """
        It will click on add new airline button from airline listing page.
        :return:
        """
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.ADD_NEW_HOTEL_BUTTON)),
                        "Add new hotel button is not visible.")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.driver.find_element_by_xpath(self.ADD_NEW_HOTEL_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_NAME)),
                        "Add new hotel page is not fully loaded.")

    def hide_buttons_on_hotel_listing_for_airline_user(self):
        try:
            self.driver.find_element_by_xpath(self.ADD_NEW_HOTEL_BUTTON)
            self.driver.find_element_by_css_selector(self.SEND_AVAIL_BUTTON)
            return False
        except:
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, self.ADD_NEW_HOTEL_BUTTON)))
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEND_AVAIL_BUTTON)))
            return True

    def no_hotel_record_found_from_hotel_listing(self):
        """
        Find_element_by_css returns True if it finds an element, exception if not.
        :return: Bool
        """
        try:
            # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.NO_HOTEL_FOUND)))
            self.driver.find_element_by_css_selector(self.NO_HOTEL_FOUND)
            return True
        except NoSuchElementException:
            return False

    def click_on_edit_availability_button(self, no_airline=False):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EDIT_AVAILABILITY_BUTTON_OF_FIRST_HOTEL)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.EDIT_AVAILABILITY_BUTTON_OF_FIRST_HOTEL)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.driver.find_element_by_css_selector(self.EDIT_AVAILABILITY_BUTTON_OF_FIRST_HOTEL).click()
        # self.driver.execute_script(self.TIME_OUT)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DATE_MODAL)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOCKS)))
        self.driver.execute_script(self.AP_BLOCK_CLICK)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.BLOCKS_DISABLED)))
        blocks_field = self.driver.find_element_by_xpath(self.BLOCKS_XPATH)
        self.driver.execute_script("arguments[0].click();", blocks_field)
        # self.actions.send_keys(Keys.SHIFT + '\ue004').perform()
        if not no_airline:
            self.actions.key_down(Keys.SHIFT).send_keys('\ue004').perform()
        # self.driver.execute_script(self.DATE_MODAL_CLICK)
        # hotel_name = self.driver.find_element_by_css_selector(self.MODAL_HEADER).text
        # print("Blocks are added for:", hotel_name, "at", datetime.datetime.now())
        # logger.info("Blocks are added for: %s at %d", hotel_name, datetime.datetime.now())

    def click_on_additional_contacts_button(self):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.MAIN_WINDOW_HANDLER = self.driver.current_window_handle
        self.driver.find_element_by_css_selector(self.ADDITIONAL_CONTACTS_BUTTON).click()
        # sleep(1)
        additional_contacts_windows = self.driver.window_handles[1]
        self.driver.switch_to.window(additional_contacts_windows)

    def select_date_from_edit_avail_form(self, past_days=False):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DATE_MODAL)))
        self.driver.execute_script(self.DATE_MODAL_CLICK)
        # self.driver.find_element_by_css_selector(self.DATE_MODAL).click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.DATE_PICKER_MODAL)))
        # self.wait.until(EC.visibility_of(self.driver.find_element_by_xpath(self.DATE_PICKER_MODAL)))
        if past_days:
            today_m_2_days = (get_availability_date('America/Chicago') - datetime.timedelta(days=2)).day
            self.driver.find_element_by_xpath(self.CURRENT_DATE % today_m_2_days).click()
        else:
            date_day = get_availability_date("America/Chicago").day
            self.driver.find_element_by_xpath(self.CURRENT_DATE % date_day).click()
        # self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DISABLED_AIRLINE_MODAL)))

    def select_hard_block_ap_from_edit_avail_form(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HARD_BLOCK)))
        self.driver.find_element_by_css_selector(self.HARD_BLOCK).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DISABLED_AIRLINE_MODAL)))

    def select_pp_block_type_from_edit_avail_form(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.BLOCK_PAY_TYPE)))
        self.driver.find_element_by_css_selector(self.BLOCK_PAY_TYPE).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.HARD_BLOCK)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DISABLED_AIRLINE_MODAL)))

    def fill_hotel_block_form(self, block_fields, airline_name, is_hard_block=False, accessibility_room=False,
                              no_airline=False, pp_block_type=False, past_date=False, refresh_page=False,
                              rate_caps_warning=False):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DISABLED_AIRLINE_MODAL)))
        # self.actions.send_keys(Keys.SHIFT, Keys.TAB).perform()
        self.select_airline_on_edit_avail_form(airline_name, no_airline, refresh_page)
        self.select_date_from_edit_avail_form(past_date)
        self.fill_data_to_form_on_edit_avails(block_fields, is_hard_block, accessibility_room, pp_block_type,
                                              rate_caps_warning)
        self.click_on_update_button()

    def verify_new_added_hotel_blocks_on_hotel_listing(self, block_fields, airline_prefix, is_hard_block):
        self.verify_newly_added_hotel_blocks_on_hotel_listing(block_fields, airline_prefix, is_hard_block)

    def fill_data_in_new_hotel_form(self, hotel_fields, usa_country_check=False):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_NAME)),
                        "Hotel name field is not visible opn page.")
        self.driver.find_element_by_css_selector(self.HOTEL_NAME).click()
        self.driver.find_element_by_css_selector(self.HOTEL_NAME).send_keys(hotel_fields["hotel_name"])
        # value_selector_for_searchable_drop_downs(self, self.BRAND_NAME, self.BRAND_MODAL, self.BRAND_PLACEHOLDER)
        value_selector_for_drop_downs(self, self.BRAND_MODAL, self.BRAND_NAME)
        self.driver.find_element_by_css_selector(self.HOTEL_NAME).send_keys(hotel_fields["hotel_name"])
        self.driver.find_element_by_css_selector(self.PROPERTY_ID).send_keys(hotel_fields["hotel_property_id"])
        self.driver.find_element_by_css_selector(self.WORLD_SPAN).send_keys(hotel_fields["world_span"])
        self.driver.find_element_by_css_selector(self.EXPEDIA_RAPID_ID).send_keys(hotel_fields["ean_id"])
        self.driver.find_element_by_css_selector(self.ADDRESS).send_keys(hotel_fields["address"])
        if not usa_country_check:
            self.driver.find_element_by_css_selector(self.STATE).send_keys(hotel_fields["state"])
        self.driver.find_element_by_css_selector(self.POST_CODE).send_keys(hotel_fields["post_code"])
        self.driver.find_element_by_css_selector(self.CITY).send_keys(hotel_fields["city"])
        self.driver.find_element_by_css_selector(self.NOTES).send_keys(hotel_fields["notes"])
        # value_selector_for_searchable_drop_downs(self, self.COUNTRY_PREFIX, self.COUNTRY_MODAL,
        #                                          self.COUNTRY_DROPDOWN_PLACEHOLDER, prefix_only=True)
        if usa_country_check:
            value_selector_for_drop_downs(self, self.COUNTRY_MODAL, self.USA_COUNTRY)
        else:
            value_selector_for_drop_downs(self, self.COUNTRY_MODAL, self.COUNTRY_NAME)
        self.driver.find_element_by_css_selector(self.CORPORATE_CONTACT_PERSON).send_keys(
            hotel_fields["corporate_person"])
        self.driver.find_element_by_css_selector(self.CORPORATE_CONTACT_PHONE).send_keys(
            hotel_fields["corporate_phone"])
        self.driver.find_element_by_css_selector(self.PASSENGER_PAY_EMAIL).send_keys(
            hotel_fields["corporate_email"])
        self.driver.find_element_by_css_selector(self.CORPORATE_CONTACT_URL).send_keys(hotel_fields["corporate_url"])
        self.driver.find_element_by_css_selector(self.FINANCE_CONTACT_PERSON).send_keys(
            hotel_fields["finance_person"])
        self.driver.find_element_by_css_selector(self.FINANCE_CONTACT_EMAIL).send_keys(hotel_fields["finance_email"])
        self.driver.find_element_by_css_selector(self.FINANCE_CONTACT_PHONE).send_keys(hotel_fields["finance_phone"])
        self.driver.find_element_by_css_selector(self.BREAKFAST_ALLOWANCE).send_keys(hotel_fields["breakfast"])
        self.driver.find_element_by_css_selector(self.LUNCH_ALLOWANCE).send_keys(hotel_fields["lunch"])
        self.driver.find_element_by_css_selector(self.DINNER_ALLOWANCE).send_keys(hotel_fields["dinner"])
        return hotel_fields["hotel_name"]

    def click_on_hotel_save_button(self, usa_country_check=False):
        self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
        mandatory_fields_error = self.driver.find_elements_by_xpath(self.MANDATORY_FIELDS_ERRORS)
        country_check = self.driver.find_elements_by_css_selector(self.COUNTRY_MANDATORY_ERROR)
        usa_state_check = self.driver.find_elements_by_css_selector(self.USA_STATE_ERROR)
        if mandatory_fields_error or country_check:
            print([error.text for error in mandatory_fields_error] + [error.text for error in country_check],
                  "check is not working on page.")
            return False
        if usa_country_check and not usa_state_check:
            print("State is a required field for USA check is not working on page.")
            return False
        return True

    def get_hotel_id(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_ID)), "Hotel is not created ")
        hotel_id = self.driver.find_element_by_css_selector(self.HOTEL_ID).text
        return hotel_id

    def hotel_logo_uploading(self):
        self.driver.find_element_by_css_selector('[name="hotelLogo"]').send_keys(self.TEST_DATA_PATH +
                                                                                 "test_image.jpeg")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.IMAGE_UPLOAD_SUCCESS_MESSAGE)),
                        "Image is not uploaded successfully.")
        file_upload_message = self.driver.find_element_by_css_selector(self.IMAGE_UPLOAD_SUCCESS_MESSAGE).text
        return file_upload_message

    def hotel_rfp_contract_uploading(self):
        self.driver.find_element_by_css_selector('[app-file-upload="rfp.options"]').send_keys(self.TEST_DATA_PATH +
                                                                                              "test_file.pdf")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RFP_CONTRACT_UPLOAD_MESSAGE)),
                        "RFP CONTRACT file is not uploaded successfully.")
        file_upload_message = self.driver.find_element_by_css_selector(self.RFP_CONTRACT_UPLOAD_MESSAGE).text
        return file_upload_message

    def hotel_credit_application_uploading(self):
        self.driver.find_element_by_css_selector('[app-file-upload="caf.options"]').send_keys(self.TEST_DATA_PATH +
                                                                                              "test_file.pdf")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.CREDIT_APPLICATION_UPLOAD_MESSAGE)),
                        "Credit Application file is not uploaded successfully.")
        file_upload_message = self.driver.find_element_by_css_selector(self.CREDIT_APPLICATION_UPLOAD_MESSAGE).text
        return file_upload_message

    def hotel_self_billing_contract_uploading(self):
        self.driver.find_element_by_css_selector('[app-file-upload="selfBillingContract.options"]').send_keys\
            (self.TEST_DATA_PATH + "test_file.pdf")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SELF_BILLING_CONTRACT_UPLOAD_MESSAGE)),
                        "Self-Contract billing file is not uploaded successfully.")
        file_upload_message = self.driver.find_element_by_css_selector(self.SELF_BILLING_CONTRACT_UPLOAD_MESSAGE).text
        return file_upload_message

    def get_current_url_of_hotel_page(self):
        """
        Gets the URL of the current page.
        :return: string
        """
        current_url = self.driver.current_url
        return current_url

    def click_on_serviced_ports_tab_from_hotel_details(self):
        self.driver.find_element_by_css_selector(self.SERVICED_PORTS_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORTS_ACTIVE_TAB)),
                        "Ports Tab is not selected")

    def select_serviced_port(self, port_prefix):
        value_selector_for_searchable_drop_downs(self, port_prefix, self.SERVICED_PORT_MODAL,
                                                 self.SERVICED_PORT_PLACEHOLDER, prefix_only=True)
        self.driver.find_element_by_css_selector(self.SERVICED_PORT_RANKING).send_keys(1)
        self.driver.find_element_by_css_selector(self.PASSENGER_NOTES).send_keys("For the sake of automation.")

    def click_on_add_port_button(self):
        self.driver.find_element_by_css_selector(self.ADD_PORT_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ADD_PORT_BUTTON_DISABLE)),
                        "Button is still in disabled state and ports list can't be fetched if button is disabled.")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.NO_PORTS_TEXT)),
                        "Port is not added successfully.")

    def get_serviced_port_list(self):
        serviced_ports_list = self.driver.find_elements_by_css_selector(self.SERVICED_PORTS_LIST)
        for port in serviced_ports_list:
            return port.text

    def click_on_users_tab_from_hotel_details(self):
        self.driver.find_element_by_css_selector(self.USER_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_ACTIVE_TAB)),
                        "Users Tab is not selected")

    def fill_data_in_new_hotel_user(self, new_user_fields):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PERSON_NAME)))
        self.driver.find_element_by_css_selector(self.PERSON_NAME).send_keys(new_user_fields['person_name'])
        self.driver.find_element_by_css_selector(self.USER_EMAIL).send_keys(new_user_fields['user_email'])
        self.driver.find_element_by_css_selector(self.USER_ID).send_keys(new_user_fields['user_id'])
        self.driver.find_element_by_css_selector(self.USER_PASSWORD).send_keys(new_user_fields['user_password'])
        self.driver.find_element_by_css_selector(self.USER_ROLE).send_keys(new_user_fields['user_role'])
        return new_user_fields['user_id'], new_user_fields['user_password']

    def get_hotel_user_roles(self):
        roles_list = self.driver.find_elements_by_css_selector('[data-ng-model="data.userNew.role"] option')
        return [user_role.text for user_role in roles_list]

    def click_on_save_user_button(self, sso_user_format=False):
        self.driver.find_element_by_css_selector(self.SAVE_NEW_USER_BUTTON).click()
        if sso_user_format:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger ul li")),
                            "This user name should not be allowed for non sso enabled airline")
            error_message = self.driver.find_element_by_css_selector(".alert-danger ul li").text
            self.driver.find_element_by_css_selector(self.RESET_NEW_USER_BUTTON).click()
            return error_message
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.EDIT_USER_BUTTON)),
                        "Something is missing while creating new hotel user.")

    def click_on_tva_settings_tab_from_hotel_details(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.TVA_SETTINGS_TAB)))
        self.driver.find_element_by_css_selector(self.TVA_SETTINGS_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TVA_SETTINGS_ACTIVE_TAB)),
                        "TVA Settings Tab is not selected")

    def hotel_default_currency(self):
        default_currency = self.driver.find_element_by_css_selector(self.SELECTED_CURRENCY).text
        return default_currency

    def click_on_hotel_inactive_button(self, it_support_user=False):
        if it_support_user:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ENABLED_HOTEL_ACTIVE_BUTTON)),
                            "Hotel active button should not be disabled for IT Support users.")
            self.driver.find_element_by_css_selector(self.ENABLED_HOTEL_ACTIVE_BUTTON).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DEACTIVATION_REASON)),
                            "Deactivation reason input field is not visible.")
            self.driver.find_element_by_css_selector(self.DEACTIVATION_REASON).\
                send_keys("Test hotel deactivation reason!")
            self.driver.find_element_by_css_selector(self.SAVE_SETTINGS_BUTTON).click()
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SUCCESS_MESSAGE)),
                            "Hotel information is not saved successfully. There is an error while saving data")
            success_message = self.driver.find_element_by_css_selector(self.SUCCESS_MESSAGE).text
            return success_message
        else:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.DISABLED_HOTEL_ACTIVE_BUTTON)),
                            "Hotel active button should be disabled for Non IT Support users.")
            self.driver.find_element_by_css_selector(self.DISABLED_HOTEL_ACTIVE_BUTTON)
            return True

    def click_on_amenities_tab_from_hotel_details(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.AMENITIES_TAB)))
        self.driver.find_element_by_css_selector(self.AMENITIES_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AMENITIES_ACTIVE_TAB)),
                        "Amenities Tab is not selected")

    def add_amenities_of_hotel(self):
        self.driver.find_element_by_css_selector(self.AMENITY_AVAILABLE).click()
        self.driver.find_element_by_css_selector(self.AMENITY_ADD_HOUR).click()
        value_selector_for_searchable_drop_downs(self, self.AMENITY_HOUR_VALUE, self.AMENITY_OPEN_HOUR_MODAL,
                                                 self.AMENITY_PLACEHOLDER)
        value_selector_for_drop_downs(self, 'div[ng-model="amenity.close"]', '00:15')
        self.driver.find_element_by_css_selector(self.AMENITY_FEE).send_keys(100)
        self.driver.find_element_by_css_selector(self.AMENITY_NOTES).send_keys("For the sake of automation.")

    def click_on_save_amenities_button(self):
        amenity_name = self.driver.find_element_by_css_selector(self.AMENITY_NAME).text
        self.driver.find_element_by_css_selector(self.SAVE_AMENITY_BUTTON).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div .alert-success")))
        return amenity_name

    def click_on_room_rate_tab_from_hotel_details(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ROOM_RATE_TAB)))
        self.driver.find_element_by_css_selector(self.ROOM_RATE_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_RATE_ACTIVE_TAB)),
                        "Room Rate Tab is not selected")

    def change_rate_type(self):
        self.driver.find_element_by_css_selector(self.RATE_TYPE).click()

    def rate_caps_warning_on_room_rate_contracted_rate_days_field(self, rate_val, no_currency=False):
        self.driver.find_element_by_css_selector(self.CONTRACTED_RATE_MONDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.CONTRACTED_RATE_TUESDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.CONTRACTED_RATE_WEDNESDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.CONTRACTED_RATE_THURSDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.CONTRACTED_RATE_FRIDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.CONTRACTED_RATE_SATURDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.CONTRACTED_RATE_SUNDAY_RATE).send_keys(rate_val)
        try:
            if no_currency:
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR,
                                                                    self.RATE_CAP_WARNING_FOR_SPECIAL_RATE)),
                                "Rate cap warning shouldn't be shown for room rate contracted rate field. As, "
                                "no currency is associated to this hotel")
                return True
            else:
                self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                                       self.RATE_CAP_WARNING_FOR_CONTRACTED_RATE)),
                                "Rate cap warning isn't working for room rate days rate field.")
                return True
        except TimeoutException:
            return False

    def rate_caps_warning_on_room_rate_special_rate_days_field(self, rate_val, no_currency=False):
        self.driver.find_element_by_css_selector(self.SPECIAL_RATE_MONDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.SPECIAL_RATE_TUESDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.SPECIAL_RATE_WEDNESDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.SPECIAL_RATE_THURSDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.SPECIAL_RATE_FRIDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.SPECIAL_RATE_SATURDAY_RATE).send_keys(rate_val)
        self.driver.find_element_by_css_selector(self.SPECIAL_RATE_SUNDAY_RATE).send_keys(rate_val)
        try:
            if no_currency:
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR,
                                                                    self.RATE_CAP_WARNING_FOR_SPECIAL_RATE)),
                                "Rate cap warning shouldn't be shown for room rate special rate field. As, "
                                "no currency is associated to this hotel")
                return True
            else:
                self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                                       self.RATE_CAP_WARNING_FOR_SPECIAL_RATE)),
                                "Rate cap warning isn't working for room rate days rate field.")
                return True
        except TimeoutException:
            return False

    def click_on_daily_contracted_block_tab_from_hotel_details(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.DAILY_CONTRACTED_BLOCK_TAB)))
        self.driver.find_element_by_css_selector(self.DAILY_CONTRACTED_BLOCK_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.CONTRACTED_BLOCK_ACTIVE_TAB)),
                        "Daily Contracted Block Tab is not selected")

    def rate_caps_warning_on_daily_contracted_blocks_rate_field(self, rate_val, no_currency=False):
        self.driver.find_element_by_css_selector(self.CONTRACTED_BLOCK_RATE).send_keys(rate_val)
        try:
            if no_currency:
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR,
                                                                    self.CONTRACTED_BLOCK_RATE_CAP_WARNING)),
                                "Rate cap warning shouldn't be shown for contracted blocks rate field. As, "
                                "no currency is associated to this hotel")
                return True
            else:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                  self.CONTRACTED_BLOCK_RATE_CAP_WARNING)),
                                "Rate cap warning isn't working for contracted blocks rate field.")
                return True
        except TimeoutException:
            return False

    def click_on_daily_soft_block_tab_from_hotel_details(self):
        self.driver.refresh()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.DAILY_SOFT_BLOCK_TAB)))
        self.driver.find_element_by_css_selector(self.DAILY_SOFT_BLOCK_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SOFT_BLOCK_ACTIVE_TAB)),
                        "SoftBlock Tab is not selected")

    def rate_caps_warning_on_soft_blocks_rate_field(self, rate_val, no_currency=False):
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_RATE).send_keys(rate_val)
        try:
            if no_currency:
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR,
                                                                    self.RATE_CAP_WARNING_FOR_SPECIAL_RATE)),
                                "Rate cap warning shouldn't be shown for soft block rate field. As, "
                                "no currency is associated to this hotel")
                return True
            else:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SOFT_BLOCK_RATE_CAP_WARNING)),
                                "Rate cap warning isn't working for soft blocks rate field.")
                return True
        except TimeoutException:
            return False

    def select_date_from_daily_soft_block_form(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SOFT_BLOCK_FROM_DATE_MODAL)))
        self.driver.execute_script(self.SOFT_BLOCK_FROM_DATE_MODAL_CLICK)
        self.driver.execute_script(self.SOFT_BLOCK_FROM_DATE_MODAL_CLICK)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.DATE_PICKER_MODAL)))
        date_day = get_availability_date("Asia/Karachi").day
        self.driver.find_element_by_xpath(self.CURRENT_DATE % date_day).click()
        self.driver.execute_script(self.SOFT_BLOCK_UNTILL_DATE_MODAL_CLICK)
        self.driver.execute_script(self.SOFT_BLOCK_UNTILL_DATE_MODAL_CLICK)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.DATE_PICKER_MODAL)))
        date_day = get_availability_date("Asia/Karachi").day
        self.driver.find_element_by_xpath(self.CURRENT_DATE % date_day).click()

    def fill_data_to_soft_block_form(self, airline, room_type, pay_type):
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_AIRLINE).send_keys(airline)
        # self.driver.find_element_by_css_selector(self.SOFT_BLOCK_PORT).send_keys(port)
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_ROOM_TYPE).send_keys(room_type)
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_PAY_TYPE).send_keys(pay_type)
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_RATE).send_keys('150')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_MONDAY_RATE).send_keys('5')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_TUESDAY_RATE).send_keys('10')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_WEDNESDAY_RATE).send_keys('20')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_THURSDAY_RATE).send_keys('25')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_FRIDAY_RATE).send_keys('30')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_SATURDAY_RATE).send_keys('35')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_SUNDAY_RATE).send_keys('40')
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_NOTES).send_keys('Soft blocks for today.')

    def click_on_soft_block_save_button(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SOFT_BLOCK_SAVE_BUTTON)))
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_SAVE_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SOFT_BLOCK_AIRLINE_DISABLE)))
        try:
            self.driver.find_element_by_css_selector(self.SOFT_BLOCK_SAVED_DATA)
            return True
        except NoSuchElementException:
            return False
            # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SOFT_BLOCK_SAVED_DATA)),
            #                 "Soft blocks has not added successfully. There is an error while saving data.")

    def edit_soft_block_rate(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SOFT_BLOCK_EDIT_BUTTON)))
        self.driver.find_element_by_css_selector(self.SOFT_BLOCK_EDIT_BUTTON).click()
        # self.wait.until(EC.alert_is_present())
        # self.driver.switch_to.alert.accept()
        self.driver.implicitly_wait(3)
        try:
            self.driver.find_element_by_css_selector(self.SOFT_BLOCK_ERROR_MESSAGE)
            return True
        except NoSuchElementException:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SOFT_BLOCK_ERROR_MESSAGE)))
            return False

    def search_hotel_on_hotel_listing(self, hotel_id):
        self.driver.get(STORMX_URL + '/admin/hotels.php?page=&pid=&hid=' + str(hotel_id))
        # self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_SEARCH_FIELD)),
        #                 "Hotel search field is not visible on the page.")
        # self.driver.find_element_by_xpath(self.HOTEL_SEARCH_FIELD_XPATH).send_keys(hotel_id)
        # self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_ID_VALUE % hotel_id)),
                            "{}, Desired hotel is not found on listing after click on search button.".format(hotel_id))
        except TimeoutException:
            pass

    def visibility_of_search_hotel_on_expedia_button(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_ON_EXPEDIA)))
            self.driver.find_element_by_css_selector(self.SEARCH_ON_EXPEDIA)
            return True
        except TimeoutException:
            return False

    def search_hotel_on_expedia(self):
        self.driver.find_element_by_css_selector(self.SEARCH_ON_EXPEDIA).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_MODAL)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_REFRESH_SPINNER)),
                        "Expedia hotels are not fully loaded on page/ No Expedia hotel record found.")
        expedia_rapid_id = ''
        index = ""
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_FIRST_HOTEL)))
            expedia_hotel_links = self.driver.find_elements_by_css_selector(self.EXPEDIA_HOTEL_LINK)
            for index, hotel_link in enumerate(expedia_hotel_links):
                self.driver.execute_script("arguments[0].click();", hotel_link)
                hotel_index = index + 2
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_RAPID_ID_MESSAGE)))
                try:
                    self.driver.find_element_by_css_selector(self.EXPEDIA_RAPID_ID_SUCCESS_MESSAGE)
                    hotel_info = self.driver.find_element_by_css_selector(self.EXPEDIA_HOTEL_INFO % hotel_index).text
                    expedia_rapid_id = hotel_info.split()[0]
                    self.driver.find_element_by_css_selector(self.SUCCESS_ALERT).click()
                    break
                except:
                    self.driver.find_element_by_css_selector(self.EXPEDIA_RAPID_ID_ERROR_MESSAGE)
        except NoSuchElementException:
            self.driver.find_element_by_css_selector(self.NO_RECORD_FOUND)
        return expedia_rapid_id

    def click_on_search_hotel_on_expedia_button(self):
        self.driver.find_element_by_css_selector(self.SEARCH_ON_EXPEDIA).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_MODAL)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_REFRESH_SPINNER)),
                        "Expedia hotels are not fully loaded on page/ No Expedia hotel record found.")

    def search_hotel_on_expedia_without_login(self):
        self.click_on_search_hotel_on_expedia_button()
        login_error = self.driver.find_element_by_css_selector(self.LOGIN_ERROR).text
        return login_error

    def link_expedia_hotel_without_login(self):
        self.driver.find_element_by_css_selector(self.EXPEDIA_FIRST_HOTEL_LINK).click()
        self.close_expedia_modal()
        self.click_on_search_hotel_button()
        login_error = self.driver.find_element_by_css_selector(self.LOGIN_ERROR_ON_HOTEL).text
        return login_error

    def close_expedia_modal(self):
        self.driver.find_element_by_css_selector(self.CLOSE_EXPEDIA_MODAL).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_MODAL)))

    def link_multiple_expedia_rapid_ids_to_hotel(self, duplicate_id):
        expedia_links = self.driver.find_elements_by_xpath(self.EXPEDIA_LINKS % duplicate_id)
        for expedia_link in expedia_links:
            expedia_link.click()
            try:
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_RAPID_ID_ERROR_MESSAGE)))
                link_error = self.driver.find_element_by_css_selector(self.EXPEDIA_RAPID_ID_ERROR_MESSAGE)
                return link_error.text
            except TimeoutException:
                success_msg = self.driver.find_element_by_css_selector(self.EXPEDIA_RAPID_ID_SUCCESS_MESSAGE)
                return success_msg.text

    def search_expedia_hotel_with_no_port(self):
        # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_ON_EXPEDIA)),
        #                 "It seems expedia rapid id has already attached with this hotel.")
        self.driver.find_element_by_css_selector(self.SEARCH_ON_EXPEDIA).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_MODAL)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_REFRESH_SPINNER)),
                        "Expedia hotels are not fully loaded on page/ No Expedia hotel record found.")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORT_ATTACHED_ERROR)),
                        "Port attachment error is not showing for search on expedia hotels.")
        port_error = self.driver.find_element_by_css_selector(self.PORT_ATTACHED_ERROR).text
        return port_error

    def remove_expedia_rapid_id_from_hotel_profile(self):
        self.driver.find_element_by_css_selector(self.EXPEDIA_RAPID_ID).clear()
        self.click_on_hotel_save_button()

    def select_exclude_expedia_flag(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXCLUDE_EXPEDIA_FLAG)),
                        "Exclude expedia hotels button is not visible on the page.")
        self.driver.find_element_by_css_selector(self.EXCLUDE_EXPEDIA_FLAG).click()
        self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))

    def visiblility_of_search_hotel_on_expedia_buttons(self, hotel_id, exclude_expedia=False):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        if exclude_expedia:
            try:
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_ID_VALUE % hotel_id)))
                return True
            except TimeoutException:
                return False
        expedia_search_buttons = self.driver.find_elements_by_css_selector(self.SEARCH_ON_EXPEDIA)
        if len(expedia_search_buttons) > 0:
            return True
        else:
            return False

    def open_hotel_details_page(self, hotel_id):
        self.driver.get(STORMX_URL + '/admin/hotel_detail.php?rid=' + str(hotel_id))
        # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_DETAILS_BUTTON)))
        # self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.HOTEL_DETAILS_BUTTON)))
        # self.driver.find_element_by_css_selector(self.HOTEL_DETAILS_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.SAVE_BUTTON)),
                        "Hotel details page is not loaded successfully.")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.EXPEDIA_RAPID_ID)))

    def expedia_rapid_id_on_hotel_details(self):
        ean_id = self.driver.find_element_by_css_selector(self.EXPEDIA_RAPID_ID)
        return ean_id.get_attribute("value")

    def get_added_amenities_list_from_view_hotel_amenities_section(self):
        self.driver.find_element_by_css_selector(self.VIEW_HOTEL_AMENITY_BUTTON).click()
        # sleep(1)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AMENITIES_LIST)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.VIEW_AMENITIES_MODAL)))
        list_of_amenities = self.driver.find_elements_by_css_selector(self.AMENITIES_LIST)
        for amenity_name in list_of_amenities:
            return amenity_name.text

    def refresh_page(self):
        self.driver.refresh()

    def click_on_tax_tab_from_hotel_details(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.TAX_TAB)))
        self.driver.find_element_by_css_selector(self.TAX_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TAX_ACTIVE_TAB)),
                        "TAX Tab is not selected")

    def add_new_tax_entry(self):
        self.driver.find_element_by_css_selector(self.EDIT_TAX_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TAX_NAME)))
        self.actions.send_keys(Keys.TAB).perform()
        self.actions.send_keys(Keys.ENTER).perform()
        # self.driver.execute_script(self.TAX_STATUS_PARENT_MODAL_CLICK)
        self.driver.find_element_by_css_selector(self.TAX_STATUS_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.TAX_STATUS_ACTIVE)),
                        "Tax status dropdown is not opened yet.")
        self.driver.find_element_by_xpath(self.TAX_STATUS_ACTIVE).click()
        # value_selector_for_drop_downs(self, self.TAX_STATUS_PARENT_SELECTOR, self.TAX_STATUS_VALUE)
        self.actions.send_keys(Keys.TAB).perform()
        self.driver.execute_script(self.TAX_TYPE_PARENT_MODAL_CLICK)
        value_selector_for_drop_downs(self, self.TAX_TYPE_PARENT_SELECTOR, self.TAX_TYPE_VALUE)
        self.actions.send_keys(Keys.TAB).perform()
        self.driver.find_element_by_css_selector(self.TAX_AMOUNT).send_keys(self.TAX_AMOUNT_VALUE)
        date_today, date_tomorrow = get_date()
        self.driver.find_element_by_css_selector(self.TAX_START_DATE).click()
        self.driver.find_element_by_xpath(self.CURRENT_DATE % date_today.day).click()
        self.driver.find_element_by_css_selector(self.TAX_END_DATE).click()
        self.driver.find_element_by_xpath(self.CURRENT_DATE % date_tomorrow.day).click()
        self.driver.find_element_by_css_selector(self.TAX_ORDER).send_keys(self.TAX_ORDER_VALUE)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.TAX_ORDER_DISABLE)))
        self.driver.find_element_by_css_selector(self.TAX_ADD_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.TAX_MODAL)),
                        "There is an error on page while adding new tax entry.")
        try:
            tax_error = self.driver.find_element_by_css_selector(self.TAX_ERROR)
            print(tax_error.text)
            return True
        except NoSuchElementException:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.TAX_MODAL)))
            return False

    def get_taxes_per_hotel(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.TAX_PER_HOTEL_RECORD)))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, self.TAX_PER_HOTEL_XPATH)))
        taxes_per_hotel_list = self.driver.find_elements_by_css_selector(self.TAX_PER_HOTEL_RECORD)
        return taxes_per_hotel_list

    def select_airline_on_edit_avail_form(self, airline_name, no_airline=False, refresh_page=False):
        if not no_airline:
            if refresh_page:
                self.driver.execute_script("$('button[id=\"btnSearch\"]').click()")
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DISABLED_AIRLINE_MODAL)))
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_MODAL)))
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
            self.driver.execute_script(self.AIRLINE_MODAL_CLICK)
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DISABLED_AIRLINE_MODAL)))
            value_selector_for_drop_downs(self, self.AIRLINE_MODAL, airline_name)
            self.actions.send_keys(Keys.TAB, Keys.SHIFT).perform()
        else:
            pass

    def fill_data_to_form_on_edit_avails(self, block_fields, is_hard_block=False, accessibility_room=False,
                                         pp_block_type=False, rate_caps_warning=False, no_currency=False):
        if is_hard_block:
            self.select_hard_block_ap_from_edit_avail_form()
        if pp_block_type:
            self.select_pp_block_type_from_edit_avail_form()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.BLOCKS_DISABLED)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.BLOCKS)))
        self.driver.execute_script('$(\'input[name="blocks"]\').val("")')
        # self.driver.find_element_by_css_selector(self.BLOCKS).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.BLOCKS_DISABLED)))
        self.driver.find_element_by_css_selector(self.BLOCKS).send_keys(block_fields["pax_pay_block"])
        if rate_caps_warning:
            self.driver.execute_script("$('input[name=\"block_price\"]').val('')")
            self.driver.find_element_by_css_selector(self.RATE).send_keys("65")
            if no_currency:
                try:
                    self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_WARNING)),
                                    "Rate caps warning shouldn't be visible as this hotel doesn't have currency.")
                    return True
                except TimeoutException:
                    return False
            else:
                self.wait.until(EC.invisibility_of_element_located((By.XPATH,
                                                                    "//form//span[@class='alert alert-warning ng-hide']")))
                self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_WARNING)),
                                "Rate caps warning is not visible on the page.")
                rate_cap_warning = self.driver.find_element_by_css_selector(self.RATE_CAPS_WARNING).text
                return rate_cap_warning
        self.driver.execute_script("$('input[name=\"block_price\"]').val('')")
        self.driver.find_element_by_css_selector(self.RATE).send_keys(block_fields["pax_pay_rate"])
        self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.ROOM_TYPE)))
        if accessibility_room:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ROOM_TYPE_DISABLE)))
            value_selector_for_drop_downs(self, self.ROOM_TYPE_MODAL, "Accessibility Room")
            self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ISSUED_BY_DISABLE)))
        self.driver.find_element_by_css_selector(self.ISSUED_BY).send_keys(block_fields["issued_by"])
        self.actions.send_keys(Keys.TAB).perform()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.POSITION_MODAL_DISABLE)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[ng-model="data.position"]')))
        self.driver.execute_script(self.POSITION_MODAL_CLICK)
        # value_selector_for_drop_downs(self, 'div[ng-model="data.position"]', 'Director of Sales')
        self.actions.send_keys(Keys.TAB).perform()
        self.driver.find_element_by_css_selector(self.COMMENTS).send_keys(block_fields["comments"])
        self.actions.send_keys(Keys.TAB).perform()

    def fill_data_in_contacts_form(self, new_contact_fields):
        value_selector_for_searchable_drop_downs(self, self.CONTACT_TYPE_VALUE, self.CONTACT_TYPE_MODAL,
                                                 self.CONTACT_TYPE_PLACEHOLDER)
        self.driver.find_element_by_css_selector(self.CONTACT_NAME).send_keys(new_contact_fields['corporate_person'])
        self.driver.find_element_by_css_selector(self.CONTACT_PHONE).send_keys(new_contact_fields['corporate_phone'])
        self.driver.find_element_by_css_selector(self.CONTACT_EMAIL).send_keys(new_contact_fields['corporate_email'])
        self.driver.find_element_by_css_selector(self.CONTACT_ADDRESS).send_keys(new_contact_fields['address'])
        self.driver.find_element_by_css_selector(self.CONTACT_ADD_BUTTON).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.LAST_UPDATED_BY)),
                        "Contact is not added successfully.")
        last_updated_by = self.driver.find_element_by_css_selector(self.LAST_UPDATED_BY).text
        return last_updated_by

    def delete_additional_contact(self):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.DISABLE_CONTACT_DELETE_BUTTON)))
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.DELETE_ALL_CONTACTS)))
        last_updated_found = True
        while last_updated_found:
            self.driver.execute_script(self.DELETE_ALL_CONTACTS_CLICK)
            try:
                self.driver.find_element_by_css_selector(self.LAST_UPDATED_BY_TEXT)
            except NoSuchElementException:
                last_updated_found = False
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.LAST_UPDATED_BY_TEXT)))

    def verify_newly_added_hotel_blocks_on_hotel_listing(self, block_fields, airline_prefix, is_hard_block=False,
                                                         accessibility_room=False, block_found=False,
                                                         pp_block_type=False):
        """
        It will check either newly added hotel blocks are visible on hotel listing page.
        :param block_fields: dictionary
        :param airline_prefix: string
        :param is_hard_block: Bool
        :param block_found: Bool
        :param accessibility_room: Bool
        :return:
        """
        self.verify_browser_on_the_page()
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.AVAIL_BLOCKS_FOR_FIRST_HOTEL)))
        self.driver.find_element_by_css_selector(self.SEARCH_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AVAIL_BLOCKS_FOR_FIRST_HOTEL)))
        rate_table_rows = self.driver.execute_script("return $('tr:nth-of-type(1) [class=\"rate-table\"] tr').length")
        hotel_blocks_record_list = []
        for row in range(1, rate_table_rows + 1):
            hotel_blocks_records_text = self.driver.execute_script\
                ("return $('tr:nth-of-type(1) [class=\"rate-table\"] tbody tr:nth-of-type({})').text()".format(row))
            hotel_blocks_record = list(filter(None, hotel_blocks_records_text.split()))
            if len(hotel_blocks_record) > 0:
                hotel_blocks_record_list.append(hotel_blocks_record)
        compare_string = airline_prefix + (" PP" if pp_block_type else " AP") + (" HB" if is_hard_block else "") + \
                         (" AR" if accessibility_room else "") + " " + str(block_fields['pax_pay_block']) + " " \
                         + str(block_fields['pax_pay_rate'])
        sample_string = compare_string.split()
        if sample_string in hotel_blocks_record_list:
            block_found = True
        if not block_found:
            print("Newly added hotel's blocks are not matched with hotel listing block count")
        return block_found

    def select_port_from_hotel_listing(self, query_text, dropdown_modal, dropdown_placeholder):
        self.click_on_search_hotel_button()
        value_selector_for_searchable_drop_downs(self, query_text, dropdown_modal, dropdown_placeholder,
                                                 prefix_only=True)
        self.click_on_search_hotel_button()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
        hotel_id = self.driver.find_element_by_css_selector(self.HOTEL_ID_COPY).get_attribute('value')
        return hotel_id

    def select_port_filter_by_url(self):
        try:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.REFRESH_SPINNER)))
            hotel_id = self.driver.find_element_by_css_selector(self.HOTEL_ID_COPY).get_attribute('value')
            return hotel_id
        except TimeoutException:
            return None

    def click_on_search_hotel_button(self):
        click_on_search_button = self.driver.find_element_by_css_selector(self.SEARCH_BUTTON)
        self.driver.execute_script("arguments[0].click();", click_on_search_button)
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))

    def airline_room_count_from_hotel_page(self, airline_prefix):
        """
        It will return the sum of ROH rooms avails for desired airline and without airline on hotel listing page.
        :return: int
        """
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        rooms_count = self.driver.find_elements_by_xpath(self.AP_COUNTS % airline_prefix)
        # self.driver.execute_script("$('tbody tr td [class=\"rate-table\"] tr:contains(\"3K\") td:nth-of-type(2)')")
        # logger.info("Total room avails shown on Hotel listing page: %s", sum([int(room.text) for room in hotel_listing
        # _page_room_count]))
        return sum([int(self.extract_room_number(room.text)) for room in rooms_count])

    def rooms_count_without_airline(self):
        """
        It will return the sum of ROH rooms avails for without airline on hotel listing page.
        :return: int
        """
        room_count = self.driver.find_elements_by_xpath(self.AP_COUNTS)
        return sum([int(room.text) for room in room_count])
        # return sum([int(self.extract_room_number(room.text)) for room in room_count])

    def rooms_count_of_specific_airline(self, airline_prefix):
        """
        It will get the total ROH room count of specific airline.
        :return: int
        """
        room_count = self.driver.find_elements_by_xpath(self.AP_COUNT_SPECIFIC_AIRLINE % airline_prefix)
        return sum([int(room.text) for room in room_count])
        # return sum([int(self.extract_room_number(room.text)) for room in room_count])

    def hard_blocks_room_count(self, airline_prefix):
        """
        It will get the total Hard blocks room count of specific airline.
        :return: int
        """
        room_count = self.driver.find_elements_by_xpath(self.AP_COUNT_HARD_BLOCKS % airline_prefix)
        return sum([int(room.text) for room in room_count])
        # return sum([int(self.extract_room_number(room.text)) for room in room_count])

    def extract_room_number(self, room_text):
        return re.search(r'\d+', room_text).group()

    def accessibility_room_count_from_hotel_page(self, airline_prefix):
        room_count = self.driver.find_elements_by_xpath(self.AP_COUNT_FOR_ACCESSIBILITY_ROOM % airline_prefix)
        return sum([int(room.text) for room in room_count])
        # return sum([int(self.extract_room_number(room.text)) for room in room_count])

    def click_on_update_button(self):
        # button_css = '[class="modal-footer"]>button:first-of-type'
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.UPDATE_BUTTON)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.UPDATE_BUTTON)))
        self.driver.find_element_by_css_selector(self.UPDATE_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.EDIT_AVAIL_MODAL)),
                        "There is an error while filling edit avail form.")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))

    def click_on_close_button(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.CLOSE_AVAIL_BUTTON)))
        self.driver.find_element_by_css_selector(self.CLOSE_AVAIL_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.EDIT_AVAIL_MODAL)),
                        "There is an error while filling edit avail form.")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))