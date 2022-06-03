import SentrycLogin from '../pages/login_page'
let login_page

  describe('Sentryc Login tests...', () => {
    beforeEach(() => {
      // runs once before all tests in the block
      cy.visit(`${Cypress.config('baseUrl')}`)
     })

    it('Verify that user should be able to see no errors with valid credentials.', () => {
      login_page = new SentrycLogin()
      login_page.fillLoginFormWithValidCredentials()
    })

    it('Verify that user should be able to go to forgot password and send reset password request.', () => {
      login_page = new SentrycLogin()
      login_page.goToForgotPasswordPage()
      login_page.restorePassword()
    })

    it('Verify that user should be able to redirect to login page from forgot password by clicking back to login link.', () => {
      login_page = new SentrycLogin()
      login_page.goToForgotPasswordPage()
      login_page.clickBackToLoginLink()
    })

    it('Verify that user should be able to redirect to Terms and Conditions page successfully.', () => {
      login_page = new SentrycLogin()
      login_page.goToTermsPage()
      login_page.goBackToMainPage()
      login_page.goToConditionsPage()
      login_page.goBackToMainPage()
    })

    it('Verify that the errors validations with invalid email and password.', () => {
      login_page = new SentrycLogin()
      login_page.errorValidationWithInvalidCredentials()
    })

 })
 