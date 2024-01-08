FROM python:3.8.18-slim

ARG MKUSER

RUN groupadd ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER}
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git
RUN pip install --upgrade pip && \
    pip install ${INSTALL_IINFER}

#{INSTALL_ONNX}
#{INSTALL_MMDET}
#{INSTALL_MMCLS}
#{INSTALL_MMPRETRAIN}
#{INSTALL_MMROTATE}
RUN chown -R ${MKUSER}. /home/${MKUSER}/.iinfer

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server

CMD iinfer -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME}
