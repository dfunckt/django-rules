#!/bin/sh
coverage run --source=rules runtests.py --nologcapture --nocapture "$@"
result=$?
echo
coverage report -m
echo
exit $result
