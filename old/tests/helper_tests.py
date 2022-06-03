from old.tests.base_test import BaseTest
from old.pages.landing_page import ERPLandingPage
from old.pages.login_page import LoginPage
from old.pages.home_page_to_do_list import ERPHomePageToDoList
from old.dictionary import dict, parent_form_dict, child_option_dict
from old.pages.home_page_notes import ERPHomPageNotes
from old.pages.home_page_announcement import ERPHomPageAnnouncement
from old.pages.wait_for_pages import WaitForClasses
from old.pages.my_forms_page import ERPMyFormPage
from old.constants import FORM_DASHBOARD, FORM_DROPDOWN_CSS, MENU_CHOICE_CLASS
import time
from old.pages import ERPMyProfilePage


class HelperTest(BaseTest):
    """
    Class contains all test helpers
    """
    def setUp(self):
        """
        Instantiate webdriver
        """
        super(HelperTest, self).setUp()
        self.landing_page = ERPLandingPage(self.driver)
        self.login_page = LoginPage(self.driver)
        self.home_page_to_do_list = ERPHomePageToDoList(self.driver)
        self.home_page_note = ERPHomPageNotes(self.driver)
        self.home_page_announcement = ERPHomPageAnnouncement(self.driver)
        self.my_forms_page = ERPMyFormPage(self.driver)
        self.wait_for = WaitForClasses(self.driver)
        self.profile_page = ERPMyProfilePage(self.driver)

    def successfully_loggedIn(self):
        """
        Verify user can login successfully with verified account
        """
        self.landing_page.visit()
        self.landing_page.is_browser_on_page()
        self.landing_page.click_login_with_google_button()
        self.login_page.login()

    def loggedIn_and_verification_of_home_page(self):
        """
        LoggedIn
        Verification to be on HOme Page
        """
        self.successfully_loggedIn()
        self.home_page_to_do_list.is_browser_on_page()

    def adding_task_into_existing_list(self):
        """
        -Verify LoggedIn
        -Verify Browser on page
        -Verify you can click on 'My Task'
            -Dropdown display
            -click create a new list
        -A new task popup display
            -Verify you can add title
            -Click 'Save'
            -New task in a list is added
        -Click on 'Add Task' link
            -Popup display
            -Add title
            -Add details
            -Add due date
            -Click save
        """
        self.loggedIn_and_verification_of_home_page()
        self.home_page_to_do_list.click_my_task_and_create_new_list()
        user_list_name = self.home_page_to_do_list.fill_new_list_form_and_save(dict.get('enter_title_text'))
        self.assertEqual(user_list_name, dict.get('enter_title_text'))

        # Adding task into existing list
        task_list = self.home_page_to_do_list.adding_task_in_existing_list(
            task_title=dict.get('enter_title_of_task'),
            details_field_text=dict.get('add_details_text'),
            enter_due_date_month=dict.get('task_due_date_month'),
            enter_due_date_day=dict.get('task_due_date_day'),
            enter_due_date_year=dict.get('task_due_date_year')
        )
        return task_list

    def adding_note_in_my_notes(self):
        """
        -Verify LoggedIn
        -Verify Browser on page
        -Click add note button
        -Fill add note form
        -Note list of all created notes
        """
        self.loggedIn_and_verification_of_home_page()
        self.home_page_note.click_add_note_button()
        self.home_page_note.fill_add_note_form(dict.get('add_note'), dict.get('details_note_text'))
        notes_list = self.home_page_note.list_of_all_created_notes()

        # Make sure notes list is not empty
        self.assertNotEqual(len(notes_list), 0)

    def verify_user_is_in_announcement_page(self):
        """
        LoggedIn
        CLick 'view all' link in announcement section
        Verify if user is on 'announcement' page
        """
        self.loggedIn_and_verification_of_home_page()
        self.home_page_to_do_list.click_view_all_in_announcement_section()
        self.home_page_announcement.is_browser_on_page()

    def loggedIn_and_verification_of_forms_page(self):
        """
        User LoggedIn and verified home page
        Visit 'My Forms' page
        Verify if user is on 'My Forms' page
        """
        self.loggedIn_and_verification_of_home_page()
        self.my_forms_page.visit()
        self.my_forms_page.is_browser_on_page()

    def click_form_option_from_list(self, selected_option):
        """
        Logged In successfully and moving to form page
        CLick my form button and popup seems display
        Click 'choose form' option and dropdown will appear
        Click an option
        :param selected_option: form which needs to be clicked
        """
        self.loggedIn_and_verification_of_forms_page()
        self.my_forms_page.click_new_form_button()

        # Click 'choose form' dropdown
        self.assertTrue(self.my_forms_page.click_choose_form_dropdown())
        self.assertTrue(self.my_forms_page.click_option_from_list_or_sub_list(selected_option, FORM_DROPDOWN_CSS))

    def enter_amount_field_and_submit(self, selected_option, each_qs, dict_value):
        """
        Enter amount field
        Click submit
        :param selected_option: form which is selected
        :param each_qs: this is question title
        :param dict_value: value to be put in answer field
        """
        self.my_forms_page.enter_number_in_amount_field(
            parent_form_dict[selected_option][each_qs.text][dict_value])
        self.my_forms_page.click_submit_button()
        self.wait_for.wait_for_ajax()

    def verification_of_alert_message(self, selected_option, each_qs):
        """
        Note alert message
        Verify correct message display
        :param selected_option: form which is selected
        :param each_qs:this is question title
        """
        alert_from_dict = parent_form_dict.get(selected_option).get(each_qs).get('form_submission_message')
        alert_message = self.my_forms_page.note_alert_message_for_fields()
        self.assertEqual(alert_message, alert_from_dict)

    def click_and_verify_form_submission(self, selected_option, greater_amount=False, confirmation_status=False):
        """
        Choose a form option to be submitted
        First Verify each question's empty field error  messages
        Enter required answer
        Submit form successfully
        :param selected_option: form which needs to be clicked
        :param greater_amount: If greater Amount value exist(This is the 'Amount' field value, if its greater than
                                                             entitled amount)
        :param confirmation_status: either confirmation_status is yes or no(Either to choose 'yes' or 'no' for
                                                                            confirmation status)
        """
        self.click_form_option_from_list(selected_option)

        qs_list = self.my_forms_page.selected_form_questions_list()
        del qs_list[0]

        # this loop iterate all questions for each form's option
        qs = []
        for ind, each_qs in enumerate(qs_list):
            ind += 2
            time.sleep(1)
            self.my_forms_page.click_submit_button()

            # Verify each empty question field's error message
            self.assertTrue(self.my_forms_page.note_alert_message_for_fields(),
                            parent_form_dict.get(selected_option).get(each_qs.text).get('empty_field_error'))

            # Only for Amount field
            if each_qs.text == "Amount":
                if greater_amount:
                    self.enter_amount_field_and_submit(selected_option, each_qs, 'greater_input')
                    if confirmation_status:  # If to select 'Yes'
                        self.my_forms_page.amount_field_alert(1)

                    else:  # If to select 'No'
                        self.my_forms_page.amount_field_alert(2)
                        time.sleep(1)
                        self.my_forms_page.enter_number_in_amount_field(
                            parent_form_dict[selected_option][each_qs.text]['correct_input'])

                else:
                    self.my_forms_page.enter_number_in_amount_field(
                        parent_form_dict[selected_option][each_qs.text]['correct_input'])
            else:
                selected_option_class = selected_option.replace(' ', '.')
                self.assertTrue(self.wait_for.wait_for_visibility_of_element(FORM_DASHBOARD))
                call_func = getattr(self.my_forms_page, parent_form_dict.get(selected_option).get(each_qs.text)
                                    .get('func_to_call_for_qs'))
                call_func(ind_number=ind, option=selected_option_class,
                          answer=parent_form_dict.get(selected_option).get(each_qs.text).get('correct_input'))

            qs.append(each_qs)
        return qs

    def verify_submission_message_and_forms_addition_in_a_list(self, selected_option, list_value):
        """
        Click submit button
        verify forms submitted
        verify submission green message appears and correct also
        verify correct form has been added in a list on form's dashboard
        """
        self.my_forms_page.click_submit_button()
        self.verification_of_alert_message(selected_option, list_value)
        self.assertEqual(self.my_forms_page.form_is_added_in_list(), selected_option)

    def verify_submission_message_for_nested_transition_form(self, sub_option, selected_option, each_qs):
        """
        Note down Transition's submission form's message
        Click submit button
        verify forms submitted
        verify submission green message appears and correct also
        verify correct form has been added in a list on form's dashboard
        """
        alert_from_dict = child_option_dict.get(sub_option).get(each_qs).get('form_submission_message')
        self.my_forms_page.click_submit_button()

        alert_message = self.my_forms_page.note_alert_message_for_fields()
        self.assertEqual(alert_message, alert_from_dict)
        self.assertEqual(self.my_forms_page.form_is_added_in_list(), selected_option)

    def click_and_verify_transition_form_submission(self, selected_option, sub_option):
        """
        For Transition's all sub options
        :param selected_option: Option needs to be clicked
        :param sub_option: Sub-option needs to be clicked
        """
        self.click_form_option_from_list(selected_option)
        self.my_forms_page.click_transition_tab_dropdown_and_note_menu()
        self.my_forms_page.click_option_from_list_or_sub_list(sub_option, MENU_CHOICE_CLASS)

        qs_list = self.my_forms_page.selected_form_questions_list()
        del qs_list[0:2]

        qs = []
        for ind, each_qs in enumerate(qs_list):
            ind += 3
            time.sleep(1)
            self.my_forms_page.click_submit_button()

            # Verify each empty question field's error message
            self.assertTrue(self.my_forms_page.note_alert_message_for_fields(),
                            child_option_dict.get(sub_option).get(each_qs.text).get('empty_field_error'))

            call_func = getattr(self.my_forms_page, child_option_dict.get(sub_option).get(each_qs.text)
                                .get('func_to_call_for_qs'))
            call_func(ind_number=ind, option=selected_option,
                      answer=child_option_dict.get(sub_option).get(each_qs.text).get('correct_input'))
            qs.append(each_qs)
        return qs
