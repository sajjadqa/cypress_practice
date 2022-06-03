
import random
from datetime import datetime
from datetime import date


# Static function
def random_text():
    """
    Generate random text values
    """
    random_string = random.randint(1, 10)
    random_title_text = 'Test_%s' % random_string
    return random_title_text

#
# def random_number(number):
#     """
#     Generate some randome number
#     """
#     random_nmbr = random.randint(1, number)
#     return random_nmbr


random_title = random_text()

now = datetime.now()
today = date.today()
current_month = today.month
current_day = today.day

dict = {
    'enter_title_text': random_title,
    'edit_title_text_of_list': ' List',
    'enter_title_of_task': 'Automate ERP !!!',
    'add_details_text': 'Complete the task!',
    'edit_details_text': '!!!',
    'task_due_date_month': current_month,
    'task_due_date_day': current_day,
    'task_due_date_year': '2019',
    'add_note': 'Important Task to be',
    'details_note_text': 'This needs to be done tomorrow!!!',
    'Edit_note': ' Done!!!',
    'enter_some_values_for_search': 'sfgdfgsfgfgdfdfd'
}

parent_form_dict = {
    'Loan': {'Describe the purpose': {'correct_input': 'val1',
                                      'func_to_call_for_qs': 'enter_answers_for_field_questions',
                                      'empty_field_error': 'Please answer all required questions'},
             'Payback Duration': {'empty_field_error': 'Form amount is not provided',
                                  'func_to_call_for_qs': 'enter_answers_for_field_questions'},
             'Amount': {'correct_input': '2000', 'empty_field_error': 'Form amount is not provided',
                        'greater_input': '40000',
                        'form_submission_message': 'Form has been submitted successfully'},
             },
    'Social Impact': {'What\'s the name of your recommended organization?': {'correct_input': 'Support',
                      'func_to_call_for_qs': 'enter_answers_for_field_questions', 'empty_field_error':
                                                                                  'Please answer all required questions'},
                      'Briefly describe what this organization does:': {'correct_input': 'Funding',
                                                                        'func_to_call_for_qs':
                                                                            'enter_answers_for_field_questions',
                                                                        'empty_field_error':
                                                                            'Form amount is not provided'},
                      'Please enter the contact details for the point person at your recommended'
                      ' organization (Name, Phone, Email):': {'correct_input': 'TesterERP: 03024567890',
                                                              'func_to_call_for_qs': 'enter_answers_for_field_questions',
                                                              'empty_field_error': 'Form amount is not provided'},
                      'Briefly describe why you think it will be a good idea for Arbisoft'
                      ' to partner up with your recommended organization?': {'correct_input': 'Do not want to tell.',
                                                                             'func_to_call_for_qs':
                                                                                 'enter_answers_for_field_questions',
                                                                             'empty_field_error':
                                                                             'Form amount is not provided'},
                      'What\'s the proposed nature of Arbisoft\'s partnership with your recommended organization?': {
                      'func_to_call_for_qs': 'enter_answers_for_field_questions', 'empty_field_error':
                              'Form amount is not provided'},
                      'If you selected Option 02 or 03 in the above question, do you have'
                      ' enough time in your schedule to accommodate another project?': {
                          'func_to_call_for_qs': 'enter_answers_for_field_questions',
                          'empty_field_error': 'Form amount is not provided'}},
    'ISMS Incident': {'Concerning Department': {'func_to_call_for_qs': 'enter_answers_for_field_questions',
                                                'empty_field_error': 'Please answer all required questions'},
                      'Description of Incident': {'func_to_call_for_qs': 'enter_answers_for_field_questions',
                                                  'correct_input': 'ABC',
                                                  'empty_field_error': 'Please answer all required questions'},
                      'Actual loss caused by the incident': {'empty_field_error': 'Please answer all required questions',
                                                             'correct_input': 'Accident',
                                                             'func_to_call_for_qs': 'enter_answers_for_field_questions',
                                                             'form_submission_message':
                                                                 'Form has been submitted successfully'}},
    'Donation': {'Name of the person/organization': {'correct_input': 'Chester Benn.',
                                                     'empty_field_error': 'Please answer all required questions',
                                                     'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                 'Your connection with the person/organization?':
                     {'correct_input': 'collegue',
                      'func_to_call_for_qs': 'enter_answers_for_field_questions',
                      'empty_field_error': 'Please answer all required questions'},
                 'CNIC of the person receiving donation': {'correct_input': '35202196778',
                                                           'empty_field_error': 'Please answer all required questions',
                                                           'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                 'Purpose of the donation': {'correct_input': 'want to help poors',
                                             'empty_field_error': 'Please answer all required questions',
                                             'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                 'Has this person/organization received a donation from Arbisoft in the past 6/12 months?':
                     {'empty_field_error': 'Please answer all required questions',
                      'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                 'Payment type': {'empty_field_error': 'Please answer all required questions',
                                  'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                 'The amount you are looking to donate? (25% of which will be donated by the referrer)':
                     {'empty_field_error': 'Please answer all required questions',
                      'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                 'Type of donation': {'empty_field_error': 'Please answer all required questions',
                                      'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                 'Amount': {'correct_input': '4000', 'empty_field_error': 'Form amount is not provided',
                            'form_submission_message': 'Form has been submitted successfully'}},
    'Advance Salary': {'Amount': {'correct_input': '3000', 'empty_field_error': 'Form amount is not provided',
                                  'form_submission_message': 'Form has been submitted successfully'}},
    'Society Signup': {'Which society would you like to volunteer?': {'func_to_call_for_qs':
                                                                      'choose_radio_button_choices',
                                                                      'empty_field_error':
                                                                          'Please answer all required questions'},
                       'Share your reason for interest': {'empty_field_error': 'Please answer all required questions',
                                                          'func_to_call_for_qs': 'enter_answers_for_field_questions',
                                                          'correct_input': 'Interested',
                                                          'form_submission_message':
                                                              'Form has been submitted successfully'}},
    'Support Fund': {'Choose the relevant category for your case': {'empty_field_error':
                                                                    'Please answer all required questions',
                                                                    'func_to_call_for_qs':
                                                                        'enter_answers_for_field_questions'},
                     'Please provide more information about the category you have chosen': {
                        'empty_field_error': 'Please answer all required questions', 'correct_input':
                        'Testing purpose task.',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                     'If the committee cannot approve the full amount you requested, would you be '
                     'interested in availing the loan policy in combination with support fund': {
                        'empty_field_error': 'Please answer all required questions',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                     'Amount': {'empty_field_error': 'Form amount is not provided', 'correct_input': '50000',
                                'form_submission_message': 'Form has been submitted successfully'}}
}

child_option_dict = {
    'Team Lead': {'Would you be interested in a promotion within your existing project or outside it': {
                        'empty_field_error': 'Please answer all required questions',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                  'Share your reason for interest towards being a team lead/Project Manager': {
                        'empty_field_error': 'Please answer all required questions',
                        'correct_input': 'Experienced',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions',
                        'form_submission_message': 'Form has been submitted successfully'}},
    'Advisory': {'Choose the advisory committee you would like to join': {
                        'empty_field_error': 'Please answer all required questions',
                        'func_to_call_for_qs': 'choose_random_checkboxes_options'},
                 'Share your reason for interest towards the chosen advisory committee': {
                        'empty_field_error': 'Please answer all required questions',
                        'correct_input': 'Eligible for this.',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions',
                        'form_submission_message': 'Form has been submitted successfully'
                 }},
    'Functional': {'Share the tech stack you would like to move to': {
                        'empty_field_error': 'Please answer all required questions',
                        'func_to_call_for_qs': 'choose_random_checkboxes_options'},
                   'Share your reason for interest towards the particular tech stack': {
                        'empty_field_error': 'Please answer all required questions',
                        'correct_input': 'Particular experience',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions',
                        'form_submission_message': 'Form has been submitted successfully'
                   }},
    'A Team Shift': {'Mention the team/Project you would like to go to': {
                        'empty_field_error': 'Please answer all required questions',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions',
                        'correct_input': 'KAYAK BlackBox'},
                     'Share your reason for interest towards a team/project shift': {
                        'empty_field_error': 'Please answer all required questions',
                        'correct_input': 'It enough now',
                        'func_to_call_for_qs': 'enter_answers_for_field_questions',
                        'form_submission_message': 'Form has been submitted successfully'
                    }},
    'Project Manager': {'Would you be interested in a promotion within your existing project or outside it': {
                            'empty_field_error': 'Please answer all required questions',
                            'func_to_call_for_qs': 'enter_answers_for_field_questions'},
                        'Share your reason for interest towards being a team lead/Project Manager': {
                            'empty_field_error': 'Please answer all required questions',
                            'func_to_call_for_qs': 'enter_answers_for_field_questions',
                            'correct_input': 'Im much experienced in this field now.',
                            'form_submission_message': 'Form has been submitted successfully'
                        }}
}
