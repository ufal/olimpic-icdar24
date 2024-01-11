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
bash slurm/build_dataset_synthetic_01.sh
```
