import os
from old.constants import BASE_URL
from old.pages.common_helper_func import HelperFunctions


class ERPProjectLogsPage(HelperFunctions):
    """
    ERP Project Logs Page
    """

    url = os.path.join(BASE_URL, 'project-logs')

    def is_browser_on_page(self):
        """
        Verify if browser is on correct page
        """
        self.wait_for_ajax()
        return self.wait_for_visibility_of_element('[for="year-select"]')
