# -*- coding: utf-8 -*-
"""测试 运行完整空间传播分析"""
import sys; sys.path.append('src')
from models.spatial_brownian_model import SpatialBrownianModel

print("测试: 布朗运动空间传播优化 → 运行完整空间传播分析")
model = SpatialBrownianModel()
model.run_simulation()
model.generate_animation_frames()
print("[成功] 完整空间传播分析完成!")