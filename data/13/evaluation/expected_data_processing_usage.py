# 期望的数据处理库使用示例
import pandas as pd
import numpy as np

# 1. DataFrame操作
users_df = pd.DataFrame()
items_df = pd.DataFrame() 
interactions_df = pd.DataFrame()

# 2. 数据读写
df = pd.read_csv('data/file.csv')
df.to_csv('output/file.csv', index=False)

# 3. 数据清洗
df.dropna()
df.fillna(method='mean')

# 4. 数据统计
df.describe()
df.groupby('column').sum()

# 5. NumPy数组操作
arr = np.array([1, 2, 3])
result = np.mean(arr)
matrix = np.random.random((100, 50))

# 6. 数值计算
similarity_matrix = np.dot(matrix, matrix.T)
normalized_data = (data - np.mean(data)) / np.std(data)