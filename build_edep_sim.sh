#!/bin/bash

git submodule init
git submodule update

START_FOLDER=`pwd`

echo "Configure EDepSim build with cmake"
mkdir -p $EDEPSIM_BUILD_DIR
cd $EDEPSIM_BUILD_DIR/
echo "cmake -DCMAKE_INSTALL_PREFIX=$EDEPSIM_DIR $EDEPSIM_SOURCE_DIR/"
cmake -DCMAKE_INSTALL_PREFIX=$EDEPSIM_DIR $EDEPSIM_SOURCE_DIR/

echo "Start EDepSim build"
cd $EDEPSIM_BUILD_DIR
make -j4

echo "Start EDepSim install to $EDEPSIM_DIR"
make install -j4

echo "done"
cd $START_FOLDER

