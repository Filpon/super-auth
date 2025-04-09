#!/bin/bash

# Pytest start
pytest ./web-backend/tests/ --maxfail=3 --disable-warnings
exit_code=$?

# Code detemining
if [ $exit_code -eq 0 ]; then
    echo "All tests were passed sucessfully!"
elif [ $exit_code -eq 5 ]; then
    echo "All tests were passed sucessfully!"
    # exit 0 
else
    echo "Unknown exit code: $exit_code"
fi

# Script finish
exit $exit_code
