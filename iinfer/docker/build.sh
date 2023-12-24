
#!/bin/bash

VERSION=0.2.0

docker build -t hamacom2004jp/iinfer:latest --build-arg MKUSER=${USER} -f ./docker/Dockerfile .
