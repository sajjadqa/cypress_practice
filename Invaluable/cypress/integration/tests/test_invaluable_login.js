import InvaluableMainPage from '../pages/invaluable_main_page'
let login_page
let home_page

  describe('Invaluable Login tests <login>', () => {
    // beforeEach(() => {
    //   // runs once before all tests in the block
    //   cy.visit(`${Cypress.config('baseUrl')}`)
    //  })

    it('Verify that user should be login successfully.', () => {
      home_page = new InvaluableMainPage()
      home_page.verifyLoginSuccess()
      home_page.verifyAuthentication()
      home_page.clickSettingsButton()
      home_page.changeCurrency()
  })


 })
 