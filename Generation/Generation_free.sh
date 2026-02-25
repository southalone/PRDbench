MODEL_NAME=$1
port=$2
ROOT_PATH=workspace/${MODEL_NAME}_Dev_free
PYTHON_INTERPRETER_PORT=$3
FILE_OPERATIONS_PORT=$4
SYSTEM_OPERATIONS_PORT=$5
python Generation/copy_free.py data/ ${ROOT_PATH}
bash Generation/start_adk_server.sh ${MODEL_NAME} ${ROOT_PATH} ${port} ${PYTHON_INTERPRETER_PORT} ${FILE_OPERATIONS_PORT} ${SYSTEM_OPERATIONS_PORT}
sleep 15
bash Generation/experiment_free.sh $MODEL_NAME $port
sleep 2
