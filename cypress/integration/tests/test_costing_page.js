import LoginPage from '../pages/login_page'
import HomePage from '../pages/home_page'
import CostingPage from '../pages/costing_page'

let home_page
let costing_page

describe('Costing tests', () => {
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

    it('Verify that user should redirect to Costing page by clicking Costing tab from home page and default selected tab should be 2021.', () => {
        home_page = new HomePage()
        costing_page = new CostingPage()
        home_page.clickCostingTab()
        costing_page.click_2019_tab()
    })

    it('Verify that total cost on detail page should be equal to sum of people cost and overhead cost.', () => {
        costing_page = new CostingPage()
        costing_page.clickViewDetailsLink()
        costing_page.veriftyTotalCost()        
    })

    it('Verify that converted amounts should be changed by changing the currency rate.', () => {
        costing_page = new CostingPage()
        costing_page.verifyCurrencyRate()
    })

    it('Verify that new overhead cost should be added successfully. ', () => {
        costing_page = new CostingPage()
        costing_page.verifyNewAddOverheadCost()
    })

    it('Verify that alert confirmation should be shown by clicking close button on add overhead cost pop up. ', () => {
        costing_page = new CostingPage()
        costing_page.verifyPopUpAlertOnAddOverheadCost()
    })


    it('Verify that total overhead cost on detail page should be equal to sum of all overhead costs amount.', () => {
        costing_page = new CostingPage()
        costing_page.verifySumOfTotalOverheadCosts()
    })

    it('Verify that overhead cost should be searched successfully by using overhead search field. ', () => {
        costing_page = new CostingPage()
        costing_page.searchValue('full-width-tab-overheads', 'WFH Allowance!', 'description', 'search-btn')
    })

    it('Verify that overhead cost data on listing should be equal to details page overhead cost data. ', () => {
        costing_page = new CostingPage()
        costing_page.openOverheadCostDetails()
    })

    it('Verify that sum of all projects overhead cost amount on details page should be equal to amount of that overhead cost. ', () => {
        costing_page = new CostingPage()
        costing_page.verifyProjectOverheadCostSum()
    })

    it('Verify that specific project on overhead cost details page should be searched successfully by using search field. ', () => {
        costing_page = new CostingPage()
        costing_page.searchValue('simple-cost-detail-label', 'edX', 'teamName', 'search-btn')
    })

    it('Verify that overhead cost is edited successfully.', () => {
        costing_page = new CostingPage()
        costing_page.clickEditButtonOnOverheadCostDetails()
        costing_page.openOverheadCostDetails()
        costing_page.closeOverheadDilaog('simple-cost-detail-label', 'close')
    })

    it('Verify that overhead cost is deleted successfully.', () => {
        costing_page = new CostingPage()
        costing_page.clearSerachField('full-width-tab-overheads', 'search-btn')
        costing_page.deleteOverheadCost()
    })

    it('Verify that people section is opened by clicking People tab.', () => {
        costing_page = new CostingPage()
        costing_page.clickOnPeopleTab()
    })

    it('Verify that total non billable cost on detail page should be equal to sum of all non billable costs amounts from people table.', () => {
        costing_page = new CostingPage()
        costing_page.verifyTotalNonBillableCostSum()
    })

    it('Verify that total hours on detail page should be equal to sum of all total hours from people table.', () => {
        costing_page = new CostingPage()
        costing_page.verifyTotalHoursSum()
    })

    it('Verify that total people value on detail page should be equal to sum of all total cost from people table.', () => {
        costing_page = new CostingPage()
        costing_page.verifyTotalSumOfPeopleCostTable()
    })

    it('Verify that people should be searched successfully by using people search field. ', () => {
        costing_page = new CostingPage()
        costing_page.searchValue('full-width-tab-people', 'Yasser Bashir', 'personName', 'search-btn')
    })

    it('Verify that projects section is opened by clicking on Projects tab.', () => {
        costing_page = new CostingPage()
        costing_page.clickProjectsTab()
    })

    it(`Verify that project people costs is equal to sum of all people's project cost.`, () => {
        costing_page = new CostingPage()
        costing_page.searchValue('full-width-tab-projects', 'edX', 'teamName', 'search-btn')
        costing_page.verifyProjectPeopleCost()
    })

    it(`Verify that project work weight is equal to sum of all people's work weight.`, () => {
        costing_page = new CostingPage()
        costing_page.verifyProjectPeopleWorkWeight()
    })

    it(`Verify that project pro rate cost is equal to (project work weight/total work weight * total non-billable cost)`, () => {
        costing_page = new CostingPage()
        costing_page.verifyProjectProRateCost()
    })

    it(`Verify that project overhead cost is equal to sum of all project overhead costs`, () => {
        costing_page = new CostingPage()
        costing_page.verifyProjectOverheadCosts()
    })

})
