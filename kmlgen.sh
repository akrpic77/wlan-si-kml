#!/bin/sh -x

while :
do
    ./nodes.py > generated-nodes.kml-
    [ $? -eq 0 ] && mv generated-nodes.kml- www/generated-nodes.kml
    sleep 60
done

