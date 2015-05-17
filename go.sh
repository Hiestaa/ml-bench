#!/bin/bash
echo "Activating the environment..."
source .env/bin/activate || exit 1
echo "Checking missing module requirements..."
pip install -r requirements.txt || exit 1
cd src
echo "Starting server..."
python server.py -vv
