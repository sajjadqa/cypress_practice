class HomePage {
   constructor() {
      this.NEWS_HEADING = null
      this.NEWS_DATE = null
  }
   RECENT_ANNOUNCEMENTS = 'div.greeting-card li.MuiListItem-root:nth-of-type(2)>span'
   ADD_NEW_NOTE_BUTTON = 'button[aria-label="Add Note"] [role="presentation"]'
   ADD_NEW_NOTE_DIALOG = 'div[aria-labelledby="person-notes-dialog-title"]'
   ADD_NEW_NOTE_DIALOG_TITLE = 'div[aria-labelledby="person-notes-dialog-title"] #person-notes-dialog-title'
   NOTE_TITLE = 'div[aria-labelledby="person-notes-dialog-title"] #person-notes-dialog-description input[name="noteTitle"]'
   NOTE_DETAILS = 'div[aria-labelledby="person-notes-dialog-title"] #person-notes-dialog-description textarea[name="noteDetail"]'
   SAVE_NOTE_BUTTON = 'div[aria-labelledby="person-notes-dialog-title"] button[type="button"]:nth-of-type(2)'
   REQUIRED_FIELD_MESSAGE = 'div[aria-labelledby="person-notes-dialog-title"] #person-notes-dialog-description div+p.Mui-error'
   EDIT_NOTES_BUTTON = 'li:nth-of-type(1) a span.fa-pencil-alt'
   EDIT_BUTTON_ON_EDIT_NOTE_DIALOG = 'button.person-notes-card-edit-button-comp'
   DELETE_NOTES_BUTTON = 'li:nth-of-type(1) a.person-notes-delete-button-comp span.fa-trash'
   NOTES_MESSAGE_CLICK = 'li:nth-of-type(1) a.person-notes-show-note-detail-comp span'
   NOTES_LIST = 'a.person-notes-show-note-detail-comp'
   SAVE_EDIT_NOTE_BUTTON = 'button.person-notes-card-save-button-comp'
   CANCEL_NOTE_BUTTON = 'button.person-notes-card-cancel-button-comp'
   CLOSE_BUTTON_AT_NEW_NOTE_DIALOG = 'div[aria-labelledby="person-notes-dialog-title"] button[aria-label="close"]'
   DELETE_EDIT_NOTE_BUTTON = 'button.person-notes-card-delete-button-comp'
   SEARCH_NOTE_BUTTON = 'button[aria-label="Search"] [role="presentation"]'
   SEARCH_NOTE_TEXT_FIELD = 'div.expandSearch input[placeholder="Search"]'
   VIEW_ALL_ANNOUNCEMENT = 'div a[href="/home/announcements/"] span'
   ANNOUNCEMENT_PAGE = '#announcements-page .months-holder'
   PINNED_CHECKBOX = 'input[type="checkbox"]'
   CHECKED_PINNED_CHECKBOX = 'span.Mui-checked'
   SEARCH_ANNOUNCEMENT = 'input[type="text"]'
   NEWS_PIN_BUTTON = 'a[class="news-pin inner"]'
   NEWS_HEADING_TEXT = 'div.news h2'
   NEWS_DATE_TEXT = '.news div[align="right"] div'
   SEARCH_ANNOUNCEMENT_SUBJECT = 'form input[type="text"]'
   READ_MORE_DRAWER = 'div.MuiDrawer-modal .sidebar-drawer'
   CLOSE_DRAWER_BUTTON = 'a.close-heading .fa-times-circle'
   SCROLLER = '#announcements-page'
   FIRST_READ_MORE_LINK = 'li.MuiListItem-root span:nth-of-type(1) span a'
   MENU_BUTTON = 'div.MuiListItem-button[role="button"]'
   COMPLETE_PROJECT_LOGS_LINK = '//li/span/p[text()="Complete Project logs"]'
   SUBMIT_NEW_JOINER_FORM_LINK = '//li/span/p[text()="Submit new joiner form"]'
   SUBMIT_ANNUAL_REVIEW_FORM_LINK = '//li/span/p[text()="Submit annual review form"]'
   REVIEW_LEAVE_FORM_LINK = '//li/span/p[text()="Review Leave"]'
   REVIEW_AND_APPROVE_LOGS_LINK = '//li/span/p[text()="Review & Approve Project Logs"]'
   COMPLETE_PROFILE_FORM_LINK = '//li/span/p[text()="Complete your profile"]'
   ADD_TEXT_CV_FORM_LINK = '//li/span/p[text()="Add Text CV detail"]'
   ADD_TEAM_DETAILS_FORM_LINK = '//li/span/p[text()="Add team detail"]'
   TRAINING_TAB = '//nav/div/*[contains(text(),"Training")]'
   DASHBOARD_TAB = '//div/*[contains(text(),"Dashboard")]'
   COSTING_TAB = '//nav/div/*[contains(text(),"Costing")]'
   COSTING_PAGE = '.costing-dashboard h4'
   TRAINING_REQUEST_TAB = '//div/*[contains(text(),"Training Request")]'
   PUBLISHED_TRAINING_TAB = '//div/*[contains(text(),"Published Training")]'
   RECORD_TRAINING_BUTTON = 'button[title="Add training you completed"]'
   REQUEST_TRAINING_BUTTON = 'button[title="Submit a training request"]'
   PUBLISHED_TRAINING_BUTTON = 'button[title="Publish a training"]'
   MY_TRAINING_TAB = '//button/*[contains(text(),"My Training")]'
   TRAINING_CATALOG = '//button/*[contains(text(),"Training Catalog")]'

   countRecentAnnouncements() {
      cy.get(this.RECENT_ANNOUNCEMENTS).should('have.length', 6)
   }

   clickHomeTab() {
      cy.get(this.MENU_BUTTON).first().click().then(()=> {
         cy.url().should('contain', '/home/')
      })
   }

   clickAddNewNoteButton() {
      cy.get(this.ADD_NEW_NOTE_BUTTON).as('add_note_button').then(($add_note_button) => {
         expect($add_note_button).to.be.visible
         expect($add_note_button).to.have.attr('viewBox', '0 0 24 24')
         expect($add_note_button).to.have.attr('focusable', 'false')
      })
      cy.get('@add_note_button').click()
      cy.get(this.ADD_NEW_NOTE_DIALOG).should('be.visible')
      cy.get(this.ADD_NEW_NOTE_DIALOG_TITLE).invoke('text').then((dialog_title) => {
         expect(dialog_title).to.be.equal('Add a new note')
      })
   }

   clickCancelButton() {
      cy.get(this.CANCEL_NOTE_BUTTON).click().then(() => {
         cy.get(this.ADD_NEW_NOTE_DIALOG).should('not.be.visible')
      })
   }

   clickTrainingTab() {
      cy.xpath(this.TRAINING_TAB).click().then(() => {
         cy.xpath(this.DASHBOARD_TAB).should('be.visible').click().then(() => {
            cy.xpath(this.MY_TRAINING_TAB).should('be.visible')
         })
      })
   }

   clickCostingTab() {
      cy.server()
      cy.route('GET', '**/api/v1/costing/months/?year=2021&**').as('costing_data_load')
      cy.xpath(this.COSTING_TAB).click().then(() => {
         cy.get(this.COSTING_PAGE).invoke('text').then((costing_page) => {
            expect(costing_page).to.be.equal('Costing')
         })
         cy.get('#simple-tab-2021').should('have.attr', 'aria-selected', 'true')
         cy.wait('@costing_data_load').then((xhr) => {
            let status_code = xhr.status
            expect(status_code).to.equal(200)
         })
         cy.get('#simple-tab-2019').should('have.attr', 'aria-selected', 'false').and('have.attr', 'tabindex', '-1')
      })
   }

   addNewNote(title, detail) {
      cy.server()
      cy.route('POST', '**/api/v1/core/person/notes/').as('save_note')
      cy.get(this.NOTE_TITLE).type(title)
      cy.get(this.NOTE_DETAILS).type(detail)
      cy.get(this.SAVE_NOTE_BUTTON).click()
      cy.wait('@save_note').then((xhr) => {
         let status_code = xhr.status
         expect(status_code).to.equal(201)
         expect(xhr.statusMessage).to.be.equal("201 (Created)")
      })
      cy.get(this.ADD_NEW_NOTE_DIALOG_TITLE).should('not.be.visible')
   }
 
   OpenAndEditNote() {
      cy.server()
      cy.route('PATCH', '**/api/v1/core/person/notes/*').as('edit_note')
      cy.get(this.NOTES_MESSAGE_CLICK).as('Notes_title').invoke('text').then((notes_title) => {
         cy.get('@Notes_title').click()
         cy.get(this.ADD_NEW_NOTE_DIALOG_TITLE).invoke('text').then((edit_dialog_title) => {
            expect(edit_dialog_title).to.be.equal('Edit note')
         })
         cy.get(this.NOTE_TITLE).should('have.value', notes_title).and('have.attr', 'disabled')
         cy.get(this.NOTE_DETAILS).should('have.attr', 'disabled')
      }).then(() => {
         cy.get(this.EDIT_BUTTON_ON_EDIT_NOTE_DIALOG).click().then(() => {
            cy.get(this.NOTE_TITLE).should('not.have.attr', 'disabled')
            cy.get(this.NOTE_DETAILS).should('not.have.attr', 'disabled')
         }).then(() => {
            cy.get(this.NOTE_TITLE).clear().type("Edit Automated Note Title!")
            cy.get(this.NOTE_DETAILS).clear().type("Edit Details for this Automated note...")
            cy.get(this.SAVE_EDIT_NOTE_BUTTON).click().then(() => {
               cy.wait('@edit_note').then((xhr) => {
                  expect(xhr.status).to.equal(200)
                  expect(xhr.statusMessage).to.be.equal("200 (OK)")
               })
               cy.get(this.ADD_NEW_NOTE_DIALOG_TITLE).should('not.be.visible')
            })
         })
      })

   }

   editNote() {
      cy.get(this.NOTES_MESSAGE_CLICK).invoke('text').then((notes_title) => {
         cy.get(this.EDIT_NOTES_BUTTON).click().then(() => {
            cy.get(this.ADD_NEW_NOTE_DIALOG_TITLE).invoke('text').then((edit_dialog_title) => {
               expect(edit_dialog_title).to.be.equal('Edit note')
            }).then(() => {
               cy.get(this.NOTE_TITLE).should('have.value', notes_title).and('not.have.attr', 'disabled')
               cy.get(this.NOTE_DETAILS).should('not.have.attr', 'disabled')
            }).then(() => {
               cy.get(this.NOTE_TITLE).clear().type("Direct Edit Automated Note Title!")
               cy.get(this.NOTE_DETAILS).clear().type("Direct Edit Details for this Automated note...")
               cy.get(this.SAVE_EDIT_NOTE_BUTTON).click().then(() => {
                  cy.get(this.ADD_NEW_NOTE_DIALOG_TITLE).should('not.be.visible')
               })
            })
         })
      })
   }

   deletedNotes() {
      let notes_messages
      let note_title
      cy.server()
      cy.route('DELETE', '**/api/v1/core/person/notes/*').as('delete_note')
      cy.get(this.NOTES_LIST).as('notes_list').then((list) => {
         console.log(list.length);
         notes_messages = list.length
      }).then(() => {
         cy.get(this.NOTES_MESSAGE_CLICK).as('Notes_title').invoke('text').then((notes_title) => {
            note_title = notes_title
         }).then(() => {
            cy.get(this.DELETE_NOTES_BUTTON).click().then(() => {
               cy.wait('@delete_note')
               cy.get('@notes_list').then((list_after_delete_note) => {
                  expect(list_after_delete_note.length).to.be.lessThan(notes_messages)
                  cy.get('@Notes_title').invoke('text').then((deleted_note_title) => {
                     expect(deleted_note_title).not.to.be.equal(note_title)
                  })
               })
            })
         })
      })

   }

   openAndDeleteNote() {
      let notes_messages
      let note_title
      cy.server()
      cy.route('DELETE', '**/api/v1/core/person/notes/*').as('delete_note')
      cy.get(this.NOTES_LIST).as('notes_list').then((list) => {
         console.log(list.innerText);
         notes_messages = list.length
      }).then(() => {
         cy.get(this.NOTES_MESSAGE_CLICK).as('Notes_title').invoke('text').then((notes_title) => {
            note_title = notes_title
            cy.get('@Notes_title').click()
            cy.get(this.ADD_NEW_NOTE_DIALOG_TITLE).invoke('text').then((edit_dialog_title) => {
               expect(edit_dialog_title).to.be.equal('Edit note')
            })
            cy.get(this.NOTE_TITLE).should('have.value', notes_title).and('have.attr', 'disabled')
            cy.get(this.NOTE_DETAILS).should('have.attr', 'disabled')
         }).then(() => {
            cy.get(this.DELETE_EDIT_NOTE_BUTTON).click().then(() => {
               cy.wait('@delete_note')
               cy.get('@notes_list').then((list_after_delete_note) => {
                  expect(list_after_delete_note.length).to.be.lessThan(notes_messages)
                  cy.get('@Notes_title').invoke('text').then((deleted_note_title) => {
                     expect(deleted_note_title).not.to.be.equal(note_title)
                  })
               })
            })
         })
      })
   }

   searchNotes(note_title) {
      cy.server()
      cy.route('GET', '**/api/v1/core/person/notes/?sorting_order=**').as('search_notes')
      cy.get(this.SEARCH_NOTE_BUTTON).as('search_button').click()
      cy.get(this.SEARCH_NOTE_TEXT_FIELD).should('be.visible').type(note_title)
      cy.get('@search_button').click().then(() => {
         cy.wait('@search_notes').then((xhr) => {
            expect(xhr.status).to.equal(200)
         })
         cy.get(this.NOTES_MESSAGE_CLICK).then(($note_title) => {
            expect($note_title.text()).to.be.equal(note_title)
         })
      })
   }

   clickViewAllAnnouncements() {
      cy.get(this.VIEW_ALL_ANNOUNCEMENT).click().then(() => {
         cy.url().should('contain', 'announcements/')
         cy.get(this.ANNOUNCEMENT_PAGE).should('be.visible')
      })
   }

   clickFirstNewsPinnedButton() {
      let news_heading_text
      let news_date_text
      cy.get(this.SCROLLER).scrollTo('bottom', { duration: 7000 })
      cy.get(this.NEWS_PIN_BUTTON).first().as('news_pinned').click().then(() => {
         cy.get('@news_pinned').should('have.class', 'pinned')
         cy.get(this.NEWS_HEADING_TEXT).first().invoke('text').then((news_heading) => {
            news_heading_text = news_heading
            console.log(news_heading_text);
            this.NEWS_HEADING = news_heading_text
            cy.get(this.NEWS_DATE_TEXT).invoke('text')
         }).then((news_date) => {
            news_date_text = news_date
            this.NEWS_DATE = news_date_text
         })
      })
   }

   clickPinnedCheckbox() {
      cy.get(this.PINNED_CHECKBOX).check().then(() => {
         cy.get(this.CHECKED_PINNED_CHECKBOX).should('be.visible')
         cy.get(this.NEWS_PIN_BUTTON).should('not.be.visible')
      })
   }

   searchAnnouncement(news_heading) {
      cy.server()
      cy.route('GET', '**api/v1/core/announcements/list/?pa*').as('search_notes')
      cy.get(this.SEARCH_ANNOUNCEMENT_SUBJECT).type(news_heading).type('{enter}')
   }

   verifySearchedAnnouncemnet(news_heading) {
      cy.wait('@search_notes').then((xhr) => {
         expect(xhr.status).to.equal(200)
         expect(xhr.response.body.announcements[0].heading).to.be.equal(news_heading)
      })
      cy.get(this.NEWS_HEADING_TEXT)
   }

   clickReadMoreAnnouncement() {
      cy.get(this.FIRST_READ_MORE_LINK).click().then(()=> {
         cy.get(this.READ_MORE_DRAWER).should('be.visible')
      })
   }

   closeReadMoreAnnouncementDrawer() {
      cy.get(this.CLOSE_DRAWER_BUTTON).click().then(()=> {
         cy.get(this.READ_MORE_DRAWER).should('not.be.visible')
      })
   }

}

export default HomePage
