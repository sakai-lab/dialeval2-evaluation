# -*- coding: utf-8 -*-

import logging
import pyper
import scipy.stats as stats


class Kendall(object):

    def __init__(self):
        # Scipy: https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.stats.kendalltau.html
        # NSM3: https://www.rdocumentation.org/packages/NSM3/versions/1.12/topics/kendall.ci
        self.r = pyper.R()
        lines = self.r("library('NSM3')").split("\n")
        for line in lines:
            logging.debug(line)

    def __call__(self, v1, v2, alpha=0.05, **kwargs):
        tau, p_value = stats.kendalltau(v1, v2)
        ci = self.kendallci(v1, v2, alpha=alpha, **kwargs)
        return tau, ci

    def kendallci(self, v1, v2, alpha=0.05, **kwargs):
        """
> library(NSM3)
 要求されたパッケージ combinat をロード中です

 次のパッケージを付け加えます: ‘combinat’

 以下のオブジェクトは ‘package:utils’ からマスクされています:

     combn

 要求されたパッケージ MASS をロード中です
 要求されたパッケージ partitions をロード中です
 要求されたパッケージ survival をロード中です
fANCOVA 0.5-1 loaded
> v1 <- c(0.1263204008629143, 0.253230044463714, 0.24779460545872947, 0.12733346562130227, 0.1306136830069791, 0.12354453533699049, 0.12485923673067538, 0.1251284421500735, 0.12743200545590785, 0.12629784321265006)
> v2 <- c(0.08629486056653916, 0.16765069725596002, 0.1855465587044534, 0.08586856743903766, 0.08314152868486221, 0.08191686331440169, 0.08428872932669466, 0.08359861901724305, 0.08597891084094667, 0.08453251372206536)
> kendall.ci(v1, v2, alpha=0.05, bootstrap=F)

1 - alpha = 0.95 two-sided CI for tau:
0.086, 1.026

> kendall.ci(v1, v2, alpha=0.05, bootstrap=T, B=10000)

1 - alpha = 0.95 two-sided CI for tau:
0, 0.952
"""
        self.r.assign("v1", v1)
        self.r.assign("v2", v2)
        if not kwargs.get("bootstrap", None):
            lines = self.r(
                "kendall.ci(v1, v2, alpha=%f, bootstrap=FALSE)" % alpha).split("\n")
        else:
            lines = self.r("kendall.ci(v1, v2, alpha=%f, bootstrap=TRUE, B=%d)" % (
                alpha, kwargs["B"])).split("\n")
        ci = list(map(float, lines[3].replace(" ", "").split(",")))
        logging.info("CI: %s (%s)" % (ci, lines[3]))
        return ci
