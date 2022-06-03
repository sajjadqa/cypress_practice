class PhpTravel {
    HOTEL_TAB = 'button[data-bs-target="#hotels"]'
    TOUR_TAB = 'button[data-bs-target="#visa"]'
    FROM_COUNTRY = 'span[aria-labelledby="select2-from_country-container"] span[title="Select Country"]'
    TO_COUNTRY = 'span[aria-labelledby="select2-to_country-container"] span[title="Select Country"]'
    INPUT_FROM_COUNTRY = 'INPUT[role="searchbox"]'
    OPTION_COUNTRY = 'li[role="option"]'
    SELECT_DATE = 'form[id="visa-submit"] div.form-group input[name="checkin"]'
    SUBMIT_BUTTN = 'form#visa-submit [id="submit"]'
    FIRST_NAME = 'input[name="first_name"]'
    LAST_NAME = 'input[name="last_name"]'
    EMAIL = 'input[name="email"]'
    PHONE = 'input[name="phone"]'
    NOTES = 'textarea[name="notes"]'
    SUBMIT_FORM_BUTTON = 'div[class="contact-form-action"] button[type="submit"]'
    SUCCESS_MESSAGE = 'div .contact-form-action div[class="card panel-primary"] h2'
    
    constructor(username, password) {
       this.username = username
       this.password = password
    }
 
    verifyHotelTabLoaded() {
       cy.get(this.HOTEL_TAB).should('be.visible').click({force: true})
    }
 
    clickVisaTab() {
       cy.get(this.TOUR_TAB).click({force: true})
    }

    selectFromCountry() {
        cy.get(this.FROM_COUNTRY).click({force: true})
        cy.get(this.INPUT_FROM_COUNTRY).type('PAKISTAN').then(() => {
            cy.get(this.OPTION_COUNTRY).click({force: true})
        })
    }

    selectToCountry() {
        cy.get(this.TO_COUNTRY).click({force: true})
        cy.get(this.INPUT_FROM_COUNTRY).type('BANGLADESH').then(() => {
            cy.get(this.OPTION_COUNTRY).click({force: true})
        })
    }

    clickSubmitButton() {
        cy.get(this.SUBMIT_BUTTN).click({force: true}).then(() => {
            cy.get('div[class="form-content "]').should('be.visible')
        })
    }

    fillVisaForm() {
        cy.get(this.FIRST_NAME).click({force: true}).type("Fouzia")
        cy.get(this.LAST_NAME).click({force: true}).type("Badmash")
        cy.get(this.EMAIL).click({force: true}).type('fouzia@abc.com')
        cy.get(this.PHONE).click({force: true}).type("15")
        cy.get(this.NOTES).click({force: true}).type("Automation practice task for knowledge sharing.")
    }

    clickSubmitFormButton() {
        cy.get(this.SUBMIT_FORM_BUTTON).click({force: true}).then(() => {
            cy.get(this.SUCCESS_MESSAGE).should('have.text', "Your visa form has been submitted")
        })
    }
 
 }
 
 export default PhpTravel
 