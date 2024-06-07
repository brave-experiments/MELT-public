#!/bin/bash

MODEL_DIR=${MODEL_DIR:-"../../../melt_models_converted"}

for MODEL in TheBloke_Llama-2-7B TheBloke_Llama-2-13B TheBloke_Llama-2-7B-Chat TheBloke_Llama-2-13B-Chat TheBloke_Mistral-7B-Instruct-v0.1 TheBloke_stablelm-zephyr-3b;do
    CUDA_VISIBLE_DEVICES=0 lm-eval --model hf --model_args pretrained=${MODEL_DIR}/${MODEL}-GPTQ/,autogptq=model.safetensors,gptq_use_triton=True --tasks winogrande,arc_easy,truthfulqa,hellaswag --device cuda:0 --batch_size auto |& tee ${MODEL}-GPTQ.log
done
