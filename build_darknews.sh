#!/bin/bash

echo "Start darknews build"
DARKNEWS_INSTALL_DIR=${REPO_HOME_DIR}/darknews/python/
echo "dark news install dir: "${DARKNEWS_INSTALL_DIR}
mkdir -f ${DARKNEWS_INSTALL_DIR}
cd darknews/DarkNews-generator/
python3 setup.py install --home=${DARKNEWS_INSTALL_DIR}

echo "done"

