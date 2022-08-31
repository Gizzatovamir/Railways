#!/bin/bash

REQUIRED_PKG="poetry"
PKG_OK=$(which $REQUIRED_PKG|grep $REQUIRED_PKG)
echo Checking for $REQUIRED_PKG
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3.8 -
else
  echo "$REQUIRED_PKG is found: '$PKG_OK'. No installation is required."
fi

