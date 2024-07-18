#!/bin/bash

echo "Start simpledet build"
cd ${SIMPLEDET_DIR}
mkdir build
cd build
cmake ../

make install -j4

echo "done"

