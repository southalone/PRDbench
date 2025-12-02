#!/usr/bin/env python3
"""
本地 Code Agent 主程序
基于 Google ADK 的本地代码代理系统
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.code_agent_local.agent import local_code_agent_system
from examples.code_agent_local.config import WORKSPACE_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class LocalCodeAgentCLI:
    """本地 Code Agent 命令行界面"""
    
    def __init__(self):
        self.agent_system = local_code_agent_system
        self.root_agent = self.agent_system.get_root_agent()
    
    async def run_interactive(self):
        """运行交互式模式"""
        print("=" * 60)
        print("🤖 本地 Code Agent 系统")
        print("=" * 60)
        print("支持的功能:")
        print("1. 完整代码开发 (规划、编写、测试、调试、总结)")
        print("2. 快速代码执行 (数学计算、数据处理)")
        print("3. 文件管理 (创建、读取、修改、删除)")
        print("4. 工作空间管理")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print("输入 'help' 查看帮助")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n💬 请输入您的请求: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if not user_input:
                    continue
                
                print(f"\n🔄 正在处理: {user_input}")
                
                # 运行代理
                result = await self.run_agent(user_input)
                
                print(f"\n✅ 处理完成:")
                print(f"状态: {result.get('status', 'unknown')}")
                if 'response' in result:
                    print(f"响应: {result['response']}")
                if 'error' in result:
                    print(f"错误: {result['error']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，再见！")
                break
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                print(f"❌ 发生错误: {e}")
    
    async def run_single_task(self, task: str):
        """运行单个任务"""
        print(f"🔄 正在处理任务: {task}")
        
        result = await self.run_agent(task)
        
        print(f"\n✅ 任务完成:")
        print(f"状态: {result.get('status', 'unknown')}")
        if 'response' in result:
            print(f"响应: {result['response']}")
        if 'error' in result:
            print(f"错误: {result['error']}")
        
        return result
    
    async def run_agent(self, user_input: str) -> Dict[str, Any]:
        """运行代理系统"""
        try:
            # 这里应该调用实际的代理运行逻辑
            # 目前返回模拟结果
            result = {
                "status": "success",
                "user_input": user_input,
                "response": f"本地 Code Agent 已处理您的请求: {user_input}",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # 模拟处理时间
            await asyncio.sleep(1)
            
            return result
            
        except Exception as e:
            logger.error(f"代理运行错误: {e}")
            return {
                "status": "error",
                "error": str(e),
                "user_input": user_input
            }
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
📖 本地 Code Agent 帮助

🔧 主要功能:
1. 代码开发 - 创建完整的Python项目
2. 代码执行 - 运行Python代码片段
3. 文件管理 - 管理文件和目录
4. 工作空间 - 创建工作空间环境

💡 使用示例:

代码开发:
- "创建一个计算器程序"
- "帮我写一个文件处理工具"
- "开发一个简单的Web应用"

代码执行:
- "计算 2 + 2 * 3"
- "生成一个随机数列表"
- "读取CSV文件并显示前5行"

文件管理:
- "创建工作空间"
- "列出当前文件"
- "读取文件内容"

🔒 安全特性:
- 沙盒环境执行
- 文件操作限制
- 系统命令白名单

📁 工作空间: {workspace_dir}
        """.format(workspace_dir=WORKSPACE_DIR)
        
        print(help_text)
    
    def show_examples(self):
        """显示示例"""
        examples = [
            {
                "category": "代码开发",
                "examples": [
                    "创建一个简单的计算器程序",
                    "帮我写一个文件批量重命名工具",
                    "开发一个简单的待办事项应用"
                ]
            },
            {
                "category": "代码执行",
                "examples": [
                    "计算斐波那契数列的前10项",
                    "生成一个包含100个随机数的列表",
                    "读取并分析CSV数据"
                ]
            },
            {
                "category": "文件管理",
                "examples": [
                    "创建一个新的工作空间",
                    "列出当前目录的所有文件",
                    "读取并显示文件内容"
                ]
            }
        ]
        
        print("\n📚 使用示例:")
        for category in examples:
            print(f"\n{category['category']}:")
            for example in category['examples']:
                print(f"  - {example}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="本地 Code Agent - 基于 Google ADK 的代码代理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                    # 交互式模式
  python main.py -t "计算 2+2"      # 执行单个任务
  python main.py --examples         # 显示示例
  python main.py --help             # 显示帮助
        """
    )
    
    parser.add_argument(
        '-t', '--task',
        type=str,
        help='要执行的任务'
    )
    
    parser.add_argument(
        '--examples',
        action='store_true',
        help='显示使用示例'
    )
    
    parser.add_argument(
        '--workspace',
        type=str,
        default=WORKSPACE_DIR,
        help=f'工作空间目录 (默认: {WORKSPACE_DIR})'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出模式'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建工作空间目录
    workspace_path = Path(args.workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)
    
    # 创建CLI实例
    cli = LocalCodeAgentCLI()
    
    async def run():
        if args.examples:
            cli.show_examples()
        elif args.task:
            await cli.run_single_task(args.task)
        else:
            await cli.run_interactive()
    
    # 运行主程序
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        print(f"❌ 程序错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 