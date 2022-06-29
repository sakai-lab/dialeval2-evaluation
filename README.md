# dialeval2-evaluation


## Prepare the grount truth data

Put the grount truth data under `groundtruth` directory like below,

```
$ tree groundtruth
groundtruth
├── test_cn.json
└── test_en.json
```

## Prepare submitted runs (an example of DialEval-1)

```
$ tree runs
runs
├── IMTKU
│   ├── run0
│   │   ├── cn_nugget.json
│   │   ├── cn_quality.json
│   │   ├── en_nugget.json
│   │   └── en_quality.json
│   ├── run1
│   │   ├── cn_nugget.json
│   │   ├── cn_quality.json
│   │   └── en_nugget.json
│   └── run2
│       ├── cn_nugget.json
│       ├── cn_quality.json
│       └── en_nugget.json
├── NKUST
│   ├── run0
│   │   ├── nugget_cn.json
│   │   ├── nugget_en.json
│   │   ├── quality_cn.json
│   │   └── quality_en.json
│   └── run1
│       ├── nugget_cn.json
│       └── quality_cn.json
├── RSLNV
│   ├── run0
│   │   ├── cn_nugget_test_submission.json
│   │   ├── cn_quality_test_submission.json
│   │   ├── en_nugget_test_submission.json
│   │   └── en_quality_test_submission.json
│   ├── run1
│   │   └── en_nuggets_200_02_shi.json
│   └── run2
│       └── nugget_chinese_test_submission.json
├── SKYMN
│   ├── run0
│   │   └── quality_en.json
│   ├── run1
│   │   └── quality_en.json
│   └── run2
│       └── quality_en.json
├── TMUDS
│   ├── run0
│   │   └── cn_nugget.json
│   ├── run1
│   │   └── cn_nugget.json
│   └── run2
│       └── cn_nugget.json
├── TUA1
│   ├── run0
│   │   ├── cn_nugget.json
│   │   └── cn_quality.json
│   ├── run1
│   │   └── cn_quality.json
│   └── run2
│       └── cn_quality.json
└── WUST
    └── run0
        ├── nugget_cn_submission.json
        └── quality_cn_submission.json

25 directories, 34 files
```

## Prepare baseline models

### Uniform distribution model and Popularity model

```
$ bash prepare.sh
```

| Run Name | Desc |
|:--|:--|
| run1 | uniform distribution |
| run2 | popularity distribution |

### Check baseline outputs

```
$ tree runs/Baseline/
runs/Baseline/
├── run0
│   ├── nugget_cn.json
│   ├── nugget_en.json
│   ├── quality_cn.json
│   └── quality_en.json
├── run1
│   ├── nugget_cn.json
│   ├── nugget_en.json
│   ├── quality_cn.json
│   └── quality_en.json
└── run2
    ├── nugget_cn.json
    ├── nugget_en.json
    ├── quality_cn.json
    └── quality_en.json

3 directories, 12 files
```

## Testing

### Install Discpower

```
$ wget http://research.nii.ac.jp/ntcir/tools/Discpower160507.tar.gz
$ mkdir Discpower
$ tar xvfz ./Discpower160507.tar.gz -C ./Discpower
$ cd ./Discpower
$ make
$ sudo make install
$ sudo apt install gawk # if necessary
$ which gawk
/usr/bin/gawk
```

### Calculate measures

```
$ bash calc.sh
```

### Check dialogue-by-run scores

```
$ tree ./dialoguebyrun
./dialoguebyrun
├── nugget
│   ├── chinese
│   │   ├── jsd.test_data.csv
│   │   ├── jsd.test_data.dialoguebyrun
│   │   ├── rnss.test_data.csv
│   │   ├── rnss.test_data.dialoguebyrun
│   │   └── runs
│   └── english
│       ├── jsd.test_data.csv
│       ├── jsd.test_data.dialoguebyrun
│       ├── rnss.test_data.csv
│       ├── rnss.test_data.dialoguebyrun
│       └── runs
└── quality
    ├── chinese
    │   ├── nmd-A.test_data.csv
    │   ├── nmd-A.test_data.dialoguebyrun
    │   ├── nmd-E.test_data.csv
    │   ├── nmd-E.test_data.dialoguebyrun
    │   ├── nmd-S.test_data.csv
    │   ├── nmd-S.test_data.dialoguebyrun
    │   ├── rsnod-A.test_data.csv
    │   ├── rsnod-A.test_data.dialoguebyrun
    │   ├── rsnod-E.test_data.csv
    │   ├── rsnod-E.test_data.dialoguebyrun
    │   ├── rsnod-S.test_data.csv
    │   ├── rsnod-S.test_data.dialoguebyrun
    │   └── runs
    └── english
        ├── nmd-A.test_data.csv
        ├── nmd-A.test_data.dialoguebyrun
        ├── nmd-E.test_data.csv
        ├── nmd-E.test_data.dialoguebyrun
        ├── nmd-S.test_data.csv
        ├── nmd-S.test_data.dialoguebyrun
        ├── rsnod-A.test_data.csv
        ├── rsnod-A.test_data.dialoguebyrun
        ├── rsnod-E.test_data.csv
        ├── rsnod-E.test_data.dialoguebyrun
        ├── rsnod-S.test_data.csv
        ├── rsnod-S.test_data.dialoguebyrun
        └── runs

```

### Perform Randomized Tukey HSD Test

```
$ mkdir logs
$ nohup bash compare.sh 10 1> logs/compare.10.out 2> logs/compare.10.err & # about 8 minutes
$ nohup bash compare.sh 1000 1> logs/compare.1000.out 2> logs/compare.1000.err &
$ nohup bash compare.sh 10000 1> logs/compare.10000.out 2> logs/compare.10000.err &
```

NOTE: Calculating time shown [here](logs/compare.1000.out) (about 2days when B set to 1000)


### Install NSM3

To calculate confidence intervals with Kendall's tau

```
$ sudo apt install libgmp3-dev # for the gmp package which is one of dependencies of NSM3 package
$ R
> install.packages("NSM3", dependencies = TRUE)
```

### Save Tables of Results

```
$ python table.py
$ sed -i -e 's/Baseline-run0/BL-lstm/g' -e 's/Baseline-run1/BL-uniform/g' -e 's/Baseline-run2/BL-popularity/g' -e 's/\n$//' table/*.csv
```

Copy these csv files to the latex project

```
$ tree table
table
├── pvalues_chinesenuggetjsd.csv
├── pvalues_chinesenuggetrnss.csv
├── pvalues_chinesequalitynmdA.csv
├── pvalues_chinesequalitynmdE.csv
├── pvalues_chinesequalitynmdS.csv
├── pvalues_chinesequalityrsnodA.csv
├── pvalues_chinesequalityrsnodE.csv
├── pvalues_chinesequalityrsnodS.csv
├── pvalues_englishnuggetjsd.csv
├── pvalues_englishnuggetrnss.csv
├── pvalues_englishqualitynmdA.csv
├── pvalues_englishqualitynmdE.csv
├── pvalues_englishqualitynmdS.csv
├── pvalues_englishqualityrsnodA.csv
├── pvalues_englishqualityrsnodE.csv
├── pvalues_englishqualityrsnodS.csv
├── rank_chinese.csv
├── rank_english.csv
├── result_chinesenugget.csv
├── result_chinesequalityA.csv
├── result_chinesequalityE.csv
├── result_chinesequalityS.csv
├── result_englishnugget.csv
├── result_englishqualityA.csv
├── result_englishqualityE.csv
├── result_englishqualityS.csv
├── run_stat.csv
├── tau_chinesenugget.csv
├── tau_chinesequalityA.csv
├── tau_chinesequalityE.csv
├── tau_chinesequalityS.csv
├── tau_englishnugget.csv
├── tau_englishqualityA.csv
├── tau_englishqualityE.csv
└── tau_englishqualityS.csv
```
