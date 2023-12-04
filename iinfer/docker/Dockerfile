FROM python:3.8.18-slim

ARG VERSION

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0
RUN pip install --upgrade pip && \
    pip install iinfer==${VERSION}
RUN iinfer -m install -c mmdet && \
    iinfer -m install -c onnx

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV PASSWORD=password

CMD iinfer -m server --host ${REDIS_HOST} --port ${REDIS_PORT} -p ${PASSWORD}
