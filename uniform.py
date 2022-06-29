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


class UniformPredictor(PseudoPredictor):

    def transform(self, dist):
        N = len(dist)
        uni = [1.0 / N for _ in range(N)]
        return uni


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    predictor = UniformPredictor()
    test_prediction = predictor.predict_test()
