#!/bin/bash

# Note:   Script to download GPTQ and AWQ models from Hugging Face.
# Author: Stefanos Laskaridis

# Models
# 1. TinyLlama
# 2. Zephyr 3b
# 3. Mistral 7b
# 4. Llama 7b
# 5. Llama 13b

DOWNLOAD_SCRIPT_PATH=${DOWNLOAD_SCRIPT_PATH:-"../../models/"}
OUTPUT_PATH=${OUTPUT_PATH:-"../../../melt_models_converted"}
HUGGINGFACE_TOKEN=$(cat .hf_token)

MODELS=(
    TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ # GPTQ models
    TheBloke/stablelm-zephyr-3b-GPTQ
    TheBloke/Mistral-7B-Instruct-v0.1-GPTQ
    TheBloke/Llama-2-7B-GPTQ
    TheBloke/Llama-2-13B-GPTQ

    TheBloke/TinyLlama-1.1B-Chat-v1.0-AWQ # AWQ models
    TheBloke/stablelm-zephyr-3b-AWQ
    TheBloke/Mistral-7B-Instruct-v0.1-AWQ
    TheBloke/Llama-2-7B-AWQ
    TheBloke/Llama-2-13B-AWQ
)

for MODEL in ${MODELS[@]};do
    python ${DOWNLOAD_SCRIPT_PATH}/download.py -m $MODEL -d ${OUTPUT_PATH} -t ${HUGGINGFACE_TOKEN}
done
