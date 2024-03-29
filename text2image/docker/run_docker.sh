#!/bin/bash
docker run \
 -it \
 --gpus all \
 -v $(pwd)/text2image:/text2image \
 -w /text2image \
 -p 9091:9091 \
 text2image:latest bash
