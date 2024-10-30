curl -XPOST "http://localhost:9200/_reindex?wait_for_completion=false" -H "Content-Type: application/json" -d '{
    "conflicts": "proceed",
    "source":{
      "index": "'$1'"
    },
    "dest":{
      "index": "'$2'"
    }
  }'
