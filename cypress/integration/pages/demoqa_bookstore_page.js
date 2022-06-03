class DemoQaBookstore {
  
  getBooksList() {
    cy.get('.element-group:nth-of-type(6) #item-2').click()
    cy.get('.mr-2 a').invoke('text').then(($books_list) => {
      // $books_list
      for (let i = 0; i < $books_list.length; i++) {
        text += $books_list[i] + "<br>"
      }
    })
  }

  searchForBook() {
    cy.get('.element-group:nth-of-type(6) #item-2').click()
    cy.get('#searchBox').type('Git Pocket Guide').then(() => {
      cy.get('.mr-2 a').invoke('text').should('be.equal', 'Git Pocket Guide')
    })
  }

  openBookDetails() {
    cy.get('.mr-2 a').click().then(() => {
      cy.get('#ISBN-wrapper .form-label#userName-value').invoke('text').then((isbn) => {
        cy.url().should('include', isbn)
      })
    })
  }

  addBookToYourCollection() {
    cy.contains('Add To Your Collection').click()
    // cy.on('window:confirm', (text) => {
    //   expect(text).to.contains('Book added to your collection.');
    // })
    cy.contains('Back To Book Store').click()
  }

  navigateToProfile() {
    cy.get('ul.menu-list #item-3').contains('Profile').click()
    cy.url().should('include', '/profile')
  }

  verifyAddedBook() {
    cy.get('.mr-2 a').each(($li, index, $lis) => {
      console.log($lis);
    }).then(($lis) => {
        expect($lis).to.contain('Git Pocket Guid')
  })
  }


}

export default DemoQaBookstore
