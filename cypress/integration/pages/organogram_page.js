class OrganogramPage {
   invalid_password = 'testt'
   new_password = "Passenger2019!"
   EMAIL = "#erp-email-login input[name='email']"
   
   constructor(username, password) {
      this.username = username
      this.password = password
   }
   SELECT_TEAM = '.Select-value'
   SELECT_PERSON = '.Select-placeholder'
   SELECTED_TEAM = '#organogram div.user-info .name'
   SELECTED_PERSON = 'h5.MuiTypography-subtitle1'
   VIEW_TEAM_DETAIL = '#team-detail-link'
   VIEW_TEAM_DETAIL_DIALOG = 'div[aria-describedby="add-team-detail-dialog-description"]'
   TEAL_LEAD_BUTTONS = 'div[aria-describedby="add-team-detail-dialog-description"] button:not([aria-label="close"])'

   selectTeamFromDropdown(team_name) {
      cy.get(this.SELECT_TEAM).click().type(team_name).get('.Select-menu-outer').click().then(() => {
         cy.get(this.SELECTED_TEAM).should('have.text', team_name)
      })
   }

   selectPersonFromDropdown(person_name) {
      cy.get(this.SELECT_PERSON).click().type(person_name).get('.Select-menu-outer').click().then(() => {
         cy.get(this.SELECTED_PERSON).should('have.text', person_name)
      })
   }

   navigateToPersonDetailPage() {
      cy.get('#organogram').click().then(($team) => {
         expect($team).to.have.attr('aria-expanded', true)
      })
   }

   viewTeamDetailLink(team_lead=false) {
      if (team_lead) {
         cy.get(this.VIEW_TEAM_DETAIL).click().then(() => {
            cy.get(this.VIEW_TEAM_DETAIL_DIALOG).should('be.visible').get(this.TEAL_LEAD_BUTTONS).should('be.visible')
            
         })
      }
   }

}

export default OrganogramPage
