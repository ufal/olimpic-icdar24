SLICE_COUNT=50

.venv/bin/python3 -m app.datasets.synthetic_02 clear

# THE xvfb-run IS IMPORTANT FOR MUSESCORE! (virtual X-Server)
# -a means it will allocate a different server number if 99 is taken
# (which happens when there are more tasks on one worker machine)
CMD="xvfb-run -a .venv/bin/python3 -m app.datasets.synthetic_02 build --slice_count $SLICE_COUNT --slice_index \$SLURM_PROCID"
srun -u -n $SLICE_COUNT -p cpu-ms bash -c "$CMD"

.venv/bin/python3 -m app.datasets.synthetic_02 finalize
