import re
import os

from llama_index.core.node_parser import (
    MarkdownElementNodeParser,
)
from llama_index.core import Document

from main import SearchEngine
from modules.llm_client import LLMClient
from .utils import read_md, clean_text

finance_folder = './reference/finance/output'

def main():
    category = 'finance'
    engine = SearchEngine()
    llm = LLMClient(provider = 'claude')
    finance_subfolders = os.listdir(finance_folder)
    for subfolder in finance_subfolders:
        content = read_md(finance_folder, subfolder)
        document = Document(text = content)
        parser = MarkdownElementNodeParser()
        elements = parser.extract_elements(document)
    
        simple_summary = llm.generate_simple_summary(content)
        
        docs = []
        for sn, element in enumerate(elements):
            if element.type in ("table", "table_text"):
                table_text = element.element  
                table_summary = llm.generate_table_summary(table_text)
                text = f'{table_summary}\n Table: {table_text}'
            else:
                text = clean_text(element.element)
        
            docs.append({
                'id': subfolder,
                'sn': sn,
                'category': category,
                'text': f'全文摘要:{simple_summary}\n\n段落內容:{text}',
            })

        engine.index_documents(docs)
        print(f'{subfolder} done.')

if __name__ == '__main__':
    main()