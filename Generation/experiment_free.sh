#!/bin/bash

START_ID=1
NUM_RUNS=50

MODEL_NAME=$1
port=$2

for ((i=START_ID; i<START_ID+NUM_RUNS; i++)); do
    PROJECT_PATH="workspace/${MODEL_NAME}_Dev_free/${i}"
    echo "Running with ID: $i, Model: $MODEL_NAME, Port: $port, Session: $i"
    python Generation/generate_free.py --local_port $port --model_name $MODEL_NAME --session_id $i --ID $i --project_path "$PROJECT_PATH"

    # 复用 delete_network_error.py 的核心逻辑：检测到 network_error/重试上限就删除 query_response.json
    # 如果删除了文件，则重新运行一次查漏补缺
    while true; do
        python - "$PROJECT_PATH" <<'PY'
import os
import sys

project_path = sys.argv[1]
query_response_path = os.path.join(project_path, "query_response.json")

if not os.path.exists(query_response_path):
    sys.exit(0)

try:
    with open(query_response_path, "r", encoding="utf-8") as f:
        content = f.read()
    if ("network_error" in content) or ("已重试 10 次" in content):
        os.remove(query_response_path)
        print(f"[cleanup] detected network_error, removed: {query_response_path}")
        sys.exit(1)  # 返回1表示删除了文件，需要重新运行
    else:
        sys.exit(0)  # 没有错误，不需要重新运行
except Exception as e:
    # 不因为清理失败而中断整轮实验
    print(f"[cleanup] failed to inspect/remove {query_response_path}: {e}")
    sys.exit(0)
PY
        DELETE_RESULT=$?
        if [ $DELETE_RESULT -eq 1 ]; then
            echo "[retry] Re-running for ID: $i after deleting network_error"
            python Generation/generate_free.py --local_port $port --model_name $MODEL_NAME --session_id $i --ID $i --project_path "$PROJECT_PATH"
        else
            break  # 没有删除文件，退出循环
        fi
    done
done
