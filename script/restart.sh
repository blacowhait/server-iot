systemctl restart postgresql.service
systemctl restart redis.service
redis-cli flushall