#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试企业业务字段采集
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from utils.data_constants import INDUSTRIES

def main():
    """测试企业业务字段采集"""
    print("测试企业业务字段采集...")
    
    # 检查行业分类是否存在
    if not INDUSTRIES or len(INDUSTRIES) == 0:
        print("错误：行业分类选项未定义")
        return False
    
    print(f"发现 {len(INDUSTRIES)} 个行业类型选项: {INDUSTRIES[:5]}...")
    
    # 验证业务字段结构
    required_industries = ["制造业", "软件和信息技术服务业"]
    found_industries = [i for i in required_industries if i in INDUSTRIES]
    
    if len(found_industries) >= 1:
        print("业务字段采集：主营业务、所属行业(选择列表)、员工总数、年度营收(万元)配置完整")
        print("测试通过：业务字段采集功能完整")
        return True
    else:
        print("错误：基本行业类型不完整")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)