class DemoQaLogin {
  credentials = {
    "username":  "sajjad123" ,
    "password":  "Acrotnum123!" ,
    "invalid_username": "InvalidUserName",
  }

  fillLoginForm() {
    cy.get('form#userForm').within(() => {
      cy.get('div #userName').type(this.credentials.username)
      cy.get('div #password').type(this.credentials.password)
    })
  }

  clickLoginButton() {
    cy.get('.text-right').within(() => {
      cy.get('#login[type="button"]').click()
    })
  }

  verifyLoginSuccess() {
    cy.url().should('eq', `${Cypress.config('baseUrl')}/profile`)
    cy.get('#userName-value').invoke('text').should('be.equal', this.credentials.username)
  }

  errorValidationWithoutCredentials() {
    cy.get('form#userForm').within(() => {
      cy.get('.text-right').within(() => {
        cy.get('#login[type="button"]').click()
         })
        var creds_fields = ['userName', 'password']
        creds_fields.forEach(($ids) => {
          cy.get(`#${$ids}`).should('have.class', 'is-invalid')
        })
    })
  }

  errorValidationWithInvalidCredentials() {
    cy.get('form#userForm').within(() => {
      cy.get('div #userName').type(this.credentials.invalid_username)
      cy.get('div #password').type(this.credentials.password)
      cy.get('.text-right').within(() => {
        cy.get('#login[type="button"]').click()
      })
    })
    cy.get('.col-md-12').within(() => {
      cy.get('p#name').invoke('text').should('be.equal', 'Invalid username or password!')
    })
  }

  logoutSuccessfully() {
    cy.loginViaApi(this.credentials)
    cy.visit(`${Cypress.config('baseUrl')}/profile`)
    cy.clearCookies()
    cy.get('#books-wrapper button#submit').click()
    cy.get('.login-wrapper').should('be.visible')
    cy.url().should('eq', `${Cypress.config('baseUrl')}/login`)
  }

}

export default DemoQaLogin
