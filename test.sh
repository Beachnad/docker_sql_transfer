#!/bin/bash
#
# A simple script to start a Docker container
# and run Testinfra in it
# Original script: https://gist.github.com/renatomefi/bbf44d4e8a2614b1390416c6189fbb8e
# Author: @renatomefi https://twitter.com/renatomefi
#test.sj

set -eEuo pipefail

# The first parameter is a Docker tag or image id
declare -r DOCKER_TAG="docker_sql_transfer:dev-test"

printf "Starting a container for '%s'\\n" "$DOCKER_TAG"

declare -r DOCKER_CONTAINER=$(docker run --rm -t -d "$DOCKER_TAG")

docker run \
  --rm \
  --network host \
  -v "$(PWD)/tests:/tests" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  docker_sql_transfer:dev-test \
  pytest /tests -vrA --color=yes