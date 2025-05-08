#! /bin/sh

echo "Configuring redis"

echo "Checking env vars"
: "${REDIS_USER:?REDIS_USER must be set}"
: "${REDIS_PASSWORD:?REDIS_PASSWORD must be set}"
: "${REDIS_PORT:?REDIS_PORT must be set}"

echo "Creating log directory and file"
mkdir -p /var/log/redis
touch /var/log/redis/redis.log

echo "Configuring redis"
sed -e "s/{{REDIS_USER}}/${REDIS_USER}/g" \
    -e "s/{{REDIS_PASSWORD}}/${REDIS_PASSWORD}/g" \
    -e "s/{{REDIS_PORT}}/${REDIS_PORT}/g" \
    /usr/local/etc/redis/redis.conf > /tmp/redis.conf

echo "Starting redis"
exec redis-server /tmp/redis.conf