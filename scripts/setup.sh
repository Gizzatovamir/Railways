#!/bin/bash

poetry env use python3.8

poetry install
poetry run pre-commit install -t pre-commit
poetry run pre-commit install -t pre-push

