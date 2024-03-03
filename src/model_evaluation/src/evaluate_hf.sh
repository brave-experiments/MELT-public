#!/bin/bash

MODELS=(google_gemma-2b google_gemma-7b)
TASKS=(winogrande arc_easy arc_challenge truthfulqa hellaswag)


for MODEL in ${MODELS[@]}; do
    for TASK in ${TASKS[@]}; do
        echo "Evaluating $MODEL on task $TASK"
        (lm_eval --model hf --model_args pretrained=$MODEL --tasks $TASK --batch_size auto |& tee eval_${MODEL}_${TASK}.log) &
    done
done
~