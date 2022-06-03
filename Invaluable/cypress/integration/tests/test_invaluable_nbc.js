import IndigoLogin from '../pages/indigo_login_page'
import IndigoMainPage from '../pages/indigo_home_page'
let login_page
let home_page
let credentials = {
  "username":  "IntQA03" ,
  "password":  "IntQA*1234" ,
  "invalid_username": "InvalidUserName",
}


  describe('Indigo Login tests <login>', () => {

    beforeEach(() => {
      cy.IdentityServerAPILogin(credentials)
    })

    it('Verify that user should be login successfully. And go to Tax Profiles page.', () => {
      home_page = new IndigoMainPage()
      login_page = new IndigoLogin()
      cy.visit(`${Cypress.config('baseUrl')}/#/HR-People-Home`)
      login_page.verifyLoginSuccess()
      home_page.goToTaxProfilePage()
  })

    it('Verify that user should be able to add new profile.', () => {
      cy.visit(`${Cypress.config('baseUrl')}/#/List/00103/QA01/HR/Payroll/TaxProfiles`)
      home_page.addNewTaxProfile()
      home_page.saveNewProfile()
  })

    it('Verify that user is able to search and delete a profile.', () => {
      cy.visit(`${Cypress.config('baseUrl')}/#/List/00103/QA01/HR/Payroll/TaxProfiles`)
      home_page.searchByTaxProfileCode(home_page.PROFILE_CODE)
      home_page.deleteTaxProfile()
    })

    it('Verify that user is able to go to Tax Profiles rate page.', () => {
      cy.visit(`${Cypress.config('baseUrl')}/#/List/00103/QA01/HR/Payroll/TaxProfiles`)
      home_page.goToRatesTab()
  })

  it('Verify that user is able to add new Tax Profiles rate.', () => {
      cy.visit("https://indigo-testing.shireburn.com/#/List/00103/QA01/HR/Payroll/TaxProfiles/" +  home_page.PROFILE_CODE + "/Rates")
      home_page.addNewTaxProfileRate()
      home_page.saveNewProfileRate()
  })


 })
