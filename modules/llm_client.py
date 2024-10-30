from openai import AzureOpenAI
from anthropic import AnthropicVertex
import config

class LLMClient:
    def __init__(self, provider="openai", temperature=0.3, max_tokens=4096):
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        print(f"目前使用的provider: {self.provider}")
        if provider == "openai":
            self.client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
        elif provider == "claude":
            self.client = AnthropicVertex(
                region=config.GCP_REGION,
                project_id=config.GCP_PROJECT_ID,
            )
        else:
            raise ValueError("不支援的 LLM 提供者。目前支援: openai, claude")

    def generate_response(self, query: str, context: str) -> str:
        """根據選擇的 LLM 提供者生成回應"""
        try:
            if self.provider == "openai":
                return self._generate_azure_response(query, context)
            else:
                return self._generate_claude_response(query, context)
            
        except Exception as e:
            print(f"生成回應時出錯: {e}")
            return "抱歉，生成回應時發生錯誤。"
            
    def _generate_azure_response(self, query: str, context: str) -> str:
        messages = [
            {"role": "system", "content": "你是一個專業的助手，請根據提供的上下文來回答問題。如果上下文中沒有相關信息，請誠實說明。"},
            {"role": "user", "content": f"上下文：{context}\n\n問題：{query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=config.AZURE_OPENAI_GPT4_DEPLOYMENT,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content
        
    def _generate_claude_response(self, query: str, context: str) -> str:
        message = self.client.messages.create(
            model=config.GCP_SONNET_MODEL,
            max_tokens=self.max_tokens, 
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": f"你是一個專業的助手，請根據提供的上下文來回答問題。如果上下文中沒有相關信息，請誠實說明。上下文：{context}\n\n問題：{query}"
                }
            ]
        )
        return message.content[0].text

    def generate_rerank_response(self, prompt: str) -> str:
        try:
            if self.provider == "openai":
                return self._generate_azure_rerank_response(prompt)
            else:
                return self._generate_claude_rerank_response(prompt)
            
        except Exception as e:
            print(f"生成回應時出錯: {e}")
            return "抱歉，生成回應時發生錯誤。"

    def _generate_azure_rerank_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=config.AZURE_OPENAI_GPT4_DEPLOYMENT,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content

    def _generate_claude_rerank_response(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=config.GCP_SONNET_MODEL,
            max_tokens=self.max_tokens, 
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return message.content[0].text