#!/bin/bash

git clone https://github.com/agl/jbig2enc
cd jbig2enc
./autogen.sh
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "autogen.sh failed"
    exit $STATUS
fi
./configure && make
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "configure failed"
    exit $STATUS
fi
sudo make install
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "make install failed"
    exit $STATUS
fi
