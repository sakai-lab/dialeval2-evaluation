#!/usr/bin/env bash

TEST=/Users/sijietao/Discpower/Random-test
DATA_DIR=`pwd`/dialoguebyrun # absolute path

task="nugget"
for language in "chinese" "english"
do
    TARGET_DIR=$DATA_DIR/$task/$language
    cd $TARGET_DIR
    echo `date '+%Y/%m/%d %H:%M:%S'`" cd "`pwd`
    for measure in "jsd" "rnss"
    do
      echo `date '+%Y/%m/%d %H:%M:%S'`" Start "$TEST" runs $measure.test_data.dialoguebyrun $@"
      $TEST runs $measure.test_data.dialoguebyrun $@ || exit 1
      echo `date '+%Y/%m/%d %H:%M:%S'`" Finished "$TEST" runs $measure.test_data.dialoguebyrun $@"
    done
done

task="quality"
for language in "chinese" "english"
do
    TARGET_DIR=$DATA_DIR/$task/$language
    cd $TARGET_DIR
    echo `date '+%Y/%m/%d %H:%M:%S'`" cd "`pwd`
    for measure in "nmd" "rsnod"
    do
      for score_key in "A" "E" "S"
      do
        echo `date '+%Y/%m/%d %H:%M:%S'`" Start "$TEST" runs $measure-$score_key.test_data.dialoguebyrun $@"
        $TEST runs $measure-$score_key.test_data.dialoguebyrun $@ || exit 1
        echo `date '+%Y/%m/%d %H:%M:%S'`" Finished "$TEST" runs $measure-$score_key.test_data.dialoguebyrun $@"
      done
    done
done

# INCOMING_URL=""
# curl -X POST -H 'Content-type: application/json' --data '{"text":"Finished compare.sh '$@'"}' $INCOMING_URL
