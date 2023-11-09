#!/bin/bash
# wait-for-it.sh
# Usage: wait-for-it.sh host:port [-s] [-t timeout] [-- command args]
# Waits until the specified host and port are available.
# It also supports specifying a command to run once the host and port are available.

echo "Waiting for $1 to be available..."
hostport=$1
shift
timeout=15
while ! nc -z $(echo $hostport | tr ":" " "); do
  sleep 1
  timeout=$(($timeout - 1))
  if [ "$timeout" -eq 0 ]; then
    echo "Timeout occurred while waiting for $hostport"
    exit 1
  fi
done

echo "$hostport is available, executing command: $@"
exec "$@"