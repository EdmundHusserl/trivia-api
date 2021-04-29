/// <reference path="../support/index.d.ts" /> 

import { categories, apiIntegration } from '../fixtures/home' 

describe("When I'm on the home page", () => {
    beforeEach( () => {
        cy.visit("/")
    })
    it.only("I can filter question by category", () => {
        categories.forEach( (cat) => {
            cy.contains(cat).click()
            cy.wait(1000)
            cy.get(".Question-holder img.category").each( ($img) => {
                expect($img.attr("src"))
                    .to.eql(`${cat.toLowerCase()}.svg`)           
            })
        })
    })

    it.only("I can perform a search by keyword", () => {
        const query: string = "world cup"
        /*
            We're creating here two references:
                1. searchInput (DOM element)
                2. apiCallSearchQuestions (api call object)
        */
        cy.get('input[placeholder="Search questions..."]').as("searchInput")
        cy.intercept(apiIntegration.search).as("apiCallSearchQuestions")
        
        cy.get("@searchInput").clear().type(`${query}{enter}`)
        cy.wait("@apiCallSearchQuestions").then( (req) => {
            /* 
                So, after submitting our query, we want to make sure
                    that we get a valid response.
            */
            expect(req.response.statusCode).to.eql(200)
            expect(req.response).not.eql(undefined)
            cy.get(".Question").each( ($q) => {
                expect($q.get(0).textContent.toLowerCase())
                    .to.include(query)
            })
        })
    })

    it.only("I can delete a question", () => {
        cy.get('input[placeholder="Search questions..."]').as("searchInput")
        /*
            So here we're hijacking and then stubbing the response 
                that we'll get, because we don't want to actually
                perform any deletion.             
        */
        cy.intercept(apiIntegration.delete, { 
            statusCode: 204,
            body: "Whatever"
        }).as("apiCallDeleteQuestion")
        
        cy.get("@searchInput").type("maradona{enter}")
        cy.get(".delete").then( (el) => {
            el.trigger("click")
            cy.wait("@apiCallDeleteQuestion").then( (req) => {
                expect(req.response.statusCode).to.eql(204)
                expect(req.response.body).not.eql(undefined)
            })
            cy.on("window:alert", (txt) => {
                expect(txt).to.eql("")  
            })
        })
    })
    it.only("I can see the question to a given answer", () => {
        const queryString = "Anne Rice" 
        // This is a custom cypress method.
        cy.searchByKeyword(queryString)
        cy.contains(queryString).then( () => {
            cy.wait(1000)
            cy.get(".show-answer.button").click()
                .then( () => {
                    cy.get(".answer-holder span").then( ($el) => {
                            expect($el.get(0).style.visibility).to.eql("visible")
                    })
                })
        })
    })
})