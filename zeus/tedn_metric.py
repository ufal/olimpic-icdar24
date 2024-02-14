#!/usr/bin/env python3
import multiprocessing
import pickle
import sys

sys.path.append("..")
from app.evaluation.TEDn_lmx_xml import TEDn_lmx_xml

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("gold", type=str, help="Gold dataset")
    parser.add_argument("pred", type=str, help="File with predicted LMX")
    parser.add_argument("--flavor", default="full", choices=["full", "lmx"], help="Flavor of the evaluation")
    parser.add_argument("--verbose", default=1, type=int, help="Verbosity level")
    parser.add_argument("--workers", default=1, type=int, help="Number of workers to use")
    args = parser.parse_args()

    with open(f"{args.gold}.pickle", "rb") as dataset_file:
        gold = pickle.load(dataset_file)
    with open(args.pred, "r", encoding="utf-8") as pred_file:
        pred = [line.rstrip("\r\n") for line in pred_file]

    def TEDn_metric(inputs):
        gold, pred = inputs
        return TEDn_lmx_xml(pred, gold, flavor=args.flavor)

    total_gold_cost, total_edit_cost = 0, 0
    with multiprocessing.Pool(args.workers) as pool:
        total = 0
        for result in pool.imap_unordered(TEDn_metric, sorted(zip([entry["musicxml"] for entry in gold], pred), key=lambda x: len(x[1]), reverse=True)):
            total_gold_cost += result.gold_cost
            total_edit_cost += result.edit_cost
            total += 1
            if args.verbose and total % 10 == 0:
                print("Processed", total, "files", end="\r", file=sys.stderr)
    if args.verbose:
        print("Done", file=sys.stderr)

    print("TEDn-{}: {:.3f}%".format(args.flavor, 100 * total_edit_cost / total_gold_cost))
