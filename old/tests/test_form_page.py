from old.tests.helper_tests import HelperTest
from old.constants import form_option_list, form_sub_list_options


class ERPFormPageTest(HelperTest):
    """
    Verify Home Page
    """

    def setUp(self):
        super(ERPFormPageTest, self).setUp()

    def test_new_form_button_is_clickable(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is clickable
        """
        self.loggedIn_and_verification_of_forms_page()
        self.assertTrue(self.my_forms_page.click_new_form_button())

    def test_submission_of_Loan_form_with_entitled_amount(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is clickable
        Verify all options are clickable in dropdpwn
        Verify 'Loan' form is submitted successfully with entitled amount
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[0])
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[0], last_qs[-1])

    def test_submission_of_Loan_form_with_greater_amount_and_continue(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is clickable
        Verify all options are clickable in dropdpwn
        Verify 'Loan' form is showing confirmation message for more than entitled amount
        Accept 'YES'
        verify form submitted
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[0], greater_amount=True,
                                                        confirmation_status=True)
        self.verification_of_alert_message(form_option_list[0], last_qs[-1])
        self.assertEqual(self.my_forms_page.form_is_added_in_list(), form_option_list[0])

    def test_submission_of_Loan_form_with_greater_amount_and_discontinue(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is clickable
        Verify all options are clickable in dropdpwn
        Verify 'Loan' form is showing confirmation message for more than entitled amount
        Decline offer
        Verify form stays for selected option
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[0], greater_amount=True)
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[0], last_qs[-1])

    def test_submission_of_Donation_form_with_entitled_amount(self):
        """
         Logged In
         Visit Form Page
         Verify 'New Form' button is click able
         Verify all options are click able in dropdown
         Verify 'Donation' form submitted successfully with entitled amount
         """
        last_qs = self.click_and_verify_form_submission(form_option_list[1])
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[1], last_qs[-1])

    def test_submission_of_Advance_salary_form_with_entitled_amount(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Verify all options are click able in dropdown
        Verify 'Advance Salary' form submitted successfully with entitled salary
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[2])
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[2], last_qs[-1])

    def test_submission_of_ISMS_Incident_with_required_fields(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Verify all options are click able in dropdown
        Verify 'ISMS Incident' form submitted successfully with all required fields
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[3])
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[3], last_qs[-1])

    def test_submission_of_Social_Impact_with_required_fields(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Verify all options are click able in dropdown
        Verify 'Social Impact' form submitted successfully with all required fields
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[4])
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[4], last_qs[-1])

    def test_submission_of_Society_Signup_with_required_fields(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Verify all options are click able in dropdown
        Verify 'Society Signup' form submitted successfully with all required fields
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[5])
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[5], last_qs[-1])

    def test_submission_of_Support_fund_with_required_fields(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Verify all options are click able in dropdown
        Verify 'Support Fund' form submitted successfully with all required fields
        """
        last_qs = self.click_and_verify_form_submission(form_option_list[6])
        self.verify_submission_message_and_forms_addition_in_a_list(form_option_list[6], last_qs[-1].text)

    def test_submission_of_Transition_for_team_lead(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Select 'Transition' in  dropdown
        Choose 'team lead' from 'Transition' dropdown
        Verify 'Team Lead' form is submitted successfully
        """
        last_qs = self.click_and_verify_transition_form_submission(form_option_list[7], form_sub_list_options[0])
        print(last_qs[-1].text)

        self.verify_submission_message_for_nested_transition_form(form_sub_list_options[0], form_option_list[7],
                                                                  last_qs[-1].text)

    def test_submission_of_Transition_for_Advisory(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Select 'Transition' in  dropdown
        From Choose Transition ,select 'Advisory'
        Verify 'Advisory' form is submitted successfully
        """
        last_qs = self.click_and_verify_transition_form_submission(form_option_list[7], form_sub_list_options[1])
        print(last_qs[-1].text)

        self.verify_submission_message_for_nested_transition_form(form_sub_list_options[1], form_option_list[7],
                                                                  last_qs[-1].text)

    def test_submission_of_Transition_for_Functional(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Select 'Transition' in  dropdown
        From Choose Transition ,select 'Functional'
        Verify 'Functional' form is submitted successfully
        """
        last_qs = self.click_and_verify_transition_form_submission(form_option_list[7], form_sub_list_options[2])
        print(last_qs[-1].text)

        self.verify_submission_message_for_nested_transition_form(form_sub_list_options[2], form_option_list[7],
                                                                  last_qs[-1].text)

    def test_submission_of_Transition_for_A_Team_Shift(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Select 'Transition' in  dropdown
        From Choose Transition ,select 'A_Team_Shift'
        Verify 'A_Team_Shift' form is submitted successfully
        """
        last_qs = self.click_and_verify_transition_form_submission(form_option_list[7], form_sub_list_options[3])
        print(last_qs[-1].text)

        self.verify_submission_message_for_nested_transition_form(form_sub_list_options[3], form_option_list[7],
                                                                  last_qs[-1].text)

    def test_submission_of_Transition_for_Project_Manager(self):
        """
        Logged In
        Visit Form Page
        Verify 'New Form' button is click able
        Select 'Transition' in  dropdown
        From Choose Transition ,select 'Project_Manager'
        Verify 'Project_Manager' form is submitted successfully
        """
        last_qs = self.click_and_verify_transition_form_submission(form_option_list[7], form_sub_list_options[4])
        print(last_qs[-1].text)

        self.verify_submission_message_for_nested_transition_form(form_sub_list_options[4], form_option_list[7],
                                                                  last_qs[-1].text)

