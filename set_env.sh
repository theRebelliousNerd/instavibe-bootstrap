#!/bin/bash

# This script sets the environment variables required for the AI Developer Assistant.
#
# Instructions:
# 1. Source this script before running the application:
#    source set_env.sh

source /home/smoore5527/otherprojectrelatedinfo.txt

# Add the project root to the PYTHONPATH to allow imports from any directory
export PYTHONPATH=$PYTHONPATH:$(pwd)


echo "Environment variables set."
