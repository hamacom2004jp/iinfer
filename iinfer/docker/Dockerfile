FROM python:3.8.18-slim

ARG MKUSER

RUN groupadd ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER}
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git
RUN pip install --upgrade pip && \
    pip install iinfer
RUN iinfer -m install -c onnx --data /home/${MKUSER}/.iinfer
RUN iinfer -m install -c mmdet --data /home/${MKUSER}/.iinfer
RUN iinfer -m install -c mmpretrain --data /home/${MKUSER}/.iinfer
RUN chown -R ${MKUSER}. /home/${MKUSER}/.iinfer

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server

CMD iinfer -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME}
