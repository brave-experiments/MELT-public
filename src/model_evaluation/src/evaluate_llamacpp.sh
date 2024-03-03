#!/bin/bash

MODEL_DIR=${MODEL_DIR:-"../melt_models_converted"}

TASKS=("winogrande" "arc_easy" "arc_challenge" "truthfulqa" "hellaswag")
MODELS=("google_gemma-2b" "google_gemma-7b")
QUANTS=("q3_k" "q4_k" "q4_0")

counter=0
for MODEL in ${MODELS[@]}; do
    for QUANT in ${QUANTS[@]}; do
        port=$((8084 + counter))
        echo "Running server model ${MODEL} with quantization ${QUANT}"
        (python3 -m llama_cpp.server --model ${MODEL_DIR}/${MODEL}/${MODEL}-${QUANT}.gguf --n_gpu_layers 100 --host 0.0.0.0 --port $port |& tee server_${MODEL}-${QUANT}.log) &
        counter=$((counter + 1))
    done
done


counter=0
for MODEL in ${MODELS[@]}; do
    for QUANT in ${QUANTS[@]}; do
        port=$((8084 + counter))
        for TASK in ${TASKS[@]};do
            (lm-eval --model gguf --model_args base_url="http://0.0.0.0:${port}" --tasks $TASK --output_path results/${MODEL}_${QUANT} |& tee eval_${MODEL}-${QUANT}_${TASK}.log) &
        done
        counter=$((counter + 1))
    done
done