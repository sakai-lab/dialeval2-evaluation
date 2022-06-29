#!/usr/bin/env bash

ROOT_DIR=`pwd`
DATA_DIR=`pwd`/dialoguebyrun # absolute path
SHARE_DIR=`pwd`/share

task="nugget"
for language in "chinese" "english"
do
    TARGET_DIR=$DATA_DIR/$task/$language
    DES_DIR=$SHARE_DIR/$language/$task # swap
    cd $TARGET_DIR
    mkdir -p $DES_DIR
    for measure in "jsd" "rnss"
    do
      cp $measure.test_data.csv $DES_DIR
    done
done

task="quality"
for language in "chinese" "english"
do
    TARGET_DIR=$DATA_DIR/$task/$language
    DES_DIR=$SHARE_DIR/$language/$task # swap
    cd $TARGET_DIR
    mkdir -p $DES_DIR
    for measure in "nmd" "rsnod"
    do
      for score_key in "A" "E" "S"
      do
        cp $measure-$score_key.test_data.csv $DES_DIR
      done
    done
done

cd $ROOT_DIR
touch share/tree.txt
tree share > share/tree.txt
zip -r share.zip ./share
