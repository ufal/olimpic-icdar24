# OLiMPiC dataset - an ICDAR 2024 Paper

This repository contains the source code for the article:

> **Practical End-to-End Optical Music Recognition for Pianoform Music**<br>
> (the article is yet to be published)

In which we:

1. Create a dataset of synthetic and scanned pianoform music for end-to-end OMR, called OLiMPiC. The dataset is built upon the [OpenScore Lieder Corpus](https://github.com/OpenScore/Lieder).
2. We introduce the LMX format (Linearized MusicXML) and define the linearization and delinearization procedures (see [MusicXML Linearization](#musicxml-linearization) section).
3. We train a baseline, state-of-the-art model called Zeus on this dataset (see [Zeus model](#zeus-model) and [TEDn evaluation metric](#tedn-evaluation-metric) sections).
4. We compare our dataset and model to the [GrandStaff dataset](https://link.springer.com/article/10.1007/s10032-023-00432-z).

If you want to start tinkering with the code, read the [After cloning](#after-cloning) section. If you build upon this work, read the [Acknowledgement](#acknowledgement) section.


## MusicXML Linearization


## Datasets


## Zeus model


## TEDn evaluation metric


## After cloning

Setup Python venv (tested with python 3.10.12):

```bash
python3 -m venv .venv

.venv/bin/pip3 install --upgrade pip

# to run the linearization, dataset building, and evaluation
.venv/bin/pip3 install -r requirements.txt

# to run the Zeus model
# TODO:
.venv/bin/pip3 install -r requirements-zeus.txt
```

Install dependencies:

```bash
# to be able to build the datasets yourself
make install-musescore
make install-open-score-lieder-dataset

# to just download the finished datasets
# (from this repo's releases page)
make install-scanned-dataset
make install-synthetic-dataset
```


## Acknowledgement

TODO: To be added once published.
