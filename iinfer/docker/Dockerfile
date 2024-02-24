#{FROM}

ARG MKUSER

#{COPY_IINFER}
RUN groupadd ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
#{INSTALL_PYTHON}
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git build-essential
RUN pip install --upgrade pip && \
    pip install #{INSTALL_IINFER}

#{INSTALL_ONNX}
#{INSTALL_MMDET}
#{INSTALL_MMCLS}
#{INSTALL_MMPRETRAIN}
#{INSTALL_MMROTATE}
#{INSTALL_INSIGHTFACE}
RUN mkdir -p /home/${MKUSER}/.iinfer && chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}/.iinfer

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server#{INSTALL_TAG}

CMD iinfer -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME}
