import pandas as pd

file_input = "result/polpos-ku-only.csv"
file_output = "ku-only.csv"

df = pd.read_csv(file_input)
neutral = df.loc[df.label == 0]
negative = df.loc[df.label == -1]
positive = df.loc[df.label == 1]

df_pol = pd.concat([negative, positive, neutral])
df_pol["label"].loc[df_pol.label != 0] = 1

df_pos = pd.concat([negative, positive])
df_pos["label"].loc[df_pos.label == -1] = 0

df_pol.to_csv("result/polarity-" + file_output, index=False)
df_pos.to_csv("result/posneg-" + file_output, index=False)