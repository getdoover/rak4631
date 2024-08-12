#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
python3.11 -m pydoover invoke_local_task on_deploy . --agent 7ef91fcd-9f21-4388-a08d-ba1292142263 --enable-traceback
