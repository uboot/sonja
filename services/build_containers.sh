#!/bin/bash

DIRECTORY=`dirname $0`

   docker build -t uboot/crawler:latest -f $DIRECTORY/Dockerfile.crawler $DIRECTORY \
&& docker build -t uboot/agent:latest -f $DIRECTORY/Dockerfile.agent $DIRECTORY \
&& docker build -t uboot/public:latest -f $DIRECTORY/Dockerfile.public $DIRECTORY \
&& docker build -t uboot/scheduler:latest -f $DIRECTORY/Dockerfile.scheduler $DIRECTORY \
&& docker build -t uboot/frontend:latest -f $DIRECTORY/Dockerfile.frontend $DIRECTORY \
&& docker push uboot/crawler:latest \
&& docker push uboot/agent:latest \
&& docker push uboot/public:latest \
&& docker push uboot/scheduler:latest \
&& docker push uboot/frontend:latest
