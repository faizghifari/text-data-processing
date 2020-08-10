import csv
import ast
import argparse
import pandas as pd

tags = {}
tags['c'] = ['O', 'I-CONCEPT', 'B-CONCEPT']
tags['s'] = ['O', 'I-SENT', 'B-SENT']
tags['s-v2'] = ['O', 'I-POS', 'B-POS', 'I-NEG', 'B-NEG']
tags['c-v2'] = ['O', 'I-CMAIN', 'B-CMAIN', 'I-CDER', 'B-CDER']
tags['cs'] = ['O', 'I-CONCEPT', 'B-CONCEPT', 'I-SENT', 'B-SENT']
tags['sug'] = ['O', 'I-SUG', 'B-SUG']
tags['reason'] = ['O', 'I-REASON', 'B-REASON']

file_open = 'result/reason-train.csv'
file_target = 'result/reason-train.tsv'

df = pd.read_csv(file_open)

parser = argparse.ArgumentParser()
parser.add_argument('--type', type=str, required=True, help='c / cs / csw / csw-v2')

FLAGS, _ = parser.parse_known_args()

with open(file_target, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    used_tags = tags[FLAGS.type]
    count_token = [0] * len(used_tags)
    for _, row in df.iterrows():
        split_sentence = row[0].split()
        labels = ast.literal_eval(row[1])
        if len(split_sentence) == len(labels):
            for idx, word in enumerate(split_sentence):
                writer.writerow([word, used_tags[labels[idx]]])
                count_token[labels[idx]] += 1
        else:
            print(f'SENTENCE: {split_sentence}')
            print(f'LEN SENTENCE: {len(split_sentence)}')
            print(f'LABELS: {labels}')
            print(f'LEN LABELS: {len(labels)}')
            raise TypeError('Token Labels are not match with sentence')
        
        writer.writerow([])
    
    f.close()
    print(f'Token detail: {count_token}')
    print(f'result save to {file_target}')