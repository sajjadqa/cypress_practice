import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from old.constants import GOOGLE_TASK_ALERT_DIALOG
from old.pages.wait_for_pages import WaitForClasses


class HelperFunctions(WaitForClasses):

    """
    This class contains all common helper functions for pages
    """

    def adding_title_text(self, title_field_css, title_text):
        """
        Add text in title field
        """
        self.wait_for_visibility_of_element(title_field_css)
        task_title = self.wait_for_visibility_of_element('{} input[type="text"]'.format(title_field_css))
        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(task_title)
        action_chains.click(on_element=task_title)
        action_chains.send_keys(title_text)
        action_chains.perform()
        self.wait_for_ajax()

    def adding_details_text(self, details_field_css, task_details):
        """
        Add details of task
        :param details_field_css: this is the css for details field
        :param task_details: Task which is need to enter in field
        """
        self.wait_for_visibility_of_element('textarea:nth-child(3)')
        details_text = self.wait_for_visibility_of_element('{} textarea:nth-child(3)'.format(details_field_css))

        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(details_text).click(on_element=details_text)
        action_chains.send_keys(Keys.CLEAR)
        action_chains.send_keys(task_details)
        action_chains.perform()
        self.wait_for_ajax()

    def adding_due_date(self, month, date, year):
        """
        Adding due date
        """
        self.wait_for_visibility_of_element('input[type="date"]')
        due_date = self.wait_for_an_element_to_be_present('{} input[type="date"]'.format(GOOGLE_TASK_ALERT_DIALOG))

        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(due_date).click(on_element=due_date)
        action_chains.send_keys(month)
        action_chains.send_keys(Keys.TAB)
        action_chains.send_keys(date)
        action_chains.send_keys(year)
        action_chains.perform()
        self.wait_for_ajax()

    def click_save_button(self, button_css):
        """
        Click save button
        """
        self.wait_for_visibility_of_element(button_css)
        self.wait_for_ajax()
        time.sleep(3)
        element = self.wait_for_visibility_of_element('{} button:nth-child(2)'.format(button_css))

        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(element).click(on_element=element).perform()
        time.sleep(5)

    def fill_form(self, title_field=False, details_field=False, date_field=False, **kwargs):
        """
        Fill form
        :param title_field: If Title exist
        :param details_field: If Details field exist
        :param date_field: If Date field exist
        :param kwargs:
        """
        if title_field:
            self.adding_title_text(kwargs.get('title_css'), kwargs.get('text_value'))
        if details_field:
            self.adding_details_text(kwargs.get('details_css'), kwargs.get('details_value'))
        if date_field:
            self.adding_due_date(kwargs.get('month_value'), kwargs.get('date_value'), kwargs.get('year_value'))

        # click Save button
        self.click_save_button(kwargs.get('button_css'))
