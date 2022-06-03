from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from e2e_selenium_tests.BaseClasses.base import BasePage


class VoucherListingMainPage(BasePage):
    SEARCH_VOUCHER_TEXT_FIELD = '[placeholder="type voucher code here e.g 71003, 71002"]'
    PNR_BUTTON = '[title="Add New PNR"]'

    def verify_browser_on_the_page(self):
        """
        Check for the presence of voucher search text field on page.
        :return:
        """
        assert self.is_visible(self.SEARCH_VOUCHER_TEXT_FIELD)

    def hide_pnr_button_for_airline_users(self):
        try:
            self.driver.find_element_by_css_selector(self.PNR_BUTTON)
            return False
        except:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.PNR_BUTTON)))
            return True
