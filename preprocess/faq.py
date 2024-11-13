from main import SearchEngine
import json
import os

FAQ_JSON_FILE = './reference/faq/pid_map_content.json'

def main():
    with open(FAQ_JSON_FILE, 'r') as f:
        json_data = json.load(f)

    engine = SearchEngine()
    documents = []
    category = 'faq'

    keys = list(json_data.keys())
    for key in keys:
        questions = json_data[key]
        sn = 0
        for idx, i in enumerate(questions, start = 0):
            answers = i.get('answers', [])
            for answer in answers:
                text = f'{i.get("question")}\n{answer}'
                documents.append({
                    'id': key,
                    'sn': sn,
                    'category': category,
                    'text': text,
                })
                sn +=1

    engine.index_documents(documents, use_chunk=False)

if __name__ == '__main__':
    main()