#!/bin/bash

DIRECTORY=`dirname $0`

docker build -t crawler:local -f $DIRECTORY/Dockerfile.crawler $DIRECTORY \
&& docker build -t agent:local -f $DIRECTORY/Dockerfile.agent $DIRECTORY/ \
&& docker build -t public:local -f $DIRECTORY/Dockerfile.public $DIRECTORY/ \
&& docker build -t scheduler:local -f $DIRECTORY/Dockerfile.scheduler $DIRECTORY/ \
&& docker build -t frontend:local -f $DIRECTORY/Dockerfile.frontend $DIRECTORY/