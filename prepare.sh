#!/usr/bin/env bash

DATA_DIR=groundtruth

export PYTHONPATH="${PYTHONPATH}:`pwd`/stc3-baseline"

mkdir -p ./runs/Baseline/run1
for task in "nugget" "quality"
do
    for language in "chinese" "english"
    do
        python uniform.py --task $task --language $language --data-dir $DATA_DIR --output-dir ./runs/Baseline/run1 $@ || exit 1
    done
done

mkdir -p ./runs/Baseline/run2
for task in "nugget" "quality"
do
    for language in "chinese" "english"
    do
        python popularity.py --task $task --language $language --data-dir $DATA_DIR --output-dir ./runs/Baseline/run2 $@ || exit 1
    done
done
