from elasticsearch import Elasticsearch
from typing import List, Dict, Any
import config
from uuid import uuid5, NAMESPACE_DNS
import copy

from modules.rrf import WeightedRRFImplementation

DEFAULT_INDEX_NAME = config.ES_INDEX_NAME

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
            
    def index_document(self, index_name: str, doc_id: str, sn: int, category: str, content: str, embedding: List[float]):
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
            self.es.index(index=index_name, id=uuid, body=document)
        except Exception as e:
            print(f"索引文檔 {name} 時出錯: {e}")
            

    def gen_bm25_query(self, basic_query: Dict[str, Any], bool_query: Dict[str, Any], query_text: str, size: int) -> Dict[str, Any]:
        standard_query = {
            "combined_fields": {
                "query": query_text,
                "fields": ["content"],
                "operator": "or"
            }
        }
        new_bool_query = copy.deepcopy(bool_query)
        new_basic_query = copy.deepcopy(basic_query)

        new_bool_query["bool"]["must"].append(standard_query)
        new_basic_query["query"] = new_bool_query
        return new_basic_query

    
    def gen_knn_query(self, basic_query: Dict[str, Any], bool_query: Dict[str, Any], query_vector: List[float], size: int) -> Dict[str, Any]:
        knn_query = {
            "field": "embedding",
            "query_vector": query_vector,
            "k": size,
            "num_candidates": size*2,
        }

        knn_query['filter'] = bool_query

        new_basic_query = copy.deepcopy(basic_query)
        new_basic_query["knn"] = knn_query
        return new_basic_query


    def hybrid_search(self, query_text: str, query_vector: List[float], size: int, category: str = None, doc_ids: List[str] = [], knn_weight: float = 0.7, index_name: str = DEFAULT_INDEX_NAME) -> List[str]:
        """執行混合搜索"""
        try:
            # 構建基本查詢
            basic_query = {
                "size": size,
                "_source": {"excludes": ["embedding"]},
            }

            bool_query = {"bool": {"must": []}}
            if category:
                bool_query["bool"]["must"].append({"term": {"category": category}})
            if doc_ids:
                bool_query["bool"]["must"].append({"terms": {"doc_id": doc_ids}})
            
            bm25_query = self.gen_bm25_query(basic_query, bool_query, query_text, size)
            knn_query = self.gen_knn_query(basic_query, bool_query, query_vector, size)

            # import json
            # print(f"bm25_query: {json.dumps(bm25_query, ensure_ascii=False)}")
            # print(f"knn_query: {json.dumps(knn_query, ensure_ascii=False)}")

            bm25_response = self.es.search(index=index_name, body=bm25_query)
            knn_response = self.es.search(index=index_name, body=knn_query)

            # print(f"bm25_response: {len(bm25_response['hits']['hits'])}")
            # print(f"knn_response: {len(knn_response['hits']['hits'])}")

            rrf = WeightedRRFImplementation(k=60.0)
            weighted_results = rrf.merge_weighted_elasticsearch_results([(bm25_response, 1-knn_weight), (knn_response, knn_weight)])

            return weighted_results
            
            # return [hit for hit in weighted_results["hits"]["hits"]]
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"混合搜索出錯: {e}")
            return [] 