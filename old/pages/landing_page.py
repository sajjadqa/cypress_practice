import os
from old.pages.common_helper_func import HelperFunctions
from old.constants import BUTTON_CSS, BASE_URL


class ERPLandingPage(HelperFunctions):
    """
    Landing Page
    """
    url = os.path.join(BASE_URL, 'login')

    def is_browser_on_page(self):
        """
        To make sure browser is on correct page
        """
        self.wait_for_ajax()
        self.wait_for_visibility_of_element(BUTTON_CSS)

    def click_login_with_google_button(self):
        """
        Click 'login with google button'
        """
        click_button = self.wait_for_an_element_to_be_present(BUTTON_CSS)
        click_button.click()
        self.wait_for_ajax()
