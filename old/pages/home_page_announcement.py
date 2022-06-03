import os
from old.pages.common_helper_func import HelperFunctions
from old.constants import BASE_URL
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException


class ERPHomPageAnnouncement(HelperFunctions):
    """
    ERP Home Page(Announcement Section)
    """

    url = os.path.join(BASE_URL, 'announcements')

    def is_browser_on_page(self):
        """
        Verify if browser is on correct page
        """
        self.wait_for_ajax()
        return self.wait_for_visibility_of_element('.pinnedLabel')

    def enter_some_value_in_search_bar(self, search_text):
        """
        Enter some values in search bar and search
        :param search_text: text value for field to enter
        """
        search_bar = self.wait_for_an_element_to_be_present('.announcements [type="text"]')

        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(search_bar).click(on_element=search_bar)
        action_chains.send_keys(search_text)
        action_chains.send_keys(Keys.ENTER)
        action_chains.perform()
        self.wait_for_ajax()

        # Find out all searched results, else it would show timeout exception error
        try:
            self.wait_for_visibility_of_element('#announcement .news h2')
            return self.wait_for_all_elements_to_be_present('#announcement .news h2')

        except TimeoutException:
            self.wait_for_text_to_be_present('#announcement', 'No announcement to show right now')
            return self.wait_for_an_element_to_be_present('#announcement').text

    def click_read_more_link_in_announcement_results(self):
        """
        CLick read more link
        Wait for side bars
        """
        self.wait_for_visibility_of_element('#announcements-page')
        read_more = self.wait_for_an_element_to_be_present('.news a')

        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(read_more).click(on_element=read_more)
        action_chains.perform()

        # Wait for side bar to appear.
        return self.wait_for_visibility_of_element('#sidebar')

    def click_news_pin_icon(self):
        """
        Click news pin icon in result
         verify Result is pinned
        """
        try:
            self.wait_for_visibility_of_element('.pinned')
            print("Result is already pinned")
            self.wait_for_an_element_to_be_present('.news-pin.inner').click()
            self.wait_for_visibility_of_element('.pinned')

        except TimeoutException:
            self.wait_for_visibility_of_element('#announcements-page')
            self.wait_for_an_element_to_be_present('.news-pin.inner').click()
            self.wait_for_visibility_of_element('.pinned')
        return True

    def click_checkbox_for_pinned_option(self):
        """
        Click check box for pinned results
        """
        self.wait_for_an_element_to_be_present('[type="checkbox"]').click()
        self.wait_for_ajax()
        return self.wait_for_all_elements_to_be_present('.news .pinned')
