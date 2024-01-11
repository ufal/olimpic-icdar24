# Dataset `synthetic_01`

To build on your machine:

(run in repository root folder)

```bash
.venv/bin/python3 -m app.datasets.synthetic_01 clear
.venv/bin/python3 -m app.datasets.synthetic_01 build
.venv/bin/python3 -m app.datasets.synthetic_01 finalize
```

To run on the compute cluster with slurm:

```bash
# THE xvfb-run IS IMPORTANT FOR MUSESCORE! (virtual X-Server)
xvfb-run bash slurm/build_dataset_synthetic_01.sh
```
