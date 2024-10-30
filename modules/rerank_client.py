from abc import ABC, abstractmethod
import requests
from typing import List, Dict
import time

from modules.llm_client import LLMClient

from llama_index.core.prompts.default_prompts import (
    DEFAULT_CHOICE_SELECT_PROMPT,
    DEFAULT_CHOICE_SELECT_PROMPT_TMPL,
)
from llama_index.core.schema import TextNode
from llama_index.core.indices.utils import (
    default_format_node_batch_fn,
    default_parse_choice_select_answer_fn,
)


def RerankClient(mode = 'fast_rerank'):
    print(f"目前使用的重排序模式: {mode}")
    if mode == 'fast_rerank':
        return FastRerankClient()
    elif mode == 'llm_rerank':
        return LLMRerankClient()
    else:
        raise ValueError(f"不支持的重排序模式: {mode}")

class BaseRerankClient(ABC):
    """重排序客戶端的基礎類"""
    
    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int = 3,
        **kwargs
    ) -> List[Dict]:
        """重新排序搜索結果的抽象方法"""
        pass


class LLMRerankClient(BaseRerankClient):
    def __init__(self, llm_provider: str = "openai"):
        self.llm_client = LLMClient(provider=llm_provider)
        
    def rerank(self, query: str, candidates: List[Dict], top_k: int = 3, **kwargs) -> List[Dict]:
        try:
            print(f"  - 準備使用 LLM 重排序 {len(candidates)} 個文檔...")
            
            nodes = []
            for candidate in candidates:
                nodes.append(TextNode(text=candidate["content"]))
            print("  - 已將候選文檔轉換為 TextNode")

            context_str = default_format_node_batch_fn(nodes)
            variable_dict = {
                'context_str': context_str,
                'query_str': query,
            }
            prompt = DEFAULT_CHOICE_SELECT_PROMPT_TMPL.format(**variable_dict)
            prompt_prefix = 'Please only respond with the requested format, without additional explanations or clarifications.\n\n'
            print("  - 已生成重排序 prompt")

            print("  - 正在調用 LLM 進行重排序...")
            raw_response = self.llm_client.generate_rerank_response(f'{prompt_prefix}{prompt}')
            print("  - 已獲得 LLM 響應")

            raw_choices, relevances = default_parse_choice_select_answer_fn(raw_response, len(nodes))
            choice_idxs = [int(choice) - 1 for choice in raw_choices]
            # choice_nodes = [nodes[idx] for idx in choice_idxs]
            # relevances = relevances or [1.0 for _ in choice_nodes]
            print(f"  - 解析結果: 選擇了 {len(choice_idxs)} 個文檔")

            result = [candidates[int(idx)] for idx in choice_idxs[:top_k]]
            print(f"  ✓ 重排序完成，返回前 {top_k} 個結果")
            return result

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  ❌ 重排序時出錯: {e}")
            return candidates[:top_k]


class FastRerankClient(BaseRerankClient):
    def __init__(self):
        self.api_url = "https://reranker.dhr.wtf/rerank"
        
    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int = 3,
        mode: str = "ai"
    ) -> List[Dict]:
        """重新排序搜索結果"""
        try:
            print(f"  - 準備重排序 {len(candidates)} 個文檔...")
            
            items = [
                {"id": str(i), "content": doc.get('content')}
                for i, doc in enumerate(candidates)
            ]
            
            payload = {
                "query": query,
                "items": items,
                "mode": mode
            }
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"  - 調用rerank API ({mode} 模式)... 嘗試 {attempt + 1}/{max_retries}")
                    response = requests.post(
                        self.api_url,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        reranked_items = result["items"]
                        sorted_items = sorted(
                            reranked_items,
                            key=lambda x: x["finalScore"],
                            reverse=True
                        )
                        
                        print(f"  ✓ 重排序完成")
                        return [candidates[int(item["id"])] for item in sorted_items[:top_k]]
                        
                    print(f"  ❌ Rerank API 調用失敗: {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # 重試前等待2秒
                        continue
                        
                except Exception as e:
                    print(f"  ❌ 重排序時出錯: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                        
            print(f"  ❌ 重試{max_retries}次後仍然失敗, 使用備案LLM重排序")
            return LLMRerankClient(llm_provider='claude').rerank(query, candidates, top_k)
            # return candidates[:top_k]

        except Exception as e:
            print(f"  ❌ 重排序時出錯: {e}")
            return candidates[:top_k] 