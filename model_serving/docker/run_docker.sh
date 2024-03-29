#!/bin/bash
docker run \
 --gpus all \
 -v $(pwd)/model_serving:/model_serving \
 -w /model_serving \
 -p 9090:9090 \
 model_serving:latest
