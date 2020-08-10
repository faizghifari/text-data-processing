import pandas as pd
import requests

df = pd.read_csv('subjectivity.csv')
text = list(df['text'])
label = list(df['label'])

response = requests.post('http://10.181.131.244:2225/subjectivity',
                         headers={'Content-Type': 'application/json'},
                         json={'texts': text})

response = response.json()

TP = 0
TN = 0
FP = 0
FN = 0

NTP = 0
NTN = 0
NFP = 0
NFN = 0

for idx, l in enumerate(label):
    if l == response[idx]:
        if l == 'NO':
            TN += 1
            NTP += 1
        else:
            TP += 1
            NTN += 1
    else:
        if l == 'NO':
            FP += 1
            NFN += 1
        else:
            FN += 1
            NFP += 1

precision = TP/(TP + FP)
recall = TP/(TP + FN)
nprecision = NTP/(NTP + NFP)
nrecall = NTP/(NTP + NFN)

print(f'TOTAL DOC: {len(label)}\n')

print('YES RESULTS')
print(f'Accuracy: {(TP + TN)/(TP + TN + FP + FN)}')
print(f'Precision: {precision}')
print(f'Recall: {recall}')
print(f'F1-Score: {2 * precision * recall/(precision + recall)}')

print('NO RESULTS')
print(f'Accuracy: {(NTP + NTN)/(NTP + NTN + NFP + NFN)}')
print(f'Precision: {nprecision}')
print(f'Recall: {nrecall}')
print(f'F1-Score: {2 * nprecision * nrecall/(nprecision + nrecall)}')