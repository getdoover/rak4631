#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
python3.11 -m pydoover invoke_local_task on_uplink . --agent 02c3486b-14b8-45c5-9030-f49e4830eab4 --enable-traceback
