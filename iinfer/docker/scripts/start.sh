
iinfer -m web -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} --listen_port ${LISTEN_PORT}&
iinfer -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME}
