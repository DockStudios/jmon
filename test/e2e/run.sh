#!/bin/bash

set +e
set -x

docker_compose_project=jmon-e2e

function run_docker_compose_command() {
  docker-compose --env-file=./.env -p $docker_compose_project -f ./docker-compose.yml -f ./test/e2e/docker-compose.yml $@
}

# Bring up databases
run_docker_compose_command up --quiet-pull -d database broker redis minio
# Wait
sleep 30

# Run migration apps and wait for completion
run_docker_compose_command up --quiet-pull createbucket dbupgrade

# Run tests
run_docker_compose_command up --quiet-pull --build --exit-code-from testrunner server testrunner scheduler agent flower
rc=$?

# Get logs from testrunner
set +x
echo "----------------- TEST LOGS -----------------------"
run_docker_compose_command logs testrunner
echo "---------------------------------------------------"
set -x

run_docker_compose_command down -v >/dev/null

exit $rc
