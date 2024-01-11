#!/bin/bash

# Models
# 1. TinyLlama
# 2. Zephyr 3b
# 3. Mistral 7b
# 4. Llama 7b
# 5. Llama 13b
# 6. Starcoder

DOWNLOAD_SCRIPT_PATH=${DOWNLOAD_SCRIPT_PATH:-"../../models/"}
OUTPUT_PATH=${OUTPUT_PATH:-"../../../melt_models_converted"}
HUGGINGFACE_TOKEN=$(cat .hf_token)

### GPTQ MODELS
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/stablelm-zephyr-3b-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Mistral-7B-Instruct-v0.1-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Mistral-7B-Instruct-v0.2-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-7B-Chat-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-13B-Chat-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-7B-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-13B-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/starcoder-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}

### AWQ_MODELS
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/stablelm-zephyr-3b-AWQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Mistral-7B-Instruct-v0.1-AWQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Mistral-7B-Instruct-v0.2-AWQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-7B-Chat-AWQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-13B-Chat-AWQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-7B-AWQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
python ${DOWNLOAD_SCRIPT_PATH}/download.py -m TheBloke/Llama-2-13B-AWQ -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}