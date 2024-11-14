# RAG 搜索引擎

這個專案實現了一個基於檢索增強生成 (RAG) 的搜索引擎，利用向量搜索和大型語言模型 (LLM) 提供更準確和上下文相關的搜尋結果。它結合了 Elasticsearch 的高效向量搜索和 Azure OpenAI 或 Google Claude 的強大語言模型能力。

## 功能

* **混合搜索:** 結合關鍵字搜索 (BM25) 和向量搜索 (kNN) 以提高檢索準確性。
* **可配置的 LLM:** 支援 Azure OpenAI 和 Google Claude，允許您根據需求選擇不同的 LLM 提供商。
* **重排序:** 使用快速重排序 API 或基於 LLM 的重排序方法進一步優化搜索結果的相關性。
* **分塊索引:** 使用滑动窗口分塊策略，將長文檔分割成更小的塊，提高索引效率和搜索準確性。
* **批量索引:** 支援批量索引文檔，加快索引速度。
* **類別過濾:** 允許根據文檔類別篩選搜索結果。
* **文檔 ID 過濾:** 支援根據文檔 ID 列表篩選搜索結果。
* **互動模式:** 提供一個互動式命令列介面，方便測試和探索搜索引擎的功能。
* **命令列參數:** 提供豐富的命令列參數，方便控制搜索引擎的行為。


## 安裝

1.  **複製程式碼:** 將程式碼複製到您的本地機器。
2.  **建立虛擬環境:** 建議在虛擬環境中安裝依賴項，以避免與其他專案的衝突。

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # 在 Linux/macOS 上
    .venv\Scripts\activate  # 在 Windows 上
    ```
3.  **安裝依賴項:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **設定環境變數:** 將以下環境變數設定為您的 Azure OpenAI 和 Google Cloud  憑證：

    ```bash
    AZURE_OPENAI_API_KEY=<your_azure_openai_api_key>
    AZURE_OPENAI_ENDPOINT=<your_azure_openai_endpoint>
    AZURE_OPENAI_API_VERSION=<your_azure_openai_api_version>
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=<your_azure_openai_embedding_deployment_name>
    AZURE_OPENAI_GPT4_DEPLOYMENT=<your_azure_openai_gpt4_deployment_name>

    GCP_REGION=<your_gcp_region>
    GCP_PROJECT_ID=<your_gcp_project_id>
    GOOGLE_APPLICATION_CREDENTIALS=<path_to_your_gcp_credentials_json_file>
    GCP_SONNET_MODEL=<your_gcp_sonnet_model_name>
    GCP_HAIKU_MODEL=<your_gcp_haiku_model_name>

    ES_HOST=<your_elasticsearch_host> 
    ES_INDEX_NAME=<your_elasticsearch_index_name> # 預設為 "documents"
    ```

## Preprocess

1. 將reference資料夾中的pdf檔案透過[marker](https://github.com/VikParuchuri/marker)和[llama_parse](https://github.com/run-llama/llama_parse)轉換成markdown格式
2. 透過[preprocess/faq.py](./preprocess/faq.py)將reference資料夾中的faq.json轉換成elasticsearch的文件格式
3. 透過[preprocess/insurance.py](./preprocess/insurance.py)將reference資料夾中的insurance資料夾中的文件轉換成elasticsearch的文件格式
4. 透過[preprocess/finance.py](./preprocess/finance.py)將reference資料夾中的finance資料夾中的文件轉換成elasticsearch的文件格式


## 使用方法

### main.py

### 搜尋
```
python main.py --mode search --query "你的問題" --top-k 3 --category "分類" --doc_ids doc1 doc2 --knn-weight 0.8 --rerank-k 5 --llm-provider openai --rerank-mode llm_rerank --use-rerank True 
```

### 僅檢索 (不包含 LLM 回應)
```
python main.py --mode retrieve --query "你的問題" --top-k 5 --category "分類" --doc_ids doc1 doc2 --knn-weight 0.8 --rerank-k 5 --use-rerank True
```

### 互動模式
```
python main.py --mode interactive
```

### 參數說明
```
參數	說明
--mode	運行模式：index, search, retrieve, interactive (預設)
--docs	文檔 JSON 文件路徑 (僅用於 index 模式)
--query	搜索查詢 (用於 search 和 retrieve 模式)
--category	文檔類別過濾
--doc_ids	文檔 ID 列表過濾
--top-k	返回結果數量 (預設: 3)
--rerank-k	重排序候選數量 (預設: 10)
--knn-weight	向量搜索權重 (0-1 之間，預設: 0.7)
--rerank-mode	重排序模式: fast_rerank, llm_rerank (預設: fast_rerank)
--llm-provider	LLM 提供商: openai, claude (預設: openai)
--use-rerank	是否使用重排序 (預設: True)
```

### answer.py

### 產生要求的回答json檔
```
python answer.py 
```

## 參數說明
```
參數    說明
--category 問題類型 (all, finance, insurance, faq)
--num_questions 回答的數量 (預設: 0, 表示全部作答) 
```

## 架構
本專案採用模組化設計，主要包含以下模組：

es_client.py: 負責與 Elasticsearch 互動，執行索引和搜索操作。

llm_client.py: 負責與 LLM 提供商互動，生成回應和重排序。

embedding_client.py: 負責生成文本嵌入向量。

rerank_client.py: 負責對搜索結果進行重排序。

rrf.py: 負責加權RRF計算

main.py: 主程式，包含命令列介面和搜索引擎的主要邏輯。

answer.py: 答題主程式。
