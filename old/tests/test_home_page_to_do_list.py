

# This page has changed to 'Google task', So still some changes are in pipeline
# Skip for now


from old.tests.helper_tests import HelperTest
from old.dictionary import dict
from old.constants import HOME_PAGE_COL


class ERPHomePageToDoListTest(HelperTest):
    """
    Verify Home Page
    """

    def setUp(self):
        super(ERPHomePageToDoListTest, self).setUp()

    def test_home_page(self):
        """
        Verify Home page
        """
        self.loggedIn_and_verification_of_home_page()

    def test_all_columns_on_home_page(self):
        """
        -Verify LoggedIn
        -Verify Browser on page
        -Verify four columns display on home page
            .My Task
            .To Do List
            .My Notes
            .Announcements
        """
        self.loggedIn_and_verification_of_home_page()
        columns_header = self.home_page_to_do_list.home_page_columns()

        # Make sure all correct 4 columns on home page
        for title, each_col in zip(columns_header, HOME_PAGE_COL):
            title = title.text
            self.assertEqual(title, each_col)

    def test_create_new_list(self):
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
        """
        self.loggedIn_and_verification_of_home_page()
        self.home_page_to_do_list.click_my_task_and_create_new_list()
        user_list_name = self.home_page_to_do_list.fill_new_list_form_and_save(dict.get('enter_title_text'))
        self.assertEqual(user_list_name, dict.get('enter_title_text'))

    def test_add_task_into_existing_list(self):
        """
        Verify user can task add into task list
        """
        task_list = self.adding_task_into_existing_list()

        # Make sure task is showing in list
        self.assertNotEqual(len(task_list), 0)

    def test_delete_task_from_existing_list(self):
        """
        Verify user can delete an added task from a list
        """
        self.adding_task_into_existing_list()
        self.assertTrue(self.home_page_to_do_list.delete_added_task_in_a_list())

    def test_edit_task_from_existing_list(self):
        """
        Verify user can edit task
        """
        self.adding_task_into_existing_list()
        self.assertTrue(self.home_page_to_do_list.edit_task_from_a_list(dict.get('edit_details_text')))

    def test_edit_list_name_of_task(self):
        """
        Verify user can edit task list name by clicking edit from menu dropdown
        """
        self.loggedIn_and_verification_of_home_page()
        task_edit_name = self.home_page_to_do_list.edit_list_name(dict.get('edit_title_text_of_list'))
        self.assertEqual(task_edit_name, 'My Tasks List')

    def test_delete_created_list(self):
        """
        Verify user can delete already created list
        """
        self.loggedIn_and_verification_of_home_page()
        self.home_page_to_do_list.click_my_task_and_create_new_list()
        user_list_name = self.home_page_to_do_list.fill_new_list_form_and_save(dict.get('enter_title_text'))
        self.assertEqual(user_list_name, dict.get('enter_title_text'))
        self.home_page_to_do_list.delete_existing_list()

    def test_save_new_list_with_empty_field(self):
        """
        Verify user cannot save a new list with empty title field
        Note down error message
        """
        self.loggedIn_and_verification_of_home_page()
        error_message = self.home_page_to_do_list.empty_field_error_while_saving_new_list_name()
        self.assertEqual(error_message, 'Please enter any title for list')








