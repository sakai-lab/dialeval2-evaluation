#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import datetime
import json
import logging
import time
from collections import Counter
from pathlib2 import Path


from pseudo import PseudoPredictor


class PopularityPredictor(PseudoPredictor):

    def transform(self, dist):
        max_prob = np.max(dist)
        max_count = sum(dist >= max_prob)
        # if sum(dist >= max_prob) > 1:
        #     raise Exception("sum(dist >= max_prob) > 1")
        pop = [1.0 / max_count if p == max_prob else 0.0 for p in dist]
        return pop


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    predictor = PopularityPredictor()
    test_prediction = predictor.predict_test()
