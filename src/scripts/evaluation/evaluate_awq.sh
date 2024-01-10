#!/bin/bash

MODEL_DIR=${MODEL_DIR:-"../../../melt_models_converted"}

for MODEL in TheBloke_Llama-2-7B TheBloke_Llama-2-13B TheBloke_Llama-2-7B-Chat TheBloke_Llama-2-13B-Chat TheBloke_Mistral-7B-Instruct-v0.1 TheBloke_stablelm-zephyr-3b;do
    CUDA_VISIBLE_DEVICES=1 lm-eval --model vllm --model_args pretrained=${MODEL_DIR/${MODEL}-AWQ/,tensor_parallel_size=1,dtype=auto,gpu_memory_utilization=0.8,data_parallel_size=1 --tasks winogrande,arc_easy,truthfulqa,hellaswag --batch_size auto |& tee ${MODEL}-AWQ.log
done