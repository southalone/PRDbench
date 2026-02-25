MODEL_NAME=$1
port=$2
ROOT_PATH=work/workspace/${MODEL_NAME}_Dev_inference
PYTHON_INTERPRETER_PORT=$3
FILE_OPERATIONS_PORT=$4
SYSTEM_OPERATIONS_PORT=$5
python Generation/copy_infer.py PRDbench/ workspace/${MODEL_NAME}_Dev_inference
bash Generation/start_adk_server.sh ${MODEL_NAME} ${ROOT_PATH} ${port} ${PYTHON_INTERPRETER_PORT} ${FILE_OPERATIONS_PORT} ${SYSTEM_OPERATIONS_PORT}
sleep 90
bash Generation/experiment_dev.sh $MODEL_NAME $port
sleep 2
