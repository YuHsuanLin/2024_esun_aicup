from modules.es_client import ElasticsearchClient
from modules.llm_client import LLMClient
from modules.embedding_client import EmbeddingClient
from modules.rerank_client import RerankClient

from llama_index.core.node_parser import SentenceSplitter

from typing import List, Optional, Dict
import argparse
import time
import json
import sys

from config import ES_INDEX_NAME as DEFAULT_INDEX_NAME

class SearchEngine:
    def __init__(self, llm_provider: str = "openai", rerank_mode: str = 'fast_rerank', index_name: str = DEFAULT_INDEX_NAME):
        print("初始化搜索引擎組件...")
        try:
            self.es_client = ElasticsearchClient()
            self.llm_client = LLMClient(provider=llm_provider)
            self.embedding_client = EmbeddingClient()
            self.rerank_client = RerankClient(mode=rerank_mode, llm_provider=llm_provider)
            self.index_name = index_name
            print("✓ 所有組件初始化完成")
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
            raise

    def index_documents(self, documents: List[Dict], batch_size: int = 5, chunk_size: int = 512, chunk_overlap: int = 50, use_chunk: bool = True) -> None:
        """批量索引文檔，支持滑动窗口分块"""
        """
        documents = [
            {'id': '1', 'text': '這是第一個文檔', 'category': 'category1'},
            {'id': '2', 'text': '這是第二個文檔', 'category': 'category2'},
            {'id': '3', 'text': '這是第三個文檔', 'category': 'category3'},
        ]
        """

        total = len(documents)
        print(f"\n開始索引 {total} 個文檔...")

        splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        for idx, doc in enumerate(documents):
            try:
                
                # 使用滑动窗口分块文档
                text = doc.get('text')
                category = doc.get('category')
                doc_id = doc.get('id')

                print(f"[{idx}/{total}] 處理文檔...")

                if use_chunk:    
                    chunks = splitter.split_text(text)
                    for chunk_index, chunk in enumerate(chunks):
                        embeddings = self.embedding_client.get_embedding(chunk)
                        # 將 doc_id 轉為字符串，chunk_index 作為 sn
                        self.es_client.index_document(
                            doc_id=str(doc_id),
                            sn=chunk_index,
                            category=category,
                            content=chunk,
                            embedding=embeddings,
                            index_name=self.index_name,
                        )
                else:
                    sn = doc.get('sn', 0)
                    embeddings = self.embedding_client.get_embedding(text)
                    self.es_client.index_document(
                        doc_id=str(doc_id),
                        sn=sn,
                        category=category,
                        content=text,
                        embedding=embeddings,
                        index_name=self.index_name,
                    )

                print(f"✓ 已完成 {idx}/{total} 個文檔的索引")
                # time.sleep(0.5)  # 避免超過API限制
                
            except Exception as e:
                print(f"❌ 索引文檔 {doc_id} 時出錯: {e}")
                
        print(f"\n✓ 索引完成，共處理 {total} 個文檔")

    def retrieve(
        self,
        query: str,
        category: str = None,
        doc_ids: List[str] = [],
        top_k: int = 3,
        knn_weight: float = 0.7,
        rerank_k: int = 10,
        use_rerank: bool = True,  # 新增參數
    ) -> List[str]:
        """執行搜索流程"""
        try:
            print(f"\n[1/4] 開始混合搜索流程 - 查詢: '{query}'")
            
            print(f"[2/4] 生成查詢的嵌入向量...")
            query_vector = self.embedding_client.get_embedding(query)
            
            search_size = rerank_k if use_rerank else top_k
            print(f"[3/4] 執行Elasticsearch混合搜索 (檢索 {search_size} 個候選文檔)...")
            candidates = self.es_client.hybrid_search(query, query_vector, search_size, category, doc_ids, knn_weight, index_name = self.index_name)
            
            if not candidates:
                print("❌ 未找到相關文檔")
                return []
                
            print(f"✓ 找到 {len(candidates)} 個候選文檔")
            
            if use_rerank:
                print(f"[4/4] 重新排序結果...")
                candidates_content = [
                    {
                        'id': candidate.get('_source', {}).get('doc_id'),
                        'content': candidate.get('_source', {}).get('content')
                    } for candidate in candidates
                ]

                results = self.rerank_client.rerank(
                    query,
                    candidates_content,
                    top_k=top_k,
                )
                print(f"✓ 完成重排序，返回前 {top_k} 個結果")
            else:
                print("[4/4] 跳過重排序步驟...")
                results = [
                    {
                        'id': candidate.get('_source', {}).get('doc_id'),
                        'content': candidate.get('_source', {}).get('content')
                    } for candidate in candidates[:top_k]
                ]
                print(f"✓ 直接返回前 {top_k} 個結果")
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索過程出錯: {e}")
            return []

    def generate_response(self, query: str, context: str, doc_ids: List[str]) -> str:
        """生成回應"""
        return {
            'response': self.llm_client.generate_response(query, context),
            'retrieved_docs': doc_ids,
        }

def load_documents(file_path: str) -> List[str]:
    """從文件加載文檔"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 讀取文檔文件時出錯: {e}")
        return []

def setup_argparse() -> argparse.ArgumentParser:
    """設置命令行參數"""
    parser = argparse.ArgumentParser(
        description='RAG 搜索引擎 - 一個基於向量搜索和語言模型的檢索增強系統',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 索引文檔
  python main.py --mode index --docs documents.json
  
  # 搜索模式（包含 LLM 回應）
  python main.py --mode search --query "你的問題" --top-k 3
  
  # 僅檢索模式
  python main.py --mode retrieve --query "你的問題" --category "分類" --top-k 5
  
  # 互動模式
  python main.py --mode interactive
        """
    )
    
    # 運行模式參數組
    mode_group = parser.add_argument_group('運行模式')
    mode_group.add_argument('--mode', choices=['index', 'retrieve', 'search', 'interactive'],
                           default='interactive', help='運行模式 (預設: interactive)')
    mode_group.add_argument('--docs', type=str, help='文檔JSON文件路徑 (僅用於 index 模式)')
    mode_group.add_argument('--query', type=str, help='搜索查詢 (用於 search 和 retrieve 模式)')
    
    # 搜索參數組
    search_group = parser.add_argument_group('搜索參數')
    search_group.add_argument('--category', type=str, default=None, help='文檔類別過濾 (可選)')
    search_group.add_argument('--doc_ids', type=str, nargs='+', default=None, help='文檔ID列表過濾 (可選)')
    search_group.add_argument('--top-k', type=int, default=3, help='返回結果數量 (預設: 3)')
    search_group.add_argument('--rerank-k', type=int, default=10, help='重排序候選數量 (預設: 10)')
    search_group.add_argument('--knn-weight', type=float, default=0.7, 
                            help='向量搜索權重 (0-1之間，預設: 0.7)')
    
    # 模型參數組
    model_group = parser.add_argument_group('模型參數')
    model_group.add_argument('--rerank-mode', choices=['fast_rerank', 'llm_rerank'], default='llm_rerank',
                           help='重排序模式 (預設: fast_rerank)')
    model_group.add_argument('--llm-provider', type=str, default='openai',
                           choices=['openai', 'claude'],
                           help='LLM 提供商 (預設: openai)')
    model_group.add_argument('--use-rerank', type=bool, default=True,
                           help='是否使用重排序 (預設: True)')

    return parser

def interactive_mode(engine: SearchEngine):
    """互動模式"""
    print("\n=== 進入互動模式 ===")
    print("輸入 'quit' 或 'exit' 退出")
    
    while True:
        try:
            query = input("\n請輸入您的問題: ").strip()
            category = input("請輸入文檔類別: ").strip()
            doc_ids = input("請輸入文檔ID列表 (用逗號分隔): ").strip().split(',')
            knn_weight = float(input("請輸入向量搜索權重 (0-1之間): "))
            top_k = int(input("請輸入返回結果數量: "))
            
            if query.lower() in ['quit', 'exit']:
                print("謝謝使用，再見！")
                break
                
            if not query:
                continue
                
            relevant_docs = engine.retrieve(
                query,
                top_k=top_k,
                rerank_k = 10,
                category=category,
                doc_ids=doc_ids,
                knn_weight=knn_weight,
                use_rerank=True,
            )
            
            if relevant_docs:
                print("\n📚 找到的相關文檔:")
                for i, doc in enumerate(relevant_docs, 1):
                    print(f"{i}. {doc}")
                
                context = " ".join([doc.get('content') for doc in relevant_docs])
                doc_ids = [doc.get('id') for doc in relevant_docs]

                print("\n🤖 生成回應中...")
                response = engine.generate_response(query, context, doc_ids)
                print(f"\n回應: {response}")
            else:
                print("\n❌ 未找到相關文檔")
                
        except KeyboardInterrupt:
            print("\n\n再見！")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

def main():
    parser = setup_argparse()
    args = parser.parse_args()
    
    try:
        engine = SearchEngine(llm_provider=args.llm_provider, rerank_mode=args.rerank_mode)
        
        if args.mode == 'index':
            if not args.docs:
                print("❌ 請提供文檔文件路徑")
                return
            documents = load_documents(args.docs)
            if documents:
                engine.es_client.create_index_mapping()
                engine.index_documents(documents)
                
        elif args.mode == 'search':
            if not args.query:
                print("❌ 請提供搜索查詢")
                return
            relevant_docs = engine.retrieve(
                args.query,
                top_k=args.top_k,
                rerank_k=args.rerank_k,
                category=args.category,
                doc_ids=args.doc_ids,
                knn_weight=args.knn_weight,
                use_rerank=args.use_rerank,
            )
            if relevant_docs:
                print("\n📚 找到的相關文檔:")
                for i, doc in enumerate(relevant_docs, 1):
                    print(f"{i}. {doc.get('content')}")
                    
                context = " ".join([doc.get('content') for doc in relevant_docs])
                doc_ids = [doc.get('id') for doc in relevant_docs]
                print("\n🤖 生成回應中...")
                response = engine.generate_response(args.query, context, doc_ids)
                print(f"\n回應: {response}")

        elif args.mode == 'retrieve':
            if not args.query:
                print("❌ 請提供搜索查詢")
                return

            print(f"args: {args}")
            relevant_docs = engine.retrieve(
                args.query,
                top_k=args.top_k,
                rerank_k=args.rerank_k,
                category=args.category,
                doc_ids=args.doc_ids,
                knn_weight=args.knn_weight,
                use_rerank=args.use_rerank,
            )

            print(f"\n📚 找到的相關文檔:")
            for i, doc in enumerate(relevant_docs, 1):
                print(f"{i}. {doc.get('content')}")
                
        else:  # interactive mode
            interactive_mode(engine)
            
    except KeyboardInterrupt:
        print("\n\n程序被中斷")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序執行出錯: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()