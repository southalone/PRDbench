MODEL_NAME=$1
PORT=$2
ROUND=$3
PYTHON_INTERPRETER_PORT=$4
FILE_OPERATIONS_PORT=$5
SYSTEM_OPERATIONS_PORT=$6

SOURCE_PATH=/work/workspace/${MODEL_NAME}_Dev_inference
ROOT_PATH=/work/workspace/${MODEL_NAME}_Dev_inference_eval
cp -r ${SOURCE_PATH} ${ROOT_PATH}
bash Evaluation/start_adk_server.sh ${MODEL_NAME} ${ROOT_PATH} ${PORT} ${PYTHON_INTERPRETER_PORT} ${FILE_OPERATIONS_PORT} ${SYSTEM_OPERATIONS_PORT}
sleep 15
python Evaluation/delete_query_json.py ${ROOT_PATH}
python Evaluation/ready_test.py --local_port ${PORT} --model_name ${MODEL_NAME} --root_path ${ROOT_PATH} --round ${ROUND}
python Evaluation/score_cal.py --base_path ${ROOT_PATH} --round ${ROUND}