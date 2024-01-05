#!/bin/bash

# Models
# 1. TinyLlama
# 2. Zephyr 3b
# 3. Mistral 7b
# 4. Llama 7b
# 5. Llama 13b
# 6. Starcoder

LLAMA_CPP_HOME=${LLAMA_CPP_HOME:-"$PWD/../../frameworks/llama.cpp/llama.cpp"}
MLC_HOME=${MLC_HOME:-"$PWD/../../frameworks/MLC/mlc-llm"}
MODELS_PATH=${MODELS_PATH:-"../../frameworks/MLC/mlc-llm/dist/models"}
CONFIGS_PATH=${CONFIGS_PATH:-"../configs/"}
OUTPUT_PATH=${OUTPUT_PATH:-"/tmp/llm-models-converted"}

## LLAMA_CPP

for QUANT in q3_k q4_k; do
    LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_PATH}/TinyLlama_TinyLlama-1.1B-Chat-v0.5 -b ggml -q $QUANT -t metal -v -d $OUTPUT_PATH/TinyLlama_TinyLlama-1.1B-Chat-v0.5 -c ${CONFIGS_PATH}/tinyllama-1.1b-chat-v0.5.yaml
    LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_PATH}/stabilityai_stablelm-zephyr-3b -b ggml -q $QUANT -t metal -v -d $OUTPUT_PATH/stabilityai_stablelm-zephyr-3b -c ${CONFIGS_PATH}/stablelm-zephyr-3b.yaml
    LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_PATH}/mistralai_Mistral-7B-Instruct-v0.1 -b ggml -q $QUANT -t metal -v -d $OUTPUT_PATH/mistralai_Mistral-7B-Instruct-v0.1 -c ${CONFIGS_PATH}/mistral-7b-instruct-v0.1.yaml
    LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_PATH}/Llama-2-7b-chat-hf -b ggml -q $QUANT -t metal -v -d $OUTPUT_PATH/Llama-2-7b-chat-hf -c ${CONFIGS_PATH}/llama-2-7b-chat-hf.yaml
    LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_PATH}/Llama-2-13b-chat-hf -b ggml -q $QUANT -t metal -v -d $OUTPUT_PATH/Llama-2-13b-chat-hf -c ${CONFIGS_PATH}/llama-2-13b-chat-hf.yaml
    LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_PATH}/starcoder -b ggml -q $QUANT -t metal -v -d $OUTPUT_PATH/bigcode_starcoder -c ${CONFIGS_PATH}/starcoder-bigcode.yaml
done

## MLC_LLM

for QUANT in q3f16_1 q4f16_1 q0f32; do
    for BACKEND in metal iphone android; do

    MLC_HOME=$MLC_HOME python convert.py --model ${MODELS_PATH}/TinyLlama_TinyLlama-1.1B-Chat-v0.5 -b mlc -q $QUANT -t $BACKEND -v -d $OUTPUT_PATH/TinyLlama_TinyLlama-1.1B-Chat-v0.5 -c ${CONFIGS_PATH}/tinyllama-1.1b-chat-v0.5.yaml
    MLC_HOME=$MLC_HOME python convert.py --model ${MODELS_PATH}/stabilityai_stablelm-zephyr-3b -b mlc -q $QUANT -t $BACKEND -v -d $OUTPUT_PATH/stabilityai_stablelm-zephyr-3b -c ${CONFIGS_PATH}/stablelm-zephyr-3b.yaml
    MLC_HOME=$MLC_HOME python convert.py --model ${MODELS_PATH}/mistralai_Mistral-7B-Instruct-v0.1 -b mlc -q $QUANT -t $BACKEND -v -d $OUTPUT_PATH/mistralai_Mistral-7B-Instruct-v0.1 -c ${CONFIGS_PATH}/mistral-7b-instruct-v0.1.yaml
    MLC_HOME=$MLC_HOME python convert.py --model ${MODELS_PATH}/Llama-2-7b-chat-hf -b mlc -q $QUANT -t $BACKEND -v -d $OUTPUT_PATH/Llama-2-7b-chat-hf -c ${CONFIGS_PATH}/llama-2-7b-chat-hf.yaml
    MLC_HOME=$MLC_HOME python convert.py --model ${MODELS_PATH}/Llama-2-13b-chat-hf -b mlc -q $QUANT -t $BACKEND -v -d $OUTPUT_PATH/Llama-2-13b-chat-hf -c ${CONFIGS_PATH}/llama-2-13b-chat-hf.yaml
    MLC_HOME=$MLC_HOME python convert.py --model ${MODELS_PATH}/starcoder -b mlc -q $QUANT -t $BACKEND -v -d $OUTPUT_PATH/bigcode_starcoder -c ${CONFIGS_PATH}/starcoder-bigcode.yaml

    done
done