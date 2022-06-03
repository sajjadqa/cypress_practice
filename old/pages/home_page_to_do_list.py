

# This page has changed to 'Google task', So still some changes are in pipeline
# Skip for now

import os
from old.pages.common_helper_func import HelperFunctions
from old.constants import BASE_URL
from selenium.webdriver import ActionChains
from old.constants import (LIST_TASK,
                           GOOGLE_TASK_ALERT_DIALOG,
                           NEW_TASK_LIST,
                           NEW_TASK_LIST_SAVE_BUTTON, GOOGLE_TASK_ALERT_SAVE_BUTTON
                           )


class ERPHomePageToDoList(HelperFunctions):
    """
    ERP Home Page(To do list)
    """
    url = os.path.join(BASE_URL, 'home')

    def is_browser_on_page(self):
        """
        Verify if browser is on correct page
        """
        self.wait_for_ajax()
        return self.wait_for_visibility_of_element('#home-page')

    def home_page_columns(self):
        """
        Four columns display on home page
            .My Task
            .To Do List
            .My Notes
            .Announcements
        """
        return self.wait_for_all_elements_to_be_present('#home-page h2')

    def click_view_all_in_announcement_section(self):
        """
        Click on view all link in announcement section
        """
        self.wait_for_visibility_of_element('[href="/app/home/announcements"]')
        self.wait_for_an_element_to_be_present('a[href="/app/home/announcements"]').click()
        self.wait_for_ajax()

    def click_my_task_and_create_new_list(self):
        """
        Click on 'My Task'
        Dropdown is in display
        Click 'Create new list' from dropdown
        """
        self.wait_for_ajax()
        self.wait_for_visibility_of_element('.googletask-holder > div div:nth-child(2)')
        self.wait_for_text_to_be_present('.googletask-holder > div div:nth-child(2) > div', 'My Tasks')

        # Click on 'My Task'
        self.wait_for_an_element_to_be_present('.googletask-holder > div div:nth-child(2) > div').click()

        # Click 'Create new list' option from dropdown
        self.wait_for_an_element_to_be_present('#menu- ul > li:nth-last-child(1)').click()
        self.wait_for_ajax()

    def click_created_list_name(self):
        """
        Click on list that is created by user
        """
        self.wait_for_an_element_to_be_present('#menu- ul > li:nth-last-child(3)').click()
        self.wait_for_ajax()

    def fill_new_list_form_and_save(self, enter_title):
        """
        Click 'My Task' in 'To Do List'
        """
        self.fill_form(title_field=True, title_css=NEW_TASK_LIST, text_value=enter_title,
                       button_css=NEW_TASK_LIST_SAVE_BUTTON)
        self.wait_for_ajax()
        self.wait_for_visibility_of_element(LIST_TASK)

        # Return the 'entered title text' value
        return self.wait_for_an_element_to_be_present(LIST_TASK).text

    def adding_task_in_existing_list(self, **kwargs):
        """
        Add any task into existing list
        """

        # Click on link '+ Add Task'
        self.wait_for_ajax()
        self.wait_for_an_element_to_be_present('.googletask-holder div:nth-child(1) button').click()
        self.wait_for_visibility_of_element('[type="date"]')

        # Fill form
        self.fill_form(title_field=True, details_field=True, date_field=True, title_css=GOOGLE_TASK_ALERT_DIALOG,
                       text_value=kwargs.get('task_title'),
                       details_css=GOOGLE_TASK_ALERT_DIALOG,
                       details_value=kwargs.get('details_field_text'),
                       month_value=kwargs.get('enter_due_date_month'),
                       date_value=kwargs.get('enter_due_date_day'),
                       year_value=kwargs.get('enter_due_date_year'),
                       button_css=GOOGLE_TASK_ALERT_SAVE_BUTTON)

        # Task Added in a list
        return self.wait_for_all_elements_to_be_present('.googletask-holder li')

    def delete_added_task_in_a_list(self):
        """
        Delete added task in an existing list
        """
        self.wait_for_an_element_to_be_present('.fa-trash').click()

        return self.wait_for_invisibility_of_element('.googletask-holder li')

    def edit_task_from_a_list(self, edit_task_detail):
        """
        Edit added task in an existing list
        """
        self.wait_for_an_element_to_be_present('span.fa-pencil-alt').click()

        self.fill_form(details_field=True, details_css=GOOGLE_TASK_ALERT_DIALOG,
                       details_value=edit_task_detail, button_css=GOOGLE_TASK_ALERT_SAVE_BUTTON)
        self.wait_for_ajax()

        return self.wait_for_an_element_to_be_present('.googletask-holder li')

    def click_list_menu_dots(self):
        """
        Click menu dots dropdown
        """
        self.driver.find_element_by_css_selector('button[aria-label="More"]').click()
        self.wait_for_ajax()

    def click_edit_from_menu_dropdowm(self):
        """
        Click menu dots, dropdown opens
        Click edit option
        """

        # Wait for the text 'My Tasks' to be appeared
        self.wait_for_text_to_be_present('.googletask-holder > div div:nth-child(2) > div', 'My Tasks')

        # Click menu dots for a list
        self.click_list_menu_dots()

        # Wait for dropdown to display
        self.wait_for_visibility_of_element('ul[role="menu"]')

        # Click edit option and wait for popup
        edit_element = self.wait_for_an_element_to_be_present('#render-props-menu li:nth-child(1)')
        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(edit_element).click(on_element=edit_element).perform()

    def edit_list_name(self, edit_title_text):
        """
        Click menu dots and click edit option
        Edit list name in title field
        """

        self.click_edit_from_menu_dropdowm()

        # Edit the list name and save , return the new saved title text
        return self.fill_new_list_form_and_save(edit_title_text)

    def delete_existing_list(self):
        """
        Delete already existing list
        """

        # click on menu dots, dropdown display
        self.click_list_menu_dots()

        # Click delete option from dropdown, dialogue box will appear
        delete_option = self.wait_for_an_element_to_be_present('#render-props-menu li:nth-last-child(1)')
        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(delete_option).click(on_element=delete_option).perform()
        self.wait_for_visibility_of_element('[aria-labelledby="alert-dialog-title"]')

        # CLick yes from dialogue box
        element = self.wait_for_an_element_to_be_present('[aria-labelledby="alert-dialog-title"] .modalminWidth button')
        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(element).click(on_element=element).perform()
        self.wait_for_ajax()

    def empty_field_error_while_saving_new_list_name(self):
        """
        Save a new list with empty title while creating(list for task)
        Note the error message
        """

        # Click create new list option from 'My Task' dropdown
        self.click_my_task_and_create_new_list()

        # Click save button in popup
        self.click_save_button(NEW_TASK_LIST_SAVE_BUTTON)

        # return the error value text
        return self.wait_for_an_element_to_be_present('.Toastify__toast-body').text
