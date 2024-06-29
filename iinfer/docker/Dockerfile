#{FROM}

ARG MKUSER

#{COPY_IINFER}
#{COPY_IINFER_START}

RUN groupadd ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER}
RUN chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
#{INSTALL_PYTHON}
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git build-essential && \
    apt-get install -y iputils-ping net-tools
RUN pip install --upgrade pip && \
    pip install #{INSTALL_IINFER} && \
    iinfer --version

#{INSTALL_ONNX}
#{INSTALL_MMDET}
#{INSTALL_MMSEG}
#{INSTALL_MMCLS}
#{INSTALL_MMPRETRAIN}
#{INSTALL_INSIGHTFACE}
#{INSTALL_DIFFUSERS}
#{INSTALL_LLAMAINDEX}
RUN mkdir -p /home/${MKUSER}/.iinfer && chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}/.iinfer

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server#{INSTALL_TAG}
ENV LISTEN_PORT=8081

CMD bash /home/${MKUSER}/scripts/start.sh
