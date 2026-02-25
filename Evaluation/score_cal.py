import os
import json
import argparse

def parse_possible_json_string(content):
    """
    如果 content 是一个被转义的 JSON 字符串（外层是字符串），则解析为 dict。
    否则直接返回原内容。
    """
    if isinstance(content, str):
        content = content.strip()
        # 如果是被引号包裹的 JSON 字符串（常见于转义存储）
        if (content.startswith('"') and content.endswith('"')) or \
           (content.startswith("'") and content.endswith("'")):
            try:
                # 去掉外层引号
                content = content[1:-1]
                # 处理被转义的双引号
                content = content.replace('\\"', '"').replace("\\'", "'")
            except Exception:
                pass
        # 再尝试解析为 JSON
        try:
            return json.loads(content)
        except Exception:
            return content
    return content

def get_completed_metrics(report_dir):
    """
    获取已经完成的评分项（检查reports目录下的非空且有效的JSON文件，且有score字段）。
    返回：
      - completed_metrics: set，已完成的评分项名
      - reasons: dict，各类异常原因的详细列表（便于后续分析）
    """
    completed_metrics = set()
    reasons = {
        'file_empty': [],
        'invalid_json': [],
        'no_score_field': [],
        'other_error': []
    }

    if os.path.exists(report_dir):
        try:
            for filename in os.listdir(report_dir):
                if not filename.endswith('.json'):
                    continue
                file_path = os.path.join(report_dir, filename)
                metric_name = filename[:-5]

                # 1. 判断文件是否为空
                if os.path.getsize(file_path) == 0:
                    reasons['file_empty'].append({'metric': metric_name, 'file': file_path})
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if not content:
                        reasons['file_empty'].append({'metric': metric_name, 'file': file_path})
                        continue
                    try:
                        data = json.loads(content)
                        if isinstance(data, str):
                            data = parse_possible_json_string(data)
                    except json.JSONDecodeError as e:
                        reasons['invalid_json'].append({
                            'metric': metric_name,
                            'file': file_path,
                            'error': str(e),
                            'content_preview': content[:200]
                        })
                        try:
                            os.remove(file_path)
                        except Exception as del_e:
                            reasons['other_error'].append({
                                'metric': metric_name,
                                'file': file_path,
                                'error': f"Failed to delete invalid JSON file: {del_e}"
                            })
                        continue

                    if data == {} or data == []:
                        reasons['file_empty'].append({'metric': metric_name, 'file': file_path})
                        continue

                    if not isinstance(data, dict) or 'score' not in data:
                        reasons['no_score_field'].append({
                            'metric': metric_name,
                            'file': file_path,
                            'data_type': type(data).__name__,
                            'keys': list(data.keys()) if isinstance(data, dict) else None
                        })
                        continue

                    completed_metrics.add(metric_name)

                except Exception as e:
                    reasons['other_error'].append({
                        'metric': metric_name,
                        'file': file_path,
                        'error': str(e)
                    })

        except Exception as e:
            reasons['other_error'].append({
                'dir': report_dir,
                'error': str(e)
            })

    return completed_metrics, reasons

def load_expected_metrics(test_plan_path):
    """
    从detailed_test_plan.json读取所有预期的metric
    """
    expected_metrics = set()
    
    if not os.path.exists(test_plan_path):
        return None
    
    try:
        with open(test_plan_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return None
            
            data = json.loads(content)
            
            # 如果是字符串，尝试转为对象
            if isinstance(data, str):
                data = parse_possible_json_string(data)
            
            # 如果是数组，遍历每个元素
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        metric_name = item.get('metric') or item.get('metric_name') or item.get('name') or item.get('id')
                        if metric_name:
                            expected_metrics.add(str(metric_name))
            # 如果是单个对象
            elif isinstance(data, dict):
                metric_name = data.get('metric') or data.get('metric_name') or data.get('name') or data.get('id')
                if metric_name:
                    expected_metrics.add(str(metric_name))
        
        return expected_metrics if expected_metrics else None
    except Exception as e:
        return None

def calculate_score_from_directory(reports_dir, test_plan_path=None):
    """
    使用 get_completed_metrics 统计有效评分项并计算平均分。
    """
    completed_metrics, reasons = get_completed_metrics(reports_dir)
    total_score = 0
    total_count = 0

    for metric_name in completed_metrics:
        json_file = os.path.join(reports_dir, metric_name + '.json')
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                try:
                    item = json.loads(content)
                    if isinstance(item, str):
                        item = parse_possible_json_string(item)
                except Exception:
                    continue
                if isinstance(item, dict) and 'score' in item:
                    total_score += item['score']
                    total_count += 1
        except Exception:
            continue

    if total_count == 0:
        return None, None, reasons

    final_score = total_score / total_count / 2

    missing_metrics = None
    if test_plan_path:
        expected_metrics = load_expected_metrics(test_plan_path)
        if expected_metrics:
            missing_metrics = expected_metrics - completed_metrics

    return final_score, missing_metrics, reasons

def batch_calculate_and_average(base_path):
    """
    批量计算所有项目的平均分
    从base_path下的各个子目录的reports文件夹读取json文件
    同时统计缺失的metric和异常原因
    """
    results = {}
    missing_metrics_info = {}
    reasons_info = {}
    total_sum = 0
    valid_count = 0

    subdirs = [d for d in os.listdir(base_path)
               if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')]

    for subdir in sorted(subdirs):
        reports_dir = os.path.join(base_path, subdir, 'reports')
        test_plan_path = os.path.join(base_path, subdir, 'evaluation', 'detailed_test_plan.json')

        score, missing_metrics, reasons = calculate_score_from_directory(reports_dir, test_plan_path)

        if score is not None:
            results[subdir] = score
            total_sum += score
            valid_count += 1

            missing_metrics_info[subdir] = sorted(list(missing_metrics)) if missing_metrics else []
            reasons_info[subdir] = reasons
        else:
            results[subdir] = "文件不存在或无有效数据"
            missing_metrics_info[subdir] = "无法统计"
            reasons_info[subdir] = reasons

    average_score = total_sum / valid_count if valid_count > 0 else 0
    return results, average_score, valid_count, missing_metrics_info, reasons_info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="批量计算平均分")
    parser.add_argument('--base_path', type=str, required=True, help='基础路径，包含多个项目子目录')
    args = parser.parse_args()

    results, average_score, valid_count, missing_metrics_info, reasons_info = batch_calculate_and_average(args.base_path)
    output = {
        "scores": results,
        "valid_count": valid_count,
        "average_score": average_score,
        "missing_metrics": missing_metrics_info,
        "error_reasons": reasons_info
    }
    output_path = os.path.join(args.base_path, 'results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"计算完成！")
    print(f"有效项目数: {valid_count}")
    print(f"总体平均分: {average_score:.4f}")
    print(f"结果已保存到: {output_path}")

    # 打印缺失metric的统计信息
    total_missing = sum(len(v) for v in missing_metrics_info.values() if isinstance(v, list))
    projects_with_missing = sum(1 for v in missing_metrics_info.values() if isinstance(v, list) and len(v) > 0)

    if total_missing > 0:
        print(f"\n{'='*60}")
        print(f"缺失metric统计汇总:")
        print(f"  有缺失的项目数: {projects_with_missing}/{valid_count}")
        print(f"  缺失metric总数: {total_missing}")
        print(f"{'='*60}")

        for subdir, missing in missing_metrics_info.items():
            if isinstance(missing, list) and len(missing) > 0:
                print(f"\n项目: {subdir}")
                print(f"  缺失 {len(missing)} 个metric:")
                for metric in missing:
                    print(f"    - {metric}")
    else:
        print(f"\n✓ 所有项目的metric都已完成！")

    # 打印异常原因统计
    print("\n异常原因统计（可用于后续分析）：")
    for subdir, reasons in reasons_info.items():
        print(f"\n项目: {subdir}")
        for reason_type, details in reasons.items():
            print(f"  {reason_type}: {len(details)}")