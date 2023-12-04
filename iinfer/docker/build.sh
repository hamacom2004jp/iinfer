
#!/bin/bash

VERSION=0.2.0

docker build -t hamacom2004jp/iinfer:${VERSION} --build-arg VERSION=${VERSION} -f ./docker/Dockerfile .
