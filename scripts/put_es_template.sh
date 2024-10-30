#!/bin/sh
curl -XPUT 'http://localhost:9200/_template/documents' -H "Content-Type: application/json" -d '{
  "index_patterns": ["documents*"],
  "order": 1,
  "mappings": {
    "properties": {
      "doc_id": {"type": "keyword"},
      "sn": {"type": "integer"},
      "category": {"type": "keyword"},
      "content": {
        "type": "text",
	"search_analyzer": "cjk_bigram_search_analyzer",
	"analyzer": "cjk_bigram_analyzer"
      },
      "embedding": {"type": "dense_vector", "dims": 1536}
    } 
  },
  "settings": {
    "number_of_replicas" : 0,
    "analysis": {
      "filter":{
        "han_bigram_filter_with_unigram":{
          "type": "cjk_bigram",
          "output_unigrams": true
        },
        "han_bigram_filter":{
          "type": "cjk_bigram"
        }
      },
      "analyzer": {
        "cjk_bigram_analyzer":{
          "type": "custom",
          "tokenizer": "standard",
          "char_filter": [],
          "filter": ["cjk_width","lowercase","han_bigram_filter_with_unigram"]
        },
        "cjk_bigram_search_analyzer":{
          "type": "custom",
          "tokenizer": "standard",
          "char_filter": [],
          "filter": ["cjk_width","lowercase","han_bigram_filter"]
        }
      }
    } 
  }
}' 
