#!/bin/bash

# Note:   Script to easily convert all models (MLC does not use convert.py).
# Author: Stefanos Laskaridis (stefanos@brave.com)

MODELS_DIR=${MODELS_DIR:-"../../melt_models"}
CONFIGS_PATH=${CONFIGS_PATH:-"../configs"}
OUTPUT_ROOT_DIR=${OUTPUT_ROOT_DIR:-"${MODELS_DIR}_converted_new"}
LLAMA_CPP_HOME=${LLAMA_CPP_HOME:-"../../frameworks/llama.cpp/llama.cpp"}


function convert_llama_cpp() {
    MODELS=(
        google_gemma-2b-it
        google_gemma-7b-it
    )
    QUANTS=(
        q3_k
        q4_k
        q4_0
    )

    for MODEL in ${MODELS[@]};do
        for QUANT in ${QUANTS[@]};do
            echo Converting model $MODEL-$QUANT to $CONVERTED_MODEL_DIR
            LLAMA_CPP_HOME=$LLAMA_CPP_HOME python convert.py --model ${MODELS_DIR}/${MODEL} -b ggml -q $QUANT -t metal -v -d $OUTPUT_ROOT_DIR/${MODEL} -c ${CONFIGS_PATH}/${MODEL}.yaml
        done
    done
}

function convert_mlc() {
    MODELS=(
        TinyLlama_TinyLlama-1.1B-Chat-v0.5
        google_gemma-2b-it
        google_gemma-7b-it
        meta-llama_Llama-2-7b-chat-hf
        meta-llama_Llama-2-13b-chat-hf
    )

    CONV_TEMPLATES=(
        chatml
        gemma_instruction
        gemma_instruction
        llama-2
        llama-2
    )

    QUANTS=(
        q3f16_1
        q4f16_1
        q0f32
    )

    BACKENDS=(
        metal
        android
        iphone
    )

    model_counter=0
    for MODEL in ${MODELS[@]};do
        CONV_TEMPLATE=${CONV_TEMPLATES[model_counter]}
        for QUANT in ${QUANTS[@]};do
            CONVERTED_MODEL_DIR="$OUTPUT_ROOT_DIR/$MODEL-$QUANT"
            echo Converting model $MODEL-$QUANT with conv_template $CONV_TEMPLATE to $CONVERTED_MODEL_DIR
            # 1. Generate model config
            mlc_chat gen_config $MODELS_DIR/$MODEL --conv-template $CONV_TEMPLATE --quantization $QUANT -o $OUTPUT_ROOT_DIR/$MODEL-$QUANT
            for BACKEND in ${BACKENDS[@]};do
                if [ $BACKEND = "metal" ];then
                    EXTENSION="so"
                else
                    EXTENSION="tar"
                fi
                # 2. Compile model
                mlc_chat compile $CONVERTED_MODEL_DIR/mlc-chat-config.json  --device $BACKEND  --quantization $QUANT -o $CONVERTED_MODEL_DIR/$MODEL-$QUANT-$BACKEND.$EXTENSION
            # 3. Convert model weights
            mlc_chat convert_weight $MODELS_DIR/$MODEL/config.json --device ${BACKENDS[0]}  --quantization $QUANT -o $CONVERTED_MODEL_DIR
            done
        done
        model_counter=$(( model_counter + 1 ))
    done
}

pushd ../
convert_llama_cpp
convert_mlc
popd