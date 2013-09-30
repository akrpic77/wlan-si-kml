#!/bin/sh -x

while :
do
    nodes.py > generated-nodes.kml-
    mv generated-nodes.kml- www/generated-nodes.kml
    sleep 60
done

