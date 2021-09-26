#!/bin/bash

kill -9 `ps -ef | grep smidgebot | grep --invert-match grep | awk '{ print $2 }'`
