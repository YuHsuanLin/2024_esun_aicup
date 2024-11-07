from typing import List, Dict, Any, Tuple
from collections import defaultdict
import math

class WeightedRRFImplementation:
    def __init__(self, k: float = 60.0):
        """
        初始化加權 RRF 實作
        
        Args:
            k: RRF 公式中的常數，用於調整排名的權重，預設為 60
        """
        self.k = k
    
    def _calculate_rrf_score(self, rank: int, weight: float = 1.0) -> float:
        """
        計算單個項目的加權 RRF 分數
        
        Args:
            rank: 項目在排序結果中的排名（從1開始）
            weight: 這個結果集的權重
            
        Returns:
            float: 加權後的 RRF 分數
        """
        return weight * (1 / (self.k + rank))
    
    def merge_weighted_results(self, ranked_lists_with_weights: List[Tuple[List[Dict[str, Any]], float]]) -> List[Dict[str, Any]]:
        """
        合併多個具有不同權重的排序結果
        
        Args:
            ranked_lists_with_weights: 包含(排序結果,權重)元組的列表
                                     例如: [(bm25_results, 0.3), (knn_results, 0.7)]
        
        Returns:
            List[Dict]: 合併後的排序結果
        """
        rrf_scores = defaultdict(float)
        all_items = {}
        
        # 處理每個排序結果及其權重
        for ranked_list, weight in ranked_lists_with_weights:
            for rank, item in enumerate(ranked_list, 1):  # 排名從1開始
                item_id = str(item.get('_id'))
                if item_id:
                    rrf_score = self._calculate_rrf_score(rank, weight)
                    if rrf_score == 0: continue
                    rrf_scores[item_id] += rrf_score
                    all_items[item_id] = item
        
        # 根據加權 RRF 分數排序
        sorted_items = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 返回排序後的完整項目列表
        return [
            {**all_items[item_id], 'weighted_rrf_score': score}
            for item_id, score in sorted_items
        ]
    
    def merge_weighted_elasticsearch_results(
        self, 
        es_responses_with_weights: List[Tuple[Dict, float]]
    ) -> List[Dict]:
        """
        合併多個具有不同權重的 Elasticsearch 搜尋結果
        
        Args:
            es_responses_with_weights: (ES響應,權重)元組的列表
                                     例如: [(bm25_response, 0.3), (knn_response, 0.7)]
            
        Returns:
            List[Dict]: 合併後的排序結果
        """
        # 將 ES 響應轉換為標準格式
        processed_lists_with_weights = []
        for response, weight in es_responses_with_weights:
            hits = response.get('hits', {}).get('hits', [])
            processed_list = []
            for doc in hits:
                processed_doc = {
                    '_id': doc['_id'],
                    '_score': doc['_score'],
                    '_source': doc['_source']
                }
                processed_list.append(processed_doc)
            processed_lists_with_weights.append((processed_list, weight))
        
        return self.merge_weighted_results(processed_lists_with_weights)

# # 使用範例
# def example_usage():
#     # 初始化
#     rrf = WeightedRRFImplementation(k=60.0)
    
#     # 模擬 BM25 和 KNN 的搜尋結果
#     bm25_results = {
#         'hits': {
#             'hits': [
#                 {'_id': '1', '_score': 1.5, '_source': {'title': 'doc1'}},
#                 {'_id': '2', '_score': 1.3, '_source': {'title': 'doc2'}}
#             ]
#         }
#     }
    
#     knn_results = {
#         'hits': {
#             'hits': [
#                 {'_id': '2', '_score': 0.9, '_source': {'title': 'doc2'}},
#                 {'_id': '3', '_score': 0.8, '_source': {'title': 'doc3'}}
#             ]
#         }
#     }
    
#     # 設定權重：BM25 = 0.3, KNN = 0.7
#     weighted_results = [
#         (bm25_results, 0.3),
#         (knn_results, 0.7)
#     ]
    
#     # 合併結果
#     merged_results = rrf.merge_weighted_elasticsearch_results(weighted_results)
#     return merged_results