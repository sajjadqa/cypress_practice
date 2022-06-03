class LoginPage {
   invalid_password = 'testt'
   new_password = "Passenger2019!"
   EMAIL = "#erp-email-login input[name='email']"
   LOGIN_NAME_ON_RESET_PASSWORD = 'input[placeholder="Login Name"]'
   PASSWORD = "#erp-email-login input[name='password']"
   LOGIN_ERROR = 'div.Toastify__toast--error [role="alert"]'
   NON_USER_ERROR = 'div[role="alert"].Toastify__toast-body'
   LOGIN_BUTTON = '#erp-email-login button[type="submit"]'
   LOGIN_WITH_GOOGLE_BUTTON = '#erp-google-login button'
   FORGET_PASSWORD = '#erp-email-login div a[href="/login/accounts/password_reset/"]'
   PASSWORD_HELP = '//a[.//text()[contains(., "Password Help")]]'
   ADD_NEW_NOTE_BUTTON = 'button[aria-label="Add Note"]'
   PASSWORD_MISSING_ERROR = 'p.Mui-error#component-error-text'
   EMAIL_MISSING_ERROR = 'p.Mui-error:NOT(#component-error-text)'
   EMAIL_TEXTFIELD_ON_RESET_PASSWORD = 'input#id_email'
   SEND_BUTTON_ON_RESET_PASSWORD = 'input[value="Send"]'
   CANCEL_BUTTON_ON_RESET_PASSWORD = 'input[value="Cancel"]'
   PASSWORD_RESET_CONTENT = 'form[method="POST"] p:nth-of-type(3)'
   INVALID_EMAIL_ADDRESS = 'form[method="POST"] p[style="color: red"]'

   constructor(username, password) {
      this.username = username
      this.password = password
   }

   click_login_with_google_button() {
      cy.get(this.LOGIN_WITH_GOOGLE_BUTTON).click()
   }

   fillLoginForm() {
      cy.get(this.EMAIL).type(this.username)
      cy.get(this.PASSWORD).type(this.password)
   }

   submitLoginForm() {
      cy.get(this.LOGIN_BUTTON).click().then(() => {
         cy.get(this.ADD_NEW_NOTE_BUTTON).should('be.visible')
      })
   }

   loginWithInvalidCreds() {
      cy.get(this.EMAIL).type(this.username).should('have.value', this.username)
      cy.get(this.PASSWORD).type(this.invalid_password).should('have.value', this.invalid_password)
      cy.get(this.LOGIN_BUTTON).click()
   }

   errorValidationWithInvalidCredentials() {
      cy.get(this.LOGIN_ERROR).should(($loginerror) => {
         expect($loginerror.text()).to.include('Error - Invalid Credentials' || 'Error - This user does not exist')
      })
   }

   errorValidationWithNonUser() {
      cy.get(this.NON_USER_ERROR).should(($user_error) => {
         expect($user_error.text()).to.include('Error - This user does not exist')
      })
   }

   errorValidationWithoutCredentials() {
      cy.get(this.LOGIN_BUTTON).click()
      cy.get(this.EMAIL_MISSING_ERROR).should('be.visible').invoke('text').then((error) => {
         expect(error).to.be.equal('Email not provided')
      })
      cy.get(this.PASSWORD_MISSING_ERROR).should('be.visible').invoke('text').then((error) => {
         expect(error).to.be.equal('Password not provided')
      })
   }

   clearForm() {
      cy.get(this.EMAIL).clear()
      cy.get(this.PASSWORD).clear()
   }

   clickResetPasswordLink() {
      cy.get(this.FORGET_PASSWORD).click().then(()=> {
         cy.url().should('contain', 'accounts/password_reset/')
      })
   }

   clearEmailTextField() {
      cy.get(this.EMAIL_TEXTFIELD_ON_RESET_PASSWORD).clear()
   }

   clickCancelButton() {
      cy.get(this.CANCEL_BUTTON_ON_RESET_PASSWORD).click()
   }

   clickSendButton() {
      cy.get(this.SEND_BUTTON_ON_RESET_PASSWORD).click()
   }

   verifyResetPasswordContent() {
      cy.get(this.PASSWORD_RESET_CONTENT).should(($resetpasscontent) => {
         const resetpasstext = $resetpasscontent.text()
         expect(resetpasstext).to.be.equal('The email address you used to register with Workstream.')
      })
   }

   fillEmailOnResetPasswordPage(email) {
      cy.get(this.EMAIL_TEXTFIELD_ON_RESET_PASSWORD).type(email)
   }

   errorValidationWithWrongEmail() {
      cy.get(this.INVALID_EMAIL_ADDRESS).should('be.visible').invoke('text').then((error) => {
         expect(error).to.be.equal('Enter a valid email address.')
      })
   }

}

export default LoginPage
