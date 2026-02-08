
if [[ "${IINFER_DEBUG}" = "true" ]]; then
    DEBUG="--debug"
else
    DEBUG=""
fi
iinfer -m web -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
       --listen_port ${LISTEN_PORT} --data /home/${MKUSER}/.iinfer --allow_host 0.0.0.0 \
       --gunicorn_workers ${GUNICORN_WORKERS:-5} --gunicorn_timeout ${GUNICORN_TIMEOUT:-600} \
       --signin_file .iinfer/user_list.yml ${DEBUG} --language ${LANGUAGE} &
iinfer -m mcpsv -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
       --listen_port ${MCPSV_LISTEN_PORT} --data /home/${MKUSER}/.iinfer --allow_host 0.0.0.0 \
       --gunicorn_workers ${GUNICORN_WORKERS:-5} --gunicorn_timeout ${GUNICORN_TIMEOUT:-600} \
       --signin_file .iinfer/user_list.yml ${DEBUG} --language ${LANGUAGE} &
iinfer -m a2asv -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
       --listen_port ${A2ASV_LISTEN_PORT} --data /home/${MKUSER}/.iinfer --allow_host 0.0.0.0 \
       --gunicorn_workers ${GUNICORN_WORKERS:-5} --gunicorn_timeout ${GUNICORN_TIMEOUT:-600} \
       --signin_file .iinfer/user_list.yml ${DEBUG} --language ${LANGUAGE} &
if [[ -z "${SVCOUNT}" || "${SVCOUNT}" =~ ^[^0-9]+$ ]]; then
    echo "SVCOUNT is not a number. SVCOUNT=${SVCOUNT}"
    SVCOUNT=3
fi
for ((i=1; i<${SVCOUNT}; i++))
do
    iinfer -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
           --data /home/${MKUSER}/.iinfer ${DEBUG} --language ${LANGUAGE} &
done
iinfer -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
       --data /home/${MKUSER}/.iinfer ${DEBUG} --language ${LANGUAGE}