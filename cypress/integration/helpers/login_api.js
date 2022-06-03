// TBA //  
class LoginApi {
    constructor() {
        this.defaultHeaders = {
            'origin': "https://workstream-staging2.arbisoft.com",
            'referer': "https://workstream-staging2.arbisoft.com/login/",
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json;charset=utf-8",
            'cookie': null
        }
    }
    loginApi(csrftoken) {
        cy.request({
            method: 'POST',
            url: 'https://workstream-staging2.arbisoft.com/api/v1/core/email-login/',
            headers: this.defaultHeaders,
            body: {
                email: 'sajjad.akbar@arbisoft.com',
                password: 'Erp786786',
            }
        }).should((response) => {
            let user = response.body.token
            console.log(user);

        }).then((token) => {
            cy.getCookie('csrftoken')
            .should('exist').then((csrfVal) => {
              this.defaultHeaders['cookie'] = csrfVal.value
            })
            cy.request({
                method: 'GET',
                url: 'https://workstream-staging2.arbisoft.com/rewards/dashboard/',
                headers: this.defaultHeaders
            })
            cy.visit('/home/')
        })
    }
}

export default new LoginApi