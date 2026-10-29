#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker build -t idcp-assignment5-jenkins:local jenkins/
DOCKER_GID=$(docker run --rm --entrypoint stat \
    -v /var/run/docker.sock:/var/run/docker.sock \
    idcp-assignment5-jenkins:local -c '%g' /var/run/docker.sock)
export DOCKER_GID
docker compose -p assignment5 -f jenkins/compose.yml up -d --no-build
