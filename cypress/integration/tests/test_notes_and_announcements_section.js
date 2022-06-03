import LoginPage from '../pages/login_page'
import HomePage from '../pages/home_page'

let home_page
let news
let title = "Automated Note!"
let detail = "Details for this Automated note..."
let search_note_title = 'Added Note for search note functionality.'
let simple_delete_note_title = "Simple note delete title on home page."
let simple_delete_note_detail = "Simple note delete details on home page."

describe('Notes & Announcements tests', () => {
    before(() => {
        // runs once before all tests in the block
        cy.visit('/')
        const login = new LoginPage('sajjad.akbar@arbisoft.com', 'Erp786786')
        login.fillLoginForm()
        login.submitLoginForm()
    })

    beforeEach(() => {
        cy.restoreLocalStorage();
    });

    afterEach(() => {
        cy.saveLocalStorage();
    });

    it('Verify that user should view only six recent announcements on home page', () => {
        home_page = new HomePage()
        home_page.countRecentAnnouncements()
    })

    it('Verify that user should view all announcements by clicking view all link.', () => {
        news = new HomePage()
        news.clickViewAllAnnouncements()
        news.clickFirstNewsPinnedButton()
        news.clickPinnedCheckbox()
    })

    it('Verify that user should be ale to search the announcement by subject on announcement page', () => {
        home_page = new HomePage()
        home_page.searchAnnouncement(news.NEWS_HEADING)
        home_page.verifySearchedAnnouncemnet(news.NEWS_HEADING)
    })

    it('Verify that Announcemnt drawer should be open and close by clicking the Read More announcement link and close button.', () => {
        home_page = new HomePage()
        home_page.clickHomeTab()
        home_page.clickReadMoreAnnouncement()
        home_page.closeReadMoreAnnouncementDrawer()
    })

    it('Verify that Add a new note pop up should be closed by clicking cancel button.', () => {
        home_page = new HomePage()
        home_page.clickAddNewNoteButton()
        home_page.clickCancelButton()
    })

    it('Verify that user should be able to create a note on Home page.', () => {
        home_page = new HomePage()
        home_page.clickAddNewNoteButton()
        home_page.addNewNote(title, detail)
    })

    it('Verify that user should be able to search the note on Home page.', () => {
        home_page = new HomePage()
        home_page.clickAddNewNoteButton()
        home_page.addNewNote(search_note_title, detail)
        home_page.searchNotes(search_note_title)
    })

    it('Verify that user should be able to open the note and edit it on Home page.', () => {
        home_page = new HomePage()
        home_page.OpenAndEditNote()
    })

    it('Verify that user should be able to edit the note by clicking edit note button on Home page.', () => {
        home_page = new HomePage()
        home_page.editNote()
    })

    it('Verify that user should be able to delete the note by clicking delete note button on Home page.', () => {
        home_page = new HomePage()
        home_page.clickAddNewNoteButton()
        home_page.addNewNote(simple_delete_note_title, simple_delete_note_detail)
        home_page.deletedNotes()
    })

    it('Verify that user should be able to open the note and delete it.', () => {
        home_page = new HomePage()
        home_page.clickAddNewNoteButton()
        home_page.addNewNote(simple_delete_note_title, simple_delete_note_detail)
        home_page.openAndDeleteNote()
    })
})
