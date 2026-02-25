import os
import shutil
import argparse
import json
import tempfile

def check_query_response(query_response_path):
    """
    检查 query_response.json 文件内容：
    - 如果文件不存在，返回 True（需要清理）
    - 如果文件包含 'network_error' 或 '已重试 10 次'，返回 True（需要清理）
    """
    if not os.path.exists(query_response_path):
        print(f"  query_response.json 不存在，按异常处理需要清理")
        return True

    try:
        with open(query_response_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # 检测错误标记
            if 'network_error' in content or '已重试 10 次' in content:
                print(f"  检测到错误内容")
                return True

            return False

    except Exception as e:
        print(f"  读取文件时出错: {e}")
        return False


def get_files_to_preserve(folder_path, project_id, aux_data):
    """
    获取需要保留的文件和目录列表
    
    Args:
        folder_path: 项目文件夹路径
        project_id: 项目ID
        aux_data: aux_data.json 的内容字典
    
    Returns:
        需要保留的文件和目录路径列表
    """
    preserve_list = []
    
    # 保留 src/PRD.md 或 src/prd.md
    src_dir = os.path.join(folder_path, "src")
    if os.path.exists(src_dir):
        prd_file = None
        if os.path.exists(os.path.join(src_dir, "PRD.md")):
            prd_file = os.path.join(src_dir, "PRD.md")
        elif os.path.exists(os.path.join(src_dir, "prd.md")):
            prd_file = os.path.join(src_dir, "prd.md")
        
        if prd_file:
            preserve_list.append(prd_file)
    
    # 保留 evaluation 目录
    eval_dir = os.path.join(folder_path, "evaluation")
    if os.path.exists(eval_dir):
        preserve_list.append(eval_dir)
    
    # 保留 aux_data 中列出的额外文件
    if project_id in aux_data and aux_data[project_id]:
        for file_path in aux_data[project_id]:
            full_path = os.path.join(folder_path, file_path)
            if os.path.exists(full_path):
                preserve_list.append(full_path)
    
    return preserve_list


def copy_from_template(template_dir, project_id, target_folder):
    """
    从模板目录复制对应题目的所有内容到目标文件夹（全量覆盖式恢复）：
    - 会先删除 target_folder（若存在），再将 template_dir/project_id/ 整体复制到 target_folder
    - 不会跳过已存在的文件/目录
    
    Args:
        template_dir: 模板目录路径
        project_id: 项目ID
        target_folder: 目标文件夹路径
    """
    template_project_path = os.path.join(template_dir, project_id)
    
    try:
        if not os.path.exists(template_project_path):
            print(f"  模板项目目录不存在: {template_project_path}，跳过复制")
            return
        if not os.path.isdir(template_project_path):
            print(f"  模板项目路径不是目录: {template_project_path}，跳过复制")
            return

        # 全量覆盖：先删目标目录再整体复制
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
        shutil.copytree(template_project_path, target_folder)
        print(f"  已从模板目录全量复制项目内容（覆盖式）")
    except Exception as e:
        print(f"  从模板目录复制内容时出错: {e}")


def delete_folder_preserving_content(folder_path, preserve_list):
    """
    删除文件夹，但保留指定的文件和目录
    
    Args:
        folder_path: 要删除的文件夹路径
        preserve_list: 需要保留的文件和目录路径列表
    """
    if not os.path.exists(folder_path):
        return
    
    # 创建临时目录来保存需要保留的内容
    with tempfile.TemporaryDirectory() as temp_dir:
        # 备份需要保留的内容，记录相对路径
        backup_mapping = {}  # {相对路径: (源路径, 是否为目录)}
        for preserve_path in preserve_list:
            if os.path.exists(preserve_path):
                # 计算相对路径
                rel_path = os.path.relpath(preserve_path, folder_path)
                temp_backup_path = os.path.join(temp_dir, rel_path)
                
                # 创建目标目录
                temp_backup_dir = os.path.dirname(temp_backup_path)
                if temp_backup_dir and not os.path.exists(temp_backup_dir):
                    os.makedirs(temp_backup_dir)
                
                # 复制文件或目录
                is_dir = os.path.isdir(preserve_path)
                if is_dir:
                    shutil.copytree(preserve_path, temp_backup_path)
                else:
                    shutil.copy2(preserve_path, temp_backup_path)
                
                # 记录映射关系
                backup_mapping[rel_path] = (preserve_path, is_dir)
        
        # 删除原文件夹
        shutil.rmtree(folder_path)
        
        # 恢复保留的内容
        if backup_mapping:
            for rel_path, (original_path, is_dir) in backup_mapping.items():
                temp_backup_path = os.path.join(temp_dir, rel_path)
                restore_path = os.path.join(folder_path, rel_path)
                
                if os.path.exists(temp_backup_path):
                    # 创建目标目录
                    target_dir = os.path.dirname(restore_path)
                    if target_dir and not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    
                    # 恢复文件或目录
                    if is_dir:
                        if not os.path.exists(restore_path):
                            shutil.copytree(temp_backup_path, restore_path)
                    else:
                        shutil.copy2(temp_backup_path, restore_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量检测并清理有网络错误的项目文件夹')
    parser.add_argument('--base_dir', type=str, required=True, help='工作目录的路径')
    parser.add_argument('--template_dir', type=str, default=None, help='模板目录路径，如果提供则从模板目录复制对应题目的内容')
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    template_dir = os.path.abspath(args.template_dir) if args.template_dir else None
    
    if template_dir:
        print(f"模板目录: {template_dir}")
        if not os.path.exists(template_dir):
            print(f"警告: 模板目录不存在: {template_dir}")
            template_dir = None
    
    # 读取 aux_data.json（如果存在）
    aux_data = {}
    aux_data_path = os.path.join(os.path.dirname(base_dir), "aux_data.json")
    print(f"aux_data_path: {aux_data_path}")
    if os.path.exists(aux_data_path):
        try:
            with open(aux_data_path, 'r', encoding='utf-8') as f:
                aux_data = json.load(f)
            print(f"已加载 aux_data.json，包含 {len(aux_data)} 个项目的额外文件配置")
        except Exception as e:
            print(f"读取 aux_data.json 时出错: {e}，将只保留 PRD.md 和 evaluation 目录")
    else:
        print("未找到 aux_data.json，将只保留 PRD.md 和 evaluation 目录")

    for i in range(1, 51):
        project_id = str(i)
        folder_path = os.path.join(base_dir, project_id)
        query_response_path = os.path.join(folder_path, 'query_response.json')

        print(f"检查项目 {project_id}: {folder_path}")

        # 检查是否需要清理
        if check_query_response(query_response_path):
            # 如果提供了模板目录：整 repo 删除后，从模板全量复制恢复（不保留任何旧内容）
            if template_dir:
                print(f"  检测到错误，删除整个 repo 并从模板全量恢复")
                copy_from_template(template_dir, project_id, folder_path)
            else:
                print(f"  检测到错误，删除文件夹（保留必要内容）")
                
                # 获取需要保留的文件列表
                preserve_list = get_files_to_preserve(folder_path, project_id, aux_data)
                if preserve_list:
                    print(f"  将保留 {len(preserve_list)} 个文件/目录")
                
                # 删除文件夹但保留指定内容
                if os.path.exists(folder_path):
                    delete_folder_preserving_content(folder_path, preserve_list)
                    print(f"  已删除文件夹（已保留必要内容）")
            
            print()  # 空行
        else:
            print(f"  正常，跳过\n")
