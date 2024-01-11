#!/bin/bash

# Models
# 1. TinyLlama
# 2. Zephyr 3b
# 3. Mistral 7b
# 4. Llama 7b
# 5. Llama 13b
# 6. Starcoder

DOWNLOAD_SCRIPT_PATH=${DOWNLOAD_SCRIPT_PATH:-"./"}
OUTPUT_PATH=${OUTPUT_PATH:-"../../melt_models"}
HUGGINGFACE_TOKEN=$(cat .hf_token)

for MODEL in TinyLlama/TinyLlama-1.1B-Chat-v0.5 stabilityai/stablelm-zephyr-3b mistralai/Mistral-7B-Instruct-v0.1 Llama-2-7b-hf Llama-2-13b-hf Llama-2-7b-chat-hf Llama-2-13b-chat-hf starcoder; do
    python ${DOWNLOAD_SCRIPT_PATH}/download.py -m ${MODEL} -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
done
