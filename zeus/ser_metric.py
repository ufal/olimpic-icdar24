#!/usr/bin/env python3
import os
import pickle
import re

def levenshtein_distance_pure(a: list, b: list) -> int:
    len_a, len_b = len(a), len(b)

    distances = [j for j in range(len_b + 1)]
    for i in range(1, len_a + 1):
        prev_distances, distances = distances, [i] + [0] * len_b
        for j in range(1, len_b + 1):
            distances[j] = min(
                distances[j - 1] + 1, # insertion
                prev_distances[j] + 1, # deletion
                prev_distances[j - 1] + (a[i - 1] != b[j - 1]), # substitution or match
            )

    return distances[-1]

try:
    import Levenshtein
    levenshtein_distance = Levenshtein.distance
except:
    levenshtein_distance = levenshtein_distance_pure

tuplets_exceptions = {
    "tuplet:start",
    "tuplet:stop",
}
tuplets_exception_re = re.compile(r"^\d+in\d+$")

def ser_metric(gold: list[str], pred: list[str]) -> float:
    assert len(gold) == len(pred), "Gold and predicted data must have the same length"

    ser_errors, ser_total = 0, 0
    sert_errors, sert_total = 0, 0
    for gold_lmx, pred_lmx in zip(gold, pred):
        gold_lmx = gold_lmx.rstrip("\r\n").split()
        pred_lmx = pred_lmx.rstrip("\r\n").split()

        ser_errors += levenshtein_distance(gold_lmx, pred_lmx)
        ser_total += len(gold_lmx)

        gold_tuplets = [x for x in gold_lmx if x not in tuplets_exceptions and not tuplets_exception_re.match(x)]
        pred_tuplets = [x for x in pred_lmx if x not in tuplets_exceptions and not tuplets_exception_re.match(x)]
        sert_errors += levenshtein_distance(gold_tuplets, pred_tuplets)
        sert_total += len(gold_tuplets)

    assert ser_total > 0, "Gold data cannot be empty"
    return {"SER": 100 * ser_errors / ser_total, "SERnotuplets": 100 * sert_errors / sert_total}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("gold", type=str, help="File with gold dataset")
    parser.add_argument("pred", type=str, help="File with predicted data")
    args = parser.parse_args()

    with open(f"{args.gold}.pickle", "rb") as dataset_file:
        dataset = pickle.load(dataset_file)
        gold = [entry["lmx"] for entry in dataset]
    with open(args.pred, "r", encoding="utf-8") as pred_file:
        pred = [line.rstrip("\r\n") for line in pred_file]

    for metric, value in ser_metric(gold, pred).items():
        print("{}: {:.3f}%".format(metric, value))
