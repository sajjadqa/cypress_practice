

# This page has changes so update is in pipeline

from old.tests.helper_tests import HelperTest
from old.pages.home_page_notes import ERPHomPageNotes
from old.dictionary import dict


class ERPHomePageAddNoteTest(HelperTest):
    """
    Verify Home Page
    """

    def setUp(self):
        super(ERPHomePageAddNoteTest, self).setUp()
        self.home_page_note = ERPHomPageNotes(self.driver)

    def test_add_a_note_in_my_notes(self):
        """
        User can loggedIn
        Verify to be on ERP Hpme Page
        Click Add Note in 'My Notes'
        Popup is opened
        Add title and details
        Click Save
        Verify user note has been added
        """
        self.adding_note_in_my_notes()

    def test_edit_a_created_note(self):
        """
        Verify user can edit a note from a list
        """
        self.adding_note_in_my_notes()

        # Edit a note
        edited_note_text = self.home_page_note.edit_created_note(dict.get('Edit_note'))

        # Make sure edited note text is accurate
        self.assertEqual(edited_note_text, 'Important Task to be Done!!!')

    def test_delete_a_created_note(self):
        """
        Verify user can delete a note
        """
        self.adding_note_in_my_notes()

        # Delete a note and make sure its deleted
        self.assertTrue(self.home_page_note.delete_created_note())
