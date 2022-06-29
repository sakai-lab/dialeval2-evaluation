# -*- coding: utf-8 -*-

import numpy as np
import datetime
import json
import logging
import time
from collections import Counter

from pathlib2 import Path

from stc3dataset.data.eval import (
    H_NUGGET_TYPES,
    C_NUGGET_TYPES,
)
from data import (
    Task,
    CUSTOMER_NUGGET_TYPES_WITH_PAD,
    HELPDESK_NUGGET_TYPES_WITH_PAD,
    QUALITY_MEASURES,
    QUALITY_SCALES,
    customer_nugget_pred_to_dict,
    helpdesk_nugget_pred_to_dict,
)
from flags import define_flags
from train import flags2params


class GroundTruthIterator():

    def __init__(self, test_path, task=Task.nugget):
        self.test_path = test_path
        self.task = task
        self.raw_test = json.load(test_path.open())

    def __iter__(self):
        if self.task == Task.nugget:
            return self.gen_nugget_truth()
        if self.task == Task.quality:
            return self.gen_quality_truth()

    def gen_nugget_truth(self):
        def _truth2prob(labels, nugget_types):
            c = Counter(labels)
            prob = []
            for nugget_type in nugget_types:
                prob.append(c.get(nugget_type, 0))
            prob = np.array(prob, dtype=np.float64)
            prob /= prob.sum()
            return prob

        for d in self.raw_test:
            is_customer = [t["sender"] == "customer" for t in d["turns"]]
            dist_list = []
            for i, t in enumerate(d["turns"]):
                nugget_types = CUSTOMER_NUGGET_TYPES_WITH_PAD if is_customer[
                    i] else HELPDESK_NUGGET_TYPES_WITH_PAD
                truth_labels = (anno["nugget"][i]
                                for anno in d["annotations"])
                dist = _truth2prob(truth_labels, nugget_types)
                dist_list.append(dist)

            yield d["id"], dist_list, is_customer

    def gen_quality_truth(self):
        def _truth2prob(labels):
            c = Counter(labels)
            prob = []
            for scale in QUALITY_SCALES:
                score = c.pop(scale, 0)
                prob.append(score)
            prob = np.array(prob, dtype=np.float64)
            prob /= prob.sum()
            return prob

        for d in self.raw_test:
            dists = {}
            for score_key in QUALITY_MEASURES:
                truth_labels = (str(anno["quality"][score_key])
                                for anno in d["annotations"])
                dist = _truth2prob(truth_labels)
                dists[str(score_key)] = dist

            yield d["id"], dists


class PseudoPredictor():

    def __init__(self, customized_params=None):
        flags = define_flags()
        flags.output_dir = Path(flags.output_dir)
        params = flags2params(flags, customized_params)

        self.logger = logging.getLogger(__name__)
        self.logger.info("Task: " + str(params.task))
        self.logger.info("Language: " + str(params.language))
        self.task = params.task
        self.language = params.language
        self.output_dir = params.output_dir
        self.data_dir = Path(params.data_dir)

        test_path = self.data_dir / "test_en.json"
        self.test_iterator = GroundTruthIterator(test_path, task=self.task)

    def transform(self, dist):
        return dist

    def to_submission(self, result):
        if self.task == Task.nugget:
            dialog_id, dist_list, is_customer_list = result
            nugget_list = []
            for is_customer, dist in zip(is_customer_list, dist_list):
                if is_customer:
                    try:
                        dist = self.transform(dist)
                    except Exception as e:
                        print(dialog_id, is_customer, dist)
                        # import ipdb
                        # ipdb.set_trace()
                    nugget_list.append(customer_nugget_pred_to_dict(dist))
                else:
                    try:
                        dist = self.transform(dist)
                    except Exception as e:
                        print(dialog_id, is_customer, dist)
                        # import ipdb
                        # ipdb.set_trace()
                    nugget_list.append(helpdesk_nugget_pred_to_dict(dist))
            submission_format = {
                "id": dialog_id,
                "nugget": nugget_list
            }
            return submission_format

        elif self.task == Task.quality:
            dialog_id, dists = result
            result = {}
            for score_key, dist in dists.items():
                result[score_key] = {}
                try:
                    dist = self.transform(dist)
                except Exception as e:
                    print(dialog_id, dist)
                    # import ipdb
                    # ipdb.set_trace()
                for scale, prob in zip(QUALITY_SCALES, dist):
                    result[score_key][str(scale)] = float(prob)
            submission_format = {
                "id": dialog_id,
                "quality": result
            }
            return submission_format

    def predict_test(self, write_to_file=True):
        submission = []
        for test_result in self.test_iterator:
            submission.append(self.to_submission(test_result))

        if write_to_file:
            language_name = "cn" if self.language.name == "chinese" else "en"
            output_file = self.output_dir / \
                ("%s_%s.json" %
                 (self.task.name, language_name))
            output_file.parent.mkdir(parents=True, exist_ok=True)
            json.dump(submission, output_file.open("w"))

        return submission
