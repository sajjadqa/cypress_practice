var faker = require('faker')
class CostingPage {

   DASHBOARD_TAB = '//div/*[contains(text(),"Dashboard")]'
   COSTING_TAB_2019 = '#simple-tab-2019'
   COSTING_TAB_2020 = '#simple-tab-2020'
   COSTING_MONTHS_COUNT = 'div[aria-label*="month-detail"]'
   VIEW_DETAILS_LINK = 'div[aria-label*="month-detail"] a'
   MONTH_NAME = 'div.MuiGrid-item:nth-of-type(1) > div[aria-label*="month-detail"]>div:nth-of-type(1)'
   MONTH_NAME_ON_DETAILS_PAGE = 'div.MuiGrid-grid-xs-12>h5'
   TOTAL_COST_ON_LISTING_PAGE = 'div.MuiGrid-item:nth-of-type(1) > div[aria-label*="month-detail"] h3:nth-of-type(1)'
   TOTAL_COST_ON_DETAILS_PAGE = 'div[aria-label="total-cost"] h3:nth-of-type(1)'
   TOTAL_PEOPLE_COST = 'div[aria-label="total-people-cost"] h3:nth-of-type(1)'
   TOTAL_PEOPLE_COST_CONVERTED = 'div[aria-label="total-people-cost"] h3:nth-of-type(2)'
   OVERHEAD_COST = 'div[aria-label="total-overheads-cost"] h3:nth-of-type(1)'
   ADJUSTMENT_COST = 'div[aria-label="total-adjustments-cost"] h3:nth-of-type(1)'
   OVERHEAD_COST_AMOUNT = 'td[aria-label="amount"]'
   ADD_OVERHEAD_BUTTON = 'button[title="Add Overheads"] svg'
   RELOAD_OVERHEAD_BUTTON = 'button[title="Reload Overheads"] svg'
   ADD_OVERHEAD_ROW_BUTTON = 'button[aria-label="add-row-btn"]'
   ADD_OVERHEAD_DESCRIPTION = 'input[id="costs_0_description"]'
   OVERHEAD_AMOUNT = 'input[id="costs_0_amount"]'
   DELETE_OVERHEAD_ROW = 'button[aria-label="remove-row-btn"] svg'
   SUBMIT_BUTTON = 'button[aria-label="data-submit-btn"]'
   SUBMIT_BUTTON_DISABLED = 'span[title="No data to submit"] button[aria-label="data-submit-btn"]'
   OVERHEAD_COST_DIALOG = 'div[aria-describedby="upload-cost-detail-description"]'
   CLOSE_OVERHEAD_DIALOG_BUTTON = 'div[id="upload-cost-detail-label"] button[aria-label="close"]'
   CLOSE_PROJECT_COST_DIALOG_BUTTON = '[aria-labelledby="project-cost-detail-label"] button[aria-label="close"]'
   ALERT_CONFIRMATION_POPUP = 'div[aria-labelledby="alert-dialog-title"]'
   SCROLLER_ = 'div[id="people-cost-table"]'
   PEOPLE_TAB = 'button[aria-controls="simple-tabpanel-people"]'
   PROJECTS_TAB = 'button[aria-controls="simple-tabpanel-projects"]'
   PEOPLE_COST_TABPANEL = 'div[aria-labelledby="full-width-tab-people"]'
   PROJECTS_COST_TABPANEL = 'div[aria-labelledby="full-width-tab-projects"]'
   NON_BILLABLE_COST = 'td[aria-label="nonBillableCost"]'
   TOTAL_NON_BILLABLE_COST = 'div[aria-label="total-non-billable-cost"] h3:nth-of-type(1)'
   TOTAL_HOURS = 'div[aria-label="total-hours"] h3:nth-of-type(1)'
   TOTAL_PEOPLE_HOURS = 'td[aria-label="totalHours"]'
   LAST_PERSON_NAME = 'div[id="people-cost-table"] tr:last-of-type td[aria-label="personName"]'
   TOTAL_COST_ON_PEOPLE_TABLE = 'td[aria-label="totalCost"]'
   SEARCH_TEXTFIELD = 'input[name="searchValue"]'
   SEARCH_BUTTON = 'button[aria-label="search-btn"]'
   OPEN_OVERHEAD_COST = 'td[aria-label="description"] a'
   OVERHEAD_COST_CONVERTED_AMOUNT = 'td[aria-label="convertedAmount"]'
   OVERHEAD_COST_DETAIL = 'div[id="simple-cost-detail-description"] tr td.MuiTableCell-body:nth-of-type(2)'
   EDIT_OVERHEAD_COST_HEADING = 'div[aria-labelledby="simple-cost-detail-label"] h6'
   EDIT_OVERHEAD_COST_MODAL = 'div[aria-labelledby="simple-cost-detail-label"]'
   PROJECT_OVERHEAD_COST = 'td[aria-label="cost"]'
   PROJECT_OVERHEAD_COST_CONVERTED = 'td[aria-label="convertedCost"]'
   EDIT_OVERHEAD_COST_BUTTONS = 'button[type="button"]'
   CONFIRMATION_ALERT = 'div[aria-labelledby="confirmation-alert-dialog-slide-title"]'
   CURRENCY_RATE_EDIT_BUTTON = '.costing-card-icon'
   CURRENCY_RATE_FIELD = '[aria-label="currency-rate-field"] input[name="currencyRate"]'
   PROJECT_PEOPLE_COST = 'td[aria-label="totalPeopleCost"]'
   PROJECT_COST = 'td[aria-label="cost"]'
   PRO_RATE_COST = 'td[aria-label="totalProrateCost"]'
   PROJECT_WORK_WEIGHT = 'td[aria-label="workWeight"]'
   TOTAL_WORK_WEIGHT = 'div[aria-label="total-billable-work-weight"] h3:nth-of-type(1)'
   PROJECT_PEOPLE_WORK_WEIGHT = '[aria-label="project-people-table"] td[aria-label="workWeight"]'
   PROJECT_OVERHEAD_COSTS = 'td[aria-label="totalOverheadsCost"] a'
   OVERHEAD_COST_OF_PROJECT = 'td[aria-label="cost"]'

   click_2019_tab() {
      cy.server()
      cy.route('GET', '**/api/v1/costing/months/?year=2019&**').as('2019_costing_data_load')
      cy.get(this.COSTING_TAB_2019).click().then(($tab_2019) => {
         cy.wait('@2019_costing_data_load').then((xhr) => {
            let status_code = xhr.status
            expect(status_code).to.equal(200)
         })
         cy.wrap($tab_2019).should('have.attr', 'aria-selected', 'true').and('have.attr', 'tabindex', '0').then(() => {
            cy.get(this.COSTING_MONTHS_COUNT).then(($months_count) => {
               expect($months_count).to.have.length(12)
            })
         })
         cy.get(this.COSTING_TAB_2020).should('have.attr', 'aria-selected', 'false').and('have.attr', 'tabindex', '-1')
      })
   }

   clickViewDetailsLink() {
      cy.server()
      cy.route('GET', '**/api/v1/costing/months/**').as('costing_month_data')
      cy.get(this.MONTH_NAME).invoke('text').then((month_name) => {
         cy.get(this.TOTAL_COST_ON_LISTING_PAGE).invoke('text').then((cost_on_listing) => {
            cy.get(this.VIEW_DETAILS_LINK).first().click()
            cy.wait('@costing_month_data').then((xhr) => {
               let status_code = xhr.status
               expect(status_code).to.equal(200)
            })
            cy.get(this.MONTH_NAME_ON_DETAILS_PAGE).invoke('text').then((month_name_on_details) => {
               expect(month_name_on_details).to.have.string(month_name)
            })
            cy.get(this.TOTAL_COST_ON_DETAILS_PAGE).invoke('text').then((cost_on_details) => {
               expect(cost_on_details).to.be.equal(cost_on_listing)
            })
         })
      })
   }

   veriftyTotalCost() {
      cy.get(this.TOTAL_PEOPLE_COST).invoke('text').then((people_cost) => {
         let people_cost_amount = people_cost.replace('Rs ', '').replace(/,/g, '')
         cy.get(this.OVERHEAD_COST).invoke('text').then((overhead_cost) => {
            let overhead_cost_amount = overhead_cost.replace('Rs ', '').replace(/,/g, '')
            cy.get(this.ADJUSTMENT_COST).invoke('text').then((adjustment_cost) => {
               let adjustment_cost_amount = adjustment_cost.replace('Rs ', '').replace(/,/g, '')
               let total_cost_amount = Number(overhead_cost_amount) + Number(people_cost_amount) + Number(adjustment_cost_amount)
               cy.get(this.TOTAL_COST_ON_DETAILS_PAGE).invoke('text').then((total_cost) => {
                  expect(Number(total_cost.replace('Rs', '').replace(/,/g, '').trim())).to.be.equal(total_cost_amount)
               })
            })
         })
      })
   }

   verifySumOfTotalOverheadCosts() {
      let last_person_name = ''
      cy.request('GET', 'https://dev-workstream.arbisoft.com/api/v1/costing/months/14/overheads/?search_value=&order=asc&order_by=description&limit=60&offset=0&is_more=false').then((response) => {
         cy.log(response.body)
         let elements = response.body
         let length_response = response.body.length
         let loop_iterations = Math.ceil(length_response/100)
         cy.log(loop_iterations)
         let last_element = elements[length_response - 1]
         console.log(last_element);
         cy.log(last_element)
         last_person_name = last_element.person_name
         for (let i = 0; i < loop_iterations; i++) {
            cy.get('div[id="overhead-cost-table"]').scrollTo('bottom', {ensureScrollable: false }, {duration: 5000 },)
            }
      })
      cy.get(this.OVERHEAD_COST_AMOUNT).then(($overhead_costs) => {
         const list_of_overhead_costs = Array.from($overhead_costs, overhead_cost => overhead_cost.innerText.replace(/,/g, ''))
         var sum_of_overhead_costs = list_of_overhead_costs.reduce(function (a, b) {
            return Number(a) + Number(b);
         }, 0)
         console.log(sum_of_overhead_costs)
         cy.get(this.OVERHEAD_COST).invoke('text').then((overhead_cost) => {
            let overhead_cost_amount = Number(overhead_cost.replace('Rs ', '').replace(/,/g, ''))
            expect(overhead_cost_amount).to.be.equal(sum_of_overhead_costs)
         })
      })
   }

   verifyNewAddOverheadCost() {
      var COST_DESCRIPTION = faker.fake("{{random.words}}")
      var COST_AMOUNT = faker.fake("{{random.number}}")
      cy.server()
      cy.route('POST', '**/api/v1/costing/overheads/').as('new_overhead_data')
      cy.get(this.ADD_OVERHEAD_BUTTON).click().then(() => {
         cy.get(this.SUBMIT_BUTTON_DISABLED).should('be.visible')
         cy.get(this.ADD_OVERHEAD_ROW_BUTTON).click().then(() => {
            cy.get(this.ADD_OVERHEAD_DESCRIPTION).should('be.visible').as('overhead_description')
            cy.get(this.OVERHEAD_AMOUNT).should('have.attr', 'value', '0').as('overhead_amount')
            cy.get('@overhead_description').type(COST_DESCRIPTION)
            cy.get('@overhead_amount').type(COST_AMOUNT)
            cy.get(this.SUBMIT_BUTTON).should('be.visible').click().then(() => {
               // .then(($el) => {
               // expect(cypress.dom.isDom($el)).to.be.false
               //  })
               cy.get(this.OVERHEAD_COST_DIALOG).should('not.exist')
               cy.wait('@new_overhead_data').then((xhr) => {
                  expect(xhr.status).to.equal(201)
                  expect(xhr.response.body[0].description).to.be.equal(COST_DESCRIPTION)
                  expect(xhr.response.body[0].amount).to.be.equal(Number(COST_AMOUNT))

               })
            })

         })
      })
   }

   verifyPopUpAlertOnAddOverheadCost() {
      cy.get('[id="overhead-cost-table"]').scrollTo('bottom', {ensureScrollable: false }, {duration: 5000 },)
      cy.get(this.ADD_OVERHEAD_BUTTON).click().then(() => {
         cy.get(this.SUBMIT_BUTTON_DISABLED).should('be.visible')

         cy.get(this.ADD_OVERHEAD_ROW_BUTTON).click().then(() => {
            cy.get(this.ADD_OVERHEAD_DESCRIPTION).should('be.visible').as('overhead_description')
            cy.get(this.OVERHEAD_AMOUNT).should('have.attr', 'value', '0').as('overhead_amount')
            cy.get(this.CLOSE_OVERHEAD_DIALOG_BUTTON).click().then(() => {
               cy.get(this.ALERT_CONFIRMATION_POPUP).should('be.visible')
               cy.get('button').contains('Yes').click().then(() => {
                  cy.get(this.ALERT_CONFIRMATION_POPUP).should('not.exist')
               })
            })
         })
      })
   }

   clickOnPeopleTab() {
      cy.server()
      cy.route('GET', '**/api/v1/costing/months/**').as('costing_month_data')
      cy.get(this.PEOPLE_TAB).should('have.attr', 'aria-selected', 'false').then(($people_tab) => {
         cy.get(this.PEOPLE_COST_TABPANEL).should('have.attr', 'hidden').then(($people_tab_panel) => {
            cy.get($people_tab).click().then(() => {
               cy.wait('@costing_month_data').then((xhr) => {
                  let status_code = xhr.status
                  expect(status_code).to.equal(200)
               })
               expect($people_tab).to.have.attr('aria-selected', 'true')
               cy.get(this.PEOPLE_COST_TABPANEL).should('not.have.attr', 'hidden')
            })
         })
      })
   }

   verifyTotalNonBillableCostSum() {
      let last_person_name = ''
      cy.request('GET', 'https://dev-workstream.arbisoft.com/api/v1/costing/months/14/people/?search_value=&order=asc&order_by=personName&limit=1000&offset=0&is_more=true&_=1605511338082').then((response) => {
         cy.log(response.body)
         let elements = response.body
         let length_response = response.body.length
         let loop_iterations = Math.ceil(length_response/100)
         cy.log(loop_iterations)
         let last_element = elements[length_response - 1]
         console.log(last_element);
         cy.log(last_element)
         last_person_name = last_element.person_name
         for (let i = 0; i < loop_iterations; i++) {
            cy.get(this.SCROLLER_).scrollTo('bottom', {duration: 5000 }, { ensureScrollable: false })
            }
      })
      cy.get(this.NON_BILLABLE_COST).then(($non_billable_costs) => {
         const list_of_non_billable_costs = Array.from($non_billable_costs, non_billable_cost => non_billable_cost.innerText.replace(/,/g,''))
         var sum_of_non_billable_costs = list_of_non_billable_costs.reduce(function(a, b){
            return Number(a) + Number(b)
        }, 0)
        cy.log(sum_of_non_billable_costs)
        cy.get(this.TOTAL_NON_BILLABLE_COST).invoke('text').then((non_billable_cost) => {
         let non_billable_cost_amount = Number(non_billable_cost.replace('Rs ','').replace(/,/g,''))
         expect(Math.trunc(non_billable_cost_amount)).to.be.equal(Math.trunc(sum_of_non_billable_costs))
         })
      }) 
    }

   verifyTotalHoursSum() {
      cy.get(this.TOTAL_PEOPLE_HOURS).then(($total_people_hours) => {
         const list_of_total_hours = Array.from($total_people_hours, total_people_hours => total_people_hours.innerText.replace(/,/g, ''))
         var sum_of_total_people_hours = list_of_total_hours.reduce(function (a, b) {
            return Number(a) + Number(b)
         }, 0)
         cy.log(sum_of_total_people_hours)
         cy.get(this.TOTAL_HOURS).invoke('text').then((total_hours) => {
            let grand_total_hours = Number(total_hours.replace('Rs ', '').replace(/,/g, ''))
            expect(Math.trunc(grand_total_hours)).to.be.equal(Math.trunc(sum_of_total_people_hours))
         })
      })
   }

   verifyTotalSumOfPeopleCostTable() {
      cy.get(this.TOTAL_COST_ON_PEOPLE_TABLE).then(($total_people_cost) => {
         const list_of_total_people_cost = Array.from($total_people_cost, total_people_cost => total_people_cost.innerText.replace(/,/g, ''))
         var sum_of_total_people_cost = list_of_total_people_cost.reduce(function (a, b) {
            return Number(a) + Number(b)
         }, 0)
         cy.log(sum_of_total_people_cost)
         cy.get(this.TOTAL_PEOPLE_COST).invoke('text').then((total_people_cost) => {
            let grand_total_people_cost = Number(total_people_cost.replace('Rs ', '').replace(/,/g, ''))
            expect(Math.trunc(grand_total_people_cost)).to.be.equal(Math.trunc(sum_of_total_people_cost))
         })
      })
   }

   selectAriaLabel(aria_label){
      console.log(aria_label);
      return `td[aria-label="${aria_label}"]`
   }

   searchFieledAriaLabelledBy(aria_labelledby) {
      return `div[aria-labelledby="${aria_labelledby}"] input[name="searchValue"]`
   }

   searchButtonAriaLabelledBy(aria_labelledby, button_aria_label) {
      return `div[aria-labelledby="${aria_labelledby}"] button[aria-label="${button_aria_label}"]`
   }

   clearSerachField(aria_labelledby, button_aria_label) {
      cy.get(this.searchFieledAriaLabelledBy(aria_labelledby)).clear().then(() => {
         cy.get(this.searchButtonAriaLabelledBy(aria_labelledby, button_aria_label)).click()
      })
   }

   closeOverheadDilaog(aria_labelledby, button_aria_label) {
      cy.get(this.searchButtonAriaLabelledBy(aria_labelledby, button_aria_label)).click().then(() => {
         cy.get(`div[aria-labelledby="${aria_labelledby}"]`).should('not.exist')
      })
   }

   searchValue(aria_labelledby, text_value, aria_label, button_aria_label) {
      cy.get(this.searchFieledAriaLabelledBy(aria_labelledby)).click().then(($search_field)=> {
         expect($search_field).to.have.focus
         cy.get(this.searchFieledAriaLabelledBy(aria_labelledby)).type(text_value).then(() => {
            cy.get(this.searchButtonAriaLabelledBy(aria_labelledby, button_aria_label)).click().then(() => {
               cy.get(this.selectAriaLabel(aria_label)).invoke('text').then((field_name) => {
                  expect(field_name).to.have.string(text_value)
               })
            })
         })
      })
   }

   openOverheadCostDetails() {
      cy.server()
      cy.route('GET', '**api/v1/costing/overheads/**').as('overhead_data')
      cy.get(this.OPEN_OVERHEAD_COST).first().invoke('text').then((overhead_description) => {
         cy.get(this.OVERHEAD_COST_AMOUNT).first().invoke('text').then((overhead_amount) => {
            cy.get(this.OVERHEAD_COST_CONVERTED_AMOUNT).first().invoke('text').then((overhead_converted_amount) => {
               cy.get(this.OPEN_OVERHEAD_COST).first().click().then(() => {
                  cy.wait('@overhead_data').then((xhr)=> {
                     let _description = xhr.response.body.description
                     expect(_description).to.equal(overhead_description)
                  })
                  cy.get(this.EDIT_OVERHEAD_COST_MODAL).should('be.visible')
                  cy.get(this.EDIT_OVERHEAD_COST_HEADING).invoke('text').then((overhead_detail_heading) => {
                     expect(overhead_detail_heading).to.have.string(overhead_description)
                     cy.get(this.OVERHEAD_COST_DETAIL).as('overhead_cost').first().should('have.text', overhead_description)
                     cy.get('@overhead_cost').eq(1).should('have.text', overhead_amount)
                     cy.get('@overhead_cost').eq(2).should('have.text', overhead_converted_amount)
                  })
               })
            })
         })
      })
   }

   verifyProjectOverheadCostSum() {
      cy.get(this.PROJECT_OVERHEAD_COST).then(($total_project_overhead_cost) => {
      const list_of_total_project_overhead_cost = Array.from($total_project_overhead_cost, total_project_overhead_cost => total_project_overhead_cost.innerText.replace(/,/g, ''))
         var sum_of_total_project_overhead_cost = list_of_total_project_overhead_cost.reduce(function (a, b) {
            return Number(a) + Number(b)
         }, 0)
         cy.log(sum_of_total_project_overhead_cost)
         cy.get(this.OVERHEAD_COST_DETAIL).eq(1).invoke('text').then((overhead_amount) => {
            let grand_total_project_overhead_cost = Number(overhead_amount.replace('Rs ', '').replace(/,/g, ''))
            expect(grand_total_project_overhead_cost).to.be.equal(Math.round(sum_of_total_project_overhead_cost))
         })
      })
      cy.get(this.PROJECT_OVERHEAD_COST_CONVERTED).then(($total_project_overhead_cost_converted) => {
         const list_of_total_project_overhead_cost_converted = Array.from($total_project_overhead_cost_converted, total_project_overhead_cost => total_project_overhead_cost.innerText.replace(/,/g, ''))
            var sum_of_total_project_overhead_cost_converted = list_of_total_project_overhead_cost_converted.reduce(function (a, b) {
               return Number(a) + Number(b)
            }, 0)
            cy.log(sum_of_total_project_overhead_cost_converted)
            cy.get(this.OVERHEAD_COST_DETAIL).eq(2).invoke('text').then((overhead_amount_converted) => {
               let grand_total_project_overhead_cost_converted = Number(overhead_amount_converted.replace('Rs ', '').replace(/,/g, ''))
               // expect(grand_total_project_overhead_cost_converted).to.be.equal((Math.round(sum_of_total_project_overhead_cost_converted * 100) / 100).toFixed(2))
               expect(grand_total_project_overhead_cost_converted).to.be.within(sum_of_total_project_overhead_cost_converted-1, sum_of_total_project_overhead_cost_converted+1)
            })
         })
   }
   
   clickEditButtonOnOverheadCostDetails() {
      var faker = require('faker')
      var COST_DESCRIPTION = faker.fake("{{random.words}}")
      var COST_AMOUNT = faker.fake("{{random.number}}")
      cy.server()
      cy.route('PATCH', '**api/v1/costing/overheads/**').as('overhead_data')
      cy.get(this.EDIT_OVERHEAD_COST_BUTTONS).contains('Edit').click().then(() => {
         cy.get('input[name="description"]').clear().type(COST_DESCRIPTION)
         cy.get('input[name="amount"]').clear().type(COST_AMOUNT)
         cy.get('div[aria-labelledby="simple-cost-detail-label"] button[type="button"]').contains('Save').click()
         cy.wait('@overhead_data').then((xhr) => {
            let status_code = xhr.status
            let amount = xhr.response.body.amount
            expect(amount).to.equal(Number(COST_AMOUNT))
            expect(status_code).to.equal(200)
         })
         this.searchValue('full-width-tab-overheads', COST_DESCRIPTION, 'description', 'search-btn')
         cy.get(this.OVERHEAD_COST_AMOUNT).first().invoke('text').then((cost_amount) => {
            let updated_cost_amount = cost_amount.replace(/,/g, '')
            expect(updated_cost_amount).to.be.equal(COST_AMOUNT)
         })
      })
   }

   deleteOverheadCost() {
      let overhead_list
      cy.server()
      cy.route('DELETE', '**api/v1/costing/overheads/**').as('delete_overhead_data')
      cy.get('div[id="overhead-cost-table"]').scrollTo('bottom', {ensureScrollable: false }, {duration: 5000 })
      cy.get(this.OPEN_OVERHEAD_COST).as('overhead_list').then((overheads) => {
         overhead_list = overheads.length
         cy.log(overhead_list)
      }).then(() => {
         this.openOverheadCostDetails()
      }).then(() => {
         cy.get(this.EDIT_OVERHEAD_COST_BUTTONS).contains('Delete').click().then(() => {
            cy.get('button').contains('Yes').click().then(() => {
               cy.get(this.CONFIRMATION_ALERT).should('not.exist')
               cy.wait('@delete_overhead_data').then((xhr) => {
                  let status_code = xhr.status
                  expect(status_code).to.equal(204)
               })
               cy.get('div[id="overhead-cost-table"]').scrollTo('bottom', {ensureScrollable: false }, {duration: 5000 },)
               cy.get('@overhead_list').then((overhead_list_after_deletion) => {
                  let updated_overhead_list = overhead_list_after_deletion.length
                  cy.log(updated_overhead_list)
                  expect(updated_overhead_list).to.be.lessThan(overhead_list)
               })
            })
         })
      })

   }

   verifyCurrencyRate() {
      var RATE = Math.floor((Math.random() * 1000))
      cy.log(RATE)
      cy.get(this.CURRENCY_RATE_EDIT_BUTTON).click().then(() => {
         cy.get(this.CURRENCY_RATE_FIELD).clear().type(RATE).then(() => {
            cy.get('.fa-check').click().then(() => {
               cy.get(this.TOTAL_PEOPLE_COST).invoke('text').then((total_people_cost) => {
                  let people_cost = Number(total_people_cost.replace('Rs ', '').replace(/,/g, ''))
                  let people_cost_after_conversion = (people_cost/RATE).toFixed(2)
                  cy.log(people_cost_after_conversion)
                  cy.get(this.TOTAL_PEOPLE_COST_CONVERTED).invoke('text').then((total_cost) => {
                     let people_cost_converted = Number(total_cost.replace('$ ', '').replace(/,/g, ''))
                     expect(Number(people_cost_after_conversion)).to.be.equal(people_cost_converted)
                  })
               })
            })
         })
      })
   }

   clickProjectsTab() {
      cy.server()
      cy.route('GET', '**/api/v1/costing/months/**').as('projects_costing_data')
      cy.get(this.PROJECTS_TAB).should('have.attr', 'aria-selected', 'false').then(($project_tab) => {
         cy.get(this.PROJECTS_COST_TABPANEL).should('have.attr', 'hidden').then(($projects_tab_panel) => {
            cy.get($project_tab).click().then(() => {
               cy.wait('@projects_costing_data').then((xhr) => {
                  let status_code = xhr.status
                  expect(status_code).to.equal(200)
               })
               expect($project_tab).to.have.attr('aria-selected', 'true')
               cy.get(this.PROJECTS_COST_TABPANEL).should('not.have.attr', 'hidden')
            })
         })
      })
   }

   verifyProjectPeopleCost() {
      cy.get(this.PROJECT_PEOPLE_COST).as('project_people_cost').click().then(($text) => {
         cy.wrap($text).invoke('text').then((project_people_cost) => {
            let grand_total_project_cost = parseFloat(project_people_cost.replace('Rs ', '').replace(/,/g, ''))
            cy.get('[aria-labelledby="project-cost-detail-label"]').should('be.visible')
            cy.get(this.PROJECT_COST).then(($total_project_cost) => {
               const list_of_total_project_cost = Array.from($total_project_cost, total_project_people_cost => total_project_people_cost.innerText.replace(/,/g, ''))
                  var sum_of_total_project_cost = list_of_total_project_cost.reduce(function (a, b) {
                     return parseFloat(a) + parseFloat(b)
                  }, 0)
                  expect(sum_of_total_project_cost.toString().split(".")[0]).to.be.equal(grand_total_project_cost.toString().split(".")[0])
            })
         })
      })
   }

   verifyProjectProRateCost() {
      cy.get(this.PRO_RATE_COST).invoke('text').then((pro_rate) => {
         cy.log(pro_rate)
         cy.get(this.PROJECT_WORK_WEIGHT).invoke('text').then((work_weight) => {
            cy.get(this.TOTAL_WORK_WEIGHT).invoke('text').then((total_work_weight) => {
               cy.get(this.TOTAL_NON_BILLABLE_COST).invoke('text').then((non_billable_cost) => {
                  let non_billable_cost_amount = parseFloat(non_billable_cost.replace('Rs ','').replace(/,/g,''))
                  let project_pro_rate_calculation = work_weight/total_work_weight*non_billable_cost_amount
                  cy.log(project_pro_rate_calculation)
                  expect(parseFloat(pro_rate.replace('Rs ','').replace(/,/g,''))).to.be.within(Number(project_pro_rate_calculation), Number(project_pro_rate_calculation+30))
               })
            })
         })
      })
   }

   verifyProjectPeopleWorkWeight() {
      cy.get(this.PROJECT_PEOPLE_WORK_WEIGHT)
      cy.get(this.PROJECT_PEOPLE_WORK_WEIGHT).then(($total_project_work_weight) => {
         const list_of_total_project_work_weight = Array.from($total_project_work_weight, total_project_work_weight => total_project_work_weight.innerText.replace(/,/g, ''))
            var sum_of_total_project_work_weight = list_of_total_project_work_weight.reduce(function (a, b) {
               return parseFloat(a) + parseFloat(b)
            }, 0).toFixed(2)
            cy.get(this.CLOSE_PROJECT_COST_DIALOG_BUTTON).click()
            cy.get(this.PROJECT_WORK_WEIGHT).invoke('text').then((work_weight) => {
               let work_weight_ = Number(work_weight).toFixed(2)
               expect(work_weight_).to.be.equal(sum_of_total_project_work_weight)
            })
         })
   }

   verifyProjectOverheadCosts() {
      cy.get(this.PROJECT_OVERHEAD_COSTS).click().then(($text) => {
         cy.wrap($text).invoke('text').then((project_overhead_cost) => {
            let grand_total_project_overhead_cost = parseFloat(project_overhead_cost.replace('Rs ', '').replace(/,/g, ''))
            cy.get('[aria-labelledby="project-cost-detail-label"]').should('be.visible')
            cy.get(this.OVERHEAD_COST_OF_PROJECT).then(($total_project_overhead_cost) => {
               const list_of_total_project_overhead_cost = Array.from($total_project_overhead_cost, total_project_overhead_cost => total_project_overhead_cost.innerText.replace(/,/g, ''))
                  var sum_of_total_project_overhead_cost = list_of_total_project_overhead_cost.reduce(function (a, b) {
                     return parseFloat(a) + parseFloat(b)
                  }, 0)
                  expect(sum_of_total_project_overhead_cost.toString().split(".")[0]).to.be.equal(grand_total_project_overhead_cost.toString().split(".")[0])
            })
         })
      })
   }

}

export default CostingPage
