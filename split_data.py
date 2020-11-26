import ast
import pandas as pd

from sklearn.model_selection import train_test_split

# aspects = pd.read_csv('result/aspect/aspect-test.csv')
# targets = pd.read_csv('result/target/target-test.csv')
# objects = pd.read_csv('result/object/object-test.csv')

# tests = []
# tests.extend(aspects['text_a'].tolist())
# tests.extend(targets['text_a'].tolist())
# tests.extend(objects['text_a'].tolist())

# test_df = pd.DataFrame(columns=['text_a', 'label'])
# train_df = pd.DataFrame(columns=['text_a', 'label'])

data = pd.read_csv('result/rel-all-kemendikbud.csv')

# for i, row in data.iterrows():
#     if row['text_a'] in tests:
#         test_df = test_df.append(row)
#     else:
#         train_df = train_df.append(row)

train_df, test_df = train_test_split(data, test_size=500)

train_df.to_csv('result/rel-all-kemendikbud-train.csv', index=False)
test_df.to_csv('result/rel-all-kemendikbud-test.csv', index=False)