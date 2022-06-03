import os
from old.constants import BASE_URL
from old.pages.common_helper_func import HelperFunctions
from old.constants import ADD_NOTE_CSS, NOTES_HOLDER_CSS


class ERPHomPageNotes(HelperFunctions):
    """
    ERP Home Page(Notes Section)
    """

    url = os.path.join(BASE_URL, 'home')

    def is_browser_on_page(self):
        """
        Verify if browser is on correct page
        """
        self.wait_for_ajax()
        return self.wait_for_visibility_of_element('#home-page')

    def click_add_note_button(self):
        """
        Click add note button
        """
        self.wait_for_an_element_to_be_present('{} button'.format(NOTES_HOLDER_CSS)).click()
        self.wait_for_visibility_of_element(ADD_NOTE_CSS)

    def fill_add_note_form(self, note_title_text, details_text_value):
        """
        Fill form
        :param note_title_text: title text
        :param details_text_value: details value text
        Click save button
        """

        self.fill_form(title_field=True, details_field=True,
                       title_css=ADD_NOTE_CSS, text_value=note_title_text,
                       details_css=ADD_NOTE_CSS, details_value=details_text_value,
                       button_css=ADD_NOTE_CSS)

    def list_of_all_created_notes(self):
        """
        List of all created notes
        """
        return self.wait_for_all_elements_to_be_present('{} li'.format(NOTES_HOLDER_CSS))

    def edit_created_note(self, note_title_text):
        """
        User can edit already created note
        """
        self.wait_for_an_element_to_be_present('{} .fa-pencil-alt'.format(NOTES_HOLDER_CSS)).click()

        self.fill_form(title_field=True,
                       title_css=ADD_NOTE_CSS, text_value=note_title_text,
                       button_css=ADD_NOTE_CSS)

        return self.wait_for_an_element_to_be_present('{} .transparent a span'.format(NOTES_HOLDER_CSS)).text

    def delete_created_note(self):
        """
        Click Delete icon in a created note
        """
        self.wait_for_an_element_to_be_present('{} .fa-trash'.format(NOTES_HOLDER_CSS)).click()
        return self.wait_for_invisibility_of_element('{} li'.format(NOTES_HOLDER_CSS))
