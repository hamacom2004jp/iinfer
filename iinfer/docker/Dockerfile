#{FROM}

ARG MKUSER

#{COPY_CMDBOX}
#{COPY_IINFER}

RUN groupadd ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER} && \
    cp /etc/skel/.bash_logout /home/${MKUSER}/ && \
    cp /etc/skel/.bashrc /home/${MKUSER}/ && \
    cp /etc/skel/.profile /home/${MKUSER}/
RUN chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git wget
#{INSTALL_PYTHON}
RUN apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential libopencv-dev && \
    apt-get install -y iputils-ping net-tools
RUN pip install --upgrade pip && \
    pip install xmlsec==1.3.13 python3-saml google-adk litellm fastmcp && \
    pip install #{INSTALL_CMDBOX} && cmdbox --version && \
    pip install #{INSTALL_IINFER} && iinfer --version

#{INSTALL_ONNX}
#{INSTALL_MMDET}
#{INSTALL_MMSEG}
#{INSTALL_MMCLS}
#{INSTALL_MMPRETRAIN}
#{INSTALL_INSIGHTFACE}
RUN mkdir -p /home/${MKUSER}/.iinfer && chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}/.iinfer

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server#{INSTALL_TAG}
ENV MKUSER=${MKUSER}
ENV LISTEN_PORT=8081
ENV SVCOUNT=${SVCOUNT}

WORKDIR /home/${MKUSER}/
#{COPY_IINFER_START}
CMD bash
