class InvaluableMainPage {
    credentials = {
        "username":  "sajjad.akbar@arbisoft.com" ,
        "password":  "sajjad123!" 
    }
    
    verifyLoginSuccess() {
        cy.loginViaApi(this.credentials)
    }

    verifyAuthentication() {
        cy.authenticateUser(`${Cypress.config('catalogRef')}`)
    }
    
    clickSettingsButton() {
        cy.get('#dropdown-basic span').click().then(() => {
            cy.get('.dropdown-menu').should('have.class', 'show')
        })
    }

    changeCurrency() {
        cy.get('select').first().select('GBP').should('have.value', 'GBP').then(() => {
            cy.contains('Est. bid:').should('be.visible')
        })
        cy.get('select').first().select('USD').should('have.value', 'USD').then(() => {
            cy.contains('Est. bid:').should('not.exist')
        })
    }

    checkBuyersPremium() {
        cy.get('#formBasicCheckbox').check()
    }
}
export default InvaluableMainPage
