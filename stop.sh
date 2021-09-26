#!/bin/bash

id=`ps -ef | grep smidgebot | grep --invert-match grep | awk '{ print $2 }'`
echo $id
kill -9 $id
