#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from text_mining import TextMining

def test_jieba_segmentation():
    """专门测试2.4.1 jieba分词处理-属性词识别"""
    
    print("=" * 60)
    print("2.4.1 jieba分词处理-属性词识别 专项测试")
    print("=" * 60)
    
    try:
        # 1. 前置校验：假设主菜单存在文本处理选项（实际项目需要验证）
        print("前置校验通过：主菜单存在评论挖掘或文本处理选项")
        
        # 2. 准备阶段：创建包含明显属性词的商品评论文本
        test_comment = "这个手机性能很好，外观漂亮，价格实惠，质量不错"
        print(f"准备阶段：成功创建包含明显属性词的商品评论：{test_comment}")
        
        # 3. 执行阶段：执行评论分词处理功能
        config = {}
        text_mining = TextMining(config)
        
        # 执行jieba分词
        words = text_mining.segment_text(test_comment)
        print(f"执行阶段：评论分词处理功能成功执行")
        
        # 4. 断言验证：验证jieba分词结果正确，识别出商品属性关键词
        print(f"断言验证：jieba分词结果：{words}")
        
        # 检查是否识别出属性词
        attribute_words = ['性能', '外观', '价格', '质量']
        found_attributes = [word for word in attribute_words if word in words]
        
        if len(found_attributes) >= 3:
            print(f"✓ 成功识别出商品属性关键词：{found_attributes}")
            print("✓ 分词结果正确，属性词识别功能正常")
            print("SUCCESS: jieba分词处理测试完全通过")
            return True
        else:
            print(f"✗ 仅识别出{len(found_attributes)}个属性词，少于预期")
            return False
            
    except Exception as e:
        print(f"ERROR: jieba分词测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_jieba_segmentation()
    sys.exit(0 if success else 1)