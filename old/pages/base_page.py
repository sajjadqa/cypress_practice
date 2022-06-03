from old.constants import BASE_URL
from selenium.common.exceptions import WebDriverException


class BasePage:
    """
    Base Page
    """
    time_to_wait = 10
    url = BASE_URL

    def __init__(self, driver):
        """
        instantiate driver
        """
        self.driver = driver

    def visit(self):
        """
        Visit page according to given URL
        """
        try:
            self.driver.get(self.url)
        except WebDriverException:
            print('Incorrect URL')
