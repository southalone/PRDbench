
#!/usr/bin/env python3
import os
import argparse
import sys

def delete_specific_json_files(directory):
    """
    删除指定目录及其子目录下所有名为query_response.json和session_response.json的文件

    Args:
        directory: 要搜索的目录路径

    Returns:
        deleted_count: 删除的文件数量
    """
    target_files = ["query_response.json", "session_response.json"]
    deleted_count = 0

    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"错误: 目录 '{directory}' 不存在")
        return 0

    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file in target_files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除文件 '{file_path}' 时出错: {e}")

    return deleted_count

def main():
    parser = argparse.ArgumentParser(description='删除指定目录下所有名为query_response.json和session_response.json的文件')
    parser.add_argument('directory', nargs='?', default=os.getcwd(),
                        help='要搜索的目录路径 (默认为当前目录)')

    args = parser.parse_args()

    print(f"开始在 '{args.directory}' 中搜索并删除指定的JSON文件...")
    deleted_count = delete_specific_json_files(args.directory)

    print(f"\n操作完成! 共删除了 {deleted_count} 个文件")

if __name__ == "__main__":
    main()
