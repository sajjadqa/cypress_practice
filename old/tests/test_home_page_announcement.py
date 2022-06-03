

# This page has changes so update is in pipeline

from old.tests.helper_tests import HelperTest
from old.dictionary import dict


class ERPHomePageAnnouncement(HelperTest):
    """
    Verify Home Page
    """

    def setUp(self):
        super(ERPHomePageAnnouncement, self).setUp()

    def test_announcement_page_search_bar(self):
        """
        LoggedIn
        CLick 'view all' link in announcement section
        Verify if user is on 'announcement' page
        """
        self.verify_user_is_in_announcement_page()

        # Enter some values in search bar
        header = self.home_page_announcement.enter_some_value_in_search_bar(dict.get('enter_some_values_for_search'))

        if header == "No announcement to show right now":
            self.assertTrue(header)
        else:
            print("Total results found %s" % len(header))

    def test_read_more_link_works_in_announcement_page(self):
        """
        LoggedIn
        CLick 'view all' link in announcement section
        Verify if user is on 'announcement' page
        Verify user can click on read more link
        Side bar seems open
        """
        self.verify_user_is_in_announcement_page()

        # click read more link
        self.assertTrue(self.home_page_announcement.click_read_more_link_in_announcement_results())

    def test_result_can_be_pinned(self):
        """
        LoggedIn
        CLick 'view all' link in announcement section
        Verify if user is on 'announcement' page
        CLick pinned icon in any result
        """
        self.verify_user_is_in_announcement_page()

        # CLick news pin icon
        self.assertTrue(self.home_page_announcement.click_news_pin_icon())

    def test_checked_pinned_option_shows_only_pin_results(self):
        """
        LoggedIn
        CLick 'view all' link in announcement section
        Verify if user is on 'announcement' page
        CLick pinned icon in any result
        """
        self.verify_user_is_in_announcement_page()

        # CLick news pin icon from result
        self.assertTrue(self.home_page_announcement.click_news_pin_icon())

        # Click pinned checkbox and wait for results to appear and make sure there are some results in list
        pinned_results = self.home_page_announcement.click_checkbox_for_pinned_option()
        self.assertNotEqual(len(pinned_results), 0)
