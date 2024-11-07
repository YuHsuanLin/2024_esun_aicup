import json
import pandas as pd
from main import SearchEngine
import config
import argparse

class AnswerGenerator:
    def __init__(self):
        self.es_index_name = config.ES_INDEX_NAME
        self.engine = SearchEngine(
            llm_provider='openai',
            rerank_mode='llm_rerank',
            index_name=self.es_index_name
        )
        self.categories = ['insurance', 'finance', 'faq']
        
        # 為不同 category 設定不同的檢索參數
        self.retrieve_params = {
            'faq': {
                'top_k': 1,
                'knn_weight': 1,
                'use_rerank': True
            },
            'finance': {
                'top_k': 1,
                'knn_weight': 0.7,
                'use_rerank': True
            },
            'insurance': {
                'top_k': 1,
                'knn_weight': 1,
                'use_rerank': True
            }
        }
    
    def load_data(self, ground_truth_path, questions_path):
        with open(ground_truth_path, 'r') as f:
            ground_truth_json_data = json.load(f)
        
        with open(questions_path, 'r') as f:
            questions_json_data = json.load(f)
            
        self.ground_truth_df = pd.DataFrame(ground_truth_json_data.get('ground_truths'))
        self.question_df = pd.DataFrame(questions_json_data.get('questions'))
    
    def generate_answers(self, category, num_questions=0):
        if category not in self.categories:
            raise ValueError(f"Category must be one of {self.categories}")
            
        cat_questions = self.question_df[self.question_df['category'] == category].to_dict('records')
        answers = []
        
        # 獲取該 category 的檢索參數
        params = self.retrieve_params[category]
        
        cat_questions_ = cat_questions[:num_questions] if num_questions > 0 else cat_questions
        for question in cat_questions_:
            qid = question.get('qid')
            query = question.get('query')
            source = question.get('source', [])
            doc_ids = [str(i) for i in source]
            
            relevant_docs = self.engine.retrieve(
                query,
                category=category,
                doc_ids=doc_ids,
                **params  # 使用該 category 的特定參數
            )
            print(qid, relevant_docs[0])
            
            answers.append({
                'qid': int(qid),
                'retrieve': int(relevant_docs[0].get('id')),
            })
        return answers
    
    def generate_all_answers(self, num_questions=0):
        """
        為所有類別生成答案
        
        Args:
            num_questions_per_category (int): 每個類別要處理的問題數量
            
        Returns:
            list: 所有類別的答案列表
        """
        all_answers = []
        
        for category in self.categories:
            print(f"\nProcessing category: {category}")
            category_answers = self.generate_answers(
                category=category,
                num_questions=num_questions
            )
            all_answers.extend(category_answers)
            
        return all_answers
 
    def save_answers(self, answers, output_path='./output/pred_retrieve.json'):
        with open(output_path, 'w') as f:
            json.dump({'answers': answers}, f, indent=2, ensure_ascii=False)
    

def main():
    parser = argparse.ArgumentParser(description='Generate answers for questions')
    parser.add_argument('--category', type=str, choices=['all', 'insurance', 'finance', 'faq'],
                       default='all', help='Category to process (default: all)')
    parser.add_argument('--num_questions', type=int, default=0,
                       help='Number of questions to process per category (default: 0 for all questions)')
    args = parser.parse_args()
    
    generator = AnswerGenerator()
    
    # 設定檔案路徑
    ground_truth_path = './dataset/preliminary/ground_truths_example.json'
    questions_path = './dataset/preliminary/questions_example.json'
    
    # 載入資料
    generator.load_data(ground_truth_path, questions_path)
    
    # 根據參數選擇處理方式
    if args.category == 'all':
        answers = generator.generate_all_answers(num_questions=args.num_questions)
    else:
        answers = generator.generate_answers(category=args.category, num_questions=args.num_questions)
    
    # 儲存結果
    generator.save_answers(answers)

if __name__ == '__main__':
    main()
