#!/usr/bin/env bash

DATA_DIR=run_and_groundtruth
OUTPUT_DIR=output

# CUIS
unzip $DATA_DIR/CUIS.zip -d $OUTPUT_DIR/
rm -r $OUTPUT_DIR/__MACOSX/

# WIDM
unzip $DATA_DIR/WIDM.zip -d $OUTPUT_DIR/WIDM/

# WUST
unzip $DATA_DIR/WUST.zip  -d $OUTPUT_DIR/WUST/

# SLSTC
mkdir $OUTPUT_DIR/SLSTC
unzip  $DATA_DIR/SLSTC_rikiya.zip -d $OUTPUT_DIR/SLSTC/
mv $OUTPUT_DIR/SLSTC/SLSTC_rikiya $OUTPUT_DIR/SLSTC/run0
mkdir $OUTPUT_DIR/SLSTC/run1
unzip $DATA_DIR/SLSTC_DQ.zip -d $OUTPUT_DIR/
unzip $DATA_DIR/SLSTC_ND.zip -d $OUTPUT_DIR/
mv $OUTPUT_DIR/SLSTC_ND/run1/cn.json $OUTPUT_DIR/SLSTC/run1/cn_nugget.json
mv $OUTPUT_DIR/SLSTC_ND/run1/en.json $OUTPUT_DIR/SLSTC/run1/en_nugget.json
mv $OUTPUT_DIR/SLSTC_DQ/run1/cn.json $OUTPUT_DIR/SLSTC/run1/cn_quality.json
mv $OUTPUT_DIR/SLSTC_DQ/run1/en.json $OUTPUT_DIR/SLSTC/run1/en_quality.json
rm -r $OUTPUT_DIR/SLSTC_ND
rm -r $OUTPUT_DIR/SLSTC_DQ
unzip $DATA_DIR/zzh.zip -d $OUTPUT_DIR/SLSTC/
mv $OUTPUT_DIR/SLSTC/zzh $OUTPUT_DIR/SLSTC/run2
