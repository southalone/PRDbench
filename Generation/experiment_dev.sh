#!/bin/bash

START_ID=1
NUM_RUNS=50

MODEL_NAME=$1
port=$2

# 第一轮：完整生成1-50
echo "=== 第一轮生成：运行所有 ID (1-$NUM_RUNS) ==="
for ((i=1; i<=NUM_RUNS; i++)); do
    PROJECT_PATH="/work/workspace/${MODEL_NAME}_Dev_inference/${i}"
    echo "Running with ID: $i, Model: $MODEL_NAME, Port: $port, Session: $i"
    python Generation/generate_dev.py --local_port $port --model_name $MODEL_NAME --session_id $i --ID $i --project_path "$PROJECT_PATH"
done

# 重试机制：最多重试3次
MAX_RETRIES=3
for ((retry_round=1; retry_round<=MAX_RETRIES; retry_round++)); do
    echo ""
    echo "=== 检查失败项并重试 (第 $retry_round/$MAX_RETRIES 次重试) ==="
    
    # 检查哪些ID失败了，并清理network_error
    failed_ids=()
    for ((i=1; i<=NUM_RUNS; i++)); do
        PROJECT_PATH="/work/workspace/${MODEL_NAME}_Dev_inference/${i}"
        
        # 检查是否需要重试
        python - "$PROJECT_PATH" <<'PY'
import os
import sys

project_path = sys.argv[1]
query_response_path = os.path.join(project_path, "query_response.json")

# 如果文件不存在，需要重试
if not os.path.exists(query_response_path):
    sys.exit(1)

try:
    with open(query_response_path, "r", encoding="utf-8") as f:
        content = f.read()
    if ("network_error" in content) or ("已重试 10 次" in content):
        os.remove(query_response_path)
        print(f"[cleanup] detected network_error, removed: {query_response_path}")
        sys.exit(1)  # 需要重试
    else:
        sys.exit(0)  # 成功，不需要重试
except Exception as e:
    # 不因为清理失败而中断整轮实验
    print(f"[cleanup] failed to inspect/remove {query_response_path}: {e}")
    sys.exit(1)  # 检查失败，需要重试
PY
        CHECK_RESULT=$?
        
        if [ $CHECK_RESULT -ne 0 ]; then
            failed_ids+=($i)
        fi
    done
    
    # 如果没有失败的，退出重试循环
    if [ ${#failed_ids[@]} -eq 0 ]; then
        echo "所有 ID 生成成功，无需重试"
        break
    fi
    
    echo "发现 ${#failed_ids[@]} 个失败的 ID: ${failed_ids[@]}"
    echo "开始重试生成..."
    
    # 重试生成失败的ID
    for i in "${failed_ids[@]}"; do
        PROJECT_PATH="/work/workspace/${MODEL_NAME}_Dev_inference/${i}"
        echo "[retry $retry_round/$MAX_RETRIES] Re-running for ID: $i"
        python Generation/generate_dev.py --local_port $port --model_name $MODEL_NAME --session_id $i --ID $i --project_path "$PROJECT_PATH --retry_round $retry_round"
    done
done

echo ""
echo "=== 生成完成 ==="
