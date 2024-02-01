from typing import Optional
from ..config import SYNTHETIC_DATASET_PATH
from ..musescore_corpus_conversion import musescore_corpus_conversion
from ..prepare_corpus_lmx_and_musicxml import prepare_corpus_lmx_and_musicxml
from ..prepare_corpus_png_systems import prepare_corpus_png_systems
from ..take_scores import take_scores
from ..transfer_samples import transfer_samples
from ..prepare_corpus_page_geometries import prepare_corpus_page_geometries


def build(
    slice_index: int,
    slice_count: int,
    inspect: Optional[int],
    linearize_only: bool,
    soft: bool
):
    scores, slice_index, slice_count = take_scores(
        train=True,
        dev=True,
        test=True,
        slice_index=slice_index,
        slice_count=slice_count,
        inspect=inspect
    )

    # prepare corpus MXL files
    musescore_corpus_conversion(scores=scores, format="mxl", soft=soft)

    # split xml files into systems and convert to sequences
    prepare_corpus_lmx_and_musicxml(scores=scores, soft=soft)

    # copy samples
    transfer_samples(
        scores=scores,
        corpus_glob="lmx/*.lmx",
        dataset_folder=SYNTHETIC_DATASET_PATH
    )
    transfer_samples(
        scores=scores,
        corpus_glob="musicxml/*.musicxml",
        dataset_folder=SYNTHETIC_DATASET_PATH
    )

    # if we only linearize, we are done
    if linearize_only:
        return

    # prepare corpus full-page SVG files
    musescore_corpus_conversion(scores=scores, format="svg", soft=soft)

    # prepare corpus full-page PNG files
    musescore_corpus_conversion(scores=scores, format="png", soft=soft)

    # detect systems in SVG pages
    prepare_corpus_page_geometries(scores=scores)

    # slice up full-page PNGs to system-level PNGs
    prepare_corpus_png_systems(scores=scores, soft=soft)

    # copy samples
    transfer_samples(
        scores=scores,
        corpus_glob="png/*.png",
        dataset_folder=SYNTHETIC_DATASET_PATH
    )
    