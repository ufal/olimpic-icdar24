> 📢 **Want to train an end-to-end OMR model?** Check out the refactored code in two separate repositories:
> - 🌩️ [**Zeus model**](https://github.com/OmniOMR/zeus) - CLI for inference and training, Python API also provided
> - 🎵 [**LMX package**](https://github.com/OMR-Research/lmx) - MusicXML tokenization
> - 🎵 [**LMX package v2**](https://github.com/OMR-Research/lmx/tree/v2-development) - MusicXML tokenization, IO, normalization, parsing, utilities (in development but usable)
>
> This repository ⬇️ contains the original code that gave rise to Zeus and LMX and is becoming outdated. It acts as a reference for the paper. For any up-to-date research or applications, use the code linked above ⬆️.


# OLiMPiC 1.0 dataset - an ICDAR 2024 Paper

This repository contains the source code for the article:

> **Practical End-to-End Optical Music Recognition for Pianoform Music**<br>
> https://link.springer.com/chapter/10.1007/978-3-031-70552-6_4

In which we:

1. Create a dataset of synthetic and scanned pianoform music for end-to-end OMR, called OLiMPiC. The dataset is built upon the [OpenScore Lieder Corpus](https://github.com/OpenScore/Lieder).
2. We introduce the LMX format (Linearized MusicXML) and define the linearization and delinearization procedures (see [MusicXML Linearization](#musicxml-linearization) section).
3. We train a baseline, state-of-the-art model called Zeus on this dataset (see [Zeus model](#zeus-model) and [TEDn evaluation metric](#tedn-evaluation-metric) sections).
4. We compare our dataset and model to the [GrandStaff dataset](https://link.springer.com/article/10.1007/s10032-023-00432-z).

If you want to start tinkering with the code, read the [After cloning](#after-cloning) section. If you build upon this work, read the [Acknowledgement](#acknowledgement) section.


## MusicXML Linearization

Linearized MusicXML is a sequential format convertible to and from MusicXML (with minimal losses), that can be used to train img2seq ML models. The conversions are implemented in the `app.linearization` module by classes `Linearizer` and `Delinearizer`. These classes are built to convert a single system (or a part when ignoring system breaks). But you can use the CLI wrapper instead:

```bash
# MusicXML -> LMX (accepts both XML and MXL)
python3 -m app.linearization linearize example.musicxml # produces example.lmx
python3 -m app.linearization linearize example.mxl # produces example.lmx
cat input.musicxml | python3 -m app.linearization linearize - # prints to stdout (only uncompressed XML input)

# LMX -> MusicXML (only uncompressed XML output available)
python3 -m app.linearization delinearize input.lmx # produces example.musicxml
cat input.lmx | python3 -m app.linearization delinearize - # prints to stdout
```

The `app.linearization.vocabulary` module defines all the LMX tokens.

To read more about the linearization process, see the [`docs/linearized-musicxml.md`](docs/linearized-musicxml.md) documentation file.


## Datasets

The final datasets can be downloaded from the [Releases page](https://github.com/ufal/olimpic-icdar24/releases) of this repository.

The module `app.datasets` contains submodules for building the individual datasets:

1. The `splits` module defines the train/dev/test splits for the OLiMPiC dataset
2. The `synthetic` module defines the synthetic-image OLiMPiC dataset (train, dev, test)
3. The `scanned` module defines the scanned-image OLiMPiC dataset (only dev and test)
4. The `grandstaff` module defines the Grandstaff-LMX extension for the GrandStaff dataset.

All modules export a CLI `__main__.py` to execute certain commands. To learn more about how these datasets are built, study the source code for the `build` command.

The exact OpenScore Lieder scores in the train/dev/test partitions are defined in `app.datasets.splits.data` folder and can also be imported as a python module.

The manual annotation process behind the `scanned` OLiMPiC dataset dataset was powered by Inkscape and CLI commands `load-workbench` and `save-workbench`. The first one creates a `workbench.svg` inkscape file, then the user annotates the bounding boxes, and then the second command consumes the file and updates corresponding dataset values.

Screenshot from the annotation process:

<img src="docs/img/annotating-scanned-dataset.png">


## Zeus model

Zeus is the OMR model for the OLiMPiC dataset. It is described and implemented in the [`zeus`](zeus) folder of this repository.


## TEDn evaluation metric

The module `app.evaluation` contains an implementation of the TEDn tree-edit-distance evaluation metric from the paper:

> **Further Steps towards a Standard Testbed for Optical Music Recognition**<br>
> Jan Hajič jr., Jiří Novotný, Pavel Pecina, Jaroslav Pokorný<br>
> 17th International Society for Music Information Retrieval Conference (ISMIR 2016)<br>
> https://s18798.pcdn.co/ismir2016/wp-content/uploads/sites/2294/2016/07/289_Paper.pdf

The file [`app.evaluation.TEDn`](app/evaluation/TEDn.py) implements the TEDn metric as a standalone python file with only the `zss` and `Levenshtein` dependencies, taking `xml.etree.ElementTree` elements as its inputs.

But in practise, you want to use (or at least understand) the [`TEDn_lmx_xml.py`](app/evaluation/TEDn_lmx_xml.py) file, as it exposes a nicer string-based API and contains the necessary canonicalization, pre-processing and post-processing needed. This function depends on the `app.linearization` and `app.symbolic` modules.

> **Note:** The TEDn metric is computationally expensive, so you need to do the evaluation system-wise. It will not compute the error for a whole score, since the time and memory complexity goes through the roof. Evaluation of one system (cca 4 measures) takes from 30 to 120 seconds. The evaluation time seems to grow cca quadratically with the size of the trees.


## After cloning

Setup Python venv (tested with python 3.8 and 3.10):

```bash
python3 -m venv .venv

.venv/bin/pip3 install --upgrade pip

# to run the linearization, dataset building, and evaluation
.venv/bin/pip3 install -r requirements.txt

# to run the Zeus model
.venv/bin/pip3 install -r zeus/requirements.txt
```

Install dependencies:

```bash
# (all of the installations are done locally within the repository)

# to be able to build the datasets yourself
make install-musescore
make install-open-score-lieder

# to just download the finished datasets
# (from this repo's releases page)
make install-olimpic-synthetic
make install-olimpic-scanned
make install-grandstaff-lmx
```


## Licenses

Datasets are available under CC BY-SA license.

- OLiMPiC synthetic
- OLiMPiC scanned
- GrandStaff-LMX (only the added `.lmx` and `.musicxml` files)

The trained Zeus model is available under CC BY-SA license (available for download in the releases page).

Source code in this repository is available under the MIT license.


## Acknowledgement

If you publish material based on the LMX linearizer or the LMX data, we request you to include a reference to paper \[1\]. If you use the OLiMPiC dataset, you should also include a reference to the OpenScore Lieder corpus \[2\]. If you use the GrandStaff-LMX dataset, you should include a reference to the GradStaff dataset \[3\].


## References

\[1\] Jiří Mayer, Milan Straka, Jan Hajič jr., Pavel Pecina. Practical End-to-End Optical Music Recognition for Pianoform Music. *18th International Conference on Document Analysis and Recognition, ICDAR 2024.* Athens, Greece, August 30 - September 4, pp. 55-73, 2024.<br>
**DOI:** https://doi.org/10.1007/978-3-031-70552-6_4<br>
**GitHub:** https://github.com/ufal/olimpic-icdar24

\[2\] Mark Gotham, Robert Haigh, Petr Jonas. The OpenScore Lieder Corpus. *Music Encoding Conference.* Online, July 19-22, pp. 131-136, 2022.<br>
**DOI:** https://doi.org/10.17613/1my2-dm23<br>
**GitHub:** https://github.com/OpenScore/Lieder

\[3\] Antonio Ríos-Villa, David Rizo, José M. Iñesta, Jorge Calvo-Zaragoza. End-to-end optical music recognition for pianoform sheet music. *International Journal on Document Analysis and Recognition, IJDAR* vol. **26**, pp. 347-362, (2023)<br>
**DOI:** https://doi.org/10.1007/s10032-023-00432-z<br>
**GitHub:** https://github.com/multiscore/e2e-pianoform
