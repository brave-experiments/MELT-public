#!/bin/bash

MODELS_DIR=${MODELS_DIR:-"../../melt_models"}
OUTPUT_ROOT_DIR=${OUTPUT_ROOT_DIR:-"${MODELS_DIR}_converted_new"}

MODELS=(
    google_gemma-2b-it
    google_gemma-7b-it
    meta-llama_Llama-2-7b-chat-hf
)

CONV_TEMPLATES=(
    gemma_instruction
   gemma_instruction
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
        mlc_chat gen_config $MODELS_DIR/$MODEL --conv-template $CONV_TEMPLATE --quantization $QUANT -o $OUTPUT_ROOT_DIR/$MODEL-$QUANT
        for BACKEND in ${BACKENDS[@]};do
            if [ $BACKEND = "metal" ];then
                EXTENSION="so"
            else
                EXTENSION="tar"
            fi
            mlc_chat compile $CONVERTED_MODEL_DIR/mlc-chat-config.json  --device $BACKEND  --quantization $QUANT -o $CONVERTED_MODEL_DIR/$MODEL-$QUANT-$BACKEND.$EXTENSION
        mlc_chat convert_weight $MODELS_DIR/$MODEL/config.json --device ${BACKENDS[0]}  --quantization $QUANT -o $CONVERTED_MODEL_DIR
        done
    done
    model_counter=$(( model_counter + 1 ))
done
