from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from e2e_selenium_tests.BaseClasses.helper import value_selector_for_drop_downs, value_selector_for_searchable_drop_downs, \
    get_availability_date
from e2e_selenium_tests.BaseClasses.base import BasePage
import datetime
from pytz import timezone
from datetime import timedelta


class Configurations(BasePage):
    ACTIVE_ROOM_TYPES = '#page_links li'
    TABLE_HEADING_ROWS = 'div.active form[name="rateCapForm"] table tr th'
    RATE_CAPS_TAB = '#page_links li a[ng-click="tabSelected=\'9\'"]'
    RATE_CAPS_TAB_ACTIVE = '#page_links li.active a[ng-click="tabSelected=\'9\'"]'
    ADD_NEW_RATE_CAP = 'form[name="rateCapForm"] button[ng-click="HotelRateCapPopup()"]'
    RATE_CAPS_FORM = 'form[name="formRateCap"]'
    CURRENCY_MODAL = 'div[ng-model="data.currency"]'
    RATE_CAPS_WARNING = 'input[ng-model="data.warning"]'
    SAVE_BUTTON = 'form[name="formRateCap"] button[type="submit"]'
    CLOSE_BUTTON = 'form[name="formRateCap"] button[ng-click="cancel()"]'
    RATE_CAPS_TEXT_FILED = 'input[ng-model="d.rate_cap"]'
    RATE_CAPS_EDIT_BUTTON = 'button[ng-click="RateCapEdit($index,d);"]'
    RATE_CAPS_DELETE_BUTTON = 'button[ng-click="RateDelete($index, d);"]'
    RATE_CAPS_DATA = 'form[name="rateCapForm"] tr[ng-repeat="d in data.rateCaps"] '

    def verify_browser_on_the_page(self):
        """Check for the presence of room types active tab on the page. """
        self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.ACTIVE_ROOM_TYPES)),
                        "Configurations page is not loaded yet..")
        assert self.is_visible(self.ACTIVE_ROOM_TYPES)

    def click_on_rate_caps_tab(self):
        """ Click on Rate Caps tab from configurations page"""
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_TAB)))
        self.driver.find_element_by_css_selector(self.RATE_CAPS_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_TAB_ACTIVE)),
                        "Rate caps tab is not selected successfully.")
        assert self.is_visible(self.TABLE_HEADING_ROWS)

    def add_new_rate_cap(self, currency, rate_cap_warning):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_RATE_CAP)),
                        "Add new rate cap button is not visible on the page.")
        self.driver.find_element_by_css_selector(self.ADD_NEW_RATE_CAP).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_FORM)),
                        "Rate caps form is loaded successfully.")
        self.actions.send_keys(Keys.TAB).perform()
        value_selector_for_drop_downs(self, self.CURRENCY_MODAL, currency)
        self.actions.send_keys(Keys.TAB).perform()
        self.driver.find_element_by_css_selector(self.RATE_CAPS_WARNING).send_keys(rate_cap_warning)

    def click_on_save_rate_cap_button(self):
        self.driver.find_element_by_css_selector(self.SAVE_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_FORM)),
                        "There is some error on rate cap form.")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_TEXT_FILED)))

    def rate_caps_warning_value(self):
        rate_value = self.driver.find_element_by_css_selector(self.RATE_CAPS_TEXT_FILED).get_attribute("value")
        return rate_value

    def verify_newly_added_rate_caps_on_listing(self, currency, rate_cap, updated_by, region, edit_rate=False):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_DATA)))
        rate_cap_list = self.driver.find_elements_by_css_selector(self.RATE_CAPS_DATA)
        rate_caps_list = [rate_cap_value.text for rate_cap_value in rate_cap_list]
        rate_value = ''.join(rate_caps_list)
        index = rate_value.find("\n")
        listing_record = rate_value[:index] + self.rate_caps_warning_value() + rate_value[index:]
        time_zone = timezone(region)
        today = datetime.datetime.now(time_zone)
        event_date = datetime.datetime(today.year, today.month, today.day)
        date = event_date.strftime("%m/%d/%Y")
        compare_string = currency + str(rate_cap) + "\n" + str(date) + " " + updated_by + " " + "X"
        assert compare_string == listing_record, \
            "Newly added rate cap record doesn't match with rate caps listing record."

    def delete_rate_caps(self):
        # self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_DELETE_BUTTON)))
        delete_buttons = self.driver.find_elements_by_css_selector(self.RATE_CAPS_DELETE_BUTTON)
        for button in delete_buttons:
            button.click()
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '[ng-show="saving"]')),
                            "Record is not deleted yet.")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_TEXT_FILED)),
                        "Rate cap record is not deleted yet.")

    def edit_rate_caps(self, edit_rate):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RATE_CAPS_EDIT_BUTTON)))
        self.driver.find_element_by_css_selector(self.RATE_CAPS_TEXT_FILED).clear()
        self.driver.find_element_by_css_selector(self.RATE_CAPS_TEXT_FILED).send_keys(edit_rate)
        self.driver.find_element_by_css_selector(self.RATE_CAPS_EDIT_BUTTON).click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '[ng-show="saving"]')),
                        "Record is not deleted yet.")