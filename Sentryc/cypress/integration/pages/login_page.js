class SentrycLogin {
    credentials = {
      "valid_email":  "fouzia@abc.com" ,
      "valid_password":  "Password!" ,
      "invalid_username": "InvaliduserName",
      "invalid_password": "password",
      "password_less_than_8": "pass"
    }
  
    fillLoginFormWithValidCredentials() {
      cy.get('.login-page form').within(() => {
        cy.get('[name="email"]').type(this.credentials.valid_email)
        cy.get('[name="password"]').type(this.credentials.valid_password).then(() => {
            cy.contains('The email format is invalid.').should('not.exist')
            cy.contains('The email field is required.').should('not.exist')
            cy.contains('The password field is required.').should('not.exist')
            cy.contains('The password must be at least 8 characters.').should('not.exist')
            cy.contains('Password must contains 1 capital and 1 special symbol').should('not.exist')
        })
      })
    }
  
    clickLoginButton() {
      cy.get('form').within(() => {
        cy.get('[type="submit"]').click()
      })
    }

    goToForgotPasswordPage() {
      cy.contains('Forgot password?').click().then(() => {
        cy.get('.page-header__content b').invoke('text').should('be.equal', 'Forgot password')
        cy.contains('Enter your email to restore.').should('be.visible')
    })
    }

    restorePassword() {
      cy.intercept('POST', 'https://api.sentryc.com/en/api/forgot-password').as('forgot_password')  
      cy.get('input[name="email"]').type(this.credentials.valid_email)
      cy.get('[type="submit"]').click()
      cy.wait('@forgot_password').then((xhr) => {
        let status_code = xhr.response.body.code
        cy.log(status_code)
        expect(status_code).to.equal(422)
      })
    }

    clickBackToLoginLink() {
      cy.contains('Back to login.').click().then(() => {
        cy.contains('Welcome to the Sentryc.').should('be.visible')
      })
    }

    goBackToMainPage() {
      cy.go('back').then(() => {
        cy.url().should('include', 'auth/login')
      })
    }

    goToTermsPage() {
      cy.contains('Terms').click().then(() => {
        cy.url().should('include', 'terms')
        cy.contains('Terms').should('be.visible')
      })
    }
    
    goToConditionsPage() {
      cy.contains('Conditions').click().then(() => {
        cy.url().should('include', 'conditions')
        cy.contains('Conditions').should('be.visible')
      })
    }
  
    errorValidationWithInvalidCredentials() {
      cy.get('.login-page form').within(() => {
        cy.get('[name="email"]').type(this.credentials.invalid_username).then(() => {
          cy.get('[name="password"]').click()
          cy.contains('The email format is invalid.').should('be.visible')
        })
        cy.get('[name="password"]').type(this.credentials.password_less_than_8).then(() => {
            cy.get('[name="email"]').click()
            cy.contains('The password must be at least 8 characters.').should('be.visible')
        })
        cy.get('[name="password"]').type(this.credentials.invalid_password).then(() => {
          cy.get('[name="email"]').click()
          cy.contains('Password must contains 1 capital and 1 special symbol').should('be.visible')
        })
      })
    }
  
  }
  
  export default SentrycLogin