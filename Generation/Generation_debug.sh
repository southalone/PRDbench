set -euo pipefail

MODEL_NAME=${1:?MODEL_NAME required}
PORT=${2:?PORT required}
PYTHON_INTERPRETER_PORT=${3:?PYTHON_INTERPRETER_PORT required}
FILE_OPERATIONS_PORT=${4:?FILE_OPERATIONS_PORT required}
SYSTEM_OPERATIONS_PORT=${5:?SYSTEM_OPERATIONS_PORT required}

# 固定使用默认模板目录
TEMPLATE_DIR="/work/workspace/${MODEL_NAME}_Dev_inference_eval"

ROOT_PATH="/work/workspace/${MODEL_NAME}_Debug_inference"
mkdir -p "${ROOT_PATH}"

echo "[INFO] MODEL_NAME=${MODEL_NAME}"
echo "[INFO] PORT=${PORT}"
echo "[INFO] ROOT_PATH=${ROOT_PATH}"
echo "[INFO] TEMPLATE_DIR=${TEMPLATE_DIR}"

# 注意：不再在这里把 Dev_inference_eval 整体 cp 到 Debug_inference。
# experiment_debug.sh 会在跑完后，针对 network_error 的 repo 做"清理 +（可选）从模板补全"。
bash Generation/start_adk_server.sh "${MODEL_NAME}" "${ROOT_PATH}" "${PORT}" "${PYTHON_INTERPRETER_PORT}" "${FILE_OPERATIONS_PORT}" "${SYSTEM_OPERATIONS_PORT}"
sleep 60
bash Generation/experiment_debug.sh "${MODEL_NAME}" "${PORT}"
sleep 2
