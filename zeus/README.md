Zeus Recognizer for OLiMPiC 1.0
===============================

Zeus is an OMR recognizer for OLiMPiC 1.0 dataset.

Creating Dataset Pickles
------------------------

To use Zeus, datasets must be processed to a pickle format by running
```sh
python3 create_pickle.py DATASET_DIRECTORY SPLIT
```
where
- `DATASET_DIRECTORY` is a directory where OLiMPiC 1.0 or GrandStaff-LMX has
  been extracted, for example `olimpic-1.0-synthetic`
- `SPLIT` is either `train`, `dev`, or `test`

Training a Model
----------------

To train a model, run for example
```sh
python3 zeus.py --train olimpic-1.0-synthetic-train --dev olimpic-1.0-synthetic-dev olimpic-1.0-scanned-dev --test olimpic-1.0-synthetic-test olimpic-1.0-scanned-test --epochs=200
```
- the development data are evaluated every epoch
- the test data are evaluated once at the end of training
- the trained model and the dev and test predictions are stored in
  a subdirectory of `logs` directory

If you want to train using augmentations, you can add option
```sh
--augment=h:8,rotate:1,v:4,de,en3:0.2,n:0.01,c:-1:1,b:-0.5:0.2
```
which is the set of augmentations we utilize.

Prediction with the zeus-olimpic-1.0-2024-02-12.model
-----------------------------------------------------

The `zeus-olimpic-1.0-2024-02-12.model` is an OMR model trained using the above
augmentations, which we release under the CC BY-SA license. It can be downloaded
from https://github.com/ufal/olimpic-icdar24/releases .

After unpacking, you can run prediction using this model by running
```sh
python3 zeus.py --load zeus-olimpic-1.0-2024-02-12.model --exp TARGET_DIRECTORY --test INPUT_DATASET_1 [INPUT_DATASET_2 ...]
```
The predictions are stored in the `TARGET_DIRECTORY`, togehter with the SER
metrics.

Computing TEDn Metric
---------------------

The TEDn metric can be computed using a gold dataset pickle and LMX predictions
by running
```sh
python3 tedn_metric.py GOLD_DATASET PREDICTED_LMX --flavor FLAVOR --workers WORKERS
```
- the `FLAVOR` can be either `full` or `lmx`
- because the metric is computation intensive, we recommend using multiple
  workers (for example 32 workers and 128GB RAM).
