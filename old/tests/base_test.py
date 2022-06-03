import unittest
from selenium import webdriver


class BaseTest(unittest.TestCase):
    """
    Base Test Page
    """
    def setUp(self):
        # Browser to be used. It can be changed to chrome on demand.
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def tearDown(self):
        """
        Tear down
        """
        self.driver.close()
