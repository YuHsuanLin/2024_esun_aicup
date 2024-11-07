import os

# Azure OpenAI 設置
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_GPT4_DEPLOYMENT = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT")

GCP_REGION = os.getenv("GCP_REGION")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_SONNET_MODEL = os.getenv("GCP_SONNET_MODEL")
GCP_HAIKU_MODEL = os.getenv("GCP_HAIKU_MODEL")
# Elasticsearch 設置
ES_HOST = os.getenv("ES_HOST")
ES_INDEX_NAME = os.getenv("ES_INDEX_NAME")