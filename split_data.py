import ast
import pandas as pd

from sklearn.model_selection import train_test_split

data = pd.read_csv('result/cs-ku.csv')

train, test = train_test_split(data, test_size=0.1)

train.to_csv('result/cs-ku-train.csv', index=False)
test.to_csv('result/cs-ku-c-test.csv', index=False)