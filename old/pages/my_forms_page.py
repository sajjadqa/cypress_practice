import os
from old.constants import BASE_URL
import random
from selenium.common.exceptions import TimeoutException
from old.pages.common_helper_func import HelperFunctions
from old.constants import FORM_QS, MENU_LIST, SUBMIT_BUTTON_CSS, FORM_DASHBOARD, TEXT_MSG, MENU_CHOICE_CLASS
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time


class ERPMyFormPage(HelperFunctions):
    """
    ERP My Form Page
    """

    url = os.path.join(BASE_URL, 'forms/dashboard')

    def is_browser_on_page(self):
        """
        Verify if browser is on correct page
        """
        self.wait_for_ajax()
        return self.wait_for_visibility_of_element('.text-right [type="button"]')

    def click_new_form_button(self):
        """
        Click new form button
        """
        self.wait_for_an_element_to_be_present('.text-right [type="button"]').click()
        self.wait_for_ajax()

        # Wait for popup to open
        return self.wait_for_visibility_of_element('.form-type-dropdown')

    def click_choose_form_dropdown(self):
        """
        CLick select form dropdown
        """
        self.wait_for_ajax()
        click_menu = self.wait_for_an_element_to_be_present('.form-type-dropdown')

        # Use action chains to move on dropdown element and click on.
        action_chains = ActionChains(self.driver)
        action_chains.click(on_element=click_menu).perform()
        self.wait_for_ajax()

        # Wait for menu list to open
        return self.wait_for_visibility_of_all_elements(MENU_LIST)

    def click_transition_tab_dropdown_and_note_menu(self):
        """
        Click 'choose transition' form tab:
            -Wait for 'Menu' to open
        """
        transition_tab = self.wait_for_an_element_to_be_present(MENU_CHOICE_CLASS)

        # Use action chains to move and click on element
        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(transition_tab).click(on_element=transition_tab).perform()
        self.wait_for_visibility_of_all_elements(MENU_LIST)

    def click_each_option_from_list_menu(self, ind_number):
        """
        Click each option one by one from dropdown 'Choose Form' menu list
        :param ind_number: index number for each option
        :return: option text
        """
        option_text = self.wait_for_visibility_of_element('{} .{}'.format(MENU_LIST, ind_number))
        self.wait_for_ajax()
        option_text_value = option_text.text

        # Use action chains to click each child from list
        action_chains = ActionChains(self.driver)
        action_chains.click(on_element=option_text).perform()
        self.wait_for_ajax()

        # Return the text of clicked child
        return option_text_value

    def selected_form_questions_list(self):
        """
        Make sure correct form is opened after option click
        """
        self.wait_for_visibility_of_element(SUBMIT_BUTTON_CSS)
        self.wait_for_text_to_be_present(SUBMIT_BUTTON_CSS, 'Submit')
        self.wait_for_the_element_to_be_clickable(SUBMIT_BUTTON_CSS)
        time.sleep(3)
        return self.wait_for_all_elements_to_be_present('.text-bold')

    def click_submit_button(self):
        """
        Click submit button
        """
        self.wait_for_text_to_be_present(SUBMIT_BUTTON_CSS, 'Submit')
        self.wait_for_visibility_of_element(SUBMIT_BUTTON_CSS).click()
        self.wait_for_ajax()

    def note_alert_message_for_fields(self):
        """
        Note error for empty fields
        """
        return self.wait_for_visibility_of_element('{} .Toastify__toast-body'.format(FORM_DASHBOARD)).text

    def enter_answers_for_field_questions(self, **kwargs):
        """
        Two things are going to be checked here:
            -Check if question contains multiple choices answers
                .Choose random values.
            -Else, question contains a text input field for answer
                .Enter field value
        """

        try:
            self.wait_for_visibility_of_element('{}:nth-child({}) {}'.format(FORM_QS,
                                                                             kwargs['ind_number'],
                                                                             MENU_CHOICE_CLASS)).click()
            duration_list = self.wait_for_visibility_of_all_elements(MENU_LIST)
            del duration_list[0]
            random.choice(duration_list).click()
            time.sleep(1)

        except TimeoutException:
            answer_field = self.wait_for_visibility_of_element('{}:nth-child({}) .{} > div'.
                                                               format(FORM_QS, kwargs['ind_number'],
                                                                      kwargs['option']))
            action_chains = ActionChains(self.driver)
            action_chains.click(on_element=answer_field)
            action_chains.send_keys(kwargs['answer']).perform()
        self.wait_for_ajax()

    def enter_number_in_amount_field(self, amount):
        """
        Enter number is 'Amount' field
        """
        amount_field = self.wait_for_visibility_of_element('.number [type="number"]')

        # Using action chains to click on element and escape the dropdown
        action_chains = ActionChains(self.driver)
        action_chains.click(on_element=amount_field)
        action_chains.send_keys(Keys.CONTROL + Keys.BACKSPACE).perform()
        action_chains.send_keys(amount).perform()
        self.wait_for_an_element_to_be_present('[type="number"][value]')
        self.wait_for_invisibility_of_element('.Toastify__toast-body')
        time.sleep(5)
        self.wait_for_ajax()

    def choose_radio_button_choices(self, **kwargs):
        """
        Choose random choice from radio button options
        """
        all_options = self.wait_for_all_elements_to_be_present('{} label'.format(MENU_CHOICE_CLASS))
        random.choice(all_options).click()

    def choose_random_checkboxes_options(self, **kwargs):
        """
        Choose randpm choices from checkboxes
        """
        all_options = self.wait_for_all_elements_to_be_present('.multiple-choices label')
        random.choice(all_options).click()

    def click_option_from_list_or_sub_list(self, option_text, css_class):
        """
        Click options from dropdown sub list
        :param option_text: option text which needs to be selected
        :param css_class: this is the css class used for visibility of an element
        """
        self.driver.find_element_by_xpath("//li[contains(text(),'{}')]".format(option_text)).click()
        time.sleep(1)

        # Wait for element to be selected
        self.wait_for_text_to_be_present('{} div[aria-pressed]'.format(css_class), option_text)
        self.wait_for_ajax()
        return self.wait_for_visibility_of_element(SUBMIT_BUTTON_CSS)

    def amount_field_alert(self, yes_or_no_indx):
        """
        Greater Amount filed alert popup appears
        """
        self.wait_for_text_to_be_present('.modalminWidth p', TEXT_MSG)
        self.wait_for_visibility_of_element('.modalminWidth button:nth-child({})'.format(yes_or_no_indx)).click()
        self.wait_for_visibility_of_element(FORM_DASHBOARD)
        self.wait_for_ajax()

    def form_is_added_in_list(self):
        """
        Form has been added on form's dashboard
        """
        return self.wait_for_an_element_to_be_present('#main-content tbody > tr:nth-child(1) > td:nth-child(2)').text
