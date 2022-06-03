import PhpTravel from '../pages/phptravel'

describe('PhpTravel tests', () => {
    before(() => {
        // runs once before all tests in the block
        cy.visit('/')
        })

    it('Verify that user should redirect to Visa submission form after submition of Visa data.', () => {
        const phptravel = new PhpTravel()
        phptravel.verifyHotelTabLoaded()
        phptravel.clickVisaTab()
        phptravel.selectFromCountry()
        phptravel.selectToCountry()
        phptravel.clickSubmitButton()
        phptravel.fillVisaForm()
        phptravel.clickSubmitFormButton()
    })

})