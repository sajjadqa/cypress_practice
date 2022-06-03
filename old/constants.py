# Credentials
import os


USER_EMAIL = os.getenv("useremail")
USER_PWD = os.getenv("userpassword")
ADMIN_USER = os.getenv("adminuser")
ADMIN_PSWD = os.getenv("adminpassword")

# url
# BASE_URL = "https://workstream-staging3.arbisoft.com/app/"
BASE_URL = "https://workstream-staging4.arbisoft.com/app/"


# Login css_selectors
BUTTON_CSS = "#erp-google-login"
EMAIL_FIELD_CSS = "[aria-label='Email or phone']"
PWD_FIELD_CSS = "[aria-label='Enter your password']"


# Home_Page_columns
HOME_PAGE_COL = ['My Tasks', 'To Do List', 'Google Tasks', 'Announcements']

# Create new list in to do list
LIST_TASK = '.googletask-holder > div div:nth-child(2) div > div'

# Google dialogue alert
GOOGLE_TASK_ALERT_DIALOG = '#google-tasks-alert-dialog-slide-description'
NEW_TASK_LIST = '#new-task-list-alert-dialog-slide-description'
NEW_TASK_LIST_SAVE_BUTTON = '[aria-labelledby="new-task-list-alert-dialog-slide-title"]'
GOOGLE_TASK_ALERT_SAVE_BUTTON = '[aria-labelledby="google-tasks-alert-dialog-slide-title"]'

# Notes Section CSS_Selctors
ADD_NOTE_CSS = '[aria-labelledby="notes-alert-dialog-slide-title"]'
NOTES_HOLDER_CSS = '.personnote-holder'

# Elements to verify from different forms
FORM_DROPDOWN_CSS = '.form-type-dropdown'
FORM_DASHBOARD = '.forms-dashboard'
FORM_QS = '.form-question'
MENU_LIST = '#menu- ul[role="listbox"] li'
MENU_CHOICE_CLASS = '.choices'
CSS_TO_VERIFY = ['.Loan', '.Social.Impact', '.ISMS.Incident', '.Donation', '.Support.Fund', '.Transition', '.Society',
                 '.Advance.Salary']

# Submit buttons
SUBMIT_BUTTON_CSS = '.new-form-modal [type="button"]'
TEXT_MSG = 'You are applying for more than the entitled amount, do you want to continue?'

# contains all form options from droddown
form_option_list = ['Loan', 'Donation', 'Advance Salary', 'ISMS Incident', 'Social Impact', 'Society Signup',
                    'Support Fund', 'Transition']

form_sub_list_options = ['Team Lead', 'Advisory', 'Functional', 'A Team Shift', 'Project Manager']
