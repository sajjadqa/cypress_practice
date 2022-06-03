class TrainingPage {
   constructor() {
      this.NEWS_HEADING = null
      this.NEWS_DATE = null
  }
   
   TRAINING_TAB = '//nav/div/*[contains(text(),"Training")]'
   DASHBOARD_TAB = '//div/*[contains(text(),"Dashboard")]'
   TRAINING_REQUEST_TAB = '//div/*[contains(text(),"Training Request")]'
   PUBLISHED_TRAINING_TAB = '//div/*[contains(text(),"Published Training")]'
   RECORD_TRAINING_BUTTON = 'button[title="Add training you completed"]'
   REQUEST_TRAINING_BUTTON = 'button[title="Submit a training request"]'
   PUBLISHED_TRAINING_BUTTON = 'button[title="Publish a training"]'
   MY_TRAINING_TAB = '//button/*[contains(text(),"My Training")]'
   TRAINING_CATALOG = '//button/*[contains(text(),"Training Catalog")]'
   TRAINING_DRAWER = '[role="presentation"] .MuiDrawer-paper'
   RECORD_TRAINING_HEADING = '[role="presentation"] .MuiDrawer-paper h5.MuiTypography-h5'
   TRAINING_TITLE = '.Select-input input[id="[object Object]"]'
   TRAINING_TITLE_PLACEHOLDER = 'label[for="training.title"]+div .Select-placeholder'
   TRAINING_DETAILS = 'div[id="training.details"] .ql-editor p'
   TRAINING_FEE = 'label[for="training.fee"]+div input[id="training.fee"]'
   TRAINER_NAME = 'label[for="singleline"]+div input[name="training.trainer"]'
   TRAINING_TYPE = 'label[data-shrink="true"]+div svg[role="presentation"]'
   TRAINING_TYPES_LIST = 'ul[role="listbox"] li'

   clickHomeTab() {
      cy.get(this.MENU_BUTTON).first().click().then(()=> {
         cy.url().should('contain', '/home/')
      })
   }

   clickCancelButton() {
      cy.get(this.CANCEL_NOTE_BUTTON).click().then(() => {
         cy.get(this.ADD_NEW_NOTE_DIALOG).should('not.be.visible')
      })
   }

   clickTrainingTab() {
      cy.server()
      cy.route('GET', '**/api/v1/core/validate/login/?_=**').as('valid_login')
      cy.route('GET', '**api/v1/training/person_training/?offset=0&limit=20&ordering=-training__start&_=**').as('my_trainings')
      cy.xpath(this.TRAINING_TAB).click().then(() => {
         cy.xpath(this.DASHBOARD_TAB).should('be.visible').click().then(() => {
            cy.wait('@valid_login').then((xhr) => {
               let status_code = xhr.status
               expect(status_code).to.equal(200)
               expect(xhr.statusMessage).to.be.equal("200 (OK)")
               expect(xhr.response.body.valid).to.be.equal(true)
            })
            cy.xpath(this.MY_TRAINING_TAB).should('be.visible')
         })
      })
   }

   clickRecordTrainingButton() {
      cy.get(this.RECORD_TRAINING_BUTTON).click().then(() => {
         cy.get(this.TRAINING_DRAWER).should('be.visible')
         cy.get(this.RECORD_TRAINING_HEADING).invoke('text').then((drawer_title) => {
            expect(drawer_title).to.be.equal('Record a training you completed')
         })
      })
   }

   fillRecordTrainingForm() {
      // cy.get(this.TRAINING_TITLE).click().type("Automated Training!")
      cy.get(this.TRAINING_TYPE).click().then(() => {
         cy.get(this.TRAINING_TYPES_LIST).select('Online')
      })
   }

}

export default TrainingPage
