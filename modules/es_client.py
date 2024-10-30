from elasticsearch import Elasticsearch
from typing import List, Dict, Any
import config
from uuid import uuid5, NAMESPACE_DNS

class ElasticsearchClient:
    def __init__(self):
        self.es = Elasticsearch(config.ES_HOST)
        
    # def create_index_mapping(self):
    #     """創建Elasticsearch索引映射"""
    #     try:
    #         mapping = {
    #             "mappings": {
    #                 "properties": {
    #                     "doc_id": {"type": "keyword"},
    #                     "sn": {"type": "integer"},
    #                     "category": {"type": "keyword"},
    #                     "content": {"type": "text"},
    #                     "embedding": {"type": "dense_vector", "dims": 1536}
    #                 }
    #             }
    #         }
            
    #         if not self.es.indices.exists(index="documents"):
    #             self.es.indices.create(index="documents", body=mapping)
    #             print("索引創建成功")
    #     except Exception as e:
    #         print(f"創建索引映射時出錯: {e}")
            
    def index_document(self, doc_id: str, sn: int, category: str, content: str, embedding: List[float]):
        """索引單個文檔"""
        try:
            document = {
                'doc_id': doc_id,
                'sn': sn,
                'category': category,
                'content': content,
                'embedding': embedding
            }
            name = f"{category}_{doc_id}_{sn}"
            uuid = str(uuid5(NAMESPACE_DNS, name))
            self.es.index(index="documents", id=uuid, body=document)
        except Exception as e:
            print(f"索引文檔 {name} 時出錯: {e}")
            
    def hybrid_search(self, query_text: str, query_vector: List[float], size: int, category: str = None, knn_weight: float = 0.7) -> List[str]:
        """執行混合搜索"""
        try:
            # 構建基本查詢
            hybrid_query = {
                "size": size,
                "query": {
                    "combined_fields": {
                        "query": query_text,
                        "fields": ["content"],
                        "operator": "or",
                        "boost": 1 - knn_weight
                    }
                },
                "knn": {
                    "field": "embedding",
                    "query_vector": query_vector,
                    "k": size,
                    "num_candidates": size * 2,
                    "boost": knn_weight
                }
            }
            
            # 如果指定了 category，添加過濾條件
            if category:
                hybrid_query["query"] = {
                    "bool": {
                        "must": [
                            hybrid_query["query"],
                            {"term": {"category": category}}
                        ]
                    }
                }
            
            response = self.es.search(index="documents", body=hybrid_query)
            return [hit for hit in response["hits"]["hits"]]
            
        except Exception as e:
            print(f"混合搜索出錯: {e}")
            return [] 