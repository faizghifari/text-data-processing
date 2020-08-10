import pandas as pd
import ast

file_target = 'result/batch 4/c-bert/covid-c-ku-train.csv'

df = pd.read_csv(file_target)

count_o = 0
count_all = 0
count_b = 0
count_i = 0
for _, row in df.iterrows():
    labels = ast.literal_eval(row[1])
    count_all += len(labels)
    for l in labels:
        if l == 0:
            count_o += 1
        elif l == 1:
            count_i += 1
        elif l == 2:
            count_b += 1

print(f'c_all: {count_all}')
print(f'c_o: {count_o}')
print(f'c_i: {count_i}')
print(f'c_b: {count_b}')
