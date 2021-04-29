/// <reference types="cypress" />

declare namespace Cypress {
    interface Chainable {
        searchByKeyword(query: string): void
    }
}