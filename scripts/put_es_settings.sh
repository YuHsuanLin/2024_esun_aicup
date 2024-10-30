#!/bin/sh

curl -XPUT 'http://localhost:9200/documents/_settings' -H "Content-Type: application/json" -d '{
  "index" : {
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
