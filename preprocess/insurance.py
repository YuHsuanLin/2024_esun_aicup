from llama_index.core.node_parser import (
    MarkdownElementNodeParser,
    MarkdownNodeParser,
)
from llama_index.core import Document

from main import SearchEngine
from .utils import read_md, clean_text

insurance_folder = './reference/insurance/output'

def main():
    category = 'insurance'
    engine = SearchEngine()
    insurance_subfolders = os.listdir(insurance_folder)
    for subfolder in insurance_subfolders:
        content = read_md(insurance_folder, subfolder)
        document = Document(text = content)
        parser = MarkdownNodeParser(include_metadata = False, include_prev_next_rel = False)
        nodes = parser.get_nodes_from_documents([document])
        docs = []
        for sn, node in enumerate(nodes):
            docs.append({
                'id': subfolder,
                'sn': sn,
                'category': category,
                'text': clean_text(node.text),
            })
        engine.index_documents(docs)
        print(f'{subfolder} done.')

if __name__ == '__main__':
    main()