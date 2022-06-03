from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from e2e_selenium_tests.BaseClasses.base import BasePage


class DashBoardMainPage(BasePage):
    REFRESH_BUTTON = 'button#dashboard-refresh-button'
    HOME_TAB = 'ul a[href="index.php"]'
    VOUCHER_TAB = 'a[href="vouchers.php"]'
    QUICK_ROOM_TRANSFER_TAB = 'a[href="quick-room-transfer.php"]'
    MANIFEST_TAB = 'a[href="manifests.php"]'
    HOTEL_TAB = 'a[href="hotels.php"]'
    TRANSPORT_TAB = 'a[href="transports.php"]'
    HOTEL_ADDRESS_TEXT_FIELD = '[ng-model="filter.address"]'
    TRANSPORT_ADDRESS_TEXT_FIELD = '[ng-model="filter.address"]'
    REPORTS_TAB = 'a [title="Reports"]'
    PORTS_TAB = 'a [title="Ports"]'
    PORT_ALLOWANCE_TAB = 'a[href="port_allowance.php"]'
    ADD_NEW_ALLOWANCE = 'a[title="Add New Allowance"] .fa-plus'
    ROOM_COUNT_REPORT = 'a[href="issued_adjustments_report.php"]'
    ROOM_COUNT_VOUCHER_BUTTON = 'a[title="+Voucher"]'
    SECTION_TITLE = '[class="container-fluid section-title-container"] [class="section-title"]>span'
    AIRLINE_TAB = 'a[href="airlines.php"]'
    ADD_NEW_AIRLINE_BUTTON = 'a[title="Add New Airline"] i[class="fa fa-plus"]'
    AIRLINE_SEARCH_FILTER = 'input[ng-model="filter.aid"][placeholder="type airline name/ids here e.g 116, 140"]'
    ADD_NEW_USER_BUTTON = '#breadcrumb li [title="Add New User"]'
    QUICK_VOUCHER_BUTTON = '.navbar-nav li:nth-of-type(4) a[title="New Voucher"] i'
    QUICK_VOUCHER_BUTTON_XPATH = '//nav[@class="navbar"]/div/div/ul/li/a[@open-voucherp]/i'
    REQUESTING_PORT = 'label[for="vnPortRequesting"] '
    SEARCH_VOUCHER_TEXT_FIELD = '[placeholder="type voucher code here e.g 71003, 71002"]'
    TVA_USERS_TAB = 'a[href="users.php"]'
    AIRLINE_DASHBOARD_HEADER_ROWS = '#metrics-markets-table .tablesorter-headerRow th'
    SEARCH_BUTTON_DISABLE = 'button[id="btnSearch"][disabled="disabled"]'
    USER_INFO_DROPDOWN = '.navbar-right>li:nth-of-type(5) >a'
    USER_INFO_DROPDOWN_OPEN = '[class="dropdown open"]'
    CONFIGURATIONS_BUTTON = 'li[class="dropdown open"] ul[role="menu"] a[href="configurations.php"]'

    def verify_browser_on_the_page(self):
        """Check for the presence of "Refresh" button """
        assert self.is_visible(self.REFRESH_BUTTON)

    def verify_airline_dashboard_page(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_DASHBOARD_HEADER_ROWS)),
                        "Data is still loading on dashboard page, "
                        "it could be due to port is not attached to airline user.")
        header_rows_count = self.driver.find_elements_by_css_selector(self.AIRLINE_DASHBOARD_HEADER_ROWS)
        assert len(header_rows_count) == 6
        # assert self.is_visible('[ng-model="filter.pid"]')

    def click_on_hotel_tab(self):
        """Click on Hotel tab from navigation bar to  go to hotel listing page."""
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.HOTEL_TAB)))
        self.driver.find_element_by_css_selector(self.HOTEL_TAB).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOTEL_ADDRESS_TEXT_FIELD)))

    def click_on_transport_tab(self):
        """Click on Transport tab from navigation bar to  go to transport listing page."""
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TRANSPORT_TAB)))
        self.driver.find_element_by_css_selector(self.TRANSPORT_TAB).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.TRANSPORT_ADDRESS_TEXT_FIELD)))

    def click_on_quick_room_transfer_tab(self):
        """Click on Quick Room Transfer tab from navigation bar to  go to quick room transfer page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.QUICK_ROOM_TRANSFER_TAB)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.QUICK_ROOM_TRANSFER_TAB)))
        self.driver.find_element_by_css_selector(self.QUICK_ROOM_TRANSFER_TAB).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SECTION_TITLE)))

    def click_on_airline_tab(self):
        """Click on Airline tab from navigation bar to  go to airline page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.AIRLINE_TAB)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.AIRLINE_TAB)))
        self.driver.find_element_by_css_selector(self.AIRLINE_TAB).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.AIRLINE_SEARCH_FILTER)))

    def click_on_voucher_tab(self):
        """Click on Voucher tab from navigation bar to  go to voucher listing page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.VOUCHER_TAB)))
        self.driver.find_element_by_css_selector(self.VOUCHER_TAB).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SEARCH_VOUCHER_TEXT_FIELD)))

    def click_on_quick_voucher_button(self):
        """Click on Quick Voucher button from navigation bar to  go to quick voucher page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.QUICK_VOUCHER_BUTTON)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.QUICK_VOUCHER_BUTTON)))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.SEARCH_BUTTON_DISABLE)))
        self.driver.find_element_by_xpath(self.QUICK_VOUCHER_BUTTON_XPATH).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REQUESTING_PORT)))

    def click_on_reports_tab(self):
        """Click on Reports tab from navigation bar to go to drop down menu of reports. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.REPORTS_TAB)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.REPORTS_TAB)))
        self.driver.find_element_by_css_selector(self.REPORTS_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_REPORT)))

    def click_on_room_count_report(self):
        """Click on Room Count Report menu from rop down menu to go to room count report page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_REPORT)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ROOM_COUNT_REPORT)))
        self.driver.find_element_by_css_selector(self.ROOM_COUNT_REPORT).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ROOM_COUNT_VOUCHER_BUTTON)))

    def click_on_ports_tab(self):
        """Click on PORTS tab from navigation bar to go to PORTS page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORTS_TAB)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.PORTS_TAB)))
        self.driver.find_element_by_css_selector(self.PORTS_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORT_ALLOWANCE_TAB)))

    def click_on_port_allowances_tab(self):
        """Click on PORT ALLOWANCE tab from navigation bar to go to PORT ALLOWANCE page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.PORT_ALLOWANCE_TAB)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.PORT_ALLOWANCE_TAB)))
        self.driver.find_element_by_css_selector(self.PORT_ALLOWANCE_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_ALLOWANCE)))

    def click_on_tva_users_tab(self):
        """Click on TVA USERS tab from navigation bar to go to TVA USERS page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.TVA_USERS_TAB)))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.TVA_USERS_TAB)))
        self.driver.find_element_by_css_selector(self.TVA_USERS_TAB).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADD_NEW_USER_BUTTON)))

    def click_on_configurations_button(self, double_click=False):
        """ Click on Configurations button from navigation bar to go to Configurations page. """
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_INFO_DROPDOWN)))
        user_info_button = self.driver.find_element_by_css_selector(self.USER_INFO_DROPDOWN)
        self.driver.execute_script("arguments[0].click();", user_info_button)
        if double_click:
            user_info_button = self.driver.find_element_by_css_selector(self.USER_INFO_DROPDOWN)
            self.driver.execute_script("arguments[0].click();", user_info_button)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.USER_INFO_DROPDOWN_OPEN)),
                        "User info dropdown doesn't open.")
        configurations_button = self.driver.find_element_by_css_selector(self.CONFIGURATIONS_BUTTON)
        self.driver.execute_script("arguments[0].click();", configurations_button)
        self.wait.until(EC.url_contains('configurations.php'), "Configuration page is not opened yet.")
