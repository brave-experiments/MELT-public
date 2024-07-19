#!/bin/bash

# Note:   Script to evaluate the performance of the GPTQ models with lm-eval suite.
# Author: Stefanos Laskaridis

MODEL_DIR=${MODEL_DIR:-"../../../melt_models_converted"}

MODELS=(
    TheBloke_Llama-2-7B
    TheBloke_Llama-2-13B
    TheBloke_Mistral-7B-Instruct-v0.1
    TheBloke_TinyLlama-1.1B-Chat-v1.0
    TheBloke_stablelm-zephyr-3b
)

for MODEL in ${MODELS[@]};do
    CUDA_VISIBLE_DEVICES=0 lm-eval \
        --model hf \
        --model_args pretrained=${MODEL_DIR}/${MODEL}-GPTQ/,autogptq=model.safetensors,gptq_use_triton=True \
        --tasks winogrande,arc_easy,arc_challenge,truthfulqa,hellaswag \
        --device cuda:0 \
        --batch_size auto |& tee ${MODEL}-GPTQ.log
done
