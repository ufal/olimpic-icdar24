SLICE_COUNT=50

.venv/bin/python3 -m app.datasets.synthetic_01 clean

CMD=".venv/bin/python3 -m app.datasets.synthetic_01 build --slice_count $SLICE_COUNT --slice_index \$SLURM_PROCID"
srun -n $SLICE_COUNT -p cpu-ms bash -c "$CMD"

.venv/bin/python3 -m app.datasets.synthetic_01 finalize
