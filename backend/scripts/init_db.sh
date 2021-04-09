#!/bin/bash
init_trivia_db() {
    if [ -z ${POSTGRES_USER} ]; then
        echo "Setting new value POSTGRES_USER.";
        POSTGRES_USER="jorgepl";
    fi
    
    if [ -z ${POSTGRES_DB} ]; then
        echo "Setting new value to POSTGRES_DB.";
        POSTGRES_DB="trivia_test"
    fi
    psql -f /docker-entrypoint-initdb.d/trivia.psql ${POSTGRES_DB} ${POSTGRES_USER} 
}

init_trivia_db