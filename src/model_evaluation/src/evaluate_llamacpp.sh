#!/bin/bash

MODEL_DIR=${MODEL_DIR:-"../melt_models_converted"}

for MODEL in  meta-llama_Llama-2-7b-hf mistralai_Mistral-7B-Instruct-v0.1 stabilityai_stablelm-zephyr-3b TinyLlama_TinyLlama-1.1B-Chat-v0.5; do
	for QUANT in q3_k q4_k q4_0; do
		python3 -m llama_cpp.server --model ${MODEL_DIR}/${MODEL}/${MODEL}-${QUANT}.gguf --n_gpu_layers 35 --host 0.0.0.0 --port 8084 & CUDE_VISIBLE_DEVICES=0 lm-eval --model gguf --model_args base_url="http://0.0.0.0:8084" --tasks arc_challenge --output_path results/${MODEL}_${QUANT} &&
		pkill python &&
		sleep 10
	done
done

for MODEL in meta-llama_Llama-2-7b-hf mistralai_Mistral-7B-Instruct-v0.1 stabilityai_stablelm-zephyr-3b TinyLlama_TinyLlama-1.1B-Chat-v0.5; do
	python3 -m llama_cpp.server --model ${MODEL_DIR}/${MODEL}/${MODEL}.gguf --n_gpu_layers 35 --host 0.0.0.0 --port 8084 & CUDE_VISIBLE_DEVICES=0 lm-eval --model gguf --model_args base_url="http://0.0.0.0:8084" --tasks arc_challenge --output_path results/${MODEL}_base &&
	pkill python &&
	sleep 10
done
