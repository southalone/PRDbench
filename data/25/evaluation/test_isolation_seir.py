# -*- coding: utf-8 -*-
"""测试 改进隔离机制SEIR模型"""
import sys; sys.path.append('src')
from models.isolation_seir_model import IsolationSEIRModel

print("测试: 改进隔离机制SEIR模型")
model = IsolationSEIRModel()
result = model.run_simulation()
if result:
    print("[成功] 隔离SEIR模型运行完成!")
else:
    print("[失败] 隔离SEIR模型运行失败")