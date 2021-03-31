#!/bin/bash

venv() {
  export FLASK_APP=flaskr;
  export FLASK_ENV=development;
  ensure_psql;
}

ensure_psql() {
  SERVICE_NAME="psql_db";
  DIR_NAME="${PWD}"
  echo "Verifying docker status. This operation may need elevated privileges.";
  sudo systemctl start docker && docker-compose -f "${PWD}/docker-compose.yaml" up -d
  PSQL_STATUS="$(docker ps | grep ${SERVICE_NAME})"
  if [ -z "${#PSQL_STATUS}" ]; then
    echo "Something went wrong. Could initialize postgresql container.";
  else 
    echo "DB up and running.";
  fi

}

build_services() {
  docker-compose -f "${PWD}/docker-compose.yaml" up -d --build --remove-orphans
}

venv
source /home/jorgepl/Documents/udacity/trivia-api/backend/venv/bin/activate
