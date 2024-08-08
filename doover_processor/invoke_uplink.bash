#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
python3.11 -m pydoover invoke_local_task on_uplink . --agent 94add4d6-10b1-4e05-82c4-84a2669c9e8c --enable-traceback
