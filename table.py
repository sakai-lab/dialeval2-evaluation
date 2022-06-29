#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import collections
from pathlib2 import Path
import numpy as np
import pandas as pd

from kendall import Kendall

measures_dict = {
    "nugget": [
        "jsd",
        "rnss",
    ],
    "quality": [
        "rsnod",
        "nmd",
    ],
}

languages = ["chinese", "english"]

quality_scale = ["A", "S", "E"]

SCORE_DIR = Path("./dialoguebyrun")
OUTPUT_DIR = Path("./table")


def task_gen():
    for language in languages:
        for task in measures_dict.keys():
            yield language, task


def measure_gen(task):
    if task == "nugget":
        yield "", measures_dict[task]
    if task == "quality":
        for qtype in quality_scale:
            yield qtype, ["%s-%s" % (m, qtype) for m in measures_dict[task]]


def runs_statistics():
    team_counter = {}
    for language, task in task_gen():
        runs_file = SCORE_DIR / task / language / "runs"
        runs = pd.read_table(str(runs_file), names=["run"])["run"].tolist()
        runs = [tuple(run.split("-")) for run in runs]
        team_counter["%s%s" % (language, task)] = collections.Counter(
            [team for team, _ in runs if team != "BL"])

    global_teams = sorted(
        list(set([t for c in team_counter.values() for t in c.keys()])))

    data = collections.defaultdict(list)
    for team in global_teams:
        if team == "Baseline":
            continue

        data["team"].append(team)
        for k, counter in team_counter.items():
            data[k].append(counter[team])
    data["team"].append("Total")
    for k, counter in team_counter.items():
        data[k].append(sum([n for t, n in counter.items() if t != "Baseline"]))

    df = pd.DataFrame(data)
    df["total"] = df.sum(axis=1)

    return df


def one_way_anova(df):
    df_A = len(df.columns) - 1
    df_E = len(df.columns) * (len(df) - 1)
    means = df.mean()
    grand_mean = means.mean()
    S_A = len(df) * ((means - grand_mean)**2).sum()
    S_E = ((df - means)**2).sum().sum()
    S_T = S_A + S_E
    V_A = S_A / df_A
    V_E = S_E / df_E
    F_A = V_A / V_E

    result = {
        "df_A": df_A,
        "df_E": df_E,
        "S_A": S_A,
        "S_E": S_E,
        "S_T": S_T,
        "V_A": V_A,
        "V_E": V_E,
        "F_A": F_A,
    }
    return result


def sorted_results(func=None, discpower_B=1000, **kwargs):
    kendalltau = Kendall()
    results = {}
    taus = {}
    sorted_pvalues = {}
    for language, task in task_gen():
        runs_file = SCORE_DIR / task / language / "runs"
        runs = pd.read_table(str(runs_file), names=["run"])["run"].tolist()

        for qtype, measures in measure_gen(task):
            result = collections.defaultdict(list)
            result = []
            unsorted_mean_scores = []
            for measure in measures:
                dialoguebyrun_file = SCORE_DIR / task / language / \
                    ("%s.test_data.dialoguebyrun" % measure)
                pvalue_file = SCORE_DIR / task / language / \
                    ("%s.test_data.dialoguebyrun.pvalues.%d" %
                     (measure, discpower_B))

                # load scores
                scores = pd.read_table(
                    str(dialoguebyrun_file), sep=" ", names=runs)
                logging.info("Loaded scores from %s" % str(dialoguebyrun_file))

                # to calculate kendaull's tau
                unsorted_mean_scores.append(scores.mean().tolist())

                # sort mean scores
                measure = measure.replace("-", "")
                runcol = "%srun" % measure
                scorecol = "%sscore" % measure
                mean_score = scores.mean().sort_values().reset_index().rename(
                    columns={"index": runcol, 0: scorecol}, inplace=False)
                if func:
                    mean_score[scorecol] = mean_score[scorecol].apply(func)
                result.append(mean_score)

                # load pvalues
                pvalue_columns = [
                    "left_run", "right_run", "absdiff", "pvalue"]
                pvalues = pd.read_table(
                    str(pvalue_file), sep=" ", names=pvalue_columns)
                logging.info("Loaded pvalues from %s" % str(pvalue_file))
                run2rank = {run: (run_i + 1) for run_i,
                            run in enumerate(mean_score[runcol].tolist())}

                # Calculate Effect Size
                anova = one_way_anova(scores)
                pvalues["ve"] = anova["V_E"]
                pvalues["es"] = pvalues["absdiff"] / np.sqrt(pvalues["ve"])

                def switch_func(row):
                    left_rank = run2rank[row["left_run"]]
                    right_rank = run2rank[row["right_run"]]
                    min_rank = min(left_rank, right_rank)
                    if min_rank == left_rank:
                        return row["left_run"], row["right_run"], min_rank, right_rank
                    else:
                        return row["right_run"], row["left_run"], min_rank, left_rank

                sorted_pvalues[(language, task, qtype, measure)] = \
                    pd.concat([pvalues, pvalues.apply(
                        switch_func, axis=1, result_type="expand").rename(columns={
                            0: "winrun", 1: "loserun", 2: "min_rank", 3: "lose_rank"
                        }, inplace=False)
                    ], axis=1
                ).sort_values(["min_rank", "lose_rank"])[["winrun", "loserun", "absdiff", "pvalue", "es", "ve"]]

            result = pd.concat(result, axis=1)
            results[(language, task, qtype)] = result
            taus[(language, task, qtype)] = kendalltau(
                *unsorted_mean_scores, **kwargs)
    return results, taus, sorted_pvalues


def run_quality_rank(results):
    rank_data = {
        "chinese": collections.defaultdict(list),
        "english": collections.defaultdict(list),
    }

    for (lang, task, score_type), result in results.items():
        if task == "nugget":
            continue

        rank_columns = [c for c in result.columns if c.endswith("run")]
        for col in rank_columns:
            rank_data[lang]["runname"].append(col)
            for run_i, run_name in enumerate(result[col].tolist()):
                rank = run_i + 1
                rank_data[lang][run_name].append(rank)

    rank_df = {}
    for lang in rank_data.keys():
        df = pd.DataFrame(rank_data[lang])
        df = df.set_index("runname")
        sorted_run_names = sorted(df.columns.tolist())
        df = df[sorted_run_names].T

        new_df_list = []
        for qtype in quality_scale:
            filtered_columns = [
                c for c in df.columns.tolist() if c.endswith("%srun" % qtype)]
            new_df = df[filtered_columns]
            new_df.rename(columns={c: c.replace("run", "")
                                   for c in filtered_columns}, inplace=True)
            new_df["mean%s" % qtype] = new_df.mean(axis=1)
            new_df_list.append(new_df)

        df = pd.concat(new_df_list, axis=1)
        mean_columns = [c for c in df.columns.tolist() if c.startswith("mean")]
        df["meanoverall"] = df[mean_columns].mean(axis=1)

        rank_df[lang] = df

    return rank_df


def main():
    discpower_B = 5000
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    runs_statistics_file = OUTPUT_DIR / "run_stat.csv"
    runs_statistics().to_csv(str(runs_statistics_file), index=False, sep=",")
    logging.info("Saved runs statistics to %s" % str(runs_statistics_file))

    results, taus, pvalues = sorted_results(
        func=lambda s: "%1.4f" % s, bootstrap=True, B=100, discpower_B=discpower_B)  # B should be more than 100? 1000?

    rank_df = run_quality_rank(results)
    for k, df in rank_df.items():
        rank_file = OUTPUT_DIR / ("rank_%s.csv" % k)
        df.sort_values(by=["meanoverall"], ascending=True, inplace=True)
        df["meanoverall"] = df["meanoverall"].apply(lambda x: "%1.1f" % x)
        df.reset_index().rename(columns={"index": "runname"}).to_csv(
            str(rank_file), index=False, sep=",")
        logging.info("Saved a ranking information to %s" % str(rank_file))

    # Save rankings and kendall's
    for k, res in results.items():
        res_file = OUTPUT_DIR / ("result_%s.csv" % "".join(k))
        res.to_csv(str(res_file), index=False, sep=",")
        logging.info("Saved a sorted result to %s" % str(res_file))

        tau, (ci_from, ci_to) = taus[k]  # with CI
        tau_file = OUTPUT_DIR / ("tau_%s.csv" % "".join(k))
        with tau_file.open(mode="w") as f:
            f.write("tau,cifrom,cito\n")
            f.write("%s\n" % ",".join(
                ["%1.3f" % v for v in [tau, ci_from, ci_to]]))
        logging.info("Saved a tau info to %s" % str(tau_file))

    # Save only significant pvalues
    for (l, t, q, m_and_q), p_df in pvalues.items():
        # res_file = OUTPUT_DIR / ("pvalues%d_%s.csv" % (discpower_B, "".join([l, t, m_and_q])))
        res_file = OUTPUT_DIR / ("pvalues_%s.csv" % "".join([l, t, m_and_q]))

        def pvalue_to_str(p):
            if p < 0.0001:
                return "p < 0.0001"
            else:
                return "p = %1.4f" % p
        p_df["pvaluestr"] = p_df["pvalue"].apply(pvalue_to_str)
        p_df["esstr"] = p_df["es"].apply(lambda x: "%1.3f" % x)

        # filter by pvalue
        p_df = p_df[p_df["pvalue"] <= 0.05]
        p_df["winrunstr"] = p_df["winrun"]
        p_df.loc[p_df["winrun"] == p_df["winrun"].shift(), "winrunstr"] = ""

        p_df.to_csv(str(res_file), index=False, sep=",")
        logging.info("Saved pvalues to %s" % str(res_file))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Start main function")
    main()
    logging.info("Finished main function")
