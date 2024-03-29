Dataset splits (partitions)
===========================

Code in this module defines the dataset train/dev/test splits.

The final splits are stored in the `data` folder in the same yaml format used by OpenScore Lieder corpus. These files are generated by this command:

```
.venv/bin/python3 -m app.datasets.splits generate
```

The test set partition is done set-independent (*set* means one collection or one book). This means there is no set, that would be partially in train/dev and partially in test.


## The generation process

First, we take all the scores in the OpenScore Lieder corpus `datasets/OpenScore-Lieder/data/scores.yaml` and remove scores listed in [`globally_ignored_scores.yaml`](globally_ignored_scores.yaml). These are scores that cannot be used for our experiments, because they are problematic when building the synthetic dataset. This includes scores that lack piano part, scores where the piano systems cannot be automatically cropped out from the images and similar issues.

This resulting collection of scores creates the starting pool from which we generate the synthetic and scanned datasets.


### Test partition

We start by taking all the *sets* from the OpenScore Lieder corpus `datasets/OpenScore-Lieder/data/sets.yaml` and shuffling them. Then we filter out sets, that have more than 5 scores (to ensure set-diversity within the test partition). Then we go through the sets and their scores and add them to the test partition, until we hit the desired count (100 scores). While doing this, we also skip scores that were problematic to annotate manually for the *scanned* dataset (these get listed in [`annotation_problematic_scores.yaml`](annotation_problematic_scores.yaml), see that file for more info). This process produces the [`data/test_scores.yaml`](data/test_scores.yaml) file.

Finally we collect all the sets from which we've taken test scores and group them to form the [`data/test_sets.yaml`](data/test_sets.yaml) file. Scores from these sets are not present in the train or the dev partition.


### Dev partition

Dev partition is built from the starting score pool defined above. We take this pool, shuffle it randomly, and start taking scores in order, until we have the desired count (100 scores). Just like with the test set, we skip scores that are problematic to annotate manually for the *scanned* dataset. In addition, we also skip scores, whose sets are listed in the [`data/test_sets.yaml`](data/test_sets.yaml).

These sets get written to [`data/dev_scores.yaml`](data/dev_scores.yaml).


### Train partition

Train partition are all the sets, that remain in the starting pool, that are not in the [`data/test_sets.yaml`](data/test_sets.yaml), nor the [`data/dev_scores.yaml`](data/dev_scores.yaml).

Here, we CAN take scores that are listed in [`annotation_problematic_scores.yaml`](annotation_problematic_scores.yaml), because the train partition is not present in the *scanned* dataset, only in the *synthetic* one.
