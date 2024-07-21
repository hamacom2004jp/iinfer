
if [[ "${IINFER_DEBUG}" = "true" ]]; then
    DEBUG="--debug"
else
    DEBUG=""
fi
iinfer -m web -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} --listen_port ${LISTEN_PORT} --data /home/${MKUSER}/.iinfer ${DEBUG}&
iinfer -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} --data /home/${MKUSER}/.iinfer ${DEBUG}
