import LoginPage from '../pages/login_page'
import HomePage from '../pages/home_page'
import TrainingPage from '../pages/training_page'

let home_page
let training_page
let news

describe('Training tests', () => {
    before(() => {
        // runs once before all tests in the block
        cy.visit('/')
        const login = new LoginPage('sajjad.akbar@arbisoft.com', 'Erp786786')
        login.fillLoginForm()
        login.submitLoginForm()
    })

    beforeEach(() => {
        cy.restoreLocalStorage();
    });

    afterEach(() => {
        cy.saveLocalStorage();
    });

    it('Verify that user should redirect to Training Dashboard by clicking Training dashboard tab from home page', () => {
        home_page = new HomePage()
        training_page = new TrainingPage()
        home_page.clickCostingTab()
        // training_page.clickTrainingTab()
        // training_page.clickRecordTrainingButton()
        // training_page.fillRecordTrainingForm()
    })

})
