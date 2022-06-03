import LoginPage from '../pages/login_page'

describe('Login tests', () => {
    it('Verify that user should be able to login with their official account to Workstream portal successfully', () => {
        cy.visit('/')
        const login = new LoginPage('sajjad.akbar@arbisoft.com', 'Erp786786')
        login.fillLoginForm()
        login.submitLoginForm()
    })

    it('Verify that user should not be able to login with invalid credentials to Workstream portal.', () => {
        const login = new LoginPage('sajjad.akbar@arbisoft.com', 'invalidpassword')
        cy.visit('/')
        login.loginWithInvalidCreds()
        login.errorValidationWithInvalidCredentials()
    })

    it('Verify that user should not be able to login with unofficial account to Workstream portal.', () => {
        const login = new LoginPage('invalid@arbisoft.com', 'invalidpassword')
        cy.visit('/')
        login.loginWithInvalidCreds()
        login.errorValidationWithNonUser()
    })

    it('Verify that required email and password fields errors should be shown by clicking Login button without credentials.', () => {
        const login = new LoginPage('', '')
        cy.visit('/')
        login.errorValidationWithoutCredentials()
    })

    it('Verify that password reset page should be open by clicking reset password link.', () => {
        const reset_password = new LoginPage('', '')
        cy.visit('/')
        reset_password.clickResetPasswordLink()
        reset_password.verifyResetPasswordContent()
        reset_password.fillEmailOnResetPasswordPage('invalidemail@invalid')
        reset_password.clickSendButton()
        reset_password.errorValidationWithWrongEmail()
        reset_password.clearEmailTextField()
        reset_password.fillEmailOnResetPasswordPage('erpqauser@arbisoft.com')
        reset_password.clickSendButton()
        cy.url().should('contain', 'password_reset/done/')
    }) 

})
