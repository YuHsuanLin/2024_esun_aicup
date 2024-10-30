#!/bin/sh
docker pull elasticsearch:8.15.3

docker network create elastic

docker run -d \
  --name elasticsearch \
  --net elastic \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -v elasticsearch-data:/usr/share/elasticsearch/data \
  elasticsearch:8.15.3
