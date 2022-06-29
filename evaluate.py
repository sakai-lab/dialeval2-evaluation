# -*- coding: utf-8 -*-


from collections import Counter, defaultdict
from copy import deepcopy

import numpy as np

from stc3dataset.data.eval import (
    C_NUGGET_TYPES,
    H_NUGGET_TYPES,
    QUALITY_SCALES,
)


def evaluate_nugget_measure(pred, truth, measure, alpha=.5, strict=False):
    def _truth2prob(labels, nugget_types):
        c = Counter(labels)
        prob = []
        for nugget_type in nugget_types:
            prob.append(c.get(nugget_type, 0))
        prob = np.array(prob, dtype=np.float64)
        prob /= prob.sum()
        return prob

    def _pred_2_prob(score_dict, nugget_types):
        score_dict = deepcopy(score_dict)
        prob = np.array([score_dict.pop(nugget_type, 0)
                         for nugget_type in nugget_types])
        if score_dict:
            raise ValueError("contain illegal nugget type in prediction")
        return prob

    prediction = pred["nugget"]
    is_customer = [t["sender"] == "customer" for t in truth["turns"]]
    if len(is_customer) != len(prediction):
        raise ValueError("#turns != #nugget_predictions")
    c_turn_scores = []
    h_turn_scores = []
    for i, turn_pred in enumerate(prediction):
        nugget_types = C_NUGGET_TYPES if is_customer[i] else H_NUGGET_TYPES
        truth_labels = (anno["nugget"][i]
                        for anno in truth["annotations"])

        truth_prob = _truth2prob(truth_labels, nugget_types)
        score = measure(
            _pred_2_prob(turn_pred, nugget_types),
            truth_prob)
        if is_customer[i]:
            c_turn_scores.append(score)
        else:
            h_turn_scores.append(score)
    return np.mean(c_turn_scores) * alpha + np.mean(h_turn_scores) * (1 - alpha)


def evaluate_quality_measure(pred, truth, measure, strict=False):
    def _truth2prob(labels):
        c = Counter(labels)
        prob = []
        for scale in QUALITY_SCALES:
            score = c.pop(scale, 0)
            prob.append(score)
        prob = np.array(prob, dtype=np.float64)
        prob /= prob.sum()
        return prob

    def _pred_2_prob(score_dict):
        score_dict = deepcopy(score_dict)
        prob = np.array(
            [score_dict.pop(scale, 0) for scale in QUALITY_SCALES])
        if score_dict:
            raise ValueError("contain illegal quality scale in prediction")
        return prob

    if strict:
        check_missing_prediction(id2pred, id2truth)

    scores = {}
    prediction = pred["quality"]
    for score_key in prediction:
        truth_labels = (str(anno["quality"][score_key])
                        for anno in truth["annotations"])
        score = measure(
            _pred_2_prob(prediction[score_key]),
            _truth2prob(truth_labels))
        scores[score_key] = score

    return scores
