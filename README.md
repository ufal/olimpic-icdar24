# ICDAR 2024 Paper

Install dependencies:

```
make install-lilypond
make install-musescore
make install-open-score-lieder-dataset
```

Setup Python venv (tested with python 3.10.12):

```
python3 -m venv .venv

.venv/bin/pip3 install --upgrade pip

.venv/bin/pip3 install -r requirements.txt
```

Prepare the Open Score Lieder data for training.

```
make prepare-lieder-svg-and-mxl-files

# on the compute cluster run in virtual X-Server:
xvfb-run make prepare-lieder-svg-and-mxl-files
```
