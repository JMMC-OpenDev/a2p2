#!/bin/bash
# 
# TODO mke this test using sampy (because this module is for python :) )

FILE=aspro-sample.obxml

CURRENT=`pwd`

java -classpath ${CURRENT}/../../target/runtime-libs/jsamp-1.3.5.jar org.astrogrid.samp.test.MessageSender -mtype "ob.load.data" -param "url" "${CURRENT}/$FILE" > /tmp/sendtoVOT.log

if [ $? != 0 ]; then
    echo "Cannot send to ESO's p2 samp hub, sorry."
fi

