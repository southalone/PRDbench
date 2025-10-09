# -*- coding: utf-8 -*-
"""测试 空间传播模拟"""
import sys; sys.path.append('src')
from models.spatial_brownian_model import SpatialBrownianModel

print("测试: 布朗运动空间传播优化 → 空间传播模拟") 
model = SpatialBrownianModel()
result = model.run_simulation()
if result:
    print("[成功] 空间传播模拟完成!")
else:
    print("[失败] 空间传播模拟失败")