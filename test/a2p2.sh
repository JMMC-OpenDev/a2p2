#!/bin/bash
# 
# TODO mke this test using sampy (because this module is for python :) )
# else we need to install jsamp first 

if [ $# -ge 1 ]
then
  FILES=$*
else
  FILES=*.obxml
fi

for FILE in $FILES 
do
  if ! java -classpath jsamp-1.3.5.jar:${HOME}/.m2/repository/org/astrogrid/jsamp/1.3.5/jsamp-1.3.5.jar:${PWD}/../../target/runtime-libs/jsamp-1.3.5.jar org.astrogrid.samp.test.MessageSender -mtype "ob.load.data" -param "url" "${PWD}/$FILE" > /tmp/sendtoVOT.log
  then
    echo "Cannot send to A2P2 through samp hub, sorry."
  fi
done


