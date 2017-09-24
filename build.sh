#!/bin/bash

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd ${PROJECT_DIR}

if [ -d ".env" ]; then
    echo "**> virtualenv exists"
else
    echo "**> creating virtualenv"
    virtualenv .env
fi

set +u
source .env/bin/activate
set -u

pip install -U pip
pip install -U pip-tools
# This line is needed to get around a bug with pip and one of the Jinga2 dependencies
# called MarkupSafe.
pip install -U setuptools==21.2.1

pip-sync requirements.txt
