#!/bin/bash

docker build -t crawler:local -f Dockerfile.crawler . \
&& docker build -t agent:local -f Dockerfile.agent . \
&& docker build -t public:local -f Dockerfile.public . \
&& docker build -t scheduler:local -f Dockerfile.scheduler .