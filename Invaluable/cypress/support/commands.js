// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })


let LOCAL_STORAGE_MEMORY = {};

Cypress.Commands.add("saveLocalStorage", () => {
  Object.keys(localStorage).forEach(key => {
    LOCAL_STORAGE_MEMORY[key] = localStorage[key];
  })
})

Cypress.Commands.add("restoreLocalStorage", () => {
  Object.keys(LOCAL_STORAGE_MEMORY).forEach(key => {
    localStorage.setItem(key, LOCAL_STORAGE_MEMORY[key]);
  })
})


Cypress.Commands.add('loginViaApi', (user) => {
    cy.request({
      method: 'POST',
      url: `${Cypress.config('baseUrl')}/app/v2/member/login`,
      body: {
        userName: user.username,
        password: user.password,
        keepLoggedIn: true
      },
    }).then((response) => {
        cy.log(response)
        cy.request({
            method: 'POST',
            url: `${Cypress.config('baseUrl')}/boulder/login`,
            body: {
                authorization: response.headers.authorization,
                email: user.username,
                firstName: response.body.data.firstName,
                keepLoggedIn: true,
                memberID: response.body.data.memberID,
                memberRef: response.body.data.memberRef,
                // 'oastoken-stage': response.headers.oastoken-stage,
                suggestUpdatePassword: response.body.data.suggestUpdatePassword,
                userID: response.body.data.memberID,
                userName: user.username,
                // 'x-auth-token': response.headers.x-auth-token,
            }
        }).then((response) => {
            cy.log(response)
        })
    })
  })

Cypress.Commands.add('authenticateUser', (catalogRef) => {
    // let catalogRef = 'Y7ZZV6DTR2'
    cy.request({
        method: 'GET',
        url: `https://stage.invaluable.com/app/v2/bidderConsoleUrl/channel/1/catalog/${catalogRef}?baseConsoleURL=stage-live.invaluable.com&registrationUrl=stage.invaluable.com/bidNow/reqForApproval?catalogRef=${catalogRef}`
    }).then((response) => {
      cy.log(response)
      const message = response.body.consoleUrl
      var authUrl = message.substring(
        message.indexOf("?") + 1, 
        message.lastIndexOf("&channelID")
      )
      cy.log(authUrl)
      cy.visit(`https://live.invaluable.ninja/catalog.html?catalogRef=${catalogRef}&` + authUrl)
      
    })
})
