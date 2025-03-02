#!/bin/zsh

function log() {
  local level="$1"
  local message="$2"
  local timestamp=$(date +"%Y-%m-%dT%H:%M:%S%z")

  # Use a JSON-like format for structured logging
  echo "{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"message\":\"$message\"}"
}

log "INFO" "Starting evidence collection"
echo "Starting evidence collection at time: $(date)"

curl -fsS -m 10 --retry 5 http://spark:8002/ping/57ec0564-d52d-433f-8c81-a98930aae20f/start
cd /Users/edwinzamudio/notedwin/projects/tiny-spider/evid-dash
# npm run sources
npm run build:strict
# force copy over the build/data folder
cp -r build/data/ /Users/edwinzamudio/notedwin/projects/tiny-spider/evid-dash/build/data

rsync -avz build/ notedwin@192.168.0.200:/home/notedwin/docker/caddy/map/
curl -fsS -m 10 --retry 5 http://spark:8002/ping/57ec0564-d52d-433f-8c81-a98930aae20f

log "INFO" "Finished evidence collection"