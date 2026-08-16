import pandas as pd

df = pd.read_csv('cases.csv')
print('Shape:', df.shape)
print('Columns:', list(df.columns))
print('Case IDs:', df.iloc[:,0].tolist())
print('Unique case_ids:', df.iloc[:,0].nunique())
print('Missing titles:', df['title'].isna().sum())
print('Missing expected_fault:', df['expected_fault'].isna().sum())
print('Missing concept:', df['concept'].isna().sum())
print('Missing severity:', df['severity'].isna().sum())
print()
print('All cases:')
for _, row in df.iterrows():
    print(f'  {row.iloc[0]}: {row["title"]} | {row["concept"]} | {row["severity"]}')