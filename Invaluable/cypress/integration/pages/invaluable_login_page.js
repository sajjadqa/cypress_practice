class IndigoLogin {
  credentials = {
    "username":  "IntQA03" ,
    "password":  "IntQA*1234" ,
    "invalid_username": "InvalidUserName",
  }

  fillLoginForm() {
    cy.get('form').within(() => {
      cy.get('#txtUsername[name]').type(this.credentials.username)
      cy.get('#txtPassword').type(this.credentials.password)
    })
  }

  clickLoginButton() {
    cy.get('form').within(() => {
      cy.get('.loginButton').click()
    })
  }

  verifyLoginSuccess() {
    cy.url().should('include', `/#/HR-People-Home`)
    cy.get('div .currentModuleSectionHeader').first().invoke('text').should('be.equal', 'Main')
  }

  errorValidationWithoutCredentials() {
    cy.get('form').within(() => {
        cy.get('.loginButton').click()
         })
         cy.get('.loginMessage').invoke('text').should('be.equal', 'Please input your password')
  }

  errorValidationWithInvalidCredentials() {
    cy.get('form').within(() => {
      cy.get('#txtUsername[name]').type(this.credentials.invalid_username)
      cy.get('#txtPassword').type(this.credentials.password)
      cy.get('.loginButton').click()
    })
    cy.get('form').within(() => {
      cy.get('.loginMessage').invoke('text').should('be.equal', 'Invalid user name or password')
    })
  }

  logoutSuccessfully() {
    cy.IdentityServerAPILogin(this.credentials)
    cy.visit(`${Cypress.config('baseUrl')}/#/HR-People-Home`)
    cy.get('div .currentModuleSectionHeader').first().invoke('text').should('be.equal', 'Main')
    cy.get('div#activeUserMenu img').click().then(() => {
      cy.get('.activeUser span[data-bind]').click()
    })
    cy.get('.loginPanel form').should('be.visible')
    cy.url().should('include', `${Cypress.config('baseUrl')}`)
  }

}

export default IndigoLogin