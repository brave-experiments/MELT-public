#!/bin/bash

MODELS_DIR=${MODELS_DIR:-"../../melt_models"}
CONFIGS_PATH=${CONFIGS_PATH:-"../configs"}
OUTPUT_ROOT_DIR=${OUTPUT_ROOT_DIR:-"${MODELS_DIR}_converted_new"}
LLAMA_CPP_HOME=${LLAMA_CPP_HOME:-"../../frameworks/llama.cpp/llama.cpp"}

MODELS=(
    google_gemma-2b-it
    google_gemma-7b-it
)

QUANTS=(
    q3_k
    q4_k
    q4_0
)

model_counter=0
for MODEL in ${MODELS[@]};do
    for QUANT in ${QUANTS[@]};do
        echo Converting model $MODEL-$QUANT with conv_template $CONV_TEMPLATE to $CONVERTED_MODEL_DIR
        LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_DIR}/${MODEL} -b ggml -q $QUANT -t metal -v -d $OUTPUT_ROOT_DIR/${MODEL} -c ${CONFIGS_PATH}/${MODEL}.yaml
    done
    model_counter=$(( model_counter + 1 ))
done

