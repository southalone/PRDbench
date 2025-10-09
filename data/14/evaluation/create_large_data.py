import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 设置随机种子以确保结果可重现
np.random.seed(42)
random.seed(42)

# 创建5000条记录的数据
n_records = 5000

# 基础字段
data = {
    'id': range(1, n_records + 1),
    'collector': [f'调查员{random.choice(["A", "B", "C", "D", "E"])}' for _ in range(n_records)],
    'location': [random.choice(['练习场A', '练习场B', '会员制球场C', '公众球场D', '度假村球场E']) for _ in range(n_records)],
    'timestamp': [(datetime(2023, 10, 26, 10, 0, 0) + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S') for i in range(n_records)]
}

# 添加问卷字段
# 性别 (单选)
data['gender'] = [random.choice(['男', '女']) for _ in range(n_records)]

# 年龄段 (单选)
data['age_group'] = [random.choice(['18-25', '26-35', '36-45', '46-55', '56-65', '65+']) for _ in range(n_records)]

# 职业 (开放文本)
occupations = ['企业管理者', '专业技术人员', '公务员', '教师', '医生', '律师', '工程师', '销售人员', '自由职业者', '退休人员']
data['occupation'] = [random.choice(occupations) for _ in range(n_records)]

# 场地类型偏好 (多选，用逗号分隔)
venue_types = ['公众场', '会员制', '练习场', '度假村球场']
data['venue_preference'] = [','.join(random.sample(venue_types, random.randint(1, 3))) for _ in range(n_records)]

# 量表题目 (1-5分)
data['price_influence'] = np.random.randint(1, 6, n_records)  # 价格影响程度
data['satisfaction'] = np.random.randint(1, 6, n_records)     # 满意度
data['amenities_importance'] = np.random.randint(1, 6, n_records)  # 设施重要性
data['service_quality'] = np.random.randint(1, 6, n_records)  # 服务质量评价
data['value_for_money'] = np.random.randint(1, 6, n_records)  # 性价比评价

# 消费频次
data['visit_frequency'] = [random.choice(['每周1次', '每月2-3次', '每月1次', '每季度1次', '每年几次']) for _ in range(n_records)]

# 年消费金额
data['annual_spending'] = np.random.randint(5000, 50000, n_records)

# 推荐意愿 (1-10分)
data['recommendation_score'] = np.random.randint(1, 11, n_records)

# 创建DataFrame
df = pd.DataFrame(data)

# 保存到CSV文件
df.to_csv('evaluation/large_data.csv', index=False, encoding='utf-8')
print(f"已创建包含 {len(df)} 条记录的大数据文件: evaluation/large_data.csv")
print(f"文件大小: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
print("数据字段:", list(df.columns))