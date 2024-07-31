#!/bin/bash

echo "Start darknews build"
DARKNEWS_INSTALL_DIR=${REPO_HOME_DIR}/darknews/install
echo "dark news install dir: "${DARKNEWS_INSTALL_DIR}
mkdir -p ${DARKNEWS_INSTALL_DIR}
cd darknews/DarkNews-generator/
python3.9 -m pip install --prefix=${DARKNEWS_INSTALL_DIR} .

echo "done"

