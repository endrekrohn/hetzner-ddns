#! /usr/bin/env sh

activate_poetry () { source "$( poetry env list --full-path | grep Activated | cut -d' ' -f1 )/bin/activate"; }

echo "Updating IP 🔨"
(activate_poetry && python3 ./app/main.py && deactivate)