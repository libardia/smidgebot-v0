#!/bin/bash

int=`ps -ef | grep smidgebot.py`
echo $int
id=`ps -ef | grep smidgebot.py | grep --invert-match grep | awk '{ print $2 }'`
echo Shutting down PID $id
kill $id
