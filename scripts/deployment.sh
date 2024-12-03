#!/bin/bash

# create zip with the dependencies first
cd src/dependencies
zip -x "**/__pycache__/**" -r ../../build/deployment.zip *

# add the source code with the dependencies in a flat directory
cd ../../build
zip deployment.zip ../src/lambda_function.py ../src/utils/*

# cd src/dependencies
# zip -x "**/__pycache__/**" -r ../deployment.zip *

# cd ..
# zip deployment.zip lambda_function.py utils/*

# mv deployment.zip ../build/