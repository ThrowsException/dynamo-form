#!/bin/sh

get_exposed_port() {
  docker-compose port $1 $2 | cut -d: -f2
}

# Ensure Docker is Running
if test -e /var/run/docker.sock
then
  DOCKER_IP=127.0.0.1
else
  echo "Docker environment not detected."
  exit 1
fi

# Common constants
COLOR_RESET='\033[0m'
COLOR_GREEN='\033[0;32m'

docker-compose down --volumes --remove-orphans
docker-compose pull
docker-compose up -d dynamo

cat > dev-environment << EOF
DYNAMODB_ENDPOINT=http://localhost:$(get_exposed_port dynamo 8000)
EOF
