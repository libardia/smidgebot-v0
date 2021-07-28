#!/bin/bash

kill -9 `ps -ef | grep "python bot.py" | awk '{ print $1 }'`
