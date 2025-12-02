#!/usr/bin/env python3
"""
性能测试脚本 - 测试大数据量下的报告生成性能
"""

import subprocess
import time
import os
import sys

def test_performance():
    """测试性能要求"""
    print("🚀 开始性能测试...")
    print("=" * 50)
    
    # 测试命令
    command = [
        "python", "-m", "src.main", 
        "report", "generate-full",
        "--data-path", "evaluation/large_data.csv",
        "--format", "markdown",
        "--output-path", "evaluation/performance_report.md"
    ]
    
    print(f"执行命令: {' '.join(command)}")
    print("⏱️  开始计时...")
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 执行命令
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 记录结束时间
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"⏱️  执行时间: {execution_time:.2f} 秒")
        print("=" * 50)
        
        # 检查执行结果
        if result.returncode == 0:
            print("✅ 命令执行成功!")
            print("\n📋 标准输出:")
            print(result.stdout)
            
            # 检查输出文件是否存在
            if os.path.exists("evaluation/performance_report.md"):
                file_size = os.path.getsize("evaluation/performance_report.md")
                print(f"📄 生成的报告文件大小: {file_size} 字节")
                
                # 读取文件前几行验证内容
                with open("evaluation/performance_report.md", 'r', encoding='utf-8') as f:
                    first_lines = [f.readline().strip() for _ in range(3)]
                    print("📝 报告文件前3行内容:")
                    for i, line in enumerate(first_lines, 1):
                        print(f"   {i}. {line}")
            else:
                print("❌ 输出文件未生成!")
                return False
            
            # 性能评估
            print("\n🎯 性能评估:")
            if execution_time < 30:
                print(f"✅ 性能测试通过! 执行时间 {execution_time:.2f}s < 30s")
                return True
            else:
                print(f"⚠️  性能警告: 执行时间 {execution_time:.2f}s >= 30s")
                return False
                
        else:
            print("❌ 命令执行失败!")
            print(f"返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return False
            
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"❌ 执行异常: {e}")
        print(f"执行时间: {execution_time:.2f} 秒")
        return False

if __name__ == "__main__":
    success = test_performance()
    sys.exit(0 if success else 1)