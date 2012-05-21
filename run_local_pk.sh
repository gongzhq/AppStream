#!/bin/sh

if [ ! -d "./build" ]; then
    echo "Please run: 'python setup.py build' before $0"
fi

./run_local.sh --packagekit-backend $@
