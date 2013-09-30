#!/usr/bin/env python
import re
import json
import requests
import StringIO


r = requests.get("https://nodes.wlan-si.net/network/map/#lat=46.17&long=14.96&zoom=8&type=m&project=1,3,6,7,8,9,10,11,13,15,18,19,20,21,23,24&status=up,visible,down,duped,new,pending",
          verify=False)
data = r.text
#data = open("nodes.wlan-si.net-map.html").read()

parser = re.compile("var nodes = (.*?);", re.MULTILINE | re.DOTALL)
parsed = parser.search(data).groups()[0]
nodes = json.loads(parsed.replace("'", '"'))

parser = re.compile("var links = (.*?);", re.MULTILINE | re.DOTALL)
parsed = parser.search(data).groups()[0]
links = json.loads(parsed.replace("'", '"'))


kml = StringIO.StringIO()
kml.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
<Document>
""")

for status in ('up', 'down', 'duped', 'pending', 'visible'):
  d = {'status': status,
          }
  kml.write("""
  <Style id="%(status)s">
    <IconStyle>
       <Icon>
          <href>https://nodes.wlan-si.net/images/status_%(status)s_gmap.png</href>
          <hotSpot x="0.5" y="0.5" xunits="fractions" yunits="fractions"/>
       </Icon>
    </IconStyle>
    <ListStyle>
    </ListStyle>
    <labelStyle>
       <color>cc7faa55</color>
    </labelStyle>
  </Style>""" % d)

nodes = sorted(nodes, cmp=lambda a, b: cmp(a['name'], b['name']))

for n in nodes:
  n['wname'] = n['name'].decode('utf-8')
  kml.write("""
  <Placemark id="%(pk)s">
    <name>%(wname)s</name>
    <styleUrl>#%(status)s</styleUrl>
    <description>
    <![CDATA[
      Status: %(status)s<br>
      <a href="https://nodes.wlan-si.net/node/%(pk)s/">more information</a>
    ]]>
    </description>
    <Point>
      <coordinates>%(long)s,%(lat)s,0</coordinates>
    </Point>
  </Placemark>""" % n)

ip_to_node = dict(((node['ip'], node) for node in nodes)) 

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km 

for link in links:

  link.update({'lat0': float(ip_to_node[link['src']]['lat']),
               'lon0': float(ip_to_node[link['src']]['long']),
               'lat1': float(ip_to_node[link['dst']]['lat']),
               'lon1': float(ip_to_node[link['dst']]['long']),
               'argb': '8f' + link['color'].lstrip('#'),
               'id': (link['src']+'_to_'+link['dst']).replace('.','_')})

  dist_km = haversine(link['lon0'], link['lat0'],
                      link['lon1'], link['lat1'])

  link['dist'] = dist_km
  link['from'] = ip_to_node[link['src']]
  link['from.pk'] = ip_to_node[link['src']]['pk']
  link['from.name'] = ip_to_node[link['src']]['name']
  link['to.pk'] = ip_to_node[link['dst']]['pk']
  link['to.name'] = ip_to_node[link['dst']]['name']
    
  kml.write("""
  <Placemark>
    <description>
    <![CDATA[
      From: <a href="https://nodes.wlan-si.net/node/%(from.pk)s/">%(from.name)s</a> (%(src)s)<br>
      To: <a href="https://nodes.wlan-si.net/node/%(to.pk)s/">%(to.name)s</a> (%(dst)s)<br>
      Distance: %(dist).2f km<br>
    ]]>
    </description>
      <Style>
        <LineStyle>
          <color>%(argb)s</color>
          <width>4</width>
        </LineStyle>
      </Style>
      <LineString id="%(id)s">
        <coordinates>
          %(lon0)s,%(lat0)s,0
          %(lon1)s,%(lat1)s,0
        </coordinates>
      </LineString>
  </Placemark>""" % link)


kml.write("""
</Document>
</kml>
""")

print kml.getvalue()
