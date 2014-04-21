#!/bin/sh -x

while :
do
    ./nodes.py > generated-nodes.kml-
    [ $? == 0 ] && mv generated-nodes.kml- www/generated-nodes.kml
    sleep 60
done

