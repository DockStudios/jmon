#!/bin/bash

set +e
set -x

docker_compose_project=jmon-e2e

docker-compose --env-file=./.env -p $docker_compose_project -f ./test/e2e/docker-compose.yml up --quiet-pull --build --exit-code-from testrunner
rc=$?

# Get logs from testrunner
set +x
echo "----------------- TEST LOGS -----------------------"
docker-compose --env-file=./.env -p $docker_compose_project -f ./test/e2e/docker-compose.yml logs testrunner
echo "---------------------------------------------------"
set -x

docker-compose --env-file=./.env -p $docker_compose_project -f ./test/e2e/docker-compose.yml down -v

exit $rc
