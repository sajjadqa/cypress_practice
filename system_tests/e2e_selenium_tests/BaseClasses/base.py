import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from e2e_selenium_tests.BaseClasses.constant import STORMX_URL, MAX_EXPLICIT_WAIT


class BasePage(object):
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, MAX_EXPLICIT_WAIT)
        self.actions = ActionChains(self.driver)

    def request(self):
        request = requests.Session()
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            request.cookies.set(cookie['name'], cookie['value'])
        return request

    def get_page_html_source(self):
        """It will get the page response to verify that either it is the desired page or not.
        :return: string
        """
        current_url = self.driver.current_url
        resp = self.request().get(current_url)
        html_source = resp.content
        encode_html_source = str(html_source, encoding='utf8')
        return encode_html_source

    def get_hotel_inventory(self, port_id, airline_id):
        """
        :param port_id: int
        :param airline_id: int
        :return: Response Object

         It will get the hotel inventory info from QRT page."""
        resp = self.request().request(method='GET', url=STORMX_URL + "/admin/remote/voucher.php?type=getBookingHistory&"
                                                                     "pid=%s&airline_id=%s" % (port_id, airline_id))
        return resp

    def is_visible(self, locator):
        """
        :param locator: string
        :return: Bool
        """
        if self.driver.find_element_by_css_selector(locator):
            return True
        else:
            return False, "Element is not visible on the page."
