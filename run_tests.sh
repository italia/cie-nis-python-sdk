#!/bin/bash

python -m pkg.tests.AlgorithmsTest || exit 1
python -m pkg.tests.UtilitiesTest || exit 1