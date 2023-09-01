#!/bin/bash

set +e
set -x

docker_compose_project=jmon-e2e

# Bring up databases
docker-compose --env-file=./.env -p $docker_compose_project -f ./test/e2e/docker-compose.yml up --quiet-pull -d database broker redis minio
# Wait
sleep 30

# Run migration apps and wait for completion
docker-compose --env-file=./.env -p $docker_compose_project -f ./test/e2e/docker-compose.yml up --quiet-pull createbucket dbupgrade

# Run tests
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
