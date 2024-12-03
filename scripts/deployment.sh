#!/bin/bash

# create zip with the dependencies first
cd src/dependencies
zip -x "**/__pycache__/**" -r ../deployment.zip *

# add the source code with the dependencies in a flat directory
cd ..
zip deployment.zip lambda_function.py utils/*

# move the zip to the build directory
mv deployment.zip ../build/