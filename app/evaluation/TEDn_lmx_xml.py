from ..linearization.Delinearizer import Delinearizer
from .TEDn import TEDn, TEDnResult
from ..symbolic.Pruner import Pruner
from ..symbolic.actual_durations_to_fractional import actual_durations_to_fractional
from ..symbolic.debug_compare import compare_parts
import xml.etree.ElementTree as ET
from typing import TextIO, Optional, Literal
import traceback


def TEDn_lmx_xml(
    predicted_lmx: str,
    gold_musicxml: str,
    flavor: Literal["full", "lmx"],
    debug=False,
    canonicalize_gold=True,
    errout: Optional[TextIO] = None
) -> TEDnResult:
    """
    Provides access to the TEDn metric with a nice string-based interface.

    Apart from having nice API, it also performs useful processing:
    - Delinearizes LMX back to MusicXML
    - Allows for "LMX-only" subset of MusicXML to be evaluated, see flavor="lmx"
    - Converts <duration> elements to fractional representation
        (number of quarter notes in fractions.Fraction stringified),
        which is necessary for proper <forward>, <backup> evaluation

    :param str predicted_lmx: The LMX string that was predicted by your img2seq model
    :param str gold_musicxml: The gold XML data loaded from the .musicxml annotation file
    :param str flavor: Use 'full' to do a regular TEDn computation, or 'lmx'
        to prune the gold target down to the set of musical concepts covered by LMX,
        for example removing <direction>, <harmony>, or <barline> elements.
    :param bool debug: Prints when a strict XML string comparison fails to get
        some idea about the places the model makes mistakes.
    :param bool canonicalize_gold: Run XML canonicalization on the gold string.
        Not necessary, but recommended. It primarily strips away whitespace
        (but TEDn ignores whitespace anyway).
    :param Optional[TextIO] errout: Delinearizer soft and hard errors are sent here.
    """

    assert flavor in {"full", "lmx"}

    # preprocess gold XML to remove whitespace
    # (not necessary after the TEDn .strip() bugfix, but present just in case...)
    if canonicalize_gold:
        gold_musicxml = ET.canonicalize(
            gold_musicxml,
            strip_text=True
        )

    # prepare gold data
    gold_score = ET.fromstring(gold_musicxml)
    assert gold_score.tag == "score-partwise"
    gold_parts = gold_score.findall("part")
    assert len(gold_parts) == 1
    gold_part = gold_parts[0]
    actual_durations_to_fractional(gold_part) # evaluate in fractional durations

    # prepare predicted data
    try:
        delinearizer = Delinearizer(
            errout=errout,
            keep_fractional_durations=True # evaluate in fractional durations
        )
        delinearizer.process_text(predicted_lmx)
        predicted_part = delinearizer.part_element
    except Exception:
        # should not happen, unless there's a bug in the delinearizer
        if errout is not None:
            print("DELINEARIZATION CRASHED:", traceback.format_exc(), file=errout)
        predicted_part = ET.Element("part") # pretend empty output
    
    # prune down to the elements that we actually predict
    # (otherwise TEDn penalizes missing <direction> and various ornaments)
    if flavor == "lmx":
        pruner = Pruner(
            
            # these are acutally also ignored by TEDn
            prune_durations=False, # MUST BE FALSE! Is used in backups and forwards
            prune_measure_attributes=False,
            prune_prints=True,
            prune_slur_numbering=True,

            # these measure elements are not encoded in LMX, prune them
            prune_directions=True,
            prune_barlines=True,
            prune_harmony=True,
            
        )
        pruner.process_part(gold_part)
        pruner.process_part(predicted_part)

    if debug:
        compare_parts(expected=gold_part, given=predicted_part)

    return TEDn(predicted_part, gold_part)
    # return TEDnResult(1, 1, 1) # debugging
