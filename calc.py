#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import glob
import collections
from pathlib2 import Path


from stc3dataset.data.eval import (
    jensen_shannon_div,
    root_normalized_squared_error,
    rsnod,
    normalized_match_dist,
)
from data import QUALITY_MEASURES  # ("A", "E", "S")

from evaluate import (
    evaluate_nugget_measure,
    evaluate_quality_measure,
)

measures = {
    "nugget": {
        "jsd": jensen_shannon_div,
        "rnss": root_normalized_squared_error,
    },
    "quality": {
        "rsnod": rsnod,
        "nmd": normalized_match_dist,
    },
}

languages = ["chinese", "english"]

TRUTH_PATH = "./groundtruth/test_en.json"
GLOB_RUN_PATH = "./runs/**/**/*.json"
OUTPUT_DIR = "./dialoguebyrun"


class Runs():

    def __init__(self, output_dir):
        self.dir = Path(output_dir)
        self.task2runs = {t: {l: [] for l in languages}
                          for t in ["nugget", "quality"]}

    def add(self, task, lang, run_name):
        self.task2runs[task][lang].append(run_name)

    def __call__(self, task):
        for measure, measure_func in measures[task].items():
            for lang in languages:
                run_names = sorted(self.task2runs[task][lang])

                run_name_file = self.dir / task / lang / "runs"
                run_name_file.parent.mkdir(parents=True, exist_ok=True)
                if not run_name_file.exists():
                    with run_name_file.open(mode="w") as f:
                        for run_name in run_names:
                            f.write("%s\n" % run_name)
                    logging.info("Created %s" % str(run_name_file))

                yield lang, measure, measure_func, run_names, run_name_file


def get_lang_and_tasks(path):
    team_name = path.parent.parent.name
    run_num = path.parent.name
    run_name = "%s-%s" % (team_name, run_num)
    jsonname = path.name

    lang = ""
    if "en" in jsonname:
        lang = "english"
    if "cn" in jsonname or "chinese" in jsonname:
        lang += "chinese"
    if not lang in ["english", "chinese"]:
        raise Exception("Invalid: %s" % path)

    json_data = json.load(open(path, encoding="utf-8"))
    id2pred = {d["id"]: d for d in json_data}

    subtasks = []
    if "nugget" in json_data[0]:
        subtasks.append("nugget")
    if "quality" in json_data[0]:
        subtasks.append("quality")

    return run_name, lang, subtasks, id2pred


def main():
    truth_data = json.load(open(TRUTH_PATH, encoding="utf-8"))
    id2truth = {d["id"]: d for d in truth_data}

    runs = Runs(OUTPUT_DIR)
    run2id2pred = {t: {l: {} for l in languages}
                   for t in ["nugget", "quality"]}

    run_path_list = Path().glob(GLOB_RUN_PATH)
    for jsonpath in run_path_list:
        run_name, lang, tasks, id2pred = get_lang_and_tasks(jsonpath)
        for task in tasks:
            runs.add(task, lang, run_name)
            run2id2pred[task][lang][run_name] = id2pred

    task = "nugget"
    for lang, measure, measure_func, run_names, run_name_file in runs(task):
        output_file = run_name_file.parent / \
            ("%s.test_data.dialoguebyrun" % measure)
        logging.info("Writing scores into %s" % str(output_file))
        f = output_file.open(mode="w")

        csv_file = run_name_file.parent / ("%s.test_data.csv" % measure)
        logging.info("Writing columns and scores into %s" % str(csv_file))
        csv_f = csv_file.open(mode="w")
        csv_f.write("%s,%s\n" % ("dialogue_id", ",".join(run_names)))

        for idx, truth in id2truth.items():
            scores = []
            for run_name in run_names:
                pred = run2id2pred[task][lang][run_name][idx]
                score = evaluate_nugget_measure(pred, truth, measure_func)
                scores.append(score)
            f.write("%s\n" % " ".join(map(str, scores)))
            csv_f.write("%s,%s\n" % (idx, ",".join(map(str, scores))))
        f.close()
        csv_f.close()
        logging.info("Wrote scores into %s" % str(output_file))
        logging.info("Wrote columns and scores into %s" % str(csv_file))

    task = "quality"
    for lang, measure, measure_func, run_names, run_name_file in runs(task):
        output_files = {score_key: run_name_file.parent /
                        ("%s-%s.test_data.dialoguebyrun" % (measure, score_key))
                        for score_key in QUALITY_MEASURES}  # ("A", "E", "S")
        for output_file in output_files.values():
            logging.info("Writing scores into %s" % str(output_file))
        f = {k: output_file.open(mode="w")
             for k, output_file in output_files.items()}

        csv_files = {score_key: run_name_file.parent /
                     ("%s-%s.test_data.csv" % (measure, score_key))
                     for score_key in QUALITY_MEASURES}  # ("A", "E", "S")
        for csv_file in csv_files.values():
            logging.info("Writing columns and scores into %s" % str(csv_file))
        csv_f = {k: csv_file.open(mode="w")
                 for k, csv_file in csv_files.items()}
        for k in csv_f.keys():
            csv_f[k].write("%s,%s\n" % ("dialogue_id", ",".join(run_names)))

        for idx, truth in id2truth.items():
            scores_dict = collections.defaultdict(list)
            for run_name in run_names:
                pred = run2id2pred[task][lang][run_name][idx]
                score = evaluate_quality_measure(pred, truth, measure_func)
                for k, v in score.items():
                    scores_dict[k].append(v)
            for k in f.keys():
                f[k].write("%s\n" % " ".join(map(str, scores_dict[k])))
            for k in csv_f.keys():
                csv_f[k].write("%s,%s\n" %
                               (idx, ",".join(map(str, scores_dict[k]))))
        for k in f.keys():
            f[k].close()
            logging.info("Wrote scores into %s" % str(output_files[k]))
        for k in csv_f.keys():
            csv_f[k].close()
            logging.info("Wrote columns and cores into %s" % str(csv_files[k]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
