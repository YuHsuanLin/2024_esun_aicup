import json

def calculate_accuracy(ground_truth_file, prediction_file):
    # 讀取檔案
    with open(ground_truth_file, 'r') as f:
        ground_truths = json.load(f)['ground_truths']
    
    with open(prediction_file, 'r') as f:
        predictions = json.load(f)['answers']
    
    # 轉換成字典格式以便查詢
    gt_dict = {item['qid']: int(item['retrieve']) for item in ground_truths}
    pred_dict = {item['qid']: int(item['retrieve']) for item in predictions}  # 轉換字串為整數
    
    # 計算正確數量
    correct = 0
    total = len(ground_truths)
    
    for qid in gt_dict:
        if gt_dict[qid] == pred_dict[qid]:
            correct += 1
    
    # 計算正確率
    accuracy = correct / total
    
    return {
        'correct': correct,
        'total': total,
        'accuracy': accuracy
    }

# 計算正確率
result = calculate_accuracy('dataset/preliminary/ground_truths_example.json', 
                          'output/pred_retrieve.json')

print(f"正確數量: {result['correct']}")
print(f"總數量: {result['total']}")
print(f"正確率: {result['accuracy']:.2%}")

# 也可以依照類別計算正確率
def calculate_accuracy_by_category(ground_truth_file, prediction_file):
    # 讀取檔案
    with open(ground_truth_file, 'r') as f:
        ground_truths = json.load(f)['ground_truths']
    
    with open(prediction_file, 'r') as f:
        predictions = json.load(f)['answers']
    
    # 轉換成字典格式
    pred_dict = {item['qid']: int(item['retrieve']) for item in predictions}
    
    # 依類別統計
    categories = {}
    
    for gt in ground_truths:
        category = gt['category']
        if category not in categories:
            categories[category] = {
                'correct': 0, 
                'total': 0,
                'wrong_qids': []  # 新增錯誤qid列表
            }
        
        categories[category]['total'] += 1
        if gt['retrieve'] == pred_dict[gt['qid']]:
            categories[category]['correct'] += 1
        else:
            categories[category]['wrong_qids'].append(gt['qid'])  # 記錄錯誤的qid
    
    # 計算每個類別的正確率
    for category in categories:
        categories[category]['accuracy'] = categories[category]['correct'] / categories[category]['total']
    
    return categories

# 計算各類別正確率
category_results = calculate_accuracy_by_category('dataset/preliminary/ground_truths_example.json',
                                                'output/pred_retrieve.json')

print("\n各類別正確率:")
for category, result in category_results.items():
    print(f"{category}:")
    print(f"  正確數量: {result['correct']}")
    print(f"  總數量: {result['total']}")
    print(f"  正確率: {result['accuracy']:.2%}")
    print(f"  錯誤的QID: {result['wrong_qids']}")  # 新增輸出錯誤的QID列表
